-- Business question:
-- Do observed default rates increase across predicted risk bands?

SELECT
    risk_band,
    COUNT(*) AS applicant_count,
    AVG(risk_score) AS avg_risk_score,
    AVG(TARGET) AS observed_default_rate,
    AVG(high_risk_flag_015) AS high_risk_flag_rate,
    AVG(AMT_INCOME_TOTAL) AS avg_income,
    AVG(AMT_CREDIT) AS avg_credit,
    AVG(AMT_ANNUITY) AS avg_annuity
FROM risk_analytics_base
GROUP BY risk_band
ORDER BY
    CASE risk_band
        WHEN 'Band 1 - Lowest Risk' THEN 1
        WHEN 'Band 2' THEN 2
        WHEN 'Band 3' THEN 3
        WHEN 'Band 4' THEN 4
        WHEN 'Band 5 - Highest Risk' THEN 5
        ELSE 99
    END;
