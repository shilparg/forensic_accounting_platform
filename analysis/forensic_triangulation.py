import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Load the reconciled dataset (Source 1 + Source 2 + AI Scores)
DATA_PATH = "ai_scored_forensic_dataset.csv"

def run_triangulation_plots():
    df = pd.read_csv(DATA_PATH)
    sns.set_theme(style="darkgrid")
    output_dir = "analysis/plots"
    os.makedirs(output_dir, exist_ok=True)

    # --- PLOT 1: The "Smoking Gun" Regression ---
    # Links SEC Sentiment (Source 1) to Short Ratio (Source 2)
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x='sentiment_score', y='short_ratio', 
                scatter_kws={'s':100, 'alpha':0.5}, line_kws={'color':'red'})
    
    # Annotate the most critical anomalies
    for i in range(len(df)):
        if df.iloc[i]['fraud_risk_status'] == 'CRITICAL ANOMALY':
            plt.text(df.iloc[i]['sentiment_score'], df.iloc[i]['short_ratio'], 
                     df.iloc[i]['ticker'], color='black', weight='bold')
                     
    plt.title("Source 1 vs Source 2: Sentiment vs. Market Short Interest", fontsize=14)
    plt.savefig(f"{output_dir}/forensic_regression_analysis.png")
    print("✅ Saved Regression Analysis.")

    # --- PLOT 2: Audit Priority Matrix ---
    # Visualizes the results of your 'fct_red_flag_report.sql'
    plt.figure(figsize=(12, 4))
    # Fallback to sentiment_score if risk_score wasn't pulled from BigQuery
    target_metric = 'risk_score' if 'risk_score' in df.columns else 'sentiment_score'
    pivot_df = df.pivot_table(index='ticker', columns='fiscal_year', values=target_metric)

    sns.heatmap(pivot_df, annot=True, cmap="YlOrRd", cbar_kws={'label': 'Weighted Risk Score'})
    plt.title("Executive Audit Priority: Heatmap of Weighted Risk Scores", fontsize=14)
    plt.savefig(f"{output_dir}/audit_priority_heatmap.png")
    print("✅ Saved Audit Priority Heatmap.")

if __name__ == "__main__":
    run_triangulation_plots()