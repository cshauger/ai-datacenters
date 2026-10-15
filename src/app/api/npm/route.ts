import { NextResponse } from 'next/server';
import { Pool } from 'pg';

export async function GET() {
  let client = null;
  try {
    if (!process.env.DATABASE_URL) {
      throw new Error("DATABASE_URL is not defined in environment.");
    }
    
    const pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: {
        rejectUnauthorized: false
      }
    });

    client = await pool.connect();
    
    // Get rolling 7-day average of daily downloads for the last 30 days
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
    
    // Format data for Recharts
    const chartDataMap = new Map();
    
    rows.forEach(row => {
      // Safely parse the date
      let dateObj;
      if (row.download_date instanceof Date) {
          dateObj = row.download_date;
      } else {
          dateObj = new Date(row.download_date);
      }
      
      const dateStr = dateObj.toISOString().split('T')[0];
      
      if (!chartDataMap.has(dateStr)) {
        chartDataMap.set(dateStr, { date: dateStr });
      }
      
      const dayData = chartDataMap.get(dateStr);
      dayData[row.company_ticker] = Math.round(row.rolling_avg);
    });
    
    const formattedData = Array.from(chartDataMap.values());
    
    return NextResponse.json({ success: true, data: formattedData });
  } catch (error) {
    console.error('Database Error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json({ success: false, error: errorMessage }, { status: 500 });
  } finally {
      if (client) client.release();
  }
}
