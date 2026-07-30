-- ============================================================
-- HCP Insights & Segmentation Dashboard — SQL Analysis
-- Run against data/sample_payments.csv loaded into a table
-- named `payments` (see README.md for load instructions).
-- Schema: physician_id, physician_specialty, physician_state,
--         payment_date, payment_amount, payment_type, paying_company
-- ============================================================

-- 1. Total payment volume and count by specialty
SELECT
    physician_specialty,
    COUNT(*)                AS num_payments,
    SUM(payment_amount)     AS total_paid,
    ROUND(AVG(payment_amount), 2) AS avg_payment
FROM payments
GROUP BY physician_specialty
ORDER BY total_paid DESC;

-- 2. Total payment volume by state (for map/geo drill-down)
SELECT
    physician_state,
    COUNT(*)                AS num_payments,
    SUM(payment_amount)     AS total_paid
FROM payments
GROUP BY physician_state
ORDER BY total_paid DESC;

-- 3. Per-physician summary — base table for RFM scoring in Python
--    (recency reference date is the max payment date in the dataset)
SELECT
    physician_id,
    physician_specialty,
    physician_state,
    MAX(payment_date)                  AS last_payment_date,
    COUNT(*)                           AS frequency,
    SUM(payment_amount)                AS total_value,
    ROUND(AVG(payment_amount), 2)      AS avg_payment_value
FROM payments
GROUP BY physician_id, physician_specialty, physician_state
ORDER BY total_value DESC;

-- 4. Breakdown by payment type (consulting fee, speaker fee, etc.)
SELECT
    payment_type,
    COUNT(*)                AS num_payments,
    SUM(payment_amount)     AS total_paid
FROM payments
GROUP BY payment_type
ORDER BY total_paid DESC;

-- 5. Top 20 physicians by total payment value
SELECT
    physician_id,
    physician_specialty,
    physician_state,
    SUM(payment_amount) AS total_value
FROM payments
GROUP BY physician_id, physician_specialty, physician_state
ORDER BY total_value DESC
LIMIT 20;

-- 6. Paying company concentration — is spend concentrated in a few companies?
SELECT
    paying_company,
    COUNT(DISTINCT physician_id) AS physicians_engaged,
    SUM(payment_amount)          AS total_paid
FROM payments
GROUP BY paying_company
ORDER BY total_paid DESC;
