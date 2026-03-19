import os
import json
import requests
import pymongo
import certifi
import re
import argparse
import warnings
from datetime import datetime
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from dotenv import load_dotenv, find_dotenv
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Environment & Database Setup
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
load_dotenv(find_dotenv(usecwd=True), override=True)

def get_mongo_client():
    """Handles both local and Atlas SSL connections based on .env."""
    mongo_uri = os.getenv("MONGO_URI")
    try:
        # Reconciled: Uses your SSL fix for Atlas connections
        ca = certifi.where()
        return pymongo.MongoClient(mongo_uri, tlsCAFile=ca)
    except:
        # Fallback for local testing
        return pymongo.MongoClient(mongo_uri)

client = get_mongo_client()
db = client["forensic_accounting"]
collection = db["raw_sec_filings"]

HEADERS = {
    'User-Agent': os.getenv("SEC_USER_AGENT", "ForensicBot (shilpakangya2025@gmail.com)"),
    'Accept-Encoding': 'gzip, deflate'
}

# 2. Forensic Utilities (Your Original Logic)
def calculate_similarity(new_text, ticker):
    """Detects 'Reporting Inertia' by comparing with the last year in DB."""
    prev_doc = collection.find_one({"ticker": ticker}, sort=[("fiscal_year", -1)])
    if not prev_doc or "parsed_text_sample" not in prev_doc:
        return 1.0
    try:
        vec = TfidfVectorizer().fit_transform([prev_doc["parsed_text_sample"], new_text])
        return float(cosine_similarity(vec[0:1], vec[1:2])[0][0])
    except:
        return 1.0

def extract_and_clean_text(doc_url):
    """Uses lxml to extract and clean text for accurate dbt word counts."""
    response = requests.get(doc_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, features="lxml")
    raw_text = soup.get_text(separator=' ')
    # Reconciled: Ruthlessly cleans whitespace to ensure dbt density logic works
    return re.sub(r'\s+', ' ', raw_text).strip()

# 3. Core Extraction Logic
def get_latest_10k_url(cik, target_year=None):
    """Fetches the 10-K URL from SEC EDGAR."""
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return None, None, None
    
    data = response.json()
    filings = data['filings']['recent']
    for idx, form in enumerate(filings['form']):
        if form == '10-K':
            f_date = filings['filingDate'][idx]
            f_year = int(f_date.split('-')[0])
            
            if target_year and f_year != int(target_year):
                continue
                
            acc_num = filings['accessionNumber'][idx].replace('-', '')
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num}/{filings['primaryDocument'][idx]}"
            return doc_url, f_date, f_year
            
    return None, None, None

def process_ticker(ticker, cik, target_year=None):
    """The main audit function for a single company."""
    print(f"[{datetime.now()}] 🚀 Auditing {ticker} (Year: {target_year if target_year else 'Latest'})")
    
    doc_url, filing_date, actual_year = get_latest_10k_url(cik, target_year)
    if not doc_url:
        print(f"❌ No 10-K found for {ticker}")
        return

    filing_text = extract_and_clean_text(doc_url)
    analysis = TextBlob(filing_text)
    similarity = calculate_similarity(filing_text, ticker)

    # 4. Final Reconciled Payload (Bridges local MongoDB to BQ/dbt schema)
    document_payload = {
        "ticker": ticker.upper(),
        "cik": str(cik).zfill(10),
        "form_type": "10-K",
        "fiscal_year": int(actual_year),
        "filing_date": filing_date,
        "sentiment_score": float(analysis.sentiment.polarity),
        "subjectivity_score": float(analysis.sentiment.subjectivity), # Required for your Risk Report
        "similarity_index": float(similarity),
        "source_url": doc_url,
        "extraction_timestamp": datetime.now(),
        "parsed_text_sample": filing_text[:40000] # Increased for better Gemini AI analysis
    }
    
    collection.insert_one(document_payload)
    print(f"✅ Saved {ticker} FY{actual_year}. Sent: {document_payload['sentiment_score']:.2f}")

# 5. CLI Entry Point (For Dagster Integration)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker_map", help="JSON string of {ticker: cik} from Dagster UI")
    args = parser.parse_args()

    if args.ticker_map:
        # Dynamic execution via Dagster Web UI
        targets = json.loads(args.ticker_map)
        for t, c in targets.items():
            process_ticker(t, c)
    else:
        # Manual execution / testing
        process_ticker("AAPL", "320193")