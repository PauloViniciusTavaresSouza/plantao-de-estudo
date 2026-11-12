/** Aplica as migrações da pasta drizzle/. Uso: pnpm db:migrate */
import { join } from 'node:path';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { criarDb } from './client.js';

try {
  process.loadEnvFile();
} catch {
  // sem .env: usa as variáveis do ambiente
}

const { db, pool } = criarDb();
await migrate(db, {
  migrationsFolder: join(import.meta.dirname, '..', '..', 'drizzle'),
});
await pool.end();
console.log('Migrações aplicadas.');
