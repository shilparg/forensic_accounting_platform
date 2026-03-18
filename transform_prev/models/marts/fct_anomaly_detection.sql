-- models/marts/fct_anomaly_detection.sql
WITH metrics AS (
    SELECT * FROM {{ ref('int_forensic_metrics') }}
),
stats AS (
    -- Calculate Industry Averages for Benchmarking
    SELECT 
        AVG(sentiment_score) OVER() as avg_industry_sentiment,
        STDDEV(sentiment_score) OVER() as stddev_sentiment
    FROM metrics
)
SELECT 
    m.*,
    -- Z-Score: (Value - Mean) / StdDev
    -- A Z-score > 2 or < -2 is a statistical anomaly (Red Flag)
    (m.sentiment_score - s.avg_industry_sentiment) / NULLIF(s.stddev_sentiment, 0) as sentiment_z_score
FROM metrics m, stats s