-- Business question:
-- If threshold 0.15 is used as a candidate high-risk flag, how different are
-- the flagged and non-flagged groups?

SELECT
    high_risk_flag_015,
    COUNT(*) AS applicant_count,
    AVG(risk_score) AS avg_risk_score,
    AVG(TARGET) AS observed_default_rate,
    AVG(AMT_INCOME_TOTAL) AS avg_income,
    AVG(AMT_CREDIT) AS avg_credit,
    AVG(AMT_ANNUITY) AS avg_annuity
FROM risk_analytics_base
GROUP BY high_risk_flag_015
ORDER BY high_risk_flag_015;
