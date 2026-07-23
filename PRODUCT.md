# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary user: a hiring manager or analytics lead reviewing a junior data
analyst portfolio. The reviewer needs to understand the business question,
analytical approach, technical skills, and recommended action in under five
minutes.

Assumption: the demonstrated operating audience is a B2B SaaS growth team
running a monthly retention review.

## Product Purpose

Demonstrate end-to-end data-analysis ability through a small but realistic SaaS
retention case study. Success means the reviewer can inspect the SQL, reproduce
the metrics, understand the KPI definitions, and see how evidence becomes a
business recommendation.

## Positioning

This is not a decorative dashboard exercise. It connects deterministic source
data, SQL transformations, auditable KPI definitions, a decision-oriented
dashboard, and automated reconciliation checks in one compact repository.

## Operating Context

The fictional growth team reviews monthly recurring revenue, net revenue
retention, logo churn, activation, trial conversion, acquisition-channel
quality, and cohort retention. The portfolio reviewer can run the pipeline
locally with Python and SQLite without external credentials.

## Capabilities and Constraints

- All business data is deterministic and synthetic.
- SQLite is the analytical engine so the project remains portable.
- The dashboard is a self-contained, read-only HTML snapshot.
- Metric definitions and source SQL must remain visible and reproducible.
- Findings are descriptive; the project must not imply causal impact.

## Evidence on Hand

The repository will contain generated account, product-event, and monthly
subscription data; SQL queries; reviewed aggregate outputs; tests; a portable
dashboard; and a metric dictionary. No real customer, employer, benchmark, or
commercial performance claim is available or should be fabricated.

## Product Principles

1. Define the denominator before showing the rate.
2. Lead with the decision, then expose the evidence.
3. Keep every headline number traceable to runnable SQL.
4. Prefer a small set of actionable KPIs over vanity metrics.
5. Label synthetic evidence wherever it could be mistaken for real data.

## Accessibility & Inclusion

The dashboard must remain readable without color alone, support narrow screens,
use sufficient contrast, and preserve a semantic fallback when JavaScript is
unavailable.
