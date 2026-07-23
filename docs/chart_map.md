# Chart map

| Section | Analytical question | Form | Dataset | Supported reading |
|---|---|---|---|---|
| Revenue trend | Is recurring revenue moving over complete monthly periods? | Single-series line | `monthly_trend` | Twelve points show direction without mixing units. |
| Segment NRR | Which customer segment retains revenue best? | Categorical bar | `segment_health` | NRR is directly comparable across three segments. |
| Channel activation | Which acquisition sources reach the activation milestone? | Sorted categorical bar | `channel_health` | Channel differences prioritize investigation, not causal conclusions. |
| Cohort retention | How does retention decay across paid cohorts? | Heatmap | `cohort_retention` | Dense month-by-cohort pattern with cohort-size context. |
| Risk queue | Which segment-channel combinations merit follow-up? | Exact lookup table | `risk_segments` | Activation, churn, NRR, and current MRR stay visible together. |

Palette policy: route blue carries ordinary analytical movement; mint, amber,
and coral communicate healthy, watch, and risk states with text redundancy.
Neutral ink and dividers handle structure without adding category-color noise.
