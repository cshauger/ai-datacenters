import asyncio
import os
import psycopg2
from playwright.async_api import async_playwright

DB_URI = os.environ.get("DATABASE_URL")

async def scan_domain(domain, browser):
    applovin_found = False
    url = f"http://{domain}" if not domain.startswith('http') else domain
    
    context = await browser.new_context()
    page = await context.new_page()
    
    def handle_request(request):
        nonlocal applovin_found
        if 'applovin' in request.url.lower() or 'axon' in request.url.lower():
            applovin_found = True
            
    page.on('request', handle_request)
    
    try:
        # Load page and wait for dynamic network requests to finish
        await page.goto(url, wait_until="networkidle", timeout=15000)
    except Exception:
        pass
        
    await context.close()
    return applovin_found

async def scan_loop():
    print("Starting Playwright-based AppLovin pixel scanner...")
    
    while True:
        try:
            if not DB_URI:
                print("DATABASE_URL not set!")
                await asyncio.sleep(60)
                continue
                
            conn = psycopg2.connect(DB_URI)
            cur = conn.cursor()
            
            # Find domains that haven't been scanned recently
            cur.execute("""
                SELECT id, domain 
                FROM ecommerce_sites 
                WHERE domain NOT IN (SELECT domain FROM applovin_scan_history WHERE scan_date > CURRENT_TIMESTAMP - INTERVAL '7 days')
                ORDER BY RANDOM() LIMIT 50;
            """)
            sites = cur.fetchall()
            
            if not sites:
                print("No un-scanned sites found. Sleeping for 1 hour...")
                cur.close()
                conn.close()
                await asyncio.sleep(3600)
                continue
                
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
                for site_id, domain in sites:
                    found = await scan_domain(domain, browser)
                    status = 'Found' if found else 'Not Found'
                    
                    cur.execute(
                        "INSERT INTO applovin_scan_history (scan_date, domain, status) VALUES (CURRENT_TIMESTAMP, %s, %s)",
                        (domain, status)
                    )
                    conn.commit()
                await browser.close()
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print("Database or Playwright error during loop:", e)
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(scan_loop())
