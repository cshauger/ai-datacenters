import yfinance as yf
from datetime import datetime, timezone
import pytz
import psycopg2
import os

def publish_earnings_calendar():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set.")
        return
        
    tickers = ["OUST", "MDB", "PANW", "FTNT", "CRWD", "ZS", "MSFT", "GOOGL", "AMZN", "ORCL", "WULF", "APP", "POET"]
    now = datetime.now(pytz.utc)
    results = []

    print(f"[{now.isoformat()}] Fetching earnings dates...")
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            ed = t.get_earnings_dates(limit=10)
            if ed is not None and not ed.empty:
                future_dates = [d for d in ed.index if d > now]
                if future_dates:
                    next_date = sorted(future_dates)[0]
                    results.append((ticker, next_date))
        except Exception as e:
            print(f"Error for {ticker}: {e}")

    results.sort(key=lambda x: x[1])

    html = f'''
    <div class="border-b border-gray-200 pb-4 mb-4">
        <h2 class="text-2xl font-bold text-gray-900 mb-2">📅 Upcoming Coverage Earnings Calendar</h2>
        <p class="text-sm text-gray-500">Automated Market Intelligence - {now.strftime('%B %d, %Y')}</p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    '''
    for ticker, date in results:
        date_str = date.strftime('%b %d, %Y')
        html += f'''
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
            <span class="font-bold text-blue-600">{ticker}</span>
            <span class="text-gray-700 font-medium">{date_str}</span>
        </div>
        '''
    html += '</div>'
    html += '<div class="mt-6 text-sm text-gray-400 italic">This data is automatically sourced from Yahoo Finance API daily.</div>'

    print("Inserting into Postgres...")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        today = datetime.now(timezone.utc).date()
        
        cur.execute("""
            INSERT INTO daily_reports (report_date, html_content, markdown_content, summary)
            VALUES (%s, %s, %s, 'Earnings Calendar')
            ON CONFLICT (report_date) DO UPDATE 
            SET html_content = EXCLUDED.html_content, markdown_content = EXCLUDED.markdown_content;
        """, (today, html, "",))
        
        conn.commit()
        cur.close()
        conn.close()
        print("Success publishing earnings!")
    except Exception as e:
        print("DB Error:", e)

if __name__ == "__main__":
    publish_earnings_calendar()
