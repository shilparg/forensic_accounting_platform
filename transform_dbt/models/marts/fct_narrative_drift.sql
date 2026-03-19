-- models/marts/fct_narrative_drift.sql

WITH staged_data AS (
    SELECT * FROM {{ ref('stg_sec_filings') }}
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