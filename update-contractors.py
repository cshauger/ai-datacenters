#!/usr/bin/env python3
"""
Manage datacenter contractor information
Usage:
  python update-contractors.py list [--contractor <name>] [--build-model <model>]
  python update-contractors.py update <datacenter_id> --contractor <name> [--cooling <supplier>] [--notes "..."] [--model <build_model>]
  python update-contractors.py search <company_name>
  python update-contractors.py stats
"""

import os
import sys
import psycopg2
from collections import defaultdict

DATABASE_URL = os.environ.get('DATABASE_URL')

VALID_BUILD_MODELS = ['In-house', 'Contractor', 'Design-Build', 'Hybrid', 'Unknown']

def list_datacenters(contractor_filter=None, build_model_filter=None):
    """List all datacenters with contractor info"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    query = """
        SELECT 
            id,
            company,
            location,
            mw_capacity,
            status,
            prime_contractor,
            build_model,
            cooling_supplier
        FROM ai_datacenters
        WHERE 1=1
    """
    
    params = []
    if contractor_filter:
        query += " AND prime_contractor ILIKE %s"
        params.append(f'%{contractor_filter}%')
    
    if build_model_filter:
        query += " AND build_model = %s"
        params.append(build_model_filter)
    
    query += " ORDER BY company, location;"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    
    if not rows:
        print("No datacenters found.")
        return
    
    print(f"\n{'ID':<5} {'Company':<20} {'Location':<25} {'MW':<8} {'Status':<15} {'Contractor':<20} {'Model':<15}")
    print("-" * 125)
    
    for row in rows:
        dc_id, company, location, mw, status, contractor, build_model, cooling = row
        mw_str = f"{mw:.0f}" if mw else "N/A"
        contractor_str = contractor[:19] if contractor else "N/A"
        build_model_str = build_model[:14] if build_model else "N/A"
        
        print(f"{dc_id:<5} {company[:19]:<20} {location[:24]:<25} {mw_str:<8} {status[:14]:<15} {contractor_str:<20} {build_model_str:<15}")
    
    print(f"\nTotal: {len(rows)} datacenters")
    
    cur.close()
    conn.close()

def update_contractor(datacenter_id, contractor=None, cooling=None, notes=None, build_model=None):
    """Update contractor information for a datacenter"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Verify datacenter exists
    cur.execute("SELECT company, location FROM ai_datacenters WHERE id = %s", (datacenter_id,))
    result = cur.fetchone()
    
    if not result:
        print(f"❌ Error: Datacenter ID {datacenter_id} not found.")
        return
    
    company, location = result
    
    # Build update query
    updates = []
    params = []
    
    if contractor:
        updates.append("prime_contractor = %s")
        params.append(contractor)
    
    if cooling:
        updates.append("cooling_supplier = %s")
        params.append(cooling)
    
    if notes:
        updates.append("contractor_track_record = %s")
        params.append(notes)
    
    if build_model:
        if build_model not in VALID_BUILD_MODELS:
            print(f"❌ Error: Invalid build model. Must be one of: {', '.join(VALID_BUILD_MODELS)}")
            return
        updates.append("build_model = %s")
        params.append(build_model)
    
    if not updates:
        print("❌ Error: No updates specified.")
        return
    
    query = f"UPDATE ai_datacenters SET {', '.join(updates)} WHERE id = %s"
    params.append(datacenter_id)
    
    cur.execute(query, params)
    conn.commit()
    
    print(f"✅ Updated contractor info for {company} - {location}")
    if contractor:
        print(f"   Contractor: {contractor}")
    if cooling:
        print(f"   Cooling: {cooling}")
    if build_model:
        print(f"   Build Model: {build_model}")
    if notes:
        print(f"   Notes: {notes[:60]}...")
    
    cur.close()
    conn.close()

def search_company(company_name):
    """Search for datacenters by company name"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id,
            company,
            location,
            mw_capacity,
            status,
            prime_contractor,
            build_model
        FROM ai_datacenters
        WHERE company ILIKE %s
        ORDER BY location;
    """, (f'%{company_name}%',))
    
    rows = cur.fetchall()
    
    if not rows:
        print(f"No datacenters found matching '{company_name}'")
        return
    
    print(f"\n{'ID':<5} {'Company':<20} {'Location':<30} {'MW':<8} {'Status':<15} {'Contractor':<20} {'Model':<12}")
    print("-" * 120)
    
    for row in rows:
        dc_id, company, location, mw, status, contractor, build_model = row
        mw_str = f"{mw:.0f}" if mw else "N/A"
        contractor_str = contractor[:19] if contractor else "N/A"
        build_model_str = build_model[:11] if build_model else "N/A"
        print(f"{dc_id:<5} {company[:19]:<20} {location[:29]:<30} {mw_str:<8} {status[:14]:<15} {contractor_str:<20} {build_model_str:<12}")
    
    print(f"\nFound {len(rows)} datacenters")
    
    cur.close()
    conn.close()

def show_stats():
    """Show statistics on contractors and build models"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Stats by contractor
    cur.execute("""
        SELECT 
            prime_contractor,
            COUNT(*) as site_count,
            SUM(CASE WHEN mw_capacity IS NOT NULL THEN mw_capacity ELSE 0 END) as total_mw
        FROM ai_datacenters
        WHERE prime_contractor IS NOT NULL
        GROUP BY prime_contractor
        ORDER BY site_count DESC;
    """)
    
    contractor_stats = cur.fetchall()
    
    print("\n📊 Contractor Statistics:")
    print(f"\n{'Contractor':<30} {'Sites':<10} {'Total MW':<12}")
    print("-" * 55)
    
    for contractor, count, mw in contractor_stats:
        mw_str = f"{mw:.0f}" if mw else "N/A"
        print(f"{contractor[:29]:<30} {count:<10} {mw_str:<12}")
    
    # Stats by build model
    cur.execute("""
        SELECT 
            build_model,
            COUNT(*) as site_count,
            SUM(CASE WHEN mw_capacity IS NOT NULL THEN mw_capacity ELSE 0 END) as total_mw
        FROM ai_datacenters
        WHERE build_model IS NOT NULL
        GROUP BY build_model
        ORDER BY site_count DESC;
    """)
    
    model_stats = cur.fetchall()
    
    print(f"\n\n📊 Build Model Statistics:")
    print(f"\n{'Build Model':<20} {'Sites':<10} {'Total MW':<12}")
    print("-" * 45)
    
    for model, count, mw in model_stats:
        mw_str = f"{mw:.0f}" if mw else "N/A"
        print(f"{model[:19]:<20} {count:<10} {mw_str:<12}")
    
    # Company breakdown
    cur.execute("""
        SELECT 
            company,
            COUNT(*) as site_count,
            COUNT(DISTINCT prime_contractor) as contractor_count,
            build_model
        FROM ai_datacenters
        WHERE prime_contractor IS NOT NULL
        GROUP BY company, build_model
        ORDER BY company, build_model;
    """)
    
    company_stats = cur.fetchall()
    
    print(f"\n\n📊 Company Build Strategies:")
    print(f"\n{'Company':<20} {'Sites':<10} {'Contractors':<15} {'Build Model':<15}")
    print("-" * 65)
    
    for company, count, contractor_count, model in company_stats:
        model_str = model if model else "N/A"
        print(f"{company[:19]:<20} {count:<10} {contractor_count:<15} {model_str[:14]:<15}")
    
    cur.close()
    conn.close()

def print_usage():
    print("""
Usage:
  python update-contractors.py list [--contractor <name>] [--build-model <model>]
  python update-contractors.py update <id> --contractor <name> [--cooling <supplier>] [--notes "..."] [--model <build_model>]
  python update-contractors.py search <company_name>
  python update-contractors.py stats

Valid build models: In-house, Contractor, Design-Build, Hybrid, Unknown

Examples:
  python update-contractors.py list
  python update-contractors.py list --contractor "Data One"
  python update-contractors.py list --build-model "Contractor"
  python update-contractors.py update 15 --contractor "Data One USA" --model "Contractor" --notes "No US datacenter experience"
  python update-contractors.py search "Nebius"
  python update-contractors.py stats
""")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        contractor = None
        build_model = None
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--contractor' and i + 1 < len(sys.argv):
                contractor = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--build-model' and i + 1 < len(sys.argv):
                build_model = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        list_datacenters(contractor, build_model)
    
    elif command == 'update':
        if len(sys.argv) < 4:
            print_usage()
            sys.exit(1)
        
        try:
            dc_id = int(sys.argv[2])
        except ValueError:
            print("❌ Error: Datacenter ID must be a number")
            sys.exit(1)
        
        # Parse arguments
        contractor = None
        cooling = None
        notes = None
        build_model = None
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--contractor' and i + 1 < len(sys.argv):
                contractor = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--cooling' and i + 1 < len(sys.argv):
                cooling = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--notes' and i + 1 < len(sys.argv):
                notes = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--model' and i + 1 < len(sys.argv):
                build_model = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        update_contractor(dc_id, contractor, cooling, notes, build_model)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print_usage()
            sys.exit(1)
        search_company(sys.argv[2])
    
    elif command == 'stats':
        show_stats()
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)
