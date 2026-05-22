# Datacenter Permit Tracking Guide

## Overview

Added permit tracking fields to the `ai_datacenters` table:
- `permit_status` - Current permit status (Approved, Pending, Denied, etc.)
- `permit_date` - Date permit was approved/applied/denied
- `permit_notes` - Details about permits, regulatory issues, etc.
- `permit_url` - Link to permit documents, filings, etc.

---

## Setup

### 1. Add permit fields to database

```bash
python3 add_permit_fields.py
```

This will add the four new columns to your existing `ai_datacenters` table.

---

## Usage

### List all datacenters with permit status

```bash
python3 update-permits.py list
```

### List only datacenters with pending permits

```bash
python3 update-permits.py list --pending
```

### Update permit information

```bash
# Add permit status
python3 update-permits.py update 15 --status "Pending"

# Add permit with date and notes
python3 update-permits.py update 15 \
  --status "Approved" \
  --date "2026-05-20" \
  --notes "Building permit approved by Vineland Planning Board"

# Add full permit details
python3 update-permits.py update 15 \
  --status "Pending" \
  --date "2026-03-15" \
  --notes "Air quality permit under review by NJ DEP. 30 natural gas generators require air permit." \
  --url "https://www.nj.gov/dep/aqpp/permit123456"
```

### Search for datacenters by company

```bash
python3 update-permits.py search "CoreWeave"
python3 update-permits.py search "Nebius"
python3 update-permits.py search "Lambda"
```

---

## Valid Permit Statuses

- **Approved** - Permit granted
- **Pending** - Application submitted, awaiting decision
- **Denied** - Permit denied
- **Applied** - Application filed
- **In Review** - Actively being reviewed by agency
- **Appealed** - Denial appealed
- **Unknown** - Status unclear

---

## Examples

### Nebius Vineland Example

```bash
# Find Nebius datacenter ID
python3 update-permits.py search "Nebius"

# Update with permit details (assuming ID is 42)
python3 update-permits.py update 42 \
  --status "Pending" \
  --date "2026-03-15" \
  --notes "Behind-the-meter power using 30 generators. Air quality permit pending NJ DEP review. Expert assessment: 50/50 outcome. Project downsized 70% from original 2.4M sq ft." \
  --url "https://www.ci.vineland.nj.us/planning/permit-PI-75894"
```

### CoreWeave NYC Example

```bash
python3 update-permits.py update 8 \
  --status "Approved" \
  --date "2025-11-20" \
  --notes "NYC DOB permits approved for 400MW NYC facility"
```

---

## Dashboard Integration

The permit fields will automatically appear in:
- **AI Datacenter Tracker** main Kanban board
- **Table View** (filterable by permit status)
- **Intelligence** page (can highlight regulatory risks)

To filter by permit status in the dashboard, add a dropdown filter for `permit_status`.

---

## Workflow Recommendations

### Initial Population
1. Run `python3 update-permits.py list` to see all datacenters
2. For known projects (like Nebius Vineland), update permit details
3. Leave unknown projects as NULL (they'll show "N/A" in listings)

### Ongoing Monitoring
1. Use Google Alerts for company names + "permit" + jurisdiction
2. Check quarterly for permit updates
3. Link to NJ Datacenter Permit Tracker for deep-dive analysis

### Risk Flagging
Use `permit_status` to identify high-risk projects:
- **Pending** + old `permit_date` = Possible delays
- **In Review** + notes about opposition = Regulatory risk
- **Denied** or **Appealed** = Major red flag

---

## Next Steps

**Want to add more features?**
- [ ] Add permit filtering to dashboard
- [ ] Create automated permit alert worker (like `worker_nj_alerts.py`)
- [ ] Add "Days in review" calculation
- [ ] Create permit risk scoring (0-100 based on status, age, notes)

---

*Created: 2026-05-22*  
*Database: gpu-pricing-db*  
*Tables: ai_datacenters*
