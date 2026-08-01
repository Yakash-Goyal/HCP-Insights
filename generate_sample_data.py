"""Generate synthetic HCP payment data for the sample project."""

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT_PATH = Path("data") / "sample_payments.csv"

np.random.seed(42)

specialties = [
    "Cardiology",
    "Oncology",
    "Endocrinology",
    "Neurology",
    "Pulmonology",
    "Rheumatology",
    "General Practice",
    "Psychiatry",
]
states = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
payment_types = [
    "Consulting Fee",
    "Speaker Fee",
    "Travel & Lodging",
    "Meal",
    "Research Payment",
    "Royalty",
]
paying_companies = [
    "Acme Pharma",
    "NovaHealth Inc",
    "BioGen Solutions",
    "MedCore Ltd",
]

n_physicians = 500
n_payments = 4000

physician_ids = [f"PHY{str(i).zfill(5)}" for i in range(1, n_physicians + 1)]
physician_specialty = {pid: np.random.choice(specialties) for pid in physician_ids}
physician_state = {pid: np.random.choice(states) for pid in physician_ids}

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)


def create_payment_row(physician_id: str) -> dict[str, object]:
    days_offset = np.random.randint(0, (end_date - start_date).days + 1)
    payment_date = start_date + timedelta(days=int(days_offset))
    payment_amount = round(np.random.lognormal(mean=5.5, sigma=1.2), 2)

    return {
        "physician_id": physician_id,
        "physician_specialty": physician_specialty[physician_id],
        "physician_state": physician_state[physician_id],
        "payment_date": payment_date.strftime("%Y-%m-%d"),
        "payment_amount": payment_amount,
        "payment_type": np.random.choice(payment_types),
        "paying_company": np.random.choice(paying_companies),
    }


rows = []

# Add one row for each HCP so every synthetic physician appears in the sample.
for physician_id in physician_ids:
    rows.append(create_payment_row(physician_id))

for _ in range(n_payments - n_physicians):
    rows.append(create_payment_row(np.random.choice(physician_ids)))

df = pd.DataFrame(rows)
OUTPUT_PATH.parent.mkdir(exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"Generated {len(df):,} payment records.")
print(f"Unique HCPs: {df['physician_id'].nunique():,}")
print(f"Saved to {OUTPUT_PATH}")
