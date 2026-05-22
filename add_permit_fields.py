#!/usr/bin/env python3
"""
Add permit tracking fields to ai_datacenters table
"""

import os
import psycopg2
from psycopg2 import sql

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')

def add_permit_fields():
    """Add permit tracking columns to ai_datacenters table"""
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Add permit fields
    alter_queries = [
        """
        ALTER TABLE ai_datacenters 
        ADD COLUMN IF NOT EXISTS permit_status VARCHAR(50),
        ADD COLUMN IF NOT EXISTS permit_date DATE,
        ADD COLUMN IF NOT EXISTS permit_notes TEXT,
        ADD COLUMN IF NOT EXISTS permit_url TEXT;
        """,
        
        # Create index for filtering by permit status
        """
        CREATE INDEX IF NOT EXISTS idx_permit_status 
        ON ai_datacenters(permit_status);
        """
    ]
    
    for query in alter_queries:
        cur.execute(query)
        print(f"Executed: {query[:80]}...")
    
    conn.commit()
    
    # Verify columns were added
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'ai_datacenters' 
        AND column_name LIKE 'permit%'
        ORDER BY column_name;
    """)
    
    print("\n✅ Permit fields added successfully:")
    for row in cur.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    add_permit_fields()
