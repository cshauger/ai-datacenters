#!/usr/bin/env python3
"""
Revenue projection model for AI datacenter companies

Business Model Assumptions:
- GPU Cloud (CoreWeave, Lambda, Nebius): $250-350k revenue per MW per year
- Colocation: $150-200k per MW per year  
- Hyperscaler (self-use): Not revenue-generating, exclude from projections

Utilization Ramp:
- Q1 online: 0-20%
- Q2: 40-60%
- Q3: 60-80%
- Q4+: 80-95%
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

DATABASE_URL = os.environ.get('DATABASE_URL')

# Revenue models (annual $ per MW)
REVENUE_MODELS = {
    'gpu_cloud': {
        'conservative': 200000,
        'base': 275000,
        'aggressive': 350000
    },
    'colocation': {
        'conservative': 120000,
        'base': 165000,
        'aggressive': 210000
    },
    'hyperscaler': {
        'conservative': 0,
        'base': 0,
        'aggressive': 0
    }
}

# Company to business model mapping
COMPANY_BUSINESS_MODELS = {
    'CoreWeave': 'gpu_cloud',
    'Lambda Labs': 'gpu_cloud',
    'Nebius': 'gpu_cloud',
    'Crusoe Energy': 'gpu_cloud',
    'Applied Digital': 'gpu_cloud',
    'Genesis Cloud': 'gpu_cloud',
    'Voltage Park': 'gpu_cloud',
    'FluidStack': 'gpu_cloud',
    'Together.ai': 'gpu_cloud',
    'DataCrunch': 'gpu_cloud',
    'Ori': 'gpu_cloud',
    
    # Add others as colocation or hyperscaler
    # Default to colocation if unknown
}

def get_business_model(company):
    """Get business model for a company"""
    return COMPANY_BUSINESS_MODELS.get(company, 'colocation')

def get_utilization_ramp(quarters_since_online):
    """
    Get utilization % based on quarters since datacenter came online
    
    Args:
        quarters_since_online: 0 = launch quarter, 1 = first full quarter, etc.
    
    Returns:
        tuple: (conservative_util%, base_util%, aggressive_util%)
    """
    ramps = {
        0: (5, 15, 25),    # Launch quarter
        1: (25, 40, 55),   # Q+1
        2: (45, 65, 80),   # Q+2
        3: (65, 80, 90),   # Q+3
        4: (75, 85, 95),   # Q+4
    }
    
    # After Q+4, use mature utilization
    if quarters_since_online >= 4:
        return (75, 85, 95)
    
    return ramps.get(quarters_since_online, (0, 0, 0))

def parse_quarter(quarter_str):
    """Parse 'Q1-2026' into start/end dates"""
    q, year = quarter_str.split('-')
    quarter_num = int(q[1])
    year = int(year)
    
    quarter_starts = {
        1: (1, 1),
        2: (4, 1),
        3: (7, 1),
        4: (10, 1)
    }
    
    start_month, start_day = quarter_starts[quarter_num]
    start_date = datetime(year, start_month, start_day).date()
    end_date = (start_date + relativedelta(months=3) - timedelta(days=1))
    
    return start_date, end_date

def generate_quarterly_projections(start_quarter, end_quarter, scenario='base'):
    """
    Generate revenue projections for all datacenters
    
    Args:
        start_quarter: 'Q1-2026'
        end_quarter: 'Q4-2027'
        scenario: 'conservative', 'base', or 'aggressive'
    """
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Get all datacenters
    cur.execute("""
        SELECT 
            id, company, location, mw_capacity, status, 
            online_date, construction_start_date
        FROM ai_datacenters
        WHERE mw_capacity IS NOT NULL
        ORDER BY company, location;
    """)
    
    datacenters = cur.fetchall()
    
    print(f"\n🔄 Generating {scenario} revenue projections...")
    print(f"   Period: {start_quarter} to {end_quarter}")
    print(f"   Datacenters: {len(datacenters)}\n")
    
    # Generate quarters
    quarters = generate_quarter_list(start_quarter, end_quarter)
    
    projections_created = 0
    
    for dc in datacenters:
        dc_id, company, location, mw_capacity, status, online_date, construction_date = dc
        
        business_model = get_business_model(company)
        revenue_per_mw = REVENUE_MODELS[business_model][scenario]
        
        # Skip hyperscalers (no revenue)
        if revenue_per_mw == 0:
            continue
        
        # Estimate online date if not set
        if not online_date:
            online_date = estimate_online_date(status, construction_date)
        
        if not online_date:
            print(f"   ⚠️  Skipping {company} - {location}: No online date")
            continue
        
        for quarter in quarters:
            quarter_start, quarter_end = parse_quarter(quarter)
            
            # Calculate operational MW and utilization
            if online_date > quarter_end:
                # Not online yet
                operational_mw = 0
                utilization = 0
            elif online_date <= quarter_start:
                # Fully operational for entire quarter
                quarters_since_online = calculate_quarters_since(online_date, quarter_start)
                operational_mw = mw_capacity
                _, utilization, _ = get_utilization_ramp(quarters_since_online)
                if scenario == 'conservative':
                    utilization, _, _ = get_utilization_ramp(quarters_since_online)
                elif scenario == 'aggressive':
                    _, _, utilization = get_utilization_ramp(quarters_since_online)
            else:
                # Came online mid-quarter (partial)
                days_in_quarter = (quarter_end - quarter_start).days + 1
                days_online = (quarter_end - online_date).days + 1
                partial_factor = days_online / days_in_quarter
                
                operational_mw = mw_capacity * partial_factor
                _, utilization, _ = get_utilization_ramp(0)  # Launch quarter
                if scenario == 'conservative':
                    utilization, _, _ = get_utilization_ramp(0)
                elif scenario == 'aggressive':
                    _, _, utilization = get_utilization_ramp(0)
            
            # Calculate quarterly revenue
            quarterly_revenue = (operational_mw * (utilization / 100) * revenue_per_mw) / 4
            
            # Insert projection
            cur.execute("""
                INSERT INTO datacenter_revenue_projections 
                    (datacenter_id, quarter_year, quarter_start_date, quarter_end_date,
                     operational_mw, utilization_percent, revenue_per_mw_annual,
                     quarterly_revenue, model_version, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (datacenter_id, quarter_year) 
                DO UPDATE SET
                    operational_mw = EXCLUDED.operational_mw,
                    utilization_percent = EXCLUDED.utilization_percent,
                    revenue_per_mw_annual = EXCLUDED.revenue_per_mw_annual,
                    quarterly_revenue = EXCLUDED.quarterly_revenue,
                    model_version = EXCLUDED.model_version,
                    last_updated = CURRENT_TIMESTAMP;
            """, (
                dc_id, quarter, quarter_start, quarter_end,
                round(operational_mw, 2), round(utilization, 2), revenue_per_mw,
                round(quarterly_revenue, 2), f"v1.0-{scenario}",
                f"{business_model} model, online {online_date}"
            ))
            
            projections_created += 1
    
    conn.commit()
    
    print(f"\n✅ Created {projections_created} quarterly projections")
    
    # Show summary
    cur.execute("""
        SELECT 
            company,
            COUNT(DISTINCT quarter_year) as quarters,
            SUM(quarterly_revenue) as total_revenue
        FROM company_quarterly_revenue
        GROUP BY company
        ORDER BY total_revenue DESC;
    """)
    
    print(f"\n📊 Company Revenue Summary ({scenario} scenario):\n")
    print(f"{'Company':<25} {'Quarters':<10} {'Total Revenue':<20}")
    print("-" * 60)
    
    for row in cur.fetchall():
        company, quarters, total_revenue = row
        revenue_str = f"${total_revenue/1e6:.1f}M" if total_revenue else "$0"
        print(f"{company:<25} {quarters:<10} {revenue_str:<20}")
    
    cur.close()
    conn.close()

def generate_quarter_list(start_quarter, end_quarter):
    """Generate list of quarters from start to end"""
    start_q, start_y = int(start_quarter[1]), int(start_quarter[3:])
    end_q, end_y = int(end_quarter[1]), int(end_quarter[3:])
    
    quarters = []
    current_y, current_q = start_y, start_q
    
    while (current_y < end_y) or (current_y == end_y and current_q <= end_q):
        quarters.append(f"Q{current_q}-{current_y}")
        current_q += 1
        if current_q > 4:
            current_q = 1
            current_y += 1
    
    return quarters

def calculate_quarters_since(online_date, current_quarter_start):
    """Calculate how many quarters since datacenter came online"""
    months_diff = (current_quarter_start.year - online_date.year) * 12
    months_diff += current_quarter_start.month - online_date.month
    return max(0, months_diff // 3)

def estimate_online_date(status, construction_date):
    """Estimate online date based on status and construction date"""
    if status == 'Operational':
        return datetime.now().date()  # Assume already online
    elif status == 'Under Construction' and construction_date:
        # Assume 18-month build time
        return construction_date + relativedelta(months=18)
    elif status == 'Planned' and construction_date:
        # Assume starts in 6 months, 18-month build
        return construction_date + relativedelta(months=24)
    else:
        return None

def print_usage():
    print("""
Usage:
  python revenue-model.py generate <start_quarter> <end_quarter> [scenario]
  python revenue-model.py show-company <company_name>

Examples:
  python revenue-model.py generate Q1-2026 Q4-2027
  python revenue-model.py generate Q1-2026 Q4-2027 aggressive
  python revenue-model.py show-company CoreWeave

Scenarios: conservative, base (default), aggressive
""")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'generate':
        if len(sys.argv) < 4:
            print_usage()
            sys.exit(1)
        
        start_quarter = sys.argv[2]
        end_quarter = sys.argv[3]
        scenario = sys.argv[4] if len(sys.argv) > 4 else 'base'
        
        generate_quarterly_projections(start_quarter, end_quarter, scenario)
    
    elif command == 'show-company':
        if len(sys.argv) < 3:
            print_usage()
            sys.exit(1)
        
        company = sys.argv[2]
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT quarter_year, total_quarterly_revenue, total_operational_mw, avg_utilization_percent
            FROM company_quarterly_revenue
            WHERE company ILIKE %s
            ORDER BY quarter_start_date;
        """, (f'%{company}%',))
        
        rows = cur.fetchall()
        
        if not rows:
            print(f"No projections found for {company}")
            sys.exit(1)
        
        print(f"\n📈 Revenue Projections for {company}:\n")
        print(f"{'Quarter':<12} {'Revenue':<18} {'Operational MW':<18} {'Utilization %':<15}")
        print("-" * 70)
        
        for row in rows:
            quarter, revenue, mw, util = row
            revenue_str = f"${revenue/1e6:.2f}M" if revenue else "$0"
            mw_str = f"{mw:.1f} MW" if mw else "0 MW"
            util_str = f"{util:.1f}%" if util else "0%"
            print(f"{quarter:<12} {revenue_str:<18} {mw_str:<18} {util_str:<15}")
        
        total_revenue = sum(row[1] or 0 for row in rows)
        print(f"\nTotal Revenue: ${total_revenue/1e6:.2f}M")
        
        cur.close()
        conn.close()
    
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
