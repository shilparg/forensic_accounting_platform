import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

DATA_PATH = "ai_scored_forensic_dataset.csv"

def run_presentation_visuals():
    df = pd.read_csv(DATA_PATH)
    sns.set_theme(style="whitegrid")
    output_dir = "analysis/plots"
    os.makedirs(output_dir, exist_ok=True)

    # --- 1. Time-Series Narrative Drift (Fault-Tolerant) ---
    plt.figure(figsize=(10, 5))
    target_company = df['ticker'].iloc[0] 
    company_data = df[df['ticker'] == target_company].sort_values('fiscal_year')
    
    # Dynamically select the metric to plot
    drift_metric = 'similarity_index' if 'similarity_index' in df.columns else 'word_count'
    drift_label = 'Boilerplate Index' if drift_metric == 'similarity_index' else 'Word Count (Density)'

    if len(company_data) > 1:
        ax1 = sns.lineplot(data=company_data, x='fiscal_year', y=drift_metric, color='blue', marker='o', label=drift_label)
        ax2 = plt.twinx()
        sns.lineplot(data=company_data, x='fiscal_year', y='sentiment_score', color='red', marker='X', ax=ax2, label='Sentiment Score')
        
        plt.title(f"{target_company}: 5-Year Narrative Drift vs Sentiment", fontsize=14)
        plt.savefig(f"{output_dir}/narrative_drift_timeseries.png")
        print("✅ Saved Time-Series Plot.")

    # --- 2. AI Feature Importance (Radar Chart - Fault-Tolerant) ---
    anomalies = df[df['fraud_risk_status'] == 'CRITICAL ANOMALY']
    if not anomalies.empty:
        target = anomalies.iloc[0]
        avg = df.mean(numeric_only=True)
        
        labels = ['Sentiment', 'Density/Words', 'Short Ratio', 'Debt/Equity']
        
        # Safely get values, defaulting to 0 if the ML model dropped the column
        target_stats = [
            target.get('sentiment_score', 0), 
            target.get('density_index', target.get('word_count', 0)), 
            target.get('short_ratio', 0), 
            target.get('debt_to_equity', 0)
        ]
        avg_stats = [
            avg.get('sentiment_score', 0), 
            avg.get('density_index', avg.get('word_count', 0)), 
            avg.get('short_ratio', 0), 
            avg.get('debt_to_equity', 0)
        ]
        
        # Math to close the radar circle
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        target_stats += target_stats[:1]
        avg_stats += avg_stats[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, target_stats, color='red', linewidth=2, label=f"Anomaly: {target['ticker']}")
        ax.fill(angles, target_stats, color='red', alpha=0.25)
        ax.plot(angles, avg_stats, color='gray', linewidth=2, linestyle='dashed', label='Industry Average')
        
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.title("AI Decision Matrix: Why it was flagged", y=1.08)
        
        plt.savefig(f"{output_dir}/ai_radar_chart.png", bbox_inches='tight')
        print("✅ Saved Radar Chart.")

if __name__ == "__main__":
    run_presentation_visuals()