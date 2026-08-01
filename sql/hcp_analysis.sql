-- ============================================================
-- HCP Insights & Segmentation Dashboard - SQL Analysis
-- ============================================================
-- Load data/sample_payments.csv into a table named payments.
--
-- Expected columns:
-- physician_id, physician_specialty, physician_state, payment_date,
-- payment_amount, payment_type, paying_company
--
-- Optional dashboard table:
-- Load output/hcp_segments.csv into a table named hcp_segments to run
-- the final segment and regional gap queries.
-- ============================================================

-- 1. Total payment volume and count by specialty.
SELECT
    physician_specialty,
    COUNT(*) AS num_payments,
    COUNT(DISTINCT physician_id) AS physicians_engaged,
    ROUND(SUM(payment_amount), 2) AS total_paid,
    ROUND(AVG(payment_amount), 2) AS avg_payment
FROM payments
GROUP BY physician_specialty
ORDER BY total_paid DESC;

-- 2. Total payment volume by state for geography drill-downs.
SELECT
    physician_state,
    COUNT(*) AS num_payments,
    COUNT(DISTINCT physician_id) AS physicians_engaged,
    ROUND(SUM(payment_amount), 2) AS total_paid,
    ROUND(AVG(payment_amount), 2) AS avg_payment
FROM payments
GROUP BY physician_state
ORDER BY total_paid DESC;

-- 3. Per-HCP payment summary, the SQL equivalent of the RFM base table.
SELECT
    physician_id,
    physician_specialty,
    physician_state,
    MAX(payment_date) AS last_payment_date,
    COUNT(*) AS frequency,
    ROUND(SUM(payment_amount), 2) AS total_value,
    ROUND(AVG(payment_amount), 2) AS avg_payment_value,
    COUNT(DISTINCT payment_type) AS payment_types,
    COUNT(DISTINCT paying_company) AS companies_engaged
FROM payments
GROUP BY physician_id, physician_specialty, physician_state
ORDER BY total_value DESC;

-- 4. Breakdown by payment type.
SELECT
    payment_type,
    COUNT(*) AS num_payments,
    COUNT(DISTINCT physician_id) AS physicians_engaged,
    ROUND(SUM(payment_amount), 2) AS total_paid,
    ROUND(AVG(payment_amount), 2) AS avg_payment
FROM payments
GROUP BY payment_type
ORDER BY total_paid DESC;

-- 5. Top 20 HCPs by total payment value.
SELECT
    physician_id,
    physician_specialty,
    physician_state,
    COUNT(*) AS frequency,
    ROUND(SUM(payment_amount), 2) AS total_value
FROM payments
GROUP BY physician_id, physician_specialty, physician_state
ORDER BY total_value DESC
LIMIT 20;

-- 6. Paying company concentration.
SELECT
    paying_company,
    COUNT(*) AS num_payments,
    COUNT(DISTINCT physician_id) AS physicians_engaged,
    ROUND(SUM(payment_amount), 2) AS total_paid,
    ROUND(AVG(payment_amount), 2) AS avg_payment
FROM payments
GROUP BY paying_company
ORDER BY total_paid DESC;

-- 7. Segment summary for dashboard cards.
-- Requires output/hcp_segments.csv loaded as hcp_segments.
SELECT
    segment,
    COUNT(*) AS hcps,
    ROUND(SUM(value), 2) AS total_value,
    ROUND(AVG(rfm_score), 2) AS avg_rfm_score,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 1) AS avg_frequency
FROM hcp_segments
GROUP BY segment
ORDER BY avg_rfm_score DESC;

-- 8. State-level engagement gap view.
-- Requires output/hcp_segments.csv loaded as hcp_segments.
SELECT
    physician_state,
    COUNT(*) AS hcps,
    SUM(CASE WHEN segment = 'High Priority' THEN 1 ELSE 0 END) AS high_priority_hcps,
    ROUND(
        1.0 * SUM(CASE WHEN segment = 'High Priority' THEN 1 ELSE 0 END) / COUNT(*),
        3
    ) AS high_priority_share,
    ROUND(SUM(value), 2) AS total_value,
    ROUND(AVG(rfm_score), 2) AS avg_rfm_score
FROM hcp_segments
GROUP BY physician_state
ORDER BY total_value DESC, high_priority_share ASC;
