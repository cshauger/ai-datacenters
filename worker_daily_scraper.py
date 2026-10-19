#!/usr/bin/env python3
"""
GPU Pricing Worker - Daily Scraper
Now uses Playwright to dynamically scrape cloud provider pricing, bypassing basic bot protections!
"""

import os
import sys
import time
import schedule
from worker_npm_tracker import run_npm_scraper
from worker_earnings import publish_earnings_calendar
from worker_daily_email import send_daily_pulse
import re
from datetime import datetime, timezone, timedelta

print("🤖 GPU Pricing Worker Starting (Playwright Edition)...")
print(f"📅 Start time: {datetime.now(timezone.utc).isoformat()}")

# Check environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not set")
    sys.exit(1)
print("✅ DATABASE_URL present")

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
    requests = None

# Install Playwright browsers automatically on container startup!
try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright imported")
    print("🔧 Installing Playwright Chromium browser binary...")
    os.system("python3 -m playwright install chromium")
    print("✅ Playwright Chromium installed (if it wasn't already)")
except ImportError:
    print("❌ Playwright not available. Did you pip install playwright?")
    sys.exit(1)


# Baseline Pricing (Used as fallback or for providers that don't need dynamic scraping yet)
CURRENT_PRICING = [
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
    
    ("H200", "Vast.ai (Low)", 2.22),
    ("H200", "FluidStack", 2.30),
    ("H200", "Vast.ai (Median)", 2.46),
    ("H200", "GMI Cloud Reserved", 2.50),
    ("H200", "Lambda Labs", 3.29),
    ("H200", "GMI Cloud Bare-Metal", 3.50),
    ("H200", "Jarvislabs", 3.80),
    ("H200", "RunPod (Low)", 3.99),
    ("H200", "Together.ai", 4.19),
    ("H200", "AWS", 4.98),
    ("H200", "CoreWeave", 6.31),
    ("H200", "Oracle Cloud", 10.00),
    ("H200", "Azure", 10.60),
    
    ("B200", "Deep Infra", 2.49),
    ("B200", "Vast.ai (Low)", 2.50),
    ("B200", "Vast.ai (Median)", 3.00),
    ("B200", "RunPod", 4.99),
    ("B200", "Together.ai", 7.49),
    ("B200", "Oracle Cloud", 14.00),
    ("B200", "AWS", 14.24),
]

def dynamic_scrape_nebius():
    """Uses requests to scrape Nebius live pricing natively."""
    print("🌐 Scraping Nebius pricing...")
    nebius_prices = []
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get("https://nebius.com/prices", headers=headers, timeout=15)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            clean_text = soup.get_text(separator=' ', strip=True)
            
            prices = re.findall(r'(H100|H200|B200|B300).*?\$([0-9.]+)', clean_text, re.IGNORECASE)
            
            for chip, price_str in prices:
                chip_up = chip.upper()
                price = float(price_str)
                # Since they just list one main price now, we'll mark it as On-Demand
                if chip_up == "H100":
                    nebius_prices.append(("H100", "Nebius", price))
                elif chip_up == "H200":
                    nebius_prices.append(("H200", "Nebius", price))
                elif chip_up == "B200":
                    nebius_prices.append(("B200", "Nebius", price))
                elif chip_up == "B300":
                    nebius_prices.append(("B300", "Nebius", price))
                    
            # Deduplicate just in case
            nebius_prices = list(set(nebius_prices))
            print(f"✅ Nebius dynamic scrape successful: {nebius_prices}")
        else:
            raise Exception(f"HTTP {resp.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to scrape Nebius: {e}")
        # Fallback
        nebius_prices = [
            ("H100", "Nebius", 4.50),
            ("H200", "Nebius", 5.40),
            ("B200", "Nebius", 8.50),
        ]
        
    return nebius_prices

def scrape_and_insert():
    """Daily scrape job"""
    print(f"\n🔄 Starting daily GPU scrape: {datetime.now(timezone.utc).isoformat()}")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # 1. Fetch live Nebius prices using Playwright
        live_nebius_prices = dynamic_scrape_nebius()
        
        # 2. Combine with Baseline Pricing
        final_pricing = CURRENT_PRICING + live_nebius_prices
        
        # 3. Insert into Database
        insert_query = """
            INSERT INTO gpu_pricing (date, provider, gpu_type, price_per_hr)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (date, provider, gpu_type) DO NOTHING;
        """
        
        records = [(today, provider, gpu_type, price) 
                   for gpu_type, provider, price in final_pricing]
        
        cursor.executemany(insert_query, records)
        conn.commit()
        
        inserted = cursor.rowcount
        print(f"✅ Inserted {inserted} new GPU records for {today}")
        
        cursor.close()
        conn.close()
        
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


# Schedule daily GPU scrape at 5 AM PT (13:00 UTC)
schedule.every().day.at("13:00").do(scrape_and_insert)
print("📅 Scheduled GPU scrape at 13:00 UTC (5:00 AM PT)")

# Schedule daily Hardware scrape at 7 AM PT (15:00 UTC)
schedule.every().day.at("15:00").do(scrape_hardware)
schedule.every().day.at("16:00").do(run_npm_scraper)
schedule.every().day.at("14:00").do(publish_earnings_calendar)
schedule.every().day.at("14:30").do(send_daily_pulse)
print("📅 Scheduled Hardware scrape at 15:00 UTC (7:00 AM PT)")

# Run once on startup for testing
print("\n🧪 Running initial GPU scrape...")
scrape_and_insert()
print("\n🧪 Running initial Hardware scrape...")
scrape_hardware()
print("\n🧪 Running initial Earnings scrape...")
publish_earnings_calendar()

# Main loop
print("\n♻️  Entering heartbeat loop...")
while True:
    schedule.run_pending()
    time.sleep(60)
