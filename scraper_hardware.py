import os
import requests
import re
import psycopg2
from datetime import datetime

PG_URI = os.environ.get("DATABASE_URL")
if not PG_URI:
    print("No DATABASE_URL found in environment.")
    exit(1)

def get_db_connection():
    return psycopg2.connect(PG_URI)

def scrape_dramexchange():
    results = []
    try:
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
                        price_float = float(price)
                        results.append({
                            "category": "DRAM",
                            "mfg": "Market Spot",
                            "name": item,
                            "cap": "Varies",
                            "price": price_float,
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
                        price_float = float(price)
                        results.append({
                            "category": "NAND Flash / SSD",
                            "mfg": "Market Spot",
                            "name": item,
                            "cap": "Varies",
                            "price": price_float,
                            "notes": "DRAMeXchange Daily Spot Average"
                        })
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Error scraping DRAMeXchange: {e}")
    
    return results

def get_cpu_prices():
    return [
        {"category": "CPU", "mfg": "AMD", "name": "EPYC 9654 Genoa", "cap": "96-Core 2.4 GHz", "price": 11805.00, "notes": "Baseline B2B Disti Price"},
        {"category": "CPU", "mfg": "AMD", "name": "EPYC 9754 Bergamo", "cap": "128-Core 2.25 GHz", "price": 11900.00, "notes": "Baseline B2B Disti Price"},
        {"category": "CPU", "mfg": "Intel", "name": "Xeon Platinum 8490H", "cap": "60-Core 1.9 GHz", "price": 17000.00, "notes": "Baseline B2B Disti Price"}
    ]

def main():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
    except Exception as e:
        print(f"Database connection failed: {e}")
        exit(1)
        
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
    print(f"Inserted {count} new price records.")

if __name__ == "__main__":
    main()
