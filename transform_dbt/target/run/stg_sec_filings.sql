

  create or replace view `forensic-accounting-bot`.`forensic_data`.`stg_sec_filings`
  OPTIONS()
  as -- models/staging/stg_sec_filings.sql


WITH raw_data AS (
    -- This references the source we will define in your schema.yml
    SELECT * FROM `forensic-accounting-bot`.`forensic_data`.`raw_filings`
)

SELECT
    -- 1. Standardized Identifiers
    UPPER(CAST(ticker AS STRING)) AS ticker,
    CAST(fiscal_year AS INT64) AS fiscal_year,
    
    -- 2. Cleaned Forensic Metrics
    COALESCE(CAST(sentiment_score AS FLOAT64), 0.0) AS sentiment_score,
    COALESCE(CAST(similarity_index AS FLOAT64), 0.0) AS similarity_index,
    
    -- 3. Text for Disclosure Density & Obfuscation Analysis
    TRIM(parsed_text_sample) AS filing_text,
    
    -- 4. Audit Metadata
    CURRENT_TIMESTAMP() AS processed_at
FROM raw_data
-- Safety check: ensure we don't process empty rows
WHERE ticker IS NOT NULL;

