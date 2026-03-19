-- created_at: 2026-03-19T14:13:56.822778633+00:00
-- finished_at: 2026-03-19T14:13:59.815336130+00:00
-- elapsed: 3.0s
-- outcome: success
-- dialect: bigquery
-- node_id: not available
-- query_id: AFLvkcjiFqQ5z9FjDt4fM8FsAM3
-- desc: execute adapter call
/* {"app": "dbt", "connection_name": "", "dbt_version": "2.0.0", "profile_name": "forensic_profile", "target_name": "dev"} */

    select distinct schema_name from `forensic-accounting-bot`.INFORMATION_SCHEMA.SCHEMATA;
  ;
-- created_at: 2026-03-19T14:14:00.115242557+00:00
-- finished_at: 2026-03-19T14:14:03.295176375+00:00
-- elapsed: 3.2s
-- outcome: success
-- dialect: bigquery
-- node_id: model.forensic_transform.stg_sec_filings
-- query_id: gUUtwjmv6B29H2cVYenB6U0CBaf
-- desc: get_relation > list_relations call
SELECT
    table_catalog,
    table_schema,
    table_name,
    table_type
FROM 
    `forensic-accounting-bot`.`forensic_data`.INFORMATION_SCHEMA.TABLES;
-- created_at: 2026-03-19T14:14:03.317340377+00:00
-- finished_at: 2026-03-19T14:14:03.204154897+00:00
-- outcome: success
-- dialect: bigquery
-- node_id: model.forensic_transform.stg_sec_filings
-- query_id: 6uGUd42t4nBqlVj70PTSwXETpcV
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.forensic_transform.stg_sec_filings", "profile_name": "forensic_profile", "target_name": "dev"} */


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

;
-- created_at: 2026-03-19T14:14:03.237267315+00:00
-- finished_at: 2026-03-19T14:14:08.011661109+00:00
-- elapsed: 4.8s
-- outcome: success
-- dialect: bigquery
-- node_id: model.forensic_transform.fct_disclosure_density
-- query_id: oOJS67VDK7MyajYCXiWhHdfZH6y
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.forensic_transform.fct_disclosure_density", "profile_name": "forensic_profile", "target_name": "dev"} */

  
    

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
  ;
-- created_at: 2026-03-19T14:14:03.220646076+00:00
-- finished_at: 2026-03-19T14:14:08.355537142+00:00
-- elapsed: 5.1s
-- outcome: success
-- dialect: bigquery
-- node_id: model.forensic_transform.int_forensic_metrics
-- query_id: mEbsOwdZEpiYjFdjM8riAOObEif
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.forensic_transform.int_forensic_metrics", "profile_name": "forensic_profile", "target_name": "dev"} */

  
    

    create or replace table `forensic-accounting-bot`.`forensic_data`.`int_forensic_metrics`
      
    
    

    
    OPTIONS()
    as (
      WITH staged AS (
    SELECT * FROM `forensic-accounting-bot`.`forensic_data`.`stg_sec_filings`
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
    );
  ;
-- created_at: 2026-03-19T14:14:03.230595451+00:00
-- finished_at: 2026-03-19T14:14:09.268926197+00:00
-- elapsed: 6.0s
-- outcome: success
-- dialect: bigquery
-- node_id: model.forensic_transform.fct_narrative_drift
-- query_id: daXwn3l8KbFpl6AG72Gj15mOjkq
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.forensic_transform.fct_narrative_drift", "profile_name": "forensic_profile", "target_name": "dev"} */

  
    

    create or replace table `forensic-accounting-bot`.`forensic_data`.`fct_narrative_drift`
      
    
    

    
    OPTIONS()
    as (
      -- models/marts/fct_narrative_drift.sql

WITH staged_data AS (
    SELECT * FROM `forensic-accounting-bot`.`forensic_data`.`stg_sec_filings`
),

drift_calculation AS (
    SELECT
        ticker,
        fiscal_year,
        sentiment_score,
        similarity_index,
        -- Get the similarity from the PREVIOUS year for the same ticker
        LAG(similarity_index) OVER (PARTITION BY ticker ORDER BY fiscal_year) AS prev_year_similarity,
        -- Calculate the "Drift" (Change in narrative)
        similarity_index - LAG(similarity_index) OVER (PARTITION BY ticker ORDER BY fiscal_year) AS similarity_drift
    FROM staged_data
)

SELECT
    *,
    -- Forensic Flag: High similarity but high drift in sentiment is a red flag
    CASE 
        WHEN ABS(similarity_drift) > 0.15 THEN 'HIGH DRIFT'
        WHEN similarity_index > 0.95 THEN 'BOILERPLATE RISK'
        ELSE 'STABLE'
    END AS audit_status
FROM drift_calculation
    );
  ;
-- created_at: 2026-03-19T14:14:03.226172678+00:00
-- finished_at: 2026-03-19T14:14:11.090639160+00:00
-- elapsed: 7.9s
-- outcome: success
-- dialect: bigquery
-- node_id: model.forensic_transform.fct_red_flag_report
-- query_id: APkx3i5tnXIWxMgrPRLMIEX2F62
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.forensic_transform.fct_red_flag_report", "profile_name": "forensic_profile", "target_name": "dev"} */

  
    

    create or replace table `forensic-accounting-bot`.`forensic_data`.`fct_red_flag_report`
      
    
    

    
    OPTIONS()
    as (
      

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
    FROM `forensic-accounting-bot`.`forensic_data`.`stg_sec_filings` -- This creates the link to your Silver layer
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
    );
  ;
-- created_at: 2026-03-19T14:14:09.275330555+00:00
-- finished_at: 2026-03-19T14:14:11.526062399+00:00
-- elapsed: 2.3s
-- outcome: success
-- dialect: bigquery
-- node_id: model.forensic_transform.rpt_boilerplate_offenders
-- query_id: Z65xkSgMmYHsOiAT9nyEk3iBWfd
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.forensic_transform.rpt_boilerplate_offenders", "profile_name": "forensic_profile", "target_name": "dev"} */


  create or replace view `forensic-accounting-bot`.`forensic_data`.`rpt_boilerplate_offenders`
  OPTIONS()
  as 

SELECT 
    ticker, 
    COUNT(fiscal_year) as consecutive_boilerplate_years,
    ROUND(AVG(similarity_index), 4) as avg_similarity
FROM `forensic-accounting-bot`.`forensic_data`.`fct_narrative_drift`
WHERE similarity_index > 0.95
GROUP BY ticker
HAVING COUNT(fiscal_year) > 3
ORDER BY consecutive_boilerplate_years DESC;

;
-- created_at: 2026-03-19T14:14:08.369347683+00:00
-- finished_at: 2026-03-19T14:14:16.442187345+00:00
-- elapsed: 8.1s
-- outcome: success
-- dialect: bigquery
-- node_id: model.forensic_transform.fct_anomaly_detection
-- query_id: UcifYyWrVYh7IlpnfyY7Ld8AWVE
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.forensic_transform.fct_anomaly_detection", "profile_name": "forensic_profile", "target_name": "dev"} */

  
    

    create or replace table `forensic-accounting-bot`.`forensic_data`.`fct_anomaly_detection`
      
    
    

    
    OPTIONS()
    as (
      -- models/marts/fct_anomaly_detection.sql
WITH metrics AS (
    SELECT * FROM `forensic-accounting-bot`.`forensic_data`.`int_forensic_metrics`
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
    );
  ;
-- created_at: 2026-03-19T14:14:16.449534453+00:00
-- finished_at: 2026-03-19T14:14:18.774108215+00:00
-- elapsed: 2.3s
-- outcome: success
-- dialect: bigquery
-- node_id: model.forensic_transform.rpt_sentiment_reversal
-- query_id: qSfnzN9d9ZGQHeLqxMJWUvXR25C
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.forensic_transform.rpt_sentiment_reversal", "profile_name": "forensic_profile", "target_name": "dev"} */


  create or replace view `forensic-accounting-bot`.`forensic_data`.`rpt_sentiment_reversal`
  OPTIONS()
  as 

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
LIMIT 10;

;
