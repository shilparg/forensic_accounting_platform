import pandas as pd
import numpy as np
import yfinance as yf
import os
from google.cloud import bigquery
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

# 1. Connection
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-service-account.json"
client = bigquery.Client()

# 2. Source A: SEC Metrics from your dbt model
print("🧠 Fetching dbt metrics...")
sec_df = client.query("SELECT * FROM `forensic-accounting-bot.forensic_data.fct_disclosure_density`").to_dataframe()

# 3. Source B: Expanded Market Data (From your original script)
market_data = []
for ticker in sec_df['ticker'].dropna().unique():
    try:
        info = yf.Ticker(ticker).info
        market_data.append({
            'ticker': ticker,
            'short_ratio': info.get('shortRatio', 0),
            'debt_to_equity': info.get('debtToEquity', 0),
            'return_on_equity': info.get('returnOnEquity', 0),
            'operating_margin': info.get('operatingMargins', 0),
            'held_institutions': info.get('heldPercentInstitutions', 0)
        })
    except: pass

master_df = pd.merge(sec_df, pd.DataFrame(market_data), on='ticker', how='left')

# 4. The AI Model (Isolation Forest)
# We use ALL these features to find anomalies multi-dimensionally
features = ['sentiment_score', 'density_index', 'short_ratio', 'debt_to_equity', 'return_on_equity', 'operating_margin']
X = master_df[features].fillna(0)
X_scaled = StandardScaler().fit_transform(X)

model = IsolationForest(contamination=0.10, random_state=42)
master_df['fraud_risk_status'] = ['CRITICAL ANOMALY' if x == -1 else 'NORMAL' for x in model.fit_predict(X_scaled)]

master_df.to_csv("ai_scored_forensic_dataset.csv", index=False)
print("✅ AI Scoring complete with expanded feature set.")