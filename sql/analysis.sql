-- query: headline_kpis
WITH bounds AS (
    SELECT MAX(month) AS latest_month,
           DATE(MAX(month), '-1 month') AS previous_month,
           DATE(MAX(month), '+1 month', '-1 day') AS analysis_end_date
    FROM subscription_monthly
),
current_base AS (
    SELECT s.account_id, s.mrr
    FROM subscription_monthly s, bounds b
    WHERE s.month = b.latest_month
),
previous_base AS (
    SELECT s.account_id, s.mrr
    FROM subscription_monthly s, bounds b
    WHERE s.month = b.previous_month
),
retained AS (
    SELECT p.account_id,
           p.mrr AS previous_mrr,
           COALESCE(c.mrr, 0.0) AS current_mrr
    FROM previous_base p
    LEFT JOIN current_base c USING (account_id)
),
activation AS (
    SELECT
        COUNT(*) AS eligible_accounts,
        SUM(CASE WHEN configured_date IS NOT NULL
                      AND integrated_date IS NOT NULL
                      AND configured_date <= DATE(signup_date, '+14 day')
                      AND integrated_date <= DATE(signup_date, '+14 day')
                 THEN 1 ELSE 0 END) AS activated_accounts
    FROM (
        SELECT a.account_id, a.signup_date,
               MIN(CASE WHEN e.event_type = 'workspace_configured' THEN e.event_date END) AS configured_date,
               MIN(CASE WHEN e.event_type = 'integration_connected' THEN e.event_date END) AS integrated_date
        FROM accounts a
        LEFT JOIN product_events e USING (account_id), bounds b
        WHERE a.signup_date <= DATE(b.analysis_end_date, '-14 day')
        GROUP BY a.account_id, a.signup_date
    )
),
conversion AS (
    SELECT
        COUNT(*) AS eligible_trials,
        SUM(CASE WHEN paid_date IS NOT NULL
                      AND paid_date <> ''
                      AND paid_date <= DATE(signup_date, '+30 day')
                 THEN 1 ELSE 0 END) AS converted_trials
    FROM accounts a, bounds b
    WHERE a.signup_date <= DATE(b.analysis_end_date, '-30 day')
)
SELECT
    b.analysis_end_date AS as_of_date,
    ROUND((SELECT SUM(mrr) FROM current_base), 2) AS mrr,
    (SELECT COUNT(*) FROM current_base) AS active_accounts,
    ROUND(
        (SELECT SUM(mrr) FROM current_base) /
        NULLIF((SELECT SUM(mrr) FROM previous_base), 0) - 1,
        4
    ) AS mrr_mom_growth,
    ROUND(SUM(r.current_mrr) / NULLIF(SUM(r.previous_mrr), 0), 4) AS nrr,
    ROUND(
        SUM(CASE WHEN r.current_mrr = 0 THEN 1.0 ELSE 0.0 END) /
        NULLIF(COUNT(*), 0),
        4
    ) AS logo_churn_rate,
    ROUND(
        (SELECT SUM(mrr) FROM current_base) /
        NULLIF((SELECT COUNT(*) FROM current_base), 0),
        2
    ) AS arpa,
    ROUND(a.activated_accounts * 1.0 / NULLIF(a.eligible_accounts, 0), 4) AS activation_rate,
    ROUND(c.converted_trials * 1.0 / NULLIF(c.eligible_trials, 0), 4) AS trial_to_paid_rate,
    a.eligible_accounts,
    a.activated_accounts,
    c.eligible_trials,
    c.converted_trials
FROM bounds b
CROSS JOIN retained r
CROSS JOIN activation a
CROSS JOIN conversion c;

-- query: monthly_trend
WITH months AS (
    SELECT DISTINCT month FROM subscription_monthly
    WHERE month >= '2025-01-01'
),
monthly AS (
    SELECT month, ROUND(SUM(mrr), 2) AS mrr, COUNT(*) AS active_accounts
    FROM subscription_monthly
    WHERE month >= '2025-01-01'
    GROUP BY month
),
signups AS (
    SELECT DATE(signup_date, 'start of month') AS month, COUNT(*) AS new_accounts
    FROM accounts
    WHERE signup_date >= '2025-01-01'
    GROUP BY DATE(signup_date, 'start of month')
),
churns AS (
    SELECT DATE(churn_date, 'start of month') AS month, COUNT(*) AS churned_accounts
    FROM accounts
    WHERE churn_date IS NOT NULL AND churn_date <> '' AND churn_date >= '2025-01-01'
    GROUP BY DATE(churn_date, 'start of month')
)
SELECT m.month, m.mrr, m.active_accounts,
       COALESCE(s.new_accounts, 0) AS new_accounts,
       COALESCE(c.churned_accounts, 0) AS churned_accounts
FROM monthly m
LEFT JOIN signups s USING (month)
LEFT JOIN churns c USING (month)
ORDER BY m.month;

-- query: segment_health
WITH bounds AS (
    SELECT MAX(month) AS latest_month,
           DATE(MAX(month), '-1 month') AS previous_month,
           DATE(MAX(month), '+1 month', '-1 day') AS analysis_end_date
    FROM subscription_monthly
),
current_base AS (
    SELECT a.segment, s.account_id, s.mrr
    FROM subscription_monthly s JOIN accounts a USING (account_id), bounds b
    WHERE s.month = b.latest_month
),
previous_base AS (
    SELECT a.segment, s.account_id, s.mrr
    FROM subscription_monthly s JOIN accounts a USING (account_id), bounds b
    WHERE s.month = b.previous_month
),
retention AS (
    SELECT p.segment, p.account_id, p.mrr AS previous_mrr,
           COALESCE(c.mrr, 0.0) AS current_mrr
    FROM previous_base p
    LEFT JOIN current_base c USING (segment, account_id)
),
segment_retention AS (
    SELECT segment,
           SUM(current_mrr) / NULLIF(SUM(previous_mrr), 0) AS nrr,
           SUM(CASE WHEN current_mrr = 0 THEN 1.0 ELSE 0.0 END) / COUNT(*) AS logo_churn_rate
    FROM retention
    GROUP BY segment
),
segment_activation AS (
    SELECT segment,
           AVG(CASE WHEN configured_date IS NOT NULL
                         AND integrated_date IS NOT NULL
                         AND configured_date <= DATE(signup_date, '+14 day')
                         AND integrated_date <= DATE(signup_date, '+14 day')
                    THEN 1.0 ELSE 0.0 END) AS activation_rate
    FROM (
        SELECT a.account_id, a.segment, a.signup_date,
               MIN(CASE WHEN e.event_type = 'workspace_configured' THEN e.event_date END) AS configured_date,
               MIN(CASE WHEN e.event_type = 'integration_connected' THEN e.event_date END) AS integrated_date
        FROM accounts a LEFT JOIN product_events e USING (account_id), bounds b
        WHERE a.signup_date <= DATE(b.analysis_end_date, '-14 day')
        GROUP BY a.account_id, a.segment, a.signup_date
    )
    GROUP BY segment
)
SELECT c.segment,
       COUNT(*) AS active_accounts,
       ROUND(SUM(c.mrr), 2) AS mrr,
       ROUND(r.nrr, 4) AS nrr,
       ROUND(r.logo_churn_rate, 4) AS logo_churn_rate,
       ROUND(a.activation_rate, 4) AS activation_rate
FROM current_base c
JOIN segment_retention r USING (segment)
JOIN segment_activation a USING (segment)
GROUP BY c.segment, r.nrr, r.logo_churn_rate, a.activation_rate
ORDER BY mrr DESC;

-- query: channel_health
WITH bounds AS (
    SELECT MAX(month) AS latest_month,
           DATE(MAX(month), '+1 month', '-1 day') AS analysis_end_date
    FROM subscription_monthly
),
activation AS (
    SELECT acquisition_channel,
           COUNT(*) AS eligible_accounts,
           AVG(CASE WHEN configured_date IS NOT NULL
                         AND integrated_date IS NOT NULL
                         AND configured_date <= DATE(signup_date, '+14 day')
                         AND integrated_date <= DATE(signup_date, '+14 day')
                    THEN 1.0 ELSE 0.0 END) AS activation_rate,
           AVG(CASE WHEN paid_date IS NOT NULL
                         AND paid_date <> ''
                         AND paid_date <= DATE(signup_date, '+30 day')
                    THEN 1.0 ELSE 0.0 END) AS trial_to_paid_rate
    FROM (
        SELECT a.account_id, a.acquisition_channel, a.signup_date, a.paid_date,
               MIN(CASE WHEN e.event_type = 'workspace_configured' THEN e.event_date END) AS configured_date,
               MIN(CASE WHEN e.event_type = 'integration_connected' THEN e.event_date END) AS integrated_date
        FROM accounts a LEFT JOIN product_events e USING (account_id), bounds b
        WHERE a.signup_date <= DATE(b.analysis_end_date, '-30 day')
        GROUP BY a.account_id, a.acquisition_channel, a.signup_date, a.paid_date
    )
    GROUP BY acquisition_channel
)
SELECT acquisition_channel, eligible_accounts,
       ROUND(activation_rate, 4) AS activation_rate,
       ROUND(trial_to_paid_rate, 4) AS trial_to_paid_rate
FROM activation
ORDER BY activation_rate DESC;

-- query: cohort_retention
WITH RECURSIVE month_offsets(month_number) AS (
    VALUES(0)
    UNION ALL
    SELECT month_number + 1
    FROM month_offsets
    WHERE month_number < 6
),
paid_cohorts AS (
    SELECT a.account_id, DATE(a.paid_date, 'start of month') AS cohort_month
    FROM accounts a
    WHERE a.paid_date IS NOT NULL AND a.paid_date <> ''
      AND a.paid_date BETWEEN '2025-01-01' AND '2025-06-30'
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM paid_cohorts
    GROUP BY cohort_month
),
cohort_grid AS (
    SELECT c.cohort_month,
           o.month_number,
           DATE(c.cohort_month, printf('+%d months', o.month_number)) AS activity_month,
           c.cohort_size
    FROM cohort_sizes c
    CROSS JOIN month_offsets o
),
retention AS (
    SELECT g.cohort_month,
           g.month_number,
           g.cohort_size,
           COUNT(DISTINCT s.account_id) AS retained_accounts
    FROM cohort_grid g
    JOIN paid_cohorts p
      ON p.cohort_month = g.cohort_month
    LEFT JOIN subscription_monthly s
      ON s.account_id = p.account_id
     AND s.month = g.activity_month
    GROUP BY g.cohort_month, g.month_number, g.cohort_size
)
SELECT cohort_month, month_number, retained_accounts, cohort_size,
       ROUND(retained_accounts * 1.0 / cohort_size, 4) AS retention_rate
FROM retention
ORDER BY cohort_month, month_number;

-- query: risk_segments
WITH bounds AS (
    SELECT MAX(month) AS latest_month,
           DATE(MAX(month), '-1 month') AS previous_month,
           DATE(MAX(month), '+1 month', '-1 day') AS analysis_end_date
    FROM subscription_monthly
),
activation AS (
    SELECT segment, acquisition_channel, COUNT(*) AS eligible_accounts,
           AVG(CASE WHEN configured_date IS NOT NULL
                         AND integrated_date IS NOT NULL
                         AND configured_date <= DATE(signup_date, '+14 day')
                         AND integrated_date <= DATE(signup_date, '+14 day')
                    THEN 1.0 ELSE 0.0 END) AS activation_rate
    FROM (
        SELECT a.account_id, a.segment, a.acquisition_channel, a.signup_date,
               MIN(CASE WHEN e.event_type = 'workspace_configured' THEN e.event_date END) AS configured_date,
               MIN(CASE WHEN e.event_type = 'integration_connected' THEN e.event_date END) AS integrated_date
        FROM accounts a LEFT JOIN product_events e USING (account_id), bounds b
        WHERE a.signup_date <= DATE(b.analysis_end_date, '-14 day')
        GROUP BY a.account_id, a.segment, a.acquisition_channel, a.signup_date
    )
    GROUP BY segment, acquisition_channel
),
previous_base AS (
    SELECT a.segment, a.acquisition_channel, s.account_id, s.mrr
    FROM subscription_monthly s JOIN accounts a USING (account_id), bounds b
    WHERE s.month = b.previous_month
),
current_base AS (
    SELECT a.segment, a.acquisition_channel, s.account_id, s.mrr
    FROM subscription_monthly s JOIN accounts a USING (account_id), bounds b
    WHERE s.month = b.latest_month
),
retention AS (
    SELECT p.segment, p.acquisition_channel, p.account_id, p.mrr AS previous_mrr,
           COALESCE(c.mrr, 0.0) AS current_mrr
    FROM previous_base p
    LEFT JOIN current_base c
      ON p.segment = c.segment
     AND p.acquisition_channel = c.acquisition_channel
     AND p.account_id = c.account_id
)
SELECT r.segment, r.acquisition_channel,
       a.eligible_accounts,
       ROUND(a.activation_rate, 4) AS activation_rate,
       ROUND(SUM(CASE WHEN r.current_mrr = 0 THEN 1.0 ELSE 0.0 END) / COUNT(*), 4) AS logo_churn_rate,
       ROUND(SUM(r.current_mrr) / NULLIF(SUM(r.previous_mrr), 0), 4) AS nrr,
       ROUND(SUM(r.current_mrr), 2) AS current_mrr
FROM retention r
JOIN activation a USING (segment, acquisition_channel)
GROUP BY r.segment, r.acquisition_channel, a.eligible_accounts, a.activation_rate
HAVING COUNT(*) >= 12
ORDER BY activation_rate ASC, logo_churn_rate DESC;

