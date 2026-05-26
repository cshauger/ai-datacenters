# AI Datacenter Revenue Projections Guide

## Overview

Translate your AI datacenter capacity data into quarterly revenue forecasts for each company.

**System Components:**
1. **Revenue Models** - $/MW assumptions by business type (GPU cloud, colocation, etc.)
2. **Utilization Ramps** - 0-20% (launch) → 80-95% (mature) over 4+ quarters
3. **Quarterly Projections** - Per-datacenter revenue forecasts
4. **Company Aggregations** - Roll-up to company-level quarterly revenue

---

## Business Model Assumptions

### GPU Cloud (CoreWeave, Lambda, Nebius, etc.)

**Revenue per MW (annual):**
- Conservative: $200,000
- Base: $275,000
- Aggressive: $350,000

**Rationale:** GPU cloud providers charge $2-4/hour per H100 GPU. At ~400W per GPU:
- 1 MW = ~2,500 GPUs
- Revenue = 2,500 GPUs × $3/hr × 8,760 hrs/yr × 80% utilization = ~$525k/MW
- Discount for wholesale, competition, downtime → $200-350k/MW

### Colocation

**Revenue per MW (annual):**
- Conservative: $120,000
- Base: $165,000
- Aggressive: $210,000

**Rationale:** Colocation charges $100-200/kW/month:
- 1 MW = 1,000 kW
- Revenue = 1,000 kW × $150/kW/month × 12 months = $1.8M/MW
- Discount for wholesale contracts, power costs → $120-210k/MW

### Hyperscaler (Self-Use)

**Revenue per MW:** $0

**Rationale:** Not a revenue-generating business (internal use only).

---

## Utilization Ramp Assumptions

Datacenters don't go from 0% → 100% overnight. Typical ramp:

| Quarters Since Online | Conservative | Base | Aggressive |
|-----------------------|--------------|------|------------|
| Q0 (Launch quarter)   | 5%           | 15%  | 25%        |
| Q+1                   | 25%          | 40%  | 55%        |
| Q+2                   | 45%          | 65%  | 80%        |
| Q+3                   | 65%          | 80%  | 90%        |
| Q+4+                  | 75%          | 85%  | 95%        |

**Example:** CoreWeave datacenter with 100 MW comes online Q1-2026:
- Q1-2026: 100 MW × 15% = 15 MW utilized → Revenue = 15 × $275k / 4 = $1.03M
- Q2-2026: 100 MW × 40% = 40 MW utilized → Revenue = $2.75M
- Q3-2026: 100 MW × 65% = 65 MW utilized → Revenue = $4.47M
- Q4-2026: 100 MW × 80% = 80 MW utilized → Revenue = $5.50M

---

## Setup

### 1. Create Revenue Projections Table

```bash
python3 create_revenue_projections_table.py
```

This creates:
- `datacenter_revenue_projections` table (per-datacenter, per-quarter)
- `company_quarterly_revenue` view (aggregated by company)
- Indexes for fast querying

---

## Usage

### Generate Projections (Base Scenario)

```bash
python3 revenue-model.py generate Q1-2026 Q4-2027
```

**Output:**
```
🔄 Generating base revenue projections...
   Period: Q1-2026 to Q4-2027
   Datacenters: 81

✅ Created 648 quarterly projections

📊 Company Revenue Summary (base scenario):

Company                   Quarters   Total Revenue       
------------------------------------------------------------
CoreWeave                 8          $1,234.5M
Lambda Labs               8          $567.8M
Nebius                    8          $432.1M
...
```

### Generate Projections (Conservative)

```bash
python3 revenue-model.py generate Q1-2026 Q4-2027 conservative
```

Lower revenue per MW + slower utilization ramps.

### Generate Projections (Aggressive)

```bash
python3 revenue-model.py generate Q1-2026 Q4-2027 aggressive
```

Higher revenue per MW + faster utilization ramps.

---

## View Results

### Show Company-Level Revenue

```bash
python3 revenue-model.py show-company CoreWeave
```

**Output:**
```
📈 Revenue Projections for CoreWeave:

Quarter      Revenue            Operational MW     Utilization %
----------------------------------------------------------------------
Q1-2026      $12.34M            45.0 MW            15.0%
Q2-2026      $37.50M            150.0 MW           40.0%
Q3-2026      $89.38M            275.0 MW           65.0%
Q4-2026      $176.00M           440.0 MW           80.0%
Q1-2027      $224.06M           528.0 MW           85.0%
Q2-2027      $280.88M           660.0 MW           85.0%
Q3-2027      $336.56M           792.0 MW           85.0%
Q4-2027      $392.25M           924.0 MW           85.0%

Total Revenue: $1,548.97M
```

### Query Projections Directly (SQL)

```sql
-- Company-level quarterly revenue
SELECT * FROM company_quarterly_revenue
WHERE company = 'CoreWeave'
ORDER BY quarter_start_date;

-- Per-datacenter detail
SELECT 
    d.company,
    d.location,
    r.quarter_year,
    r.operational_mw,
    r.utilization_percent,
    r.quarterly_revenue
FROM datacenter_revenue_projections r
JOIN ai_datacenters d ON r.datacenter_id = d.id
WHERE d.company = 'Nebius'
ORDER BY r.quarter_start_date, d.location;

-- Top revenue generators (single quarter)
SELECT 
    d.company,
    d.location,
    r.quarterly_revenue
FROM datacenter_revenue_projections r
JOIN ai_datacenters d ON r.datacenter_id = d.id
WHERE r.quarter_year = 'Q4-2027'
ORDER BY r.quarterly_revenue DESC
LIMIT 10;
```

---

## Customization

### Add New Company Business Model

Edit `revenue-model.py`:

```python
COMPANY_BUSINESS_MODELS = {
    'CoreWeave': 'gpu_cloud',
    'YourNewCompany': 'colocation',  # <-- Add here
    ...
}
```

### Adjust Revenue Models

Edit `revenue-model.py`:

```python
REVENUE_MODELS = {
    'gpu_cloud': {
        'conservative': 220000,  # <-- Increase from $200k
        'base': 300000,          # <-- Increase from $275k
        'aggressive': 380000     # <-- Increase from $350k
    },
    ...
}
```

### Adjust Utilization Ramps

Edit `get_utilization_ramp()` function in `revenue-model.py`:

```python
def get_utilization_ramp(quarters_since_online):
    ramps = {
        0: (10, 20, 30),   # <-- Faster ramp in launch quarter
        1: (30, 50, 70),   # <-- Faster Q+1
        ...
    }
```

---

## Integration with Dashboard

### Add Revenue Tab to AI Datacenter Tracker

**pages/6_Revenue_Projections.py:**

```python
import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Revenue Projections", page_icon="💰")

# Fetch company revenue
conn = psycopg2.connect(st.secrets["DATABASE_URL"])
df = pd.read_sql("""
    SELECT 
        company,
        quarter_year,
        total_quarterly_revenue as revenue,
        total_operational_mw as mw
    FROM company_quarterly_revenue
    ORDER BY company, quarter_start_date;
""", conn)

# Pivot for chart
pivot = df.pivot(index='quarter_year', columns='company', values='revenue')

st.title("💰 Revenue Projections")
st.line_chart(pivot)

# Table view
st.dataframe(df)
```

---

## Export to Excel

```bash
# Export CoreWeave projections to CSV
python3 << EOF
import psycopg2
import csv

conn = psycopg2.connect("DATABASE_URL_HERE")
cur = conn.cursor()

cur.execute("""
    SELECT * FROM company_quarterly_revenue
    WHERE company = 'CoreWeave'
    ORDER BY quarter_start_date;
""")

with open('coreweave_revenue.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow([desc[0] for desc in cur.description])
    writer.writerows(cur.fetchall())

print("✅ Exported to coreweave_revenue.csv")
EOF
```

---

## Scenarios & Sensitivity Analysis

### Run All Three Scenarios

```bash
python3 revenue-model.py generate Q1-2026 Q4-2027 conservative
python3 revenue-model.py generate Q1-2026 Q4-2027 base
python3 revenue-model.py generate Q1-2026 Q4-2027 aggressive
```

**Compare results:** Query `model_version` field to filter by scenario.

```sql
SELECT 
    company,
    quarter_year,
    SUM(CASE WHEN model_version LIKE 'v1.0-conservative%' THEN quarterly_revenue ELSE 0 END) as conservative,
    SUM(CASE WHEN model_version LIKE 'v1.0-base%' THEN quarterly_revenue ELSE 0 END) as base,
    SUM(CASE WHEN model_version LIKE 'v1.0-aggressive%' THEN quarterly_revenue ELSE 0 END) as aggressive
FROM datacenter_revenue_projections r
JOIN ai_datacenters d ON r.datacenter_id = d.id
WHERE company = 'CoreWeave'
GROUP BY company, quarter_year
ORDER BY quarter_year;
```

---

## Key Assumptions & Limitations

### Assumptions:
1. **Linear MW pricing** - Assumes revenue scales linearly with MW (not always true; bulk discounts exist)
2. **Constant pricing** - Doesn't model GPU price erosion over time
3. **No churn** - Assumes datacenters stay at utilization plateau (no customer churn modeled)
4. **Instant online** - Assumes datacenter goes live on `online_date` (no soft launches modeled)
5. **No seasonality** - Assumes constant quarterly demand (AI workloads have some seasonality)

### Limitations:
- **No capital structure** - Doesn't model debt, equity dilution, or fundraising
- **No opex** - Revenue only, no COGS/opex → Can't calculate EBITDA/margins
- **No competitive dynamics** - Doesn't model pricing pressure from new entrants
- **No regulatory risk** - Doesn't model permit delays, energy curtailment

### Recommended Use:
- **Top-down market sizing** ✅
- **Relative company comparison** ✅  
- **Fundraising deck revenue projections** ✅
- **DCF valuation inputs** ⚠️ (add opex model first)
- **Trading models** ❌ (too simplified for short-term price movements)

---

## Troubleshooting

### "No online date" Warnings

**Problem:** Datacenters without `online_date` are skipped.

**Fix:** Update `ai_datacenters` table with estimated online dates:

```sql
UPDATE ai_datacenters
SET online_date = '2027-06-01'
WHERE company = 'Nebius' AND location LIKE '%Vineland%';
```

**Or:** The model auto-estimates based on:
- `status = 'Operational'` → Assume already online (today)
- `status = 'Under Construction'` + `construction_start_date` → Assume 18-month build
- `status = 'Planned'` + `construction_start_date` → Assume 6-month delay + 18-month build

### Revenue Looks Too High/Low

**Check:**
1. Business model assignment (GPU cloud vs colocation)
2. Utilization ramp (conservative vs aggressive)
3. MW capacity (is it realistic?)

**Adjust:** Edit `REVENUE_MODELS` or `get_utilization_ramp()` in `revenue-model.py`.

---

## Next Steps

**Enhancements to build:**
1. **Opex Model** - Model power costs, labor, depreciation → Calculate EBITDA
2. **Capital Model** - Model capex per MW, funding rounds → Calculate cash burn/runway
3. **Competitive Pricing** - Model GPU price erosion (H100 → H200 → B200)
4. **Permit Risk** - Integrate with `permit_status` field → Adjust online dates for delays
5. **Export to Google Sheets** - Auto-sync projections for easy sharing

---

*Created: 2026-05-26*  
*Database: gpu-pricing-db*  
*Tables: datacenter_revenue_projections, company_quarterly_revenue (view)*
