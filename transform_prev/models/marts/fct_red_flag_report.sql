{{ config(materialized='table') }}

WITH forensic_metrics AS (
    SELECT 
        ticker, 
        fiscal_year,
        sentiment_score,
        -- Note: Ensure subjectivity_score exists in your stg_sec_filings or add it there
        COALESCE(sentiment_score, 0) as sentiment, 
        similarity_index,
        
        -- Calculate a weighted risk score (0 to 100)
        -- High risk = Low Sentiment + High Similarity
        ROUND(
            ((1 - sentiment_score) * 50) + 
            (similarity_index * 50), 2
        ) as risk_score
    FROM {{ ref('stg_sec_filings') }} -- This creates the link to your Silver layer
)

SELECT 
    *,
    CASE 
        WHEN risk_score > 75 THEN '🔴 CRITICAL: Potential Disclosure Masking'
        WHEN risk_score > 55 THEN '🟡 WARNING: Defensive Reporting'
        ELSE '🟢 LOW: Standard Disclosure' 
    END as audit_priority
FROM forensic_metrics
ORDER BY risk_score DESC