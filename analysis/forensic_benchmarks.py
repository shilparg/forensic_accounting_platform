import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Load the merged SEC + Yahoo Finance data
DATA_PATH = "ai_scored_forensic_dataset.csv"

def run_benchmark_plots():
    df = pd.read_csv(DATA_PATH)
    sns.set_theme(style="white")
    output_dir = "analysis/plots"
    os.makedirs(output_dir, exist_ok=True)

    # --- PLOT 1: Industry Sentiment Boxplot ---
    # Highlights the outliers (Z-Score anomalies)
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='ticker', y='sentiment_score', palette="Set3")
    plt.title("Industry Sentiment Distribution: Identifying Outliers", fontsize=14)
    plt.savefig(f"{output_dir}/industry_sentiment_boxplot.png")
    print("✅ Saved Industry Boxplot.")

    # --- PLOT 2: Forensic Correlation Heatmap ---
    # Shows if Negative Sentiment correlates with High Debt or Short Interest
    plt.figure(figsize=(10, 8))
    
    # Dynamically select columns that actually exist in the CSV
    desired_cols = ['sentiment_score', 'risk_score', 'short_ratio', 'debt_to_equity', 'word_count', 'similarity_index']
    corr_cols = [col for col in desired_cols if col in df.columns]
    
    corr_matrix = df[corr_cols].corr(numeric_only=True) # Added numeric_only to prevent string errors

    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title("Forensic Triangulation: SEC Metrics vs. Market Pressure", fontsize=14)
    plt.savefig(f"{output_dir}/forensic_correlation_heatmap.png")
    print("✅ Saved Correlation Heatmap.")

if __name__ == "__main__":
    run_benchmark_plots()