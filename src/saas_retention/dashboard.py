"""Render the standalone portfolio dashboard from reviewed query outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def _json_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return json.loads(frame.to_json(orient="records"))


def render_dashboard(results: dict[str, pd.DataFrame], output_path: Path) -> Path:
    """Write a self-contained dashboard backed by the current pipeline results."""

    payload = {
        "generatedAt": "2025-12-31T23:59:59Z",
        "status": "Synthetic portfolio data",
        "headline": _json_records(results["headline_kpis"])[0],
        "monthly": _json_records(results["monthly_trend"]),
        "segments": _json_records(results["segment_health"]),
        "channels": _json_records(results["channel_health"]),
        "cohorts": _json_records(results["cohort_retention"]),
        "risks": _json_records(results["risk_segments"]),
    }
    template_path = Path(__file__).with_name("dashboard_template.html")
    template = template_path.read_text(encoding="utf-8")
    document = template.replace(
        "__DASHBOARD_PAYLOAD__",
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    )
    output_path.write_text(document, encoding="utf-8")
    return output_path
