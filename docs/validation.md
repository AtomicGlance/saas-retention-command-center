# Validation record

## Overall assessment

Ready to share as a **synthetic portfolio demonstration**.

## Methodology

- Population, date windows, eligibility rules, and denominators are explicit in
  `sql/analysis.sql` and `docs/metric_dictionary.md`.
- Monthly comparisons use complete periods.
- Activation and conversion exclude accounts without the required observation
  window.
- NRR retains the prior-month population and assigns zero current MRR to churned
  accounts, avoiding survivorship bias.

## Automated checks

- Headline KPI query returns exactly one row.
- MRR is positive.
- Rate metrics stay within plausible bounds.
- Every cohort begins at 100% retention in month zero.
- Segment MRR reconciles to headline MRR within two cents.
- The trend dataset contains twelve complete monthly points.

## Required caveat

All source records and findings are deterministic and synthetic. Observed
channel and segment differences support prioritization of an experiment but do
not estimate causal impact.

