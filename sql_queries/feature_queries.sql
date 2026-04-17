-- =====================================================
-- SQL Queries for Home Credit Feature Engineering
-- SQLite Compatible Version 
-- =====================================================

-- 1. Past Refusal Count (In Python it's n_prev_refusals)
-- Business logic: To count the times each client is refused in previous loan applications
SELECT 
    SK_ID_CURR,
    COUNT(*) AS n_prev_refusals
FROM previous_application
WHERE NAME_CONTRACT_STATUS = 'Refused'
GROUP BY SK_ID_CURR
ORDER BY SK_ID_CURR;

-- 2. Average Loan Annuity (In Python it's avg_annuity_prev)
-- Business logic: Calculate average annuity for each client across all historical applications
SELECT 
    SK_ID_CURR,
    AVG(AMT_ANNUITY) AS avg_annuity_prev
FROM previous_application
WHERE AMT_ANNUITY > 0
GROUP BY SK_ID_CURR
ORDER BY SK_ID_CURR;

-- 3. Contract Status Distribution (SQLite compatible)
-- Business logic: View distribution of application counts by contract status
SELECT 
    NAME_CONTRACT_STATUS,
    COUNT(*) AS application_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM previous_application), 2) AS percentage
FROM previous_application
GROUP BY NAME_CONTRACT_STATUS
ORDER BY application_count DESC;

-- 4. Annuity by Contract Status (SQLite compatible)
-- Business logic: Summary statistics of annuity for each contract status
SELECT 
    NAME_CONTRACT_STATUS,
    COUNT(*) AS total_applications,
    ROUND(AVG(AMT_ANNUITY), 2) AS avg_annuity,
    ROUND(MIN(AMT_ANNUITY), 2) AS min_annuity,
    ROUND(MAX(AMT_ANNUITY), 2) AS max_annuity
FROM previous_application
WHERE AMT_ANNUITY > 0
GROUP BY NAME_CONTRACT_STATUS
ORDER BY avg_annuity DESC;

-- 5. Rank customers by annuity within each contract status (SQLite compatible)
-- Business logic: Rank customers by loan amount within their contract status group
SELECT 
    a.SK_ID_CURR,
    a.NAME_CONTRACT_STATUS,
    a.AMT_ANNUITY,
    (SELECT COUNT(*) + 1 
     FROM previous_application b 
     WHERE b.NAME_CONTRACT_STATUS = a.NAME_CONTRACT_STATUS 
       AND b.AMT_ANNUITY > a.AMT_ANNUITY) AS rank_within_status
FROM previous_application a
WHERE a.AMT_ANNUITY > 0
ORDER BY a.NAME_CONTRACT_STATUS, rank_within_status;
