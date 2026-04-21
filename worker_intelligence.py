import os
import time
import requests
import psycopg2
from duckduckgo_search import DDGS

# Environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

if not DATABASE_URL:
    print("DATABASE_URL not set. Exiting.")
    exit(1)

# Ensure postgresql:// prefix
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    # Create the intelligence table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS datacenter_intelligence (
            datacenter_id VARCHAR(50) PRIMARY KEY,
            latitude NUMERIC,
            longitude NUMERIC,
            satellite_image_url TEXT,
            recent_news TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_datacenters():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, company, name, location FROM ai_datacenters")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def geocode_location(location):
    if not GOOGLE_MAPS_API_KEY or not location:
        return None, None
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(location)}&key={GOOGLE_MAPS_API_KEY}"
        resp = requests.get(url).json()
        if resp.get("status") == "OK" and len(resp.get("results", [])) > 0:
            loc = resp["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    except Exception as e:
        print(f"Geocoding error for {location}: {e}")
    return None, None

def get_satellite_image_url(lat, lng):
    if not GOOGLE_MAPS_API_KEY or lat is None or lng is None:
        return None
    return f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom=15&size=600x400&maptype=satellite&key={GOOGLE_MAPS_API_KEY}"

def fetch_news(company, name, location):
    query = f'"{company}" "{name}" {location} datacenter OR data center OR permit OR construction'
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            news_items = []
            for r in results:
                news_items.append(f"- [{r.get('title')}]({r.get('href')})")
            return "\n".join(news_items)
    except Exception as e:
        print(f"News fetch error for {name}: {e}")
        return None

def update_intelligence(dc_id, lat, lng, image_url, news):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO datacenter_intelligence (datacenter_id, latitude, longitude, satellite_image_url, recent_news, last_updated)
        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (datacenter_id) DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            satellite_image_url = EXCLUDED.satellite_image_url,
            recent_news = EXCLUDED.recent_news,
            last_updated = CURRENT_TIMESTAMP;
    """, (dc_id, lat, lng, image_url, news))
    conn.commit()
    cur.close()
    conn.close()

def main():
    print("Starting Intelligence Worker...")
    init_db()
    
    while True:
        print("Fetching datacenters...")
        datacenters = get_datacenters()
        for dc in datacenters:
            dc_id, company, name, location = dc
            print(f"Processing: {company} - {name} ({location})")
            
            lat, lng = geocode_location(location)
            image_url = get_satellite_image_url(lat, lng)
            news = fetch_news(company, name, location)
            
            update_intelligence(dc_id, lat, lng, image_url, news)
            time.sleep(2) # rate limit
            
        print("Completed a run. Sleeping for 12 hours...")
        time.sleep(12 * 3600)

if __name__ == "__main__":
    main()
