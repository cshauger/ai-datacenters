import { NextResponse } from 'next/server';
import { Pool } from 'pg';

export async function GET() {
  let client = null;
  try {
    let dbUrl = process.env.DATABASE_URL;
    if (!dbUrl) {
      console.error("DATABASE_URL is totally missing");
      return NextResponse.json({ success: false, error: "Database not configured" }, { status: 500 });
    }
    
    // Fix SSL mode for newer pg versions
    if (dbUrl.includes('sslmode=require')) {
      dbUrl = dbUrl.replace('sslmode=require', 'sslmode=no-verify');
    }
    
    const pool = new Pool({
      connectionString: dbUrl,
    });

    client = await pool.connect();
    
    const query = `
      WITH DailyTotals AS (
        SELECT 
          download_date, 
          company_ticker, 
          company_name,
          SUM(daily_downloads) as total_downloads
        FROM npm_data_tracker
        WHERE daily_downloads > 0
        GROUP BY download_date, company_ticker, company_name
      )
      SELECT 
        download_date,
        company_ticker,
        company_name,
        total_downloads,
        AVG(total_downloads) OVER (
          PARTITION BY company_ticker 
          ORDER BY download_date 
          ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as rolling_avg
      FROM DailyTotals
      ORDER BY download_date ASC, company_ticker ASC;
    `;
    
    const { rows } = await client.query(query);
    
    const chartDataMap = new Map();
    
    rows.forEach(row => {
      const dateObj = new Date(row.download_date);
      const dateStr = dateObj.toISOString().split('T')[0];
      
      if (!chartDataMap.has(dateStr)) {
        chartDataMap.set(dateStr, { date: dateStr });
      }
      
      const dayData = chartDataMap.get(dateStr);
      dayData[row.company_ticker] = Math.round(row.rolling_avg);
    });
    
    const formattedData = Array.from(chartDataMap.values());
    
    return NextResponse.json({ success: true, data: formattedData });
  } catch (error: any) {
    console.error('API Error:', error.message || error);
    return NextResponse.json({ success: false, error: error.message || 'Unknown error' }, { status: 500 });
  } finally {
      if (client) client.release();
  }
}
