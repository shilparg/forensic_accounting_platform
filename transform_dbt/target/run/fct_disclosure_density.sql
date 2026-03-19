
  
    

    create or replace table `forensic-accounting-bot`.`forensic_data`.`fct_disclosure_density`
      
    
    

    
    OPTIONS()
    as (
      

WITH cleaned_data AS (
    -- We reference the 'Staging' layer we built earlier
    SELECT * FROM `forensic-accounting-bot`.`forensic_data`.`stg_sec_filings`
)

SELECT
    ticker,
    fiscal_year,
    sentiment_score,
    -- 1. Calculate Word Count
    ARRAY_LENGTH(SPLIT(filing_text, ' ')) AS word_count,
    
    -- 2. Calculate Density Index (Words per unit of Sentiment)
    -- We use ABS() because we want the magnitude of the sentiment
    SAFE_DIVIDE(ARRAY_LENGTH(SPLIT(filing_text, ' ')), ABS(sentiment_score)) AS density_index,
    
    -- 3. The 'Red Flag' Logic (The most important part for your audit)
    CASE 
        WHEN ARRAY_LENGTH(SPLIT(filing_text, ' ')) > 15000 AND sentiment_score < 0 THEN 'POTENTIAL OBFUSCATION'
        WHEN sentiment_score < -0.2 THEN 'HIGH NEGATIVE RISK'
        ELSE 'NORMAL'
    END AS forensic_label
FROM cleaned_data
    );
  