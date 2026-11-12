import { defineConfig } from 'drizzle-kit';

try {
  process.loadEnvFile();
} catch {
  // sem .env: usa as variáveis do ambiente
}

export default defineConfig({
  dialect: 'postgresql',
  schema: './src/db/schema.ts',
  out: './drizzle',
  dbCredentials: { url: process.env.DATABASE_URL! },
});
