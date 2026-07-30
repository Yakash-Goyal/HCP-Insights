# HCP Insights & Segmentation Dashboard

Analyzes physician-payment data (structured like CMS Open Payments) to identify
and segment high-value healthcare providers (HCPs) for targeted engagement —
a common commercial analytics workflow in life sciences.

## What it does
1. **SQL analysis** (`sql/hcp_analysis.sql`) — profiles payment volume by
   specialty, region, payment type, and top physicians.
2. **RFM segmentation** (`notebooks/rfm_segmentation.py`) — scores each
   physician on Recency, Frequency, and Value of industry payments, and
   buckets them into Low / Medium / High priority segments.
3. **Dashboard** (Power BI) — visualizes segments with drill-downs by
   specialty and geography.

## Data
This repo ships with `data/sample_payments.csv`, a **synthetic** dataset
generated to match the schema of the real [CMS Open Payments](https://openpaymentsdata.cms.gov/)
dataset. Swap it for a real CMS export and everything downstream (SQL,
Python, dashboard) runs unchanged, since column names match.

| Column | Description |
|---|---|
| physician_id | Unique physician identifier |
| physician_specialty | Medical specialty |
| physician_state | US state |
| payment_date | Date of payment |
| payment_amount | Payment amount (USD) |
| payment_type | Consulting fee, speaker fee, travel, meal, research, royalty |
| paying_company | Company making the payment |

## How to run
```bash
pip install -r requirements.txt
python notebooks/rfm_segmentation.py
```
This produces `output/hcp_segments.csv`, which is what the Power BI
dashboard is built from.

For the SQL analysis, load `data/sample_payments.csv` into a table named
`payments` (any SQL engine — SQLite, MySQL, Postgres) and run the queries
in `sql/hcp_analysis.sql`.

## Project structure
```
hcp-insights-dashboard/
├── data/                     # sample (synthetic) payment data
├── sql/                      # SQL profiling queries
├── notebooks/                # RFM segmentation script
├── output/                   # generated segment scores (dashboard input)
├── generate_sample_data.py   # regenerates the synthetic dataset
├── requirements.txt
└── info.md                   # full project write-up
```

See `info.md` for the full project write-up, approach, and findings.
