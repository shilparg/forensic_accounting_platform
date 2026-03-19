import os
import requests
import pymongo
import certifi
import re
import warnings
from datetime import datetime
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from dotenv import load_dotenv, find_dotenv
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
load_dotenv(find_dotenv(usecwd=True), override=True)

ca = certifi.where()
client = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile=ca)
collection = client["forensic_accounting"]["raw_sec_filings"]

HEADERS = {'User-Agent': os.getenv("SEC_USER_AGENT"), 'Accept-Encoding': 'gzip, deflate'}

def calculate_similarity(new_text, ticker):
    prev_doc = collection.find_one({"ticker": ticker}, sort=[("fiscal_year", -1)])
    if not prev_doc or "parsed_text_sample" not in prev_doc:
        return 1.0
    try:
        vec = TfidfVectorizer().fit_transform([prev_doc["parsed_text_sample"], new_text])
        return float(cosine_similarity(vec[0:1], vec[1:2])[0][0])
    except:
        return 1.0

def get_latest_10k_url(cik):
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200: return None, None, None
        
    filings = response.json()['filings']['recent']
    for idx, form in enumerate(filings['form']):
        if form == '10-K':
            f_date = filings['filingDate'][idx]
            f_year = int(f_date.split('-')[0])
            acc_num = filings['accessionNumber'][idx].replace('-', '')
            doc_name = filings['primaryDocument'][idx]
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num}/{doc_name}"
            return doc_url, f_date, f_year
    return None, None, None

def run_extraction():
    # In full production, this reads the JSON dumped by Dagster's first asset.
    # For now, it defaults to the tech peer group for stability.
    target_dict = {"AAPL": "320193", "MSFT": "789019", "NVDA": "1045810", "META": "1326801"}
    
    for ticker, cik in target_dict.items():
        doc_url, filing_date, actual_year = get_latest_10k_url(cik)
        if not doc_url: continue

        response = requests.get(doc_url, headers=HEADERS)
        soup = BeautifulSoup(response.content, features="lxml")
        filing_text = re.sub(r'\s+', ' ', soup.get_text(separator=' ')).strip()
        
        analysis = TextBlob(filing_text)
        similarity = calculate_similarity(filing_text, ticker)

        collection.insert_one({
            "ticker": ticker,
            "cik": str(cik),
            "fiscal_year": actual_year,
            "sentiment_score": analysis.sentiment.polarity,
            "similarity_index": similarity,
            "extraction_timestamp": datetime.now(),
            "parsed_text_sample": filing_text[:30000]
        })

if __name__ == "__main__":
    run_extraction()