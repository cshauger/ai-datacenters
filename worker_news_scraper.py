import os
import urllib.request
import urllib.error
import urllib.parse
import json
import psycopg2
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

PG_URI = os.environ.get("DATABASE_URL")
if not PG_URI:
    print("No database URL")
    exit(1)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBQ6WuuyYwI-IBdBzl4iO67lbBjwvenmic")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "8259734518"

# Search queries
QUERIES = [
    '"AI data center" AND ("megawatts" OR "lease" OR "announces" OR "capacity")',
    'hyperscaler AND "data center" AND "megawatts"',
    '"Nvidia" AND "data center" AND ("investment" OR "megawatts")'
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
        urllib.request.urlopen(req)
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")

def get_db_connection():
    return psycopg2.connect(PG_URI)

def analyze_article_with_gemini(title, link):
    prompt = f"""
You are an AI data center industry analyst. Review the following news headline and link.
Determine if it represents a NEW data center capacity announcement, a new lease, or a new construction project.
If it is generic news, earnings recap (without new capacity), or rumor, set "is_new_capacity" to false.

Headline: {title}
Link: {link}

Return ONLY a JSON object with the following fields:
- is_new_capacity (boolean)
- company (string, who is building/leasing it)
- partner (string, if a hyperscaler or landlord is mentioned, otherwise null)
- megawatts (number, extract the MW capacity if mentioned, otherwise null)
- investment_billions (number, extract the investment in billions USD if mentioned, otherwise null)
- location (string, city/state/country if mentioned, otherwise null)
- summary (string, 1-2 sentence summary of the deal/build)

Ensure the output is strictly valid JSON.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        resp_data = json.loads(resp.read().decode('utf-8'))
        content = resp_data['candidates'][0]['content']['parts'][0]['text']
        return json.loads(content)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return None

def fetch_google_news(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    articles = []
    try:
        xml_data = urllib.request.urlopen(req).read()
        root = ET.fromstring(xml_data)
        for item in root.findall('./channel/item')[:10]:
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            articles.append({"title": title, "link": link, "pubDate": pub_date})
    except Exception as e:
        print(f"Error fetching RSS for {query}: {e}")
    return articles

def run_news_scraper():
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("Starting News Scraper...")
    
    all_articles = []
    for q in QUERIES:
        all_articles.extend(fetch_google_news(q))
        
    for article in all_articles:
        cur.execute("SELECT id FROM datacenter_news_alerts WHERE url = %s", (article["link"],))
        if cur.fetchone():
            continue
            
        print(f"Analyzing: {article['title']}")
        analysis = analyze_article_with_gemini(article['title'], article['link'])
        
        if analysis and analysis.get("is_new_capacity"):
            print(f"Found new capacity announcement: {analysis['company']} - {analysis['megawatts']}MW")
            
            try:
                pub_date_obj = datetime.now(timezone.utc).date()
                
                cur.execute("""
                    INSERT INTO datacenter_news_alerts (headline, url, published_date, company, megawatts, investment_usd, location, summary)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING RETURNING id;
                """, (
                    article['title'],
                    article['link'],
                    pub_date_obj,
                    analysis.get('company'),
                    analysis.get('megawatts'),
                    analysis.get('investment_billions'),
                    analysis.get('location'),
                    analysis.get('summary')
                ))
                
                inserted = cur.fetchone()
                if inserted:
                    conn.commit()
                    msg = f"🚨 <b>New AI Datacenter Announcement</b>\n\n"
                    msg += f"<b>Company:</b> {analysis.get('company', 'Unknown')}\n"
                    if analysis.get('partner'):
                        msg += f"<b>Partner/Tenant:</b> {analysis['partner']}\n"
                    if analysis.get('megawatts'):
                        msg += f"<b>Capacity:</b> {analysis['megawatts']} MW\n"
                    if analysis.get('investment_billions'):
                        msg += f"<b>Investment:</b> ${analysis['investment_billions']}B\n"
                    if analysis.get('location'):
                        msg += f"<b>Location:</b> {analysis['location']}\n\n"
                    msg += f"{analysis.get('summary', '')}\n\n"
                    msg += f"<a href='{article['link']}'>Read Article</a>"
                    
                    send_telegram_alert(msg)
                    
                    cur.execute("UPDATE datacenter_news_alerts SET notified = TRUE WHERE id = %s", (inserted[0],))
                    conn.commit()
            except Exception as e:
                print(f"Database error saving article: {e}")
                conn.rollback()

    cur.close()
    conn.close()
    print("News Scraper completed.")


import time
import schedule

if __name__ == "__main__":
    print("Starting News Scraper Scheduler...")
    run_news_scraper()
    
    schedule.every(4).hours.do(run_news_scraper)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

