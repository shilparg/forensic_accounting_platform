{{ config(materialized='view') }}

SELECT 
    ticker, 
    COUNT(fiscal_year) as consecutive_boilerplate_years,
    ROUND(AVG(similarity_index), 4) as avg_similarity
FROM {{ ref('fct_narrative_drift') }}
WHERE similarity_index > 0.95
GROUP BY ticker
HAVING COUNT(fiscal_year) > 3
ORDER BY consecutive_boilerplate_years DESC