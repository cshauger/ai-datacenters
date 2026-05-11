#!/usr/bin/env python3
"""
GPU Pricing Worker - Daily Scraper
Matches current database schema (gpu_type, price_per_hr)
And now also includes Hardware Pricing Scraper
"""

import os
import sys
import time
import schedule
import re
from datetime import datetime, timezone, timedelta

print("🤖 GPU Pricing Worker Starting...")
print(f"📅 Start time: {datetime.now(timezone.utc).isoformat()}")

# Check environment
DATABASE_URL = os.getenv("DATABASE_URL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "cshauger@gmail.com")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not set")
    sys.exit(1)
print("✅ DATABASE_URL present")

if not SENDGRID_API_KEY:
    print("⚠️  WARNING: SENDGRID_API_KEY not set - email reports disabled")
else:
    print("✅ SENDGRID_API_KEY present")

# Import dependencies
try:
    import psycopg2
    print("✅ psycopg2 imported")
except ImportError:
    print("❌ psycopg2 not available")
    sys.exit(1)

try:
    import requests
    print("✅ requests imported")
except ImportError:
    print("⚠️  WARNING: requests not available")
    requests = None

# Current GPU pricing (manually curated)
CURRENT_PRICING = [
    # H100
    ("H100", "Thunder Compute", 1.38),
    ("H100", "Vast.ai (Low)", 1.50),
    ("H100", "Tensordock Spot", 1.91),
    ("H100", "RunPod PCIe", 1.99),
    ("H100", "Vast.ai (Median)", 2.00),
    ("H100", "GMI Cloud", 2.10),
    ("H100", "Tensordock On-Demand", 2.25),
    ("H100", "FluidStack", 2.50),
    ("H100", "Jarvislabs", 2.69),
    ("H100", "RunPod SXM", 2.69),
    ("H100", "Lambda Labs On-Demand", 2.86),
    ("H100", "Together.ai", 3.49),
    ("H100", "CoreWeave PCIe", 4.76),
    ("H100", "CoreWeave HGX", 6.16),
    ("H100", "Oracle Cloud", 10.00),
    # H200
    ("H200", "Vast.ai (Low)", 2.22),
    ("H200", "FluidStack", 2.30),
    ("H200", "Nebius Commitment", 2.30),
    ("H200", "Vast.ai (Median)", 2.46),
    ("H200", "GMI Cloud Reserved", 2.50),
    ("H200", "Lambda Labs", 3.29),
    ("H200", "Nebius On-Demand", 3.50),
    ("H200", "GMI Cloud Bare-Metal", 3.50),
    ("H200", "Jarvislabs", 3.80),
    ("H200", "RunPod (Low)", 3.99),
    ("H200", "Together.ai", 4.19),
    ("H200", "AWS", 4.98),
    ("H200", "CoreWeave", 6.31),
    ("H200", "Oracle Cloud", 10.00),
    ("H200", "Azure", 10.60),
    # B200
    ("B200", "Deep Infra", 2.49),
    ("B200", "Vast.ai (Low)", 2.50),
    ("B200", "Vast.ai (Median)", 3.00),
    ("B200", "RunPod", 4.99),
    ("B200", "Nebius", 5.50),
    ("B200", "Together.ai", 7.49),
    ("B200", "Oracle Cloud", 14.00),
    ("B200", "AWS", 14.24),
]

def generate_and_send_analysis():
    """Generate daily analysis, save to database, and email it"""
    print(f"\n📊 Generating daily GPU pricing analysis...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Get today's data
        cursor.execute("""
            SELECT gpu_type, provider, price_per_hr
            FROM gpu_pricing
            WHERE date = %s
            ORDER BY gpu_type, price_per_hr ASC;
        """, (today,))
        today_data = cursor.fetchall()
        
        # Get yesterday's data for comparison
        cursor.execute("""
            SELECT gpu_type, provider, price_per_hr
            FROM gpu_pricing
            WHERE date = %s;
        """, (yesterday,))
        yesterday_data = {(row[0], row[1]): row[2] for row in cursor.fetchall()}
        
        if not today_data:
            print("⏭️  No data for today, skipping analysis")
            cursor.close()
            conn.close()
            return
        
        # Group by GPU type
        by_gpu = {}
        for gpu_type, provider, price in today_data:
            if gpu_type not in by_gpu:
                by_gpu[gpu_type] = []
            by_gpu[gpu_type].append((provider, price))
        
        # Generate HTML email
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #2196F3; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .leaders {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .leader {{ font-size: 18px; margin: 10px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #2196F3; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .rank {{ width: 50px; text-align: center; font-weight: bold; color: #666; }}
        .price {{ font-weight: bold; color: #2196F3; }}
        .change-down {{ color: #4CAF50; font-size: 12px; }}
        .change-up {{ color: #f44336; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 GPU Pricing Daily Summary</h1>
        <p><strong>Date:</strong> {today}</p>
        <div class="leaders">
            <h2>🏆 Market Leaders</h2>
"""
        
        # Add leaders
        for gpu in ['H100', 'H200', 'B200']:
            if gpu in by_gpu and by_gpu[gpu]:
                leader = by_gpu[gpu][0]
                html += f'            <div class="leader"><strong>{gpu}:</strong> {leader[0]} @ ${leader[1]:.2f}/hr</div>\n'
        
        html += "        </div>\n"
        
        # Add pricing tables
        for gpu in ['H100', 'H200', 'B200']:
            if gpu not in by_gpu:
                continue
            
            providers = by_gpu[gpu]
            html += f"\n        <h2>{gpu} Pricing ({len(providers)} providers)</h2>\n"
            html += "        <table>\n"
            html += "            <tr><th class='rank'>#</th><th>Provider</th><th>Price/Hour</th></tr>\n"
            
            for rank, (provider, price) in enumerate(providers, 1):
                change_html = ""
                yesterday_price = yesterday_data.get((gpu, provider))
                if yesterday_price is not None:
                    if price < yesterday_price:
                        change_html = f" <span class='change-down'>⬇️ -${yesterday_price - price:.2f}</span>"
                    elif price > yesterday_price:
                        change_html = f" <span class='change-up'>⬆️ +${price - yesterday_price:.2f}</span>"
                
                html += f"            <tr><td class='rank'>{rank}</td><td>{provider}</td><td class='price'>${price:.2f}/hr{change_html}</td></tr>\n"
            
            html += "        </table>\n"
        
        html += f"""
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 14px;">
            <p>Dashboard: <a href="https://gpu-pricing-tracker-vaxov.ondigitalocean.app">https://gpu-pricing-tracker-vaxov.ondigitalocean.app</a></p>
            <p>Automated daily report from GPU Pricing Tracker</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Generate summary for blog index
        summary_lines = []
        summary_lines.append(f"Market Leaders:")
        for gpu in ['H100', 'H200', 'B200']:
            if gpu in by_gpu and by_gpu[gpu]:
                leader = by_gpu[gpu][0]
                summary_lines.append(f"{gpu}: {leader[0]} @ ${leader[1]:.2f}/hr")
        summary = " | ".join(summary_lines)
        
        # Save report to database
        cursor.execute("""
            INSERT INTO daily_reports (report_date, html_content, summary)
            VALUES (%s, %s, %s)
            ON CONFLICT (report_date) DO UPDATE
            SET html_content = EXCLUDED.html_content,
                summary = EXCLUDED.summary;
        """, (today, html, summary))
        conn.commit()
        print(f"✅ Report saved to database")
        
        # Send email
        if requests and SENDGRID_API_KEY:
            response = requests.post(
                'https://api.sendgrid.com/v3/mail/send',
                headers={
                    'Authorization': f'Bearer {SENDGRID_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'personalizations': [{
                        'to': [{'email': RECIPIENT_EMAIL}],
                        'subject': f'GPU Pricing Daily Summary - {today}'
                    }],
                    'from': {'email': 'gpu-tracker@atlascloud.ai', 'name': 'GPU Pricing Tracker'},
                    'content': [{
                        'type': 'text/html',
                        'value': html
                    }]
                },
                timeout=10
            )
            
            if response.status_code == 202:
                print(f"✅ Daily analysis emailed to {RECIPIENT_EMAIL}")
            else:
                print(f"⚠️  Email failed: {response.status_code}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

def scrape_and_insert():
    """Daily scrape job"""
    print(f"\n🔄 Starting daily GPU scrape: {datetime.now(timezone.utc).isoformat()}")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Insert today's prices
        insert_query = """
            INSERT INTO gpu_pricing (date, provider, gpu_type, price_per_hr)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (date, provider, gpu_type) DO NOTHING;
        """
        
        records = [(today, provider, gpu_type, price) 
                   for gpu_type, provider, price in CURRENT_PRICING]
        
        cursor.executemany(insert_query, records)
        conn.commit()
        
        inserted = cursor.rowcount
        print(f"✅ Inserted {inserted} new GPU records for {today}")
        
        cursor.close()
        conn.close()
        
        # Generate and send analysis after successful scrape
        generate_and_send_analysis()
        
    except Exception as e:
        print(f"❌ GPU Scrape failed: {e}")

# ==========================================
# HARDWARE SCRAPER (DRAM, NAND, CPU)
# ==========================================
def scrape_dramexchange():
    results = []
    try:
        if not requests: return []
        res = requests.get("https://www.dramexchange.com/", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        # DRAM
        dram_block = re.search(r'id="tb_NationalDramSpotPrice"(.*?)</table>', res.text, re.IGNORECASE | re.DOTALL)
        if dram_block:
            rows = re.findall(r'<tr.*?>(.*?)</tr>', dram_block.group(1), re.IGNORECASE | re.DOTALL)
            for row in rows[1:]:
                cols = re.findall(r'<td.*?>(.*?)</td>', row, re.IGNORECASE | re.DOTALL)
                if len(cols) >= 3:
                    item = re.sub(r'<[^>]+>', '', cols[0]).strip()
                    price = re.sub(r'<[^>]+>', '', cols[2]).strip()
                    try:
                        results.append({
                            "category": "DRAM",
                            "mfg": "Market Spot",
                            "name": item,
                            "cap": "Varies",
                            "price": float(price),
                            "notes": "DRAMeXchange Daily Spot Average"
                        })
                    except ValueError:
                        pass

        # NAND Flash
        nand_block = re.search(r'id="tb_NationalFlashSpotPrice"(.*?)</table>', res.text, re.IGNORECASE | re.DOTALL)
        if nand_block:
            rows = re.findall(r'<tr.*?>(.*?)</tr>', nand_block.group(1), re.IGNORECASE | re.DOTALL)
            for row in rows[1:]:
                cols = re.findall(r'<td.*?>(.*?)</td>', row, re.IGNORECASE | re.DOTALL)
                if len(cols) >= 3:
                    item = re.sub(r'<[^>]+>', '', cols[0]).strip()
                    price = re.sub(r'<[^>]+>', '', cols[2]).strip()
                    try:
                        results.append({
                            "category": "NAND Flash / SSD",
                            "mfg": "Market Spot",
                            "name": item,
                            "cap": "Varies",
                            "price": float(price),
                            "notes": "DRAMeXchange Daily Spot Average"
                        })
                    except ValueError:
                        pass
    except Exception as e:
        print(f"❌ Error scraping DRAMeXchange: {e}")
    
    return results

def get_cpu_prices():
    return [
        {"category": "CPU", "mfg": "AMD", "name": "EPYC 9654 Genoa", "cap": "96-Core 2.4 GHz", "price": 11805.00, "notes": "Baseline B2B Disti Price"},
        {"category": "CPU", "mfg": "AMD", "name": "EPYC 9754 Bergamo", "cap": "128-Core 2.25 GHz", "price": 11900.00, "notes": "Baseline B2B Disti Price"},
        {"category": "CPU", "mfg": "Intel", "name": "Xeon Platinum 8490H", "cap": "60-Core 1.9 GHz", "price": 17000.00, "notes": "Baseline B2B Disti Price"}
    ]

def scrape_hardware():
    print(f"\n🔄 Starting daily Hardware scrape: {datetime.now(timezone.utc).isoformat()}")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        items = scrape_dramexchange() + get_cpu_prices()
        
        insert_q = """
            INSERT INTO datacenter_hardware 
            (component_category, manufacturer, product_name, capacity_or_speed, price_usd, date_recorded, notes)
            VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, %s);
        """
        
        count = 0
        for item in items:
            cur.execute("""
                SELECT id FROM datacenter_hardware 
                WHERE product_name = %s AND date_recorded = CURRENT_DATE
            """, (item['name'],))
            
            if not cur.fetchone():
                cur.execute(insert_q, (
                    item['category'], item['mfg'], item['name'], item['cap'], item['price'], item['notes']
                ))
                count += 1
                
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Inserted {count} new Hardware price records")
    except Exception as e:
        print(f"❌ Hardware Scrape failed: {e}")


# Connect and verify on startup
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ Database connected: {version[:60]}...")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Database check failed: {e}")
    sys.exit(1)

# Schedule daily GPU scrape at 5 AM PT (13:00 UTC)
schedule.every().day.at("13:00").do(scrape_and_insert)
print("📅 Scheduled GPU scrape at 13:00 UTC (5:00 AM PT)")

# Schedule daily Hardware scrape at 7 AM PT (15:00 UTC)
schedule.every().day.at("15:00").do(scrape_hardware)
print("📅 Scheduled Hardware scrape at 15:00 UTC (7:00 AM PT)")

# Run once on startup for testing
print("\n🧪 Running initial GPU scrape...")
scrape_and_insert()
print("\n🧪 Running initial Hardware scrape...")
scrape_hardware()

# Main loop
print("\n♻️  Entering heartbeat loop...")
while True:
    schedule.run_pending()
    time.sleep(60)
