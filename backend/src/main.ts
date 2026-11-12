import { join } from 'node:path';
import { StandardSchemaValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import type { NestExpressApplication } from '@nestjs/platform-express';
import { AppModule } from './app.module.js';

try {
  process.loadEnvFile();
} catch {
  // sem .env: usa as variáveis do ambiente
}

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);
  app.useGlobalPipes(new StandardSchemaValidationPipe());
  app.enableCors({
    origin: (process.env.FRONTEND_URL ?? 'http://localhost:3000').split(','),
  });
  app.enableShutdownHooks();
  // Figuras das questões: GET /imagens/arquivo.png
  const baseIa =
    process.env.BASE_IA_DIR ?? join(import.meta.dirname, '..', '..', 'base-ia');
  app.useStaticAssets(join(baseIa, 'imagens'), { prefix: '/imagens/' });
  await app.listen(process.env.PORT ?? 3001);
}
await bootstrap();
