WITH staged AS (
    SELECT * FROM {{ ref('stg_sec_filings') }}
),

calculations AS (
    SELECT 
        *,
        -- 1. Disclosure Density (Word count vs Sentiment)
        SAFE_DIVIDE(ARRAY_LENGTH(SPLIT(filing_text, ' ')), ABS(sentiment_score)) AS density_index,
        
        -- 2. Sentiment Volatility (Looking at standard deviation for the ticker)
        STDDEV(sentiment_score) OVER (PARTITION BY ticker) AS sentiment_volatility,
        
        -- 3. Narrative Drift (YoY Similarity Change)
        similarity_index - LAG(similarity_index) OVER (PARTITION BY ticker ORDER BY fiscal_year) AS similarity_drift
    FROM staged
)

SELECT * FROM calculations