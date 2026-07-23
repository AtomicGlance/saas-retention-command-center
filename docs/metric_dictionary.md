# Metric dictionary

All metrics use complete monthly data through 31 December 2025. Currency is
synthetic USD.

| Metric | Definition | Decision supported | Guardrail |
|---|---|---|---|
| Monthly recurring revenue (MRR) | Sum of `mrr` for active subscription snapshots in the selected month. | Is the recurring revenue base growing? | Review NRR and logo churn so acquisition cannot hide retention loss. |
| Net revenue retention (NRR) | Current MRR from the prior-month customer base divided by that base's prior MRR. Churn contributes zero current MRR. | Is the installed base retaining and expanding revenue? | Segment mix and a one-month window can make NRR noisy. |
| Logo churn | Prior-month active accounts absent in the current month divided by prior-month active accounts. | How much customer loss is hidden by expansion? | Pair with NRR because accounts have different revenue weights. |
| 14-day activation | Eligible signups completing both workspace configuration and integration connection within 14 days. | Is onboarding reaching the product-value milestone? | Eligibility excludes signups without a complete 14-day observation window. |
| Trial-to-paid | Eligible signups with `paid_date` no later than 30 days after signup. | Does acquisition convert into revenue? | Eligibility excludes signups without a complete 30-day observation window. |
| Cohort retention | Paid accounts still active N months after first paid month divided by the paid cohort size. | Are newer customer cohorts retaining better? | Cohorts are not directly comparable if segment or channel mix changes. |

## KPI framework

Primary outcomes: MRR and NRR.

Drivers: 14-day activation and trial-to-paid conversion.

Guardrails: logo churn and cohort retention.

No external target is asserted. In a real company, targets would be anchored to
historical performance, plan, and segment economics.

