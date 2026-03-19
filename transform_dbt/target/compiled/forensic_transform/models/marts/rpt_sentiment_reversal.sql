

WITH YoY_Sentiment AS (
    SELECT 
        ticker,
        fiscal_year,
        sentiment_score,
        LAG(sentiment_score) OVER (PARTITION BY ticker ORDER BY fiscal_year) as prev_year_sentiment
    FROM `forensic-accounting-bot`.`forensic_data`.`fct_anomaly_detection`
)
SELECT 
    ticker,
    fiscal_year,
    ROUND(sentiment_score, 4) as current_sentiment,
    ROUND(prev_year_sentiment, 4) as prev_year_sentiment,
    ROUND((sentiment_score - prev_year_sentiment), 4) as sentiment_crash
FROM YoY_Sentiment
WHERE prev_year_sentiment > 0 AND sentiment_score < 0 
ORDER BY sentiment_crash ASC
LIMIT 10