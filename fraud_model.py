import pandas as pd
from google.cloud import bigquery
import yfinance as yf
import os

# 1. Source A: MAXIMUM BigQuery Data (SEC EDGAR)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-service-account.json"
client = bigquery.Client(project="forensic-accounting-bot")

print("Pulling ALL available SEC metadata and NLP metrics from Google Cloud...")
# Using SELECT * guarantees you capture every column Pandas flattened earlier
query = """
    SELECT *
    FROM `forensic-accounting-bot.raw_sec_landing.raw_sec_filings`
"""
sec_df = client.query(query).to_dataframe()

print(f" -> Grabbed {len(sec_df.columns)} columns from BigQuery.")


# 2. Source B: MAXIMUM Yahoo Finance Data (Market Reality)
print("\nFetching comprehensive market and institutional data from Yahoo Finance...")
market_data = []

# Loop through the unique tickers in your dataset
for ticker in sec_df['ticker'].dropna().unique():
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extracting the maximum amount of relevant forensic and valuation metrics
        market_data.append({
            'ticker': ticker,
            # Risk & Volatility
            'short_ratio': info.get('shortRatio'),
            'short_percent_of_float': info.get('shortPercentOfFloat'),
            'beta': info.get('beta'),
            # Valuation
            'market_cap': info.get('marketCap'),
            'enterprise_value': info.get('enterpriseValue'),
            'trailing_pe': info.get('trailingPE'),
            'price_to_book': info.get('priceToBook'),
            # Financial Health (To compare against what management says in the 10-K)
            'debt_to_equity': info.get('debtToEquity'),
            'return_on_equity': info.get('returnOnEquity'),
            'operating_margin': info.get('operatingMargins'),
            'current_ratio': info.get('currentRatio'),
            # Institutional Trust
            'held_percent_insiders': info.get('heldPercentInsiders'),
            'held_percent_institutions': info.get('heldPercentInstitutions')
        })
        print(f" -> Successfully pulled expanded market data for {ticker}")
    except Exception as e:
        print(f" -> Could not pull data for {ticker}: {e}")

market_df = pd.DataFrame(market_data)


# 3. Merge Source A and Source B
print("\nMerging sources into master dataset...")
final_df = pd.merge(sec_df, market_df, on='ticker', how='left')


# 4. Apply The Forensic Fraud Logic
final_df['fraud_risk_status'] = 'Low Risk'

# A more sophisticated threshold using the new data:
# Highly negative sentiment + High short interest + High Debt to Equity
critical_risk_conditions = (
    (final_df['sentiment_score'] < 0.1) &  
    (final_df['short_ratio'] > 4.0) &
    (final_df['debt_to_equity'] > 150.0) # Debt is 1.5x equity
)

final_df.loc[critical_risk_conditions, 'fraud_risk_status'] = 'CRITICAL FRAUD RISK'


# 5. Export for Analysis
output_filename = "comprehensive_forensic_dataset.csv"
final_df.to_csv(output_filename, index=False)

print(f"\nSUCCESS! Master dataset created with {len(final_df.columns)} total features.")
print(f"Data saved to: {output_filename}")