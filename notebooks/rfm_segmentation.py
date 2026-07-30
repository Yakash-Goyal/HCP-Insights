"""
RFM Segmentation — HCP Insights & Segmentation Dashboard
==========================================================
Scores each physician on Recency, Frequency, and Value of industry
payments, then buckets them into engagement-priority segments.

Input : data/sample_payments.csv  (swap for a real CMS Open Payments
        export — same column names — to run on real data)
Output: output/hcp_segments.csv   (feed this into Power BI)

Run: python notebooks/rfm_segmentation.py
(This is a plain script rather than a .ipynb so it's easy to read on
GitHub without rendering — convert to a notebook with `jupytext` if
you'd prefer to work in Jupyter.)
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_payments.csv"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "hcp_segments.csv"


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["payment_date"])
    return df


def build_rfm_table(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate raw payment rows into one row per physician with
    Recency, Frequency, and Value metrics."""
    reference_date = df["payment_date"].max()

    rfm = df.groupby(
        ["physician_id", "physician_specialty", "physician_state"]
    ).agg(
        last_payment_date=("payment_date", "max"),
        frequency=("payment_amount", "count"),
        value=("payment_amount", "sum"),
    ).reset_index()

    rfm["recency_days"] = (reference_date - rfm["last_payment_date"]).dt.days
    return rfm


def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    """Score each metric into quartiles (1-4) and combine into a
    single RFM score + segment label.

    Recency is inverted (lower days-since-last-payment = higher score,
    since a more recently engaged physician is more actionable).
    """
    rfm = rfm.copy()

    rfm["r_score"] = pd.qcut(rfm["recency_days"], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["v_score"] = pd.qcut(rfm["value"], 4, labels=[1, 2, 3, 4]).astype(int)

    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["v_score"]

    rfm["segment"] = pd.cut(
        rfm["rfm_score"],
        bins=[0, 5, 8, 12],
        labels=["Low Priority", "Medium Priority", "High Priority"],
    )

    return rfm


def main():
    df = load_data(DATA_PATH)
    rfm = build_rfm_table(df)
    scored = score_rfm(rfm)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    scored.sort_values("rfm_score", ascending=False).to_csv(OUTPUT_PATH, index=False)

    print(f"Scored {len(scored)} physicians.")
    print(scored["segment"].value_counts())
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
