-- Business question:
-- How does credit risk vary by income type and risk band?

SELECT
    NAME_INCOME_TYPE,
    risk_band,
    COUNT(*) AS applicant_count,
    AVG(risk_score) AS avg_risk_score,
    AVG(TARGET) AS observed_default_rate,
    AVG(high_risk_flag_015) AS high_risk_flag_rate,
    AVG(AMT_INCOME_TOTAL) AS avg_income,
    AVG(AMT_CREDIT) AS avg_credit,
    AVG(AMT_ANNUITY) AS avg_annuity,
    CASE
        WHEN COUNT(*) >= 1000 THEN 'large_sample_interpretable'
        WHEN COUNT(*) >= 100 THEN 'medium_sample_use_with_caution'
        ELSE 'small_sample_caution'
    END AS sample_size_note,
    CASE
        WHEN COUNT(*) >= 1000 THEN 1
        ELSE 0
    END AS interpretation_priority
FROM risk_analytics_base
GROUP BY
    NAME_INCOME_TYPE,
    risk_band
ORDER BY
    NAME_INCOME_TYPE,
    CASE risk_band
        WHEN 'Band 1 - Lowest Risk' THEN 1
        WHEN 'Band 2' THEN 2
        WHEN 'Band 3' THEN 3
        WHEN 'Band 4' THEN 4
        WHEN 'Band 5 - Highest Risk' THEN 5
        ELSE 99
    END;
