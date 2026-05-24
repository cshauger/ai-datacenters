#!/usr/bin/env python3
"""
Add contractor tracking fields to ai_datacenters table
"""

import os
import psycopg2

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')

def add_contractor_fields():
    """Add contractor and supply chain tracking columns to ai_datacenters table"""
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Add contractor fields
    alter_queries = [
        """
        ALTER TABLE ai_datacenters 
        ADD COLUMN IF NOT EXISTS prime_contractor VARCHAR(255),
        ADD COLUMN IF NOT EXISTS cooling_supplier VARCHAR(255),
        ADD COLUMN IF NOT EXISTS contractor_track_record TEXT,
        ADD COLUMN IF NOT EXISTS build_model VARCHAR(50);
        """,
        
        # Create indexes for filtering
        """
        CREATE INDEX IF NOT EXISTS idx_prime_contractor 
        ON ai_datacenters(prime_contractor);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_build_model 
        ON ai_datacenters(build_model);
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
        AND column_name IN ('prime_contractor', 'cooling_supplier', 'contractor_track_record', 'build_model')
        ORDER BY column_name;
    """)
    
    print("\n✅ Contractor fields added successfully:")
    for row in cur.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    # Populate known Nebius contractors
    print("\n📝 Populating known Nebius contractors...")
    
    nebius_updates = [
        # Vineland, NJ
        ("UPDATE ai_datacenters SET prime_contractor = 'Data One USA', "
         "contractor_track_record = '1-year-old company, no US datacenter track record, behind-the-meter power using 30 generators', "
         "build_model = 'Contractor' "
         "WHERE company = 'Nebius' AND location ILIKE '%Vineland%';"),
        
        # UK
        ("UPDATE ai_datacenters SET prime_contractor = 'Ark', "
         "build_model = 'Contractor' "
         "WHERE company = 'Nebius' AND location ILIKE '%UK%';"),
        
        # Iceland
        ("UPDATE ai_datacenters SET prime_contractor = 'Verne', "
         "build_model = 'Contractor' "
         "WHERE company = 'Nebius' AND location ILIKE '%Iceland%';"),
        
        # Finland
        ("UPDATE ai_datacenters SET prime_contractor = 'Caverion', "
         "build_model = 'Contractor' "
         "WHERE company = 'Nebius' AND location ILIKE '%Finland%';"),
    ]
    
    for update_query in nebius_updates:
        cur.execute(update_query)
        if cur.rowcount > 0:
            location = update_query.split("ILIKE '%")[1].split("%'")[0]
            contractor = update_query.split("'")[1]
            print(f"  ✓ Updated Nebius {location}: {contractor}")
    
    conn.commit()
    
    print("\n✅ Migration complete!")
    print("   All Nebius sites now tagged with contractors")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    add_contractor_fields()
