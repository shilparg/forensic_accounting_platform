{{ config(materialized='view') }}

WITH raw_data AS (
    -- We will define this source in the next step
    SELECT * FROM {{ source('raw_sec_landing', 'raw_filings') }}
)

SELECT
    UPPER(CAST(ticker AS STRING)) AS ticker,
    CAST(fiscal_year AS INT64) AS fiscal_year,
    COALESCE(CAST(sentiment_score AS FLOAT64), 0.0) AS sentiment_score,
    COALESCE(CAST(similarity_index AS FLOAT64), 0.0) AS similarity_index,
    TRIM(parsed_text_sample) AS filing_text,
    CURRENT_TIMESTAMP() AS processed_at
FROM raw_data
WHERE ticker IS NOT NULL