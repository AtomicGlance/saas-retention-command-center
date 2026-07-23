"""Generate deterministic synthetic B2B SaaS account and subscription data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GenerationConfig:
    seed: int = 42
    accounts: int = 900
    analysis_end: str = "2025-12-31"


PLAN_PRICE = {"Starter": 99.0, "Growth": 299.0, "Scale": 899.0}
SEGMENT_HAZARD = {"SMB": 0.050, "Mid-market": 0.024, "Enterprise": 0.012}


def _sample_signup_dates(rng: np.random.Generator, n: int) -> pd.DatetimeIndex:
    months = pd.date_range("2024-07-01", "2025-10-01", freq="MS")
    weights = np.linspace(0.7, 1.4, len(months))
    weights /= weights.sum()
    chosen = rng.choice(months, size=n, p=weights)
    offsets = rng.integers(0, 27, size=n)
    return pd.DatetimeIndex(chosen) + pd.to_timedelta(offsets, unit="D")


def generate_dataset(
    output_dir: Path,
    config: GenerationConfig = GenerationConfig(),
) -> dict[str, Path]:
    """Generate accounts, product events, and monthly subscription snapshots."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(config.seed)
    analysis_end = pd.Timestamp(config.analysis_end)

    account_ids = np.array([f"ACC-{i:04d}" for i in range(1, config.accounts + 1)])
    signup_dates = _sample_signup_dates(rng, config.accounts)
    segments = rng.choice(
        ["SMB", "Mid-market", "Enterprise"],
        size=config.accounts,
        p=[0.64, 0.26, 0.10],
    )

    plans: list[str] = []
    channels: list[str] = []
    for segment in segments:
        if segment == "SMB":
            plans.append(str(rng.choice(["Starter", "Growth"], p=[0.78, 0.22])))
            channels.append(
                str(rng.choice(["Paid Search", "Organic", "Partner", "Outbound"], p=[0.38, 0.36, 0.10, 0.16]))
            )
        elif segment == "Mid-market":
            plans.append(str(rng.choice(["Growth", "Scale"], p=[0.76, 0.24])))
            channels.append(
                str(rng.choice(["Paid Search", "Organic", "Partner", "Outbound"], p=[0.20, 0.28, 0.22, 0.30]))
            )
        else:
            plans.append("Scale")
            channels.append(
                str(rng.choice(["Organic", "Partner", "Outbound"], p=[0.18, 0.34, 0.48]))
            )

    account_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    subscription_rows: list[dict[str, object]] = []

    for account_id, signup, segment, plan, channel in zip(
        account_ids, signup_dates, segments, plans, channels, strict=True
    ):
        activation_probability = {"SMB": 0.72, "Mid-market": 0.82, "Enterprise": 0.90}[segment]
        activation_probability += {"Paid Search": -0.20, "Organic": 0.00, "Partner": 0.08, "Outbound": 0.04}[channel]
        activation_probability = float(np.clip(activation_probability, 0.30, 0.96))
        activated = bool(rng.random() < activation_probability)

        workspace_day = int(rng.integers(1, 9)) if activated else int(rng.integers(8, 28))
        integration_day = int(rng.integers(2, 14)) if activated else None
        event_rows.append(
            {
                "account_id": account_id,
                "event_date": (signup + pd.Timedelta(days=workspace_day)).date().isoformat(),
                "event_type": "workspace_configured",
            }
        )
        if integration_day is not None:
            event_rows.append(
                {
                    "account_id": account_id,
                    "event_date": (signup + pd.Timedelta(days=integration_day)).date().isoformat(),
                    "event_type": "integration_connected",
                }
            )

        paid_probability = 0.84 if activated else 0.22
        paid_probability += {"Paid Search": -0.07, "Organic": 0.02, "Partner": 0.06, "Outbound": 0.03}[channel]
        paid = bool(rng.random() < float(np.clip(paid_probability, 0.08, 0.98)))
        paid_date = signup + pd.Timedelta(days=int(rng.integers(5, 31))) if paid else pd.NaT

        base_mrr = PLAN_PRICE[plan]
        if segment == "Mid-market":
            base_mrr *= float(rng.uniform(1.0, 1.45))
        elif segment == "Enterprise":
            base_mrr *= float(rng.uniform(1.8, 3.4))
        base_mrr = round(base_mrr, 2)

        churn_date = pd.NaT
        if paid:
            month = pd.Timestamp(paid_date).to_period("M").to_timestamp()
            mrr = base_mrr
            while month <= analysis_end.to_period("M").to_timestamp():
                months_live = (month.year - pd.Timestamp(paid_date).year) * 12 + (
                    month.month - pd.Timestamp(paid_date).month
                )
                hazard = SEGMENT_HAZARD[segment]
                if not activated:
                    hazard += 0.085
                if channel == "Paid Search":
                    hazard += 0.018
                if channel == "Partner":
                    hazard -= 0.006
                hazard *= 0.65 if months_live == 0 else 1.0

                if months_live > 0 and rng.random() < max(0.002, hazard):
                    churn_date = month
                    break

                growth_mean = {"SMB": 0.002, "Mid-market": 0.009, "Enterprise": 0.015}[segment]
                if months_live > 0:
                    mrr *= 1 + float(np.clip(rng.normal(growth_mean, 0.025), -0.08, 0.10))
                subscription_rows.append(
                    {
                        "account_id": account_id,
                        "month": month.date().isoformat(),
                        "mrr": round(max(0.0, mrr), 2),
                    }
                )
                month += pd.offsets.MonthBegin(1)

        account_rows.append(
            {
                "account_id": account_id,
                "signup_date": signup.date().isoformat(),
                "segment": segment,
                "plan": plan,
                "acquisition_channel": channel,
                "paid_date": "" if pd.isna(paid_date) else pd.Timestamp(paid_date).date().isoformat(),
                "churn_date": "" if pd.isna(churn_date) else pd.Timestamp(churn_date).date().isoformat(),
                "initial_mrr": base_mrr,
            }
        )

    paths = {
        "accounts": output_dir / "accounts.csv",
        "events": output_dir / "product_events.csv",
        "subscriptions": output_dir / "subscription_monthly.csv",
    }
    pd.DataFrame(account_rows).to_csv(paths["accounts"], index=False)
    pd.DataFrame(event_rows).sort_values(["account_id", "event_date"]).to_csv(paths["events"], index=False)
    pd.DataFrame(subscription_rows).sort_values(["month", "account_id"]).to_csv(
        paths["subscriptions"], index=False
    )
    return paths

