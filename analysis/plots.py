# 1. The "Outlier" Boxplot (Peer Comparison)
# This shows if one company is a "loner" outside the industry group.

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="fiscal_year", y="sentiment_score", palette="Set2")
sns.swarmplot(data=df, x="fiscal_year", y="sentiment_score", color=".25")
plt.title("Industry Sentiment Distribution: Identifying Outliers")

# 2. The "Regression Anomaly" (Red Flag Check)
#If a company is far away from the regression line, their "Disclosure Density" is abnormal relative to their sentiment.
# Look for points far from the line
sns.lmplot(data=df, x="sentiment_score", y="density_index", hue="ticker", robust=True)
plt.title("Obfuscation Detection: Sentiment vs. Density")

# Now your Seaborn script is 'Data-Driven'
sns.scatterplot(
    data=df, 
    x="word_count", 
    y="density_index", 
    hue="forensic_label", # <--- Directly from your dbt model
    palette={"POTENTIAL OBFUSCATION": "red", "HIGH NEGATIVE RISK": "orange", "NORMAL": "green"}
)