"""RFM segmentation for HCP payment analysis.

This script takes payment-level data, creates one row per HCP, scores each HCP
on recency, frequency, and value, and writes simple CSV outputs that can be
used in Power BI.

Run:
    python notebooks/rfm_segmentation.py
"""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "sample_payments.csv"
OUTPUT_DIR = PROJECT_ROOT / "output"

REQUIRED_COLUMNS = [
    "physician_id",
    "physician_specialty",
    "physician_state",
    "payment_date",
    "payment_amount",
    "payment_type",
    "paying_company",
]


def load_payments() -> pd.DataFrame:
    payments = pd.read_csv(DATA_PATH, parse_dates=["payment_date"])

    missing_columns = set(REQUIRED_COLUMNS) - set(payments.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)}")

    payments["payment_amount"] = pd.to_numeric(
        payments["payment_amount"], errors="coerce"
    )
    payments = payments.dropna(subset=["payment_date", "payment_amount"])
    return payments


def build_rfm_table(payments: pd.DataFrame) -> pd.DataFrame:
    reference_date = payments["payment_date"].max()

    rfm = payments.groupby(
        ["physician_id", "physician_specialty", "physician_state"],
        as_index=False,
    ).agg(
        last_payment_date=("payment_date", "max"),
        frequency=("payment_amount", "count"),
        value=("payment_amount", "sum"),
    )

    rfm["recency_days"] = (reference_date - rfm["last_payment_date"]).dt.days
    rfm["value"] = rfm["value"].round(2)
    return rfm


def quartile_score(series: pd.Series, higher_is_better: bool) -> pd.Series:
    """Score values from 1 to 4 using percentile ranks."""
    percentile = series.rank(method="first", pct=True)
    score = np.ceil(percentile * 4).clip(1, 4).astype(int)

    if not higher_is_better:
        score = 5 - score

    return pd.Series(score, index=series.index)


def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    scored = rfm.copy()

    scored["r_score"] = quartile_score(scored["recency_days"], higher_is_better=False)
    scored["f_score"] = quartile_score(scored["frequency"], higher_is_better=True)
    scored["v_score"] = quartile_score(scored["value"], higher_is_better=True)
    scored["rfm_score"] = scored["r_score"] + scored["f_score"] + scored["v_score"]

    scored["segment"] = pd.cut(
        scored["rfm_score"],
        bins=[0, 5, 8, 12],
        labels=["Low Priority", "Medium Priority", "High Priority"],
    )

    return scored.sort_values(
        ["rfm_score", "value", "frequency", "physician_id"],
        ascending=[False, False, False, True],
    )


def build_segment_summary(scored: pd.DataFrame) -> pd.DataFrame:
    return scored.groupby("segment", observed=False).agg(
        hcps=("physician_id", "count"),
        total_value=("value", "sum"),
        avg_rfm_score=("rfm_score", "mean"),
    ).round(2).reset_index()


def build_specialty_summary(scored: pd.DataFrame) -> pd.DataFrame:
    summary = scored.groupby("physician_specialty", as_index=False).agg(
        hcps=("physician_id", "count"),
        high_priority_hcps=("segment", lambda x: (x == "High Priority").sum()),
        total_value=("value", "sum"),
        avg_rfm_score=("rfm_score", "mean"),
    )
    summary["high_priority_share"] = (
        summary["high_priority_hcps"] / summary["hcps"]
    ).round(3)
    return summary.round({"total_value": 2, "avg_rfm_score": 2}).sort_values(
        "total_value", ascending=False
    )


def build_regional_gap_summary(scored: pd.DataFrame) -> pd.DataFrame:
    summary = scored.groupby("physician_state", as_index=False).agg(
        hcps=("physician_id", "count"),
        high_priority_hcps=("segment", lambda x: (x == "High Priority").sum()),
        total_value=("value", "sum"),
        avg_rfm_score=("rfm_score", "mean"),
    )
    summary["high_priority_share"] = (
        summary["high_priority_hcps"] / summary["hcps"]
    ).round(3)

    value_cutoff = summary["total_value"].median()
    share_cutoff = summary["high_priority_share"].median()
    summary["regional_gap_flag"] = (
        (summary["total_value"] >= value_cutoff)
        & (summary["high_priority_share"] <= share_cutoff)
    )

    return summary.round({"total_value": 2, "avg_rfm_score": 2}).sort_values(
        ["regional_gap_flag", "total_value"], ascending=[False, False]
    )


def write_outputs(scored: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    scored.to_csv(OUTPUT_DIR / "hcp_segments.csv", index=False)
    build_segment_summary(scored).to_csv(
        OUTPUT_DIR / "segment_summary.csv", index=False
    )
    build_specialty_summary(scored).to_csv(
        OUTPUT_DIR / "specialty_summary.csv", index=False
    )
    build_regional_gap_summary(scored).to_csv(
        OUTPUT_DIR / "regional_gap_summary.csv", index=False
    )
    scored.head(50).to_csv(OUTPUT_DIR / "top_hcps.csv", index=False)


def main() -> None:
    payments = load_payments()
    rfm = build_rfm_table(payments)
    scored = score_rfm(rfm)
    write_outputs(scored)

    print(f"Loaded {len(payments):,} payment records.")
    print(f"Scored {len(scored):,} HCPs.")
    print(scored["segment"].value_counts())
    print(f"Saved outputs to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
