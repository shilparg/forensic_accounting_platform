from dagster import asset

@asset
def raw_filings():
    """Run Meltano to ingest data."""
    # Logic to trigger: meltano run tap-sec-forensics target-bigquery
    return "Ingested"

@asset(deps=[raw_filings])
def dbt_analytics():
    """Run dbt to calculate Density, Drift, and Volatility."""
    # Logic to trigger: dbt run
    return "Analyzed"

@asset(deps=[dbt_analytics])
def seaborn_plots():
    """Generate the Anomaly and Red Flag plots."""
    # Logic to run analysis/plots.py
    return "Visualized"