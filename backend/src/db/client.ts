import { drizzle, type NodePgDatabase } from 'drizzle-orm/node-postgres';
import pg from 'pg';
import * as schema from './schema.js';

export type Db = NodePgDatabase<typeof schema>;

/** Abre a conexão com o Postgres a partir de DATABASE_URL. */
export function criarDb(url = process.env.DATABASE_URL) {
  if (!url)
    throw new Error(
      'DATABASE_URL não definida. Copie backend/.env.example para backend/.env.',
    );
  const pool = new pg.Pool({ connectionString: url });
  return { db: drizzle(pool, { schema }), pool };
}
