import os
import urllib.request
import json
import psycopg2
from datetime import datetime

PG_URI = os.environ.get("DATABASE_URL")
if not PG_URI:
    print("No database URL")
    exit(1)

# Configure Telegram credentials
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "8259734518"

COMPANIES = [
    {"name": "POET Technologies", "cik": "0001437424", "forms": ["6-K", "20-F", "F-1", "8-K", "10-Q", "10-K"]}
]

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Telegram credentials, skipping alert.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    headers = {"Content-Type": "application/json"}
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    try:
        res = urllib.request.urlopen(req)
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")

def get_db_connection():
    return psycopg2.connect(PG_URI)

def check_sec_filings():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sec_alerts (
            id SERIAL PRIMARY KEY,
            company VARCHAR(100),
            filing_type VARCHAR(50),
            accession_number VARCHAR(100) UNIQUE,
            doc_link VARCHAR(255),
            date_filed DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    headers = {"User-Agent": "Shog99Bot/1.0 (cshauger@gmail.com)"}
    
    for comp in COMPANIES:
        url = f"https://data.sec.gov/submissions/CIK{comp['cik']}.json"
        req = urllib.request.Request(url, headers=headers)
        
        try:
            res = urllib.request.urlopen(req)
            data = json.loads(res.read().decode('utf-8'))
            filings = data['filings']['recent']
            
            # Check the 5 most recent filings
            for i in range(min(5, len(filings['form']))):
                form = filings['form'][i]
                
                # Check if it's a form we care about
                if form in comp['forms'] or any(f in form for f in comp['forms']):
                    date = filings['filingDate'][i]
                    acc_num = filings['accessionNumber'][i]
                    doc = filings['primaryDocument'][i]
                    acc_no_dash = acc_num.replace('-', '')
                    link = f"https://www.sec.gov/Archives/edgar/data/{int(comp['cik'])}/{acc_no_dash}/{doc}"
                    
                    # Check if we already alerted
                    cur.execute("SELECT id FROM sec_alerts WHERE accession_number = %s", (acc_num,))
                    if not cur.fetchone():
                        # Log it
                        cur.execute("""
                            INSERT INTO sec_alerts (company, filing_type, accession_number, doc_link, date_filed)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (comp['name'], form, acc_num, link, date))
                        conn.commit()
                        
                        # Send alert
                        msg = f"🚨 <b>New SEC Filing Alert</b>\n\n<b>Company:</b> {comp['name']}\n<b>Filing:</b> {form}\n<b>Date:</b> {date}\n\n<a href='{link}'>View Document</a>"
                        send_telegram_alert(msg)
                        print(f"New alert generated for {comp['name']} - {form}")
                    
        except Exception as e:
            print(f"Error checking {comp['name']}: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_sec_filings()
