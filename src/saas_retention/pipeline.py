"""Load synthetic source data into SQLite, execute reviewed SQL, and build a dashboard artifact."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from .dashboard import render_dashboard
from .generate_data import GenerationConfig, generate_dataset


QUERY_MARKER = "-- query:"


def parse_queries(sql_text: str) -> dict[str, str]:
    queries: dict[str, list[str]] = {}
    current: str | None = None
    for line in sql_text.splitlines():
        if line.startswith(QUERY_MARKER):
            current = line[len(QUERY_MARKER) :].strip()
            queries[current] = []
        elif current is not None:
            queries[current].append(line)
    return {name: "\n".join(lines).strip().rstrip(";") for name, lines in queries.items()}


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    clean = frame.where(pd.notna(frame), None)
    return clean.to_dict(orient="records")


def run_pipeline(project_root: Path, seed: int = 42) -> dict[str, Any]:
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    output_dir = project_root / "outputs"
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = generate_dataset(raw_dir, GenerationConfig(seed=seed))
    connection = sqlite3.connect(project_root / "data" / "analytics.db")
    try:
        for table, path in paths.items():
            pd.read_csv(path).to_sql(
                {"accounts": "accounts", "events": "product_events", "subscriptions": "subscription_monthly"}[table],
                connection,
                if_exists="replace",
                index=False,
            )

        sql_path = project_root / "sql" / "analysis.sql"
        queries = parse_queries(sql_path.read_text(encoding="utf-8"))
        results: dict[str, pd.DataFrame] = {}
        for name, query in queries.items():
            frame = pd.read_sql_query(query, connection)
            frame.to_csv(processed_dir / f"{name}.csv", index=False)
            results[name] = frame
    finally:
        connection.close()

    artifact = build_artifact(results, queries)
    artifact_path = project_root / "artifact.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    dashboard_path = render_dashboard(results, project_root / "dashboard.html")

    summary = validate_results(results)
    (output_dir / "validation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return {
        "artifact": artifact_path,
        "dashboard": dashboard_path,
        "summary": summary,
        "results": results,
    }


def build_artifact(
    results: dict[str, pd.DataFrame],
    queries: dict[str, str],
) -> dict[str, Any]:
    headline = results["headline_kpis"].iloc[0]
    risk = results["risk_segments"].iloc[0]
    generated_at = "2025-12-31T23:59:59Z"

    source_specs = []
    manifest_sources = []
    for name, query in queries.items():
        source_id = f"{name}_sql"
        manifest_sources.append(
            {"id": source_id, "label": name.replace("_", " ").title(), "path": "sql/analysis.sql"}
        )
        source_specs.append(
            {
                "id": source_id,
                "query": {
                    "engine": "sqlite",
                    "language": "sql",
                    "sql": query,
                    "description": f"Produces the reviewed {name.replace('_', ' ')} dataset.",
                    "tables_used": ["accounts", "product_events", "subscription_monthly"],
                    "executed_at": generated_at,
                    "filters": [
                        "Complete monthly data through 2025-12-31",
                        "Synthetic B2B SaaS accounts only",
                    ],
                    "metric_definitions": {
                        "MRR": "Sum of active monthly subscription revenue in the selected month.",
                        "NRR": "Current MRR from the prior-month customer base divided by that base's prior MRR.",
                        "Logo churn": "Prior-month active accounts absent in the current month divided by prior-month active accounts.",
                        "Activation": "Eligible signups completing workspace configuration and integration connection within 14 days.",
                        "Trial-to-paid": "Eligible signups with a paid date no later than 30 days after signup.",
                    },
                },
            }
        )

    risk_sentence = (
        f"{risk['segment']} accounts acquired through {risk['acquisition_channel']} "
        f"show the weakest activation in the reviewed segment-channel groups "
        f"({risk['activation_rate']:.1%}). Treat this as a targeting signal for an "
        "onboarding experiment, not causal proof."
    )

    manifest = {
        "version": 1,
        "surface": "dashboard",
        "title": "Retention Command Center",
        "description": "A SQL-backed operating review of synthetic SaaS growth and retention.",
        "generatedAt": generated_at,
        "cards": [
            {
                "id": "mrr_card",
                "description": "Active recurring revenue in the latest complete month.",
                "dataset": "headline_kpis",
                "sourceId": "headline_kpis_sql",
                "metrics": [
                    {"label": "Monthly recurring revenue", "field": "mrr", "format": "currency"},
                    {"label": "MoM", "field": "mrr_mom_growth", "format": "percent", "signed": True},
                ],
            },
            {
                "id": "nrr_card",
                "description": "Revenue retained from the prior-month customer base, including expansion and churn.",
                "dataset": "headline_kpis",
                "sourceId": "headline_kpis_sql",
                "metrics": [{"label": "Net revenue retention", "field": "nrr", "format": "percent"}],
            },
            {
                "id": "churn_card",
                "description": "Share of prior-month active accounts absent in the latest month.",
                "dataset": "headline_kpis",
                "sourceId": "headline_kpis_sql",
                "metrics": [{"label": "Logo churn", "field": "logo_churn_rate", "format": "percent"}],
            },
            {
                "id": "activation_card",
                "description": "Eligible signups completing both activation milestones within 14 days.",
                "dataset": "headline_kpis",
                "sourceId": "headline_kpis_sql",
                "metrics": [{"label": "14-day activation", "field": "activation_rate", "format": "percent"}],
            },
            {
                "id": "conversion_card",
                "description": "Eligible signups becoming paid customers within 30 days.",
                "dataset": "headline_kpis",
                "sourceId": "headline_kpis_sql",
                "metrics": [{"label": "Trial-to-paid", "field": "trial_to_paid_rate", "format": "percent"}],
            },
        ],
        "charts": [
            {
                "id": "mrr_trend_chart",
                "title": "Monthly recurring revenue",
                "subtitle": "Latest twelve complete months; synthetic USD.",
                "type": "line",
                "dataset": "monthly_trend",
                "sourceId": "monthly_trend_sql",
                "valueFormat": "currency",
                "encodings": {
                    "x": {"field": "month", "type": "temporal", "label": "Month"},
                    "y": {"field": "mrr", "type": "quantitative", "label": "MRR"},
                    "tooltip": [
                        {"field": "active_accounts", "type": "quantitative", "label": "Active accounts"},
                        {"field": "new_accounts", "type": "quantitative", "label": "New signups"},
                        {"field": "churned_accounts", "type": "quantitative", "label": "Churned accounts"},
                    ],
                },
            },
            {
                "id": "segment_nrr_chart",
                "title": "Net revenue retention by segment",
                "subtitle": "Latest month versus the prior-month customer base.",
                "type": "bar",
                "dataset": "segment_health",
                "sourceId": "segment_health_sql",
                "valueFormat": "percent",
                "encodings": {
                    "x": {"field": "segment", "type": "nominal", "label": "Segment"},
                    "y": {"field": "nrr", "type": "quantitative", "label": "NRR"},
                    "tooltip": [
                        {"field": "mrr", "type": "quantitative", "label": "Current MRR", "format": "currency"},
                        {"field": "logo_churn_rate", "type": "quantitative", "label": "Logo churn", "format": "percent"},
                    ],
                },
            },
            {
                "id": "channel_activation_chart",
                "title": "Activation by acquisition channel",
                "subtitle": "Both milestones completed within 14 days; eligible signups only.",
                "type": "bar",
                "dataset": "channel_health",
                "sourceId": "channel_health_sql",
                "valueFormat": "percent",
                "encodings": {
                    "x": {"field": "acquisition_channel", "type": "nominal", "label": "Channel"},
                    "y": {"field": "activation_rate", "type": "quantitative", "label": "Activation"},
                    "tooltip": [
                        {"field": "eligible_accounts", "type": "quantitative", "label": "Eligible accounts"},
                        {"field": "trial_to_paid_rate", "type": "quantitative", "label": "Trial-to-paid", "format": "percent"},
                    ],
                },
            },
            {
                "id": "cohort_heatmap",
                "title": "Paid-customer cohort retention",
                "subtitle": "Jan–Jun 2025 cohorts; months since first paid month.",
                "type": "heatmap",
                "dataset": "cohort_retention",
                "sourceId": "cohort_retention_sql",
                "valueFormat": "percent",
                "encodings": {
                    "x": {"field": "cohort_month", "type": "nominal", "label": "Paid cohort"},
                    "y": {"field": "retention_rate", "type": "quantitative", "label": "Retention"},
                    "color": {"field": "month_number", "type": "ordinal", "label": "Months since paid"},
                    "tooltip": [
                        {"field": "cohort_size", "type": "quantitative", "label": "Starting cohort"},
                        {"field": "retained_accounts", "type": "quantitative", "label": "Retained accounts"},
                    ],
                },
            },
        ],
        "tables": [
            {
                "id": "risk_table",
                "title": "Segment-channel risk queue",
                "subtitle": "Groups with at least 12 prior-month active accounts, ordered by activation.",
                "dataset": "risk_segments",
                "sourceId": "risk_segments_sql",
                "defaultSort": {"field": "activation_rate", "direction": "asc"},
                "columns": [
                    {"field": "segment", "label": "Segment", "type": "text"},
                    {"field": "acquisition_channel", "label": "Channel", "type": "text"},
                    {"field": "eligible_accounts", "label": "Eligible accounts", "format": "number"},
                    {"field": "activation_rate", "label": "Activation", "format": "percent"},
                    {"field": "logo_churn_rate", "label": "Logo churn", "format": "percent", "movement": True},
                    {"field": "nrr", "label": "NRR", "format": "percent"},
                    {"field": "current_mrr", "label": "Current MRR", "format": "currency"},
                ],
            }
        ],
        "sources": manifest_sources,
        "blocks": [
            {
                "id": "intro",
                "type": "markdown",
                "body": "## Monthly operating review\n\n**Synthetic portfolio dataset · complete through Dec 2025.** Monitor revenue retention, diagnose acquisition quality, and choose the next growth intervention.",
            },
            {
                "id": "hero_metrics",
                "type": "metric-strip",
                "cardIds": ["mrr_card", "nrr_card", "churn_card", "activation_card", "conversion_card"],
            },
            {"id": "mrr_trend", "type": "chart", "chartId": "mrr_trend_chart"},
            {
                "id": "decision_signal",
                "type": "markdown",
                "sourceId": "risk_segments_sql",
                "body": f"## Decision signal\n\n{risk_sentence}",
            },
            {"id": "segment_nrr", "type": "chart", "chartId": "segment_nrr_chart"},
            {"id": "channel_activation", "type": "chart", "chartId": "channel_activation_chart"},
            {"id": "cohorts", "type": "chart", "chartId": "cohort_heatmap"},
            {"id": "risk_queue", "type": "table", "tableId": "risk_table"},
            {
                "id": "caveat",
                "type": "markdown",
                "body": "## Interpretation boundary\n\nThis dataset is deterministic and synthetic. Segment differences are descriptive and suitable for prioritizing an experiment; they do not establish causal channel or onboarding effects.",
            },
        ],
    }

    snapshot = {
        "version": 1,
        "generatedAt": generated_at,
        "status": "fixture",
        "datasets": {name: _records(frame) for name, frame in results.items()},
        "accessIssues": [],
    }
    return {
        "surface": "dashboard",
        "manifest": manifest,
        "snapshot": snapshot,
        "sources": source_specs,
        "package_info": {
            "originUrl": "artifact://saas-retention-command-center",
            "controls": {"edit": False, "refresh": False},
        },
    }


def validate_results(results: dict[str, pd.DataFrame]) -> dict[str, Any]:
    headline = results["headline_kpis"].iloc[0]
    cohort = results["cohort_retention"]
    segment = results["segment_health"]
    checks = {
        "headline_single_row": len(results["headline_kpis"]) == 1,
        "mrr_positive": float(headline["mrr"]) > 0,
        "rates_bounded": all(
            0 <= float(headline[field]) <= 1.5
            for field in ["nrr", "logo_churn_rate", "activation_rate", "trial_to_paid_rate"]
        ),
        "cohort_month_zero_is_full": bool(
            (cohort.loc[cohort["month_number"] == 0, "retention_rate"].round(6) == 1.0).all()
        ),
        "segment_mrr_reconciles": abs(float(segment["mrr"].sum()) - float(headline["mrr"])) < 0.02,
        "trend_has_twelve_points": len(results["monthly_trend"]) == 12,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"Validation failed: {failed}")
    return {"status": "ready_to_share", "checks": checks}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run_pipeline(args.project_root.resolve(), seed=args.seed)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
