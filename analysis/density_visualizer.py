import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from google.cloud import bigquery

def plot_disclosure_density():
    client = bigquery.Client()
    # Pull the density model we just created
    df = client.query("SELECT * FROM `forensic_data.fct_disclosure_density`").to_dataframe()

    sns.set_theme(style="whitegrid")
    
    # Joint Plot: Shows both the scatter and the density distribution
    g = sns.jointplot(
        data=df, 
        x="word_count", 
        y="density_index", 
        hue="forensic_label",
        kind="scatter",
        palette={"POTENTIAL OBFUSCATION": "red", "HIGH NEGATIVE RISK": "orange", "NORMAL": "green"}
    )
    
    g.fig.suptitle("Forensic Audit: Disclosure Density vs. Obfuscation Risk", y=1.02)
    plt.savefig("analysis/plots/disclosure_density_matrix.png")
    print("✅ Density Visualization saved.")

if __name__ == "__main__":
    plot_disclosure_density()