import os
import json
import subprocess
import requests
from dagster import Config, asset, Definitions

# --- 1. Web UI Configuration Panel ---
class AuditConfig(Config):
    run_mode: str = "peer_group"  # Options: 'peer_group', 'all_sec', 'custom'
    custom_tickers: list[str] = ["AAPL", "MSFT"]

# --- 2. PHASE 1: Target Identification ---
@asset
def determine_targets(config: AuditConfig) -> str:
    """Fetches targets and creates a {Ticker: CIK} JSON map for the extractor."""
    target_map = {}
    
    if config.run_mode == "peer_group":
        # Standard Capstone Test Group
        target_map = {"AAPL": "320193", "MSFT": "789019", "NVDA": "1045810", "GOOGL": "1652044"}
        
    elif config.run_mode == "all_sec":
        # Dynamic fetch from SEC Master API
        headers = {'User-Agent': os.getenv("SEC_USER_AGENT", "ForensicBot (test@test.com)")}
        response = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
        if response.status_code == 200:
            # Taking top 10 for demonstration limits
            for k, v in list(response.json().items())[:10]:
                target_map[v['ticker']] = str(v['cik_str'])
                
    return json.dumps(target_map)

# --- 3. PHASE 2: Extraction & Data Quality Gates ---
@asset
def run_extraction(determine_targets: str):
    """Sanitizes landing zone, extracts data, and verifies quality."""
    print("🧹 Phase 2a: Sanitizing MongoDB Landing Zone...")
    subprocess.run(["python", "extract_load/cleanup_mongo.py"], check=True)
    
    print("📥 Phase 2b: Running SEC SEC Extraction...")
    subprocess.run(["python", "extract_load/extract_sec_data.py", "--ticker_map", determine_targets], check=True)
    
    print("🛡️ Phase 2c: Verifying Data Quality...")
    subprocess.run(["python", "extract_load/verify_mongo.py"], check=True)
    
    return "Extraction & DQ Checks Passed"

# --- 4. PHASE 3: Cloud Synchronization ---
@asset
def cloud_sync(run_extraction: str):
    """Pushes validated MongoDB payloads into BigQuery."""
    print("☁️ Phase 3: Syncing to Google Cloud BigQuery...")
    subprocess.run(["python", "extract_load/mongo_to_bigquery.py"], check=True)
    return "Synced to BigQuery"

# --- 5. PHASE 4: dbt Transformation (The Accounting Logic) ---
@asset
def run_dbt_models(cloud_sync: str):
    """Runs all SQL models (Z-Scores, Red Flags, Narrative Drift)."""
    print("🔄 Phase 4: Executing dbt transformations...")
    # --profiles-dir . ensures it finds your local profiles.yml to avoid the "Not Found" error
    subprocess.run(["dbt", "build", "--profiles-dir", "."], cwd="transform_dbt", check=True)
    return "dbt Analytics Engine Complete"

# --- 6. PHASE 5: AI & Executive Reporting ---
@asset
def ai_analysis_and_output(run_dbt_models: str):
    """Scores anomalies, generates all 5 presentation plots, and sends alerts."""
    print("🧠 Phase 5a: Running Machine Learning (Isolation Forest)...")
    subprocess.run(["python", "ml_engine/fraud_model.py"], check=True)
    
    print("📊 Phase 5b: Generating Executive Visuals...")
    subprocess.run(["python", "analysis/density_visualizer.py"], check=True)
    subprocess.run(["python", "analysis/forensic_benchmarks.py"], check=True)
    subprocess.run(["python", "analysis/forensic_triangulation.py"], check=True)
    subprocess.run(["python", "analysis/executive_visuals.py"], check=True)
    
    print("📧 Phase 5c: Dispatching Gen-AI Email Alerts...")
    subprocess.run(["python", "analysis/forensic_alerter.py"], check=True)
    
    return "Audit Platform Execution Complete"

# --- 7. Dagster Definitions ---
defs = Definitions(
    assets=[
        determine_targets, 
        run_extraction, 
        cloud_sync, 
        run_dbt_models, 
        ai_analysis_and_output
    ]
)