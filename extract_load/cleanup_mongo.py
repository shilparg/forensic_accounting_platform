import os
import certifi
import pymongo
from dotenv import load_dotenv, find_dotenv

# 1. Load environment
load_dotenv(find_dotenv(usecwd=True), override=True)

def sanitize_landing_zone():
    print("🧹 Starting MongoDB Sanitization (Pre-Audit Cleanup)...")
    
    # Setup Connection with your SSL fix
    ca = certifi.where()
    mongo_uri = os.getenv("MONGO_URI")
    client = pymongo.MongoClient(mongo_uri, tlsCAFile=ca)
    
    db = client["forensic_accounting"]
    collection = db["raw_sec_filings"]

    # 1. Remove records with missing Fiscal Year (Your original logic)
    result_fy = collection.delete_many({"fiscal_year": None})
    
    # 2. Remove records with empty text (Prevents ML model from crashing)
    result_text = collection.delete_many({"parsed_text_sample": ""})
    
    # 3. NEW RECONCILIATION: Remove records missing core NLP scores
    # This ensures dbt's weighted risk calculation doesn't fail
    result_scores = collection.delete_many({
        "$or": [
            {"sentiment_score": {"$exists": False}},
            {"subjectivity_score": {"$exists": False}}
        ]
    })

    print(f"✅ Cleanup Complete:")
    print(f"   - Removed {result_fy.deleted_count} records with missing years.")
    print(f"   - Removed {result_text.deleted_count} records with empty text.")
    print(f"   - Removed {result_scores.deleted_count} records with corrupted NLP metadata.")

if __name__ == "__main__":
    sanitize_landing_zone()