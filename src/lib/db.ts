import { Pool } from 'pg';

let connectionString = process.env.DATABASE_URL || '';

// Fix SSL mode for newer pg versions
if (connectionString.includes('sslmode=require')) {
  connectionString = connectionString.replace('sslmode=require', 'sslmode=no-verify');
}

const pool = new Pool({
  connectionString,
});

export default pool;
