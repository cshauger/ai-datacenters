# Datacenter Contractor Tracking Guide

## Overview

Added contractor and supply chain tracking fields to the `ai_datacenters` table:
- `prime_contractor` - General contractor/builder (e.g., Data One USA, Ark, Verne, Caverion)
- `cooling_supplier` - Liquid cooling system provider
- `contractor_track_record` - Notes on experience, past projects, risk factors
- `build_model` - Construction approach (In-house, Contractor, Design-Build, Hybrid)

---

## Setup

### 1. Add contractor fields to database

```bash
python3 add_contractor_fields.py
```

This will:
- Add 4 new columns to `ai_datacenters` table
- Auto-populate known Nebius contractors:
  - Vineland, NJ → Data One USA
  - UK → Ark
  - Iceland → Verne
  - Finland → Caverion

---

## Usage

### List all datacenters with contractor info

```bash
python3 update-contractors.py list
```

### Filter by contractor

```bash
python3 update-contractors.py list --contractor "Data One"
```

### Filter by build model

```bash
python3 update-contractors.py list --build-model "Contractor"
```

### Update contractor information

```bash
# Add contractor only
python3 update-contractors.py update 15 --contractor "Data One USA"

# Add full contractor details
python3 update-contractors.py update 15 \
  --contractor "Data One USA" \
  --model "Contractor" \
  --notes "1-year-old company, no US datacenter experience, behind-the-meter power strategy"

# Add cooling supplier
python3 update-contractors.py update 15 \
  --contractor "Data One USA" \
  --cooling "Vertiv" \
  --model "Contractor"
```

### Search by company

```bash
python3 update-contractors.py search "Nebius"
python3 update-contractors.py search "CoreWeave"
```

### View statistics

```bash
python3 update-contractors.py stats
```

Shows:
- Top contractors by site count and MW capacity
- Build model distribution
- Company build strategies

---

## Valid Build Models

- **In-house** - Company builds with own teams (e.g., hyperscalers)
- **Contractor** - Outsourced to general contractor (e.g., Nebius)
- **Design-Build** - Integrated design and construction
- **Hybrid** - Mix of in-house and contractor
- **Unknown** - Not yet determined

---

## Key Insights: Nebius Strategy

**Finding**: Nebius has NO in-house build capability or cooling supply chain. All datacenters are contractor-built.

| **Site** | **Contractor** | **Risk Level** | **Notes** |
|----------|----------------|----------------|-----------|
| **Vineland, NJ** | Data One USA | 🔴 **High** | 1-year-old, no US datacenter experience, behind-the-meter power |
| **UK** | Ark | 🟡 Medium | Established contractor |
| **Iceland** | Verne | 🟡 Medium | Local expertise |
| **Finland** | Caverion | 🟢 Low | Major Nordic contractor |

**Investment implications:**
- Higher execution risk (dependency on contractors)
- Potential timeline delays
- Less control over build quality
- Each contractor brings own liquid cooling suppliers

---

## Examples

### Update CoreWeave (In-house build)

```bash
# Find CoreWeave datacenter ID
python3 update-contractors.py search "CoreWeave"

# Tag as in-house (assuming ID 8)
python3 update-contractors.py update 8 \
  --model "In-house" \
  --notes "Vertically integrated build capability, owns manufacturing supply chain"
```

### Update Lambda Labs

```bash
python3 update-contractors.py update 22 \
  --contractor "DPR Construction" \
  --model "Contractor" \
  --cooling "Vertiv"
```

### Flag high-risk contractor

```bash
python3 update-contractors.py update 42 \
  --contractor "Data One USA" \
  --model "Contractor" \
  --notes "RED FLAG: 1-year-old company, zero US datacenter track record. Behind-the-meter power using 30 generators requires complex permitting. Expert assessment: 50/50 project outcome."
```

---

## Dashboard Integration

The contractor fields will automatically appear in:
- **AI Datacenter Tracker** main Kanban board
- **Table View** (filterable by contractor/build model)
- **Intelligence** page (highlight contractor risks)

### Recommended views:

1. **Contractor risk heatmap** - Sites by contractor experience
2. **Build model comparison** - In-house vs Contractor timelines
3. **Supply chain tracking** - Cooling suppliers across sites

---

## Workflow Recommendations

### Initial Population

1. Run migration: `python3 add_contractor_fields.py`
2. Nebius sites auto-populate with contractors
3. Manually add other known contractors
4. Leave unknown projects as NULL

### Ongoing Monitoring

1. **New project announced** → Research contractor → Update database
2. **Contractor delays** → Update `contractor_track_record` with risk notes
3. **Quarterly review** → Check contractor performance across all sites

### Risk Scoring

Use contractor data to flag high-risk projects:
- **Inexperienced contractor** (< 2 years, no datacenter history) = 🔴 High risk
- **Behind-the-meter power** + inexperienced = 🔴🔴 Critical risk
- **Established contractor** (Caverion, DPR, Turner) = 🟢 Low risk
- **In-house build** (CoreWeave, Meta, Google) = 🟢 Lowest risk

---

## Statistics & Analysis

### View contractor concentration

```bash
python3 update-contractors.py stats
```

**Example output:**
```
📊 Contractor Statistics:

Contractor                     Sites      Total MW    
-------------------------------------------------------
Data One USA                   4          1200        
Caverion                       2          600         
Ark                            1          300         

📊 Build Model Statistics:

Build Model          Sites      Total MW    
---------------------------------------------
Contractor           15         4500        
In-house             8          6000        
Design-Build         3          1200        

📊 Company Build Strategies:

Company              Sites      Contractors     Build Model    
-----------------------------------------------------------------
Nebius               4          4               Contractor
CoreWeave            12         1               In-house
Lambda Labs          5          3               Contractor
```

---

## Next Steps

**Want to add more features?**
- [ ] Add contractor filtering to dashboard
- [ ] Create contractor risk scoring (0-100)
- [ ] Track contractor delays and compare to timeline
- [ ] Add "Days in construction" field to calculate contractor performance
- [ ] Link to permit tracking (contractor + permit delays = red flag)

---

*Created: 2026-05-24*  
*Database: gpu-pricing-db*  
*Tables: ai_datacenters*
