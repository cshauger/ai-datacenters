#!/usr/bin/env python3
"""
Create revenue projections table linked to ai_datacenters
"""

import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

def create_revenue_projections_table():
    """Create table for quarterly revenue projections per datacenter"""
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Create revenue projections table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS datacenter_revenue_projections (
        id SERIAL PRIMARY KEY,
        datacenter_id INTEGER REFERENCES ai_datacenters(id),
        quarter_year VARCHAR(10) NOT NULL,  -- Format: 'Q1-2026', 'Q2-2026', etc.
        quarter_start_date DATE,
        quarter_end_date DATE,
        
        -- Revenue drivers
        operational_mw DECIMAL(10,2),  -- MW capacity operational this quarter
        utilization_percent DECIMAL(5,2),  -- 0-100%
        revenue_per_mw_annual DECIMAL(12,2),  -- Annual revenue per MW ($)
        
        -- Calculated revenue
        quarterly_revenue DECIMAL(15,2),  -- Calculated: (operational_mw * utilization * revenue_per_mw / 4)
        
        -- Metadata
        model_version VARCHAR(50),  -- Track which revenue model was used
        notes TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(datacenter_id, quarter_year)
    );
    """
    
    cur.execute(create_table_query)
    print("✅ Created datacenter_revenue_projections table")
    
    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_revenue_quarter ON datacenter_revenue_projections(quarter_year);",
        "CREATE INDEX IF NOT EXISTS idx_revenue_datacenter ON datacenter_revenue_projections(datacenter_id);",
        "CREATE INDEX IF NOT EXISTS idx_revenue_company ON datacenter_revenue_projections(datacenter_id);",
    ]
    
    for idx in indexes:
        cur.execute(idx)
    
    print("✅ Created indexes")
    
    # Create aggregation view (company-level quarterly revenue)
    view_query = """
    CREATE OR REPLACE VIEW company_quarterly_revenue AS
    SELECT 
        d.company,
        r.quarter_year,
        r.quarter_start_date,
        SUM(r.operational_mw) as total_operational_mw,
        AVG(r.utilization_percent) as avg_utilization_percent,
        SUM(r.quarterly_revenue) as total_quarterly_revenue,
        COUNT(DISTINCT r.datacenter_id) as num_datacenters,
        MAX(r.last_updated) as last_updated
    FROM datacenter_revenue_projections r
    JOIN ai_datacenters d ON r.datacenter_id = d.id
    GROUP BY d.company, r.quarter_year, r.quarter_start_date
    ORDER BY d.company, r.quarter_start_date;
    """
    
    cur.execute(view_query)
    print("✅ Created company_quarterly_revenue view")
    
    conn.commit()
    
    # Verify
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'datacenter_revenue_projections'
        ORDER BY ordinal_position;
    """)
    
    print("\n📋 Revenue Projections Table Schema:")
    for row in cur.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    create_revenue_projections_table()
