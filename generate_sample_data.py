"""
Generates a synthetic sample dataset structured like CMS Open Payments,
so the project can run end-to-end without needing to download the ~2GB
real dataset first. Swap data/sample_payments.csv for a real CMS Open
Payments export (https://openpaymentsdata.cms.gov/) to run on real data —
column names match, so no other code needs to change.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

specialties = ["Cardiology", "Oncology", "Endocrinology", "Neurology",
               "Pulmonology", "Rheumatology", "General Practice", "Psychiatry"]
states = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
payment_types = ["Consulting Fee", "Speaker Fee", "Travel & Lodging",
                  "Meal", "Research Payment", "Royalty"]

n_physicians = 500
n_payments = 4000

physician_ids = [f"PHY{str(i).zfill(5)}" for i in range(1, n_physicians + 1)]
physician_specialty = {pid: np.random.choice(specialties) for pid in physician_ids}
physician_state = {pid: np.random.choice(states) for pid in physician_ids}

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)

rows = []
for _ in range(n_payments):
    pid = np.random.choice(physician_ids)
    days_offset = np.random.randint(0, (end_date - start_date).days)
    payment_date = start_date + timedelta(days=int(days_offset))
    amount = round(np.random.lognormal(mean=5.5, sigma=1.2), 2)  # skewed, realistic-ish
    rows.append({
        "physician_id": pid,
        "physician_specialty": physician_specialty[pid],
        "physician_state": physician_state[pid],
        "payment_date": payment_date.strftime("%Y-%m-%d"),
        "payment_amount": amount,
        "payment_type": np.random.choice(payment_types),
        "paying_company": np.random.choice(
            ["Acme Pharma", "NovaHealth Inc", "BioGen Solutions", "MedCore Ltd"]
        ),
    })

df = pd.DataFrame(rows)
df.to_csv("data/sample_payments.csv", index=False)
print(f"Generated {len(df)} payment records for {n_physicians} physicians.")
print(df.head())
