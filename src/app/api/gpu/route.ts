import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export const revalidate = 0;

export async function GET() {
  try {
    const res = await pool.query('SELECT * FROM gpu_pricing ORDER BY date DESC, gpu_type, price_per_hr ASC LIMIT 2000');
    return NextResponse.json(res.rows);
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
