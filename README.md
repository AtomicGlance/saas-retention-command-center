# Retention Command Center

A compact **SQL and business-intelligence portfolio project** that turns
synthetic B2B SaaS account, product-event, and subscription data into an
auditable monthly operating review.

> Every company, customer, transaction, KPI value, and finding in this
> repository is deterministic and synthetic. The project demonstrates analysis
> technique; it does not describe a real business.

## The business question

Recurring revenue is growing, but the growth team needs to know whether it is
healthy—and which acquisition/onboarding combination should receive the next
experiment.

The project answers:

- Is MRR growth supported by retained customer revenue?
- Which segments and channels have weak activation or churn?
- Are newer paid cohorts retaining?
- Where should the team investigate before spending more on acquisition?

## Key findings

- December MRR is **$315.1k**, down **1.2% month over month**; NRR is
  **98.8%** and logo churn is **4.5%**.
- **SMB · Paid Search** is the clearest investigation queue: **57.0%**
  activation and **93.7%** NRR in the synthetic data.
- Enterprise NRR is **100.1%**, versus **95.2%** for SMB, showing why aggregate
  growth should be diagnosed by customer mix.
- Recommended next step: test a targeted integration-onboarding intervention
  for paid-search SMB accounts, with activation as the driver and NRR/logo
  churn as guardrails.

These are descriptive findings from deliberately constructed synthetic data,
not causal estimates or external benchmarks.

## Skills demonstrated

| Skill | Evidence |
|---|---|
| SQL | Multi-CTE SQLite queries, conditional aggregation, window eligibility, population-preserving joins, cohorts, and reconciliation logic |
| KPI design | Explicit outcomes, drivers, guardrails, formulas, denominators, and observation windows |
| Business analysis | A decision-oriented risk queue and recommendation bounded by evidence |
| Dashboarding | KPI hierarchy, twelve-month trend, segment/channel diagnostics, cohort heatmap, and detail table |
| Data modeling | Account, product-event, and monthly subscription grains |
| Data quality | Deterministic generation, eligibility checks, survivorship-bias prevention, and cross-query reconciliation |
| Reproducibility | One-command pipeline, portable SQLite, self-contained HTML, and automated tests |
| Stakeholder communication | Plain-language metric dictionary, source visibility, synthetic-data labeling, and causal caveats |

## Run it

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m saas_retention --project-root .
python -m unittest discover -s tests -v
python scripts/spot_check.py
```

Open `dashboard.html` for the self-contained responsive dashboard. It is
generated from the current SQL outputs and requires no server, CDN,
credentials, or external data connection.

## Repository map

```text
.
├── data/raw/                  # deterministic synthetic source tables
├── data/processed/            # reviewed SQL result datasets
├── docs/                      # KPI dictionary, chart map, validation
├── sql/analysis.sql           # complete analytical SQL
├── src/saas_retention/        # generator, pipeline, and dashboard renderer
├── tests/                     # metric and dashboard-generation checks
├── artifact.json              # canonical metric manifest + snapshot
└── dashboard.html             # portable responsive operating review
```

## Interpretation boundary

The synthetic data intentionally contains weaker activation and retention for
some acquisition/segment combinations. These differences are useful for
demonstrating prioritization and experiment design; they must not be presented
as causal estimates or real-world benchmarks.
