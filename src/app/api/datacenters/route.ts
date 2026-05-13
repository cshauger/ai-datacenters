import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export const revalidate = 0;

export async function GET() {
  try {
    const res = await pool.query('SELECT * FROM ai_datacenters');
    return NextResponse.json(res.rows);
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
