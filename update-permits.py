#!/usr/bin/env python3
"""
Manage datacenter permit information
Usage:
  python update-permits.py list [--pending]
  python update-permits.py update <datacenter_id> --status <status> [--date YYYY-MM-DD] [--notes "..."] [--url "..."]
  python update-permits.py search <company_name>
"""

import os
import sys
import psycopg2
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')

VALID_STATUSES = ['Approved', 'Pending', 'Denied', 'Applied', 'In Review', 'Appealed', 'Unknown']

def list_datacenters(pending_only=False):
    """List all datacenters with permit status"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    query = """
        SELECT 
            id,
            company,
            location,
            mw_capacity,
            status,
            permit_status,
            permit_date,
            permit_notes
        FROM ai_datacenters
    """
    
    if pending_only:
        query += " WHERE permit_status IN ('Pending', 'Applied', 'In Review')"
    
    query += " ORDER BY company, location;"
    
    cur.execute(query)
    rows = cur.fetchall()
    
    if not rows:
        print("No datacenters found.")
        return
    
    print(f"\n{'ID':<5} {'Company':<20} {'Location':<25} {'MW':<8} {'DC Status':<15} {'Permit Status':<15} {'Permit Date':<12}")
    print("-" * 120)
    
    for row in rows:
        dc_id, company, location, mw, status, p_status, p_date, p_notes = row
        mw_str = f"{mw:.0f}" if mw else "N/A"
        p_status_str = p_status or "N/A"
        p_date_str = p_date.strftime('%Y-%m-%d') if p_date else "N/A"
        
        print(f"{dc_id:<5} {company[:19]:<20} {location[:24]:<25} {mw_str:<8} {status[:14]:<15} {p_status_str[:14]:<15} {p_date_str:<12}")
    
    print(f"\nTotal: {len(rows)} datacenters")
    
    cur.close()
    conn.close()

def update_permit(datacenter_id, status=None, date=None, notes=None, url=None):
    """Update permit information for a datacenter"""
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
    
    if status:
        if status not in VALID_STATUSES:
            print(f"❌ Error: Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
            return
        updates.append("permit_status = %s")
        params.append(status)
    
    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
            updates.append("permit_date = %s")
            params.append(date)
        except ValueError:
            print(f"❌ Error: Invalid date format. Use YYYY-MM-DD")
            return
    
    if notes:
        updates.append("permit_notes = %s")
        params.append(notes)
    
    if url:
        updates.append("permit_url = %s")
        params.append(url)
    
    if not updates:
        print("❌ Error: No updates specified.")
        return
    
    query = f"UPDATE ai_datacenters SET {', '.join(updates)} WHERE id = %s"
    params.append(datacenter_id)
    
    cur.execute(query, params)
    conn.commit()
    
    print(f"✅ Updated permit info for {company} - {location}")
    if status:
        print(f"   Status: {status}")
    if date:
        print(f"   Date: {date}")
    if notes:
        print(f"   Notes: {notes[:60]}...")
    if url:
        print(f"   URL: {url}")
    
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
            permit_status
        FROM ai_datacenters
        WHERE company ILIKE %s
        ORDER BY location;
    """, (f'%{company_name}%',))
    
    rows = cur.fetchall()
    
    if not rows:
        print(f"No datacenters found matching '{company_name}'")
        return
    
    print(f"\n{'ID':<5} {'Company':<20} {'Location':<30} {'MW':<8} {'DC Status':<15} {'Permit':<15}")
    print("-" * 100)
    
    for row in rows:
        dc_id, company, location, mw, status, p_status = row
        mw_str = f"{mw:.0f}" if mw else "N/A"
        p_status_str = p_status or "N/A"
        print(f"{dc_id:<5} {company[:19]:<20} {location[:29]:<30} {mw_str:<8} {status[:14]:<15} {p_status_str[:14]:<15}")
    
    print(f"\nFound {len(rows)} datacenters")
    
    cur.close()
    conn.close()

def print_usage():
    print("""
Usage:
  python update-permits.py list [--pending]
  python update-permits.py update <id> --status <status> [--date YYYY-MM-DD] [--notes "..."] [--url "..."]
  python update-permits.py search <company_name>

Valid statuses: Approved, Pending, Denied, Applied, In Review, Appealed, Unknown

Examples:
  python update-permits.py list
  python update-permits.py list --pending
  python update-permits.py update 15 --status "Pending" --date "2026-03-15" --notes "Submitted to NJ DEP"
  python update-permits.py search "CoreWeave"
""")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        pending_only = '--pending' in sys.argv
        list_datacenters(pending_only)
    
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
        status = None
        date = None
        notes = None
        url = None
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--status' and i + 1 < len(sys.argv):
                status = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--date' and i + 1 < len(sys.argv):
                date = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--notes' and i + 1 < len(sys.argv):
                notes = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--url' and i + 1 < len(sys.argv):
                url = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        update_permit(dc_id, status, date, notes, url)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print_usage()
            sys.exit(1)
        search_company(sys.argv[2])
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)
