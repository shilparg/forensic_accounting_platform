import os
import certifi
from pymongo import MongoClient
from google.cloud import bigquery
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

# 1. Environment Setup
load_dotenv(find_dotenv(usecwd=True), override=True)

# 2. Reconciled BigQuery Connection (WSL/Windows Path Safe)
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-service-account.json")
if "\\" in credentials_path or "wsl.localhost" in credentials_path:
    credentials_path = "./gcp-service-account.json"

bq_client = bigquery.Client.from_service_account_json(credentials_path)

# 3. MongoDB Connection (Your SSL Fix)
ca = certifi.where()
mongo_client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=ca)
db = mongo_client["forensic_accounting"]
collection = db["raw_sec_filings"]

def sync_mongo_to_bigquery():
    project_id = bq_client.project
    dataset_id = os.getenv("BQ_DATASET_ID", "forensic_data")
    table_id = f"{project_id}.{dataset_id}.raw_filings"

    print(f"[{datetime.now()}] 🔄 Syncing MongoDB ➔ BigQuery Table: {table_id}")
    
    mongo_docs = list(collection.find({}))
    if not mongo_docs:
        print("⚠️ No data found in MongoDB.")
        return

    # 4. Reconciled Schema Mapping (Bridges Extraction to dbt)
    rows_to_insert = []
    for doc in mongo_docs:
        row = {
            "ticker": str(doc.get("ticker")).upper(),
            "cik": str(doc.get("cik")).zfill(10),
            "fiscal_year": int(doc.get("fiscal_year")) if doc.get("fiscal_year") else None,
            "filing_date": str(doc.get("filing_date")),
            "sentiment_score": float(doc.get("sentiment_score", 0.0)),
            "subjectivity_score": float(doc.get("subjectivity_score", 0.0)), # Reconciled field
            "similarity_index": float(doc.get("similarity_index", 1.0)),
            "source_url": str(doc.get("source_url", "")),
            "extraction_timestamp": doc.get("extraction_timestamp").isoformat() if doc.get("extraction_timestamp") else None,
            "parsed_text_sample": str(doc.get("parsed_text_sample", ""))[:40000] # Increased context
        }
        rows_to_insert.append(row)

    # 5. BigQuery Job Configuration
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("ticker", "STRING"),
            bigquery.SchemaField("cik", "STRING"),
            bigquery.SchemaField("fiscal_year", "INTEGER"),
            bigquery.SchemaField("filing_date", "STRING"),
            bigquery.SchemaField("sentiment_score", "FLOAT"),
            bigquery.SchemaField("subjectivity_score", "FLOAT"),
            bigquery.SchemaField("similarity_index", "FLOAT"),
            bigquery.SchemaField("source_url", "STRING"),
            bigquery.SchemaField("extraction_timestamp", "TIMESTAMP"),
            bigquery.SchemaField("parsed_text_sample", "STRING"),
        ],
        write_disposition="WRITE_TRUNCATE", # Replaces old data with the latest audit batch
    )

    print(f"⏳ Loading {len(rows_to_insert)} records into BigQuery...")
    job = bq_client.load_table_from_json(rows_to_insert, table_id, job_config=job_config)
    job.result()  # Wait for completion

    print(f"✅ SUCCESS: Data is now live for dbt transformations.")

if __name__ == "__main__":
    sync_mongo_to_bigquery()