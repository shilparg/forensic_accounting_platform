import os
import pymongo
import certifi
from dotenv import load_dotenv, find_dotenv

# 1. Environment Setup
load_dotenv(find_dotenv(usecwd=True), override=True)

def verify_extraction_quality():
    """
    Reconciled: Acts as a Data Quality Gate before Cloud Sync.
    Ensures all fields for the 'Weighted Risk Score' are present.
    """
    mongo_uri = os.getenv("MONGO_URI")
    ca = certifi.where()

    print(f"🔌 Connecting to MongoDB Atlas for Quality Audit...")
    client = pymongo.MongoClient(mongo_uri, tlsCAFile=ca)
    db = client["forensic_accounting"]
    collection = db["raw_sec_filings"]

    # 2. Audit the Collection
    doc_count = collection.count_documents({})
    print(f"📊 Total documents in Landing Zone: {doc_count}")

    if doc_count == 0:
        print("❌ FATAL: Landing Zone is empty. Extraction failed.")
        return False

    # 3. Deep Forensic Audit (Checking specific fields for BQ/dbt)
    print("\n📋 Forensic Integrity Check (Latest Batch):")
    recent_docs = collection.find().sort("extraction_timestamp", -1).limit(5)

    valid_records = 0
    for d in recent_docs:
        ticker = d.get('ticker', 'UNKNOWN')
        
        # Check for 'The Missing Payload' fields
        has_sentiment = 'sentiment_score' in d
        has_subjectivity = 'subjectivity_score' in d # Required for Red Flag Report
        has_text = len(d.get('parsed_text_sample', '')) > 1000
        
        status = "✅ PASS" if (has_sentiment and has_subjectivity and has_text) else "❌ FAIL"
        
        print(f"   -> Ticker: {ticker:<5} | Sent: {has_sentiment} | Subj: {has_subjectivity} | Text: {has_text} | Status: {status}")
        
        if status == "✅ PASS":
            valid_records += 1

    # 4. Content Integrity Check (Your original logic)
    latest_doc = collection.find_one(sort=[("extraction_timestamp", -1)])
    text = latest_doc.get('parsed_text_sample', 'EMPTY')
    print(f"\n--- 📝 Content Sample ({ticker}) ---")
    print(f"{text[:300]}...")

    if valid_records > 0:
        print(f"\n🟢 Quality Check Passed: {valid_records} records ready for BigQuery Sync.")
        return True
    else:
        print("\n🔴 Quality Check Failed: No valid records found for downstream AI.")
        return False

if __name__ == "__main__":
    verify_extraction_quality()