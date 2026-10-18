import os
import psycopg2
from datetime import datetime, timezone
import resend

resend.api_key = os.environ.get("RESEND_API_KEY", "")

PG_URI = os.environ.get("DATABASE_URL")

def get_latest_data():
    if not PG_URI: return {}
    data = {}
    try:
        conn = psycopg2.connect(PG_URI)
        cur = conn.cursor()
        
        # Get latest GPU prices
        cur.execute("SELECT gpu_type, provider, price_per_hr FROM gpu_pricing WHERE date = (SELECT max(date) FROM gpu_pricing) ORDER BY gpu_type, price_per_hr LIMIT 5;")
        data['gpu'] = cur.fetchall()
        
        # Get latest NPM spikes
        cur.execute("""
            SELECT company_ticker, company_name, daily_downloads 
            FROM npm_data_tracker 
            WHERE download_date = (SELECT max(download_date) FROM npm_data_tracker)
            ORDER BY daily_downloads DESC LIMIT 3;
        """)
        data['npm'] = cur.fetchall()
        
        # Get latest DC news
        cur.execute("SELECT headline, company, megawatts FROM datacenter_news_alerts ORDER BY published_date DESC LIMIT 2;")
        data['news'] = cur.fetchall()
        
        cur.close()
        conn.close()
    except Exception as e:
        print("DB Error getting data for email:", e)
        
    return data

def build_email_html(data):
    # This is a dynamic version of the template Curtis provided
    date_str = datetime.now(timezone.utc).strftime('%B %d, %Y')
    
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 650px; margin: 0 auto; color: #1a1a1a; line-height: 1.6;">
      
      <!-- Header -->
      <div style="border-bottom: 3px solid #111827; padding-bottom: 16px; margin-bottom: 24px;">
        <h1 style="margin: 0; font-size: 28px; color: #111827; letter-spacing: -0.5px;">CAS Research</h1>
        <p style="margin: 4px 0 0 0; color: #4B5563; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Daily Infrastructure & Equity Pulse</p>
        <p style="margin: 4px 0 0 0; color: #9CA3AF; font-size: 13px;">{date_str}</p>
      </div>

      <!-- Section 1: Inputs -->
      <div style="margin-bottom: 32px;">
        <h2 style="margin: 0 0 8px 0; font-size: 16px; color: #111827; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #E5E7EB; padding-bottom: 4px;">1. Commodities & Silicon Inputs</h2>
        <ul style="margin: 12px 0 0 0; padding-left: 20px; color: #374151; font-size: 15px;">
    """
    
    for gpu in data.get('gpu', []):
        html += f'<li style="margin-bottom: 8px;"><strong>GPU Spot Rates:</strong> {gpu[0]} holding at ${gpu[2]}/hr via {gpu[1]}.</li>'
        
    html += """
          <li style="margin-bottom: 8px;"><strong>BTC Price:</strong> Tracking macro trends. Hashrate stable.</li>
          <li style="margin-bottom: 8px;"><strong>Hardware:</strong> Base disti pricing intact.</li>
        </ul>
      </div>

      <!-- Section 2: Proprietary Tracking -->
      <div style="margin-bottom: 32px;">
        <h2 style="margin: 0 0 8px 0; font-size: 16px; color: #111827; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #E5E7EB; padding-bottom: 4px;">2. Proprietary Data Signals</h2>
        <ul style="margin: 12px 0 0 0; padding-left: 20px; color: #374151; font-size: 15px;">
    """
    
    npm_text = ", ".join([f"{n[0]} ({n[2]} downloads)" for n in data.get('npm', [])])
    html += f'<li style="margin-bottom: 8px;"><strong>NPM Adoption:</strong> Top daily movers: {npm_text}.</li>'
    
    html += """
          <li style="margin-bottom: 8px;"><strong>AppLovin Pixel:</strong> E-commerce rollout accelerating. Stable tracking pixel growth.</li>
    """
    
    for news in data.get('news', []):
        mw_str = f" ({news[2]} MW)" if news[2] else ""
        html += f'<li style="margin-bottom: 8px;"><strong>DC Tracker:</strong> {news[1]}{mw_str} - {news[0]}</li>'
        
    html += """
        </ul>
      </div>

      <!-- Section 3: Equity Research -->
      <div style="margin-bottom: 32px;">
        <h2 style="margin: 0 0 8px 0; font-size: 16px; color: #111827; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #E5E7EB; padding-bottom: 4px;">3. Equity Research Summary</h2>
        <p style="margin: 12px 0 0 0; color: #374151; font-size: 15px;">
          <strong>Earnings Radar:</strong> Upcoming catalysts loading. View the full earnings tracker on the dashboard for exact dates on our coverage basket (PANW, CRWD, MDB, OUST, etc).
        </p>
        <p style="margin: 12px 0 0 0; font-size: 15px;">
          <a href="https://casres.com" style="color: #2563EB; text-decoration: none; font-weight: 600;">Read full analysis on CASRES.com &rarr;</a>
        </p>
      </div>

      <!-- Footer -->
      <div style="border-top: 1px solid #E5E7EB; padding-top: 16px; font-size: 12px; color: #9CA3AF; text-align: center;">
        CONFIDENTIAL: Internal use only. Do not forward.<br>
        CAS Research &copy; 2026 Jetha Global
      </div>
    </div>
    """
    return html

def send_daily_pulse():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Preparing CAS Research Daily Pulse...")
    if not resend.api_key:
        print("Missing RESEND_API_KEY. Skipping email send.")
        return
        
    data = get_latest_data()
    html_content = build_email_html(data)
    
    try:
        r = resend.Emails.send({
            "from": "CAS Research <pulse@casres.com>",
            "to": "cshauger@gmail.com",
            "subject": f"CAS Research | Daily Infrastructure & Equity Pulse ({datetime.now().strftime('%m/%d')})",
            "html": html_content
        })
        print(f"Email sent successfully! ID: {r.get('id')}")
    except Exception as e:
        print(f"Error sending email via Resend: {e}")

if __name__ == "__main__":
    send_daily_pulse()
