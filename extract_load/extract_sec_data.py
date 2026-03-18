import os
import sys
import json
import argparse
import requests
import pymongo
import certifi
import re
import warnings
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Environment & Database Setup (Simplified Version)
env_path = find_dotenv(usecwd=True)
load_dotenv(env_path, override=True)

mongo_uri = os.getenv("MONGO_URI")

# We use ONLY tlsAllowInvalidCertificates to bypass SSL errors 
# without causing a URI conflict.
# client = pymongo.MongoClient(
#     mongo_uri,
#     tls=True,
#     tlsAllowInvalidCertificates=True, 
#     serverSelectionTimeoutMS=5000
# )

client = pymongo.MongoClient(mongo_uri) # No SSL parameters needed for localhost!

db = client["forensic_accounting"]
collection = db["raw_sec_filings"]

HEADERS = {
    'User-Agent': os.getenv("SEC_USER_AGENT", "YourName (email@example.com)"),
    'Accept-Encoding': 'gzip, deflate'
}

# 2. Forensic Utilities
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
    """Uses lxml to extract and clean text for analysis."""
    response = requests.get(doc_url, headers=HEADERS)
    response.raise_for_status()
    # Use lxml for better HTML/XML handling in Python 3.13
    soup = BeautifulSoup(response.content, features="lxml")
    raw_text = soup.get_text(separator=' ')
    return re.sub(r'\s+', ' ', raw_text).strip()

# 3. Core Pipeline
def get_latest_10k_url(cik, target_year=None):
    """Fetches the 10-K URL. If year is provided, it attempts to find that specific filing."""
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    
    filings = data['filings']['recent']
    for idx, form in enumerate(filings['form']):
        if form == '10-K':
            f_date = filings['filingDate'][idx]
            f_year = int(f_date.split('-')[0])
            
            # If target_year is specified, only take that year. Otherwise, take latest.
            if target_year and f_year != int(target_year):
                continue
                
            acc_num = filings['accessionNumber'][idx].replace('-', '')
            doc_name = filings['primaryDocument'][idx]
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num}/{doc_name}"
            return doc_url, f_date, f_year
            
    return None, None, None

def run_extraction_pipeline(cik, ticker, year=None):
    print(f"[{datetime.now()}] 🚀 Auditing {ticker} (Target Year: {year if year else 'Latest'})")
    
    doc_url, filing_date, actual_year = get_latest_10k_url(cik, year)
    
    if not doc_url:
        print(f"❌ No 10-K found for {ticker} in year {year}")
        return

    filing_text = extract_and_clean_text(doc_url)
    
    # Forensic Scoring
    analysis = TextBlob(filing_text)
    similarity = calculate_similarity(filing_text, ticker)

    document_payload = {
        "ticker": ticker,
        "cik": cik,
        "form_type": "10-K",
        "fiscal_year": actual_year,
        "filing_date": filing_date,
        "sentiment_score": analysis.sentiment.polarity,
        "subjectivity_score": analysis.sentiment.subjectivity,
        "similarity_index": similarity,
        "source_url": doc_url,
        "extraction_timestamp": datetime.now(),
        "parsed_text_sample": filing_text[:30000] # Increased for better BigQuery analysis
    }
    
    collection.insert_one(document_payload)
    print(f"✅ Success! Sent: {document_payload['sentiment_score']:.2f}, Sim: {similarity:.2f}")

# 4. Command Line Interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", action="store_true", help="Run everything in config/tickers.json")
    parser.add_argument("--ticker", help="Single ticker e.g. AAPL")
    parser.add_argument("--cik", help="Single CIK e.g. 320193")
    parser.add_argument("--year", type=int, help="Specific fiscal year")
    
    args = parser.parse_args()

    if args.batch:
        config_path = os.path.join(os.path.dirname(__file__), '../config/tickers.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            # Combine targets and peers
            all_audit = config.get('investigation_target', []) + config.get('peer_group', [])
            for item in all_audit:
                for y in item.get('years', [None]):
                    run_extraction_pipeline(item['cik'], item['ticker'], y)
    elif args.ticker and args.cik:
        run_extraction_pipeline(args.cik, args.ticker, args.year)
    else:
        # Default behavior for safety
        run_extraction_pipeline(cik="320193", ticker="AAPL")