"""Independently reconcile the headline MRR against the raw SQLite table."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    with sqlite3.connect(root / "data" / "analytics.db") as connection:
        raw_mrr = connection.execute(
            """
            SELECT ROUND(SUM(mrr), 2)
            FROM subscription_monthly
            WHERE month = (SELECT MAX(month) FROM subscription_monthly)
            """
        ).fetchone()[0]

    with (root / "data" / "processed" / "headline_kpis.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        reported_mrr = float(next(csv.DictReader(handle))["mrr"])

    reconciles = abs(float(raw_mrr) - reported_mrr) < 0.01
    print(
        {
            "raw_latest_mrr": raw_mrr,
            "reported_mrr": reported_mrr,
            "reconciles": reconciles,
        }
    )
    if not reconciles:
        raise SystemExit("Headline MRR does not reconcile to the raw subscription table.")


if __name__ == "__main__":
    main()
