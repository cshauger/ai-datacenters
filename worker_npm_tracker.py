import os
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta

def run_npm_scraper():
    print("📊 Starting daily NPM registry data scrape...")
    
    # Target NPM packages for publicly traded TMT companies
    packages = [
        ("MDB", "MongoDB", "mongodb"),
        ("MDB", "MongoDB", "mongoose"),
        ("SNOW", "Snowflake", "snowflake-sdk"),
        ("ESTC", "Elastic", "@elastic/elasticsearch"),
        ("BASE", "Couchbase", "couchbase"),
        ("DDOG", "Datadog", "dd-trace"),
        ("DDOG", "Datadog", "@datadog/browser-logs"),
        ("DT", "Dynatrace", "@dynatrace/openkit-js"),
        ("OKTA", "Okta", "@okta/okta-react"),
        ("OKTA", "Okta", "@okta/okta-auth-js"),
        ("TWLO", "Twilio", "twilio"),
        ("TWLO", "Twilio", "@twilio/conversations"),
        ("BRZE", "Braze", "@braze/web-sdk"),
        ("AMPL", "Amplitude", "amplitude-js"),
        ("AMPL", "Amplitude", "@amplitude/analytics-browser"),
        ("KVYO", "Klaviyo", "klaviyo-api"),
        ("NET", "Cloudflare", "wrangler"),
        ("FSLY", "Fastly", "@fastly/compute-js"),
        ("HCP", "HashiCorp", "cdktf"),
        ("SHOP", "Shopify", "@shopify/shopify-api"),
        ("SHOP", "Shopify", "@shopify/hydrogen"),
        ("SQ", "Block (Square)", "@square/web-sdk"),
        ("PYPL", "PayPal", "@paypal/react-paypal-js"),
        ("PYPL", "PayPal", "braintree-web"),
        ("APP", "AppLovin", "react-native-applovin-max")
    ]
    
    # NPM API is T+1. Fetch yesterday's completed download counts.
    yesterday_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    records = []
    
    for ticker, company, pkg in packages:
        try:
            url = f"https://api.npmjs.org/downloads/point/{yesterday_date}/{pkg}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                downloads = data.get("downloads", 0)
                records.append((ticker, company, pkg, yesterday_date, downloads))
                print(f"   [+] {pkg}: {downloads:,} downloads")
            else:
                print(f"   [-] Failed to fetch {pkg}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"   [!] Error fetching {pkg}: {e}")

    if not records:
        print("❌ No NPM data retrieved.")
        return

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ ERROR: DATABASE_URL not set in environment.")
        return

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # 1. Ensure Table Exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npm_data_tracker (
                id SERIAL PRIMARY KEY,
                company_ticker VARCHAR(10),
                company_name VARCHAR(100),
                package_name VARCHAR(100),
                download_date DATE,
                daily_downloads INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(package_name, download_date)
            )
        """)
        
        # 2. Insert or update the records
        insert_query = """
            INSERT INTO npm_data_tracker (company_ticker, company_name, package_name, download_date, daily_downloads)
            VALUES %s
            ON CONFLICT (package_name, download_date) 
            DO UPDATE SET daily_downloads = EXCLUDED.daily_downloads
        """
        execute_values(cursor, insert_query, records)
        conn.commit()
        
        cursor.close()
        conn.close()
        print(f"✅ Successfully inserted {len(records)} NPM records for {yesterday_date} into the database.")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    # If run directly (e.g. manual trigger), run once.
    run_npm_scraper()
