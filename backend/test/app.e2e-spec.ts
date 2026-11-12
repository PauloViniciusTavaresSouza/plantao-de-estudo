import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import request from 'supertest';
import { App } from 'supertest/types.js';

// A rota /saude não consulta o banco; a URL só precisa existir para o módulo subir.
process.env.DATABASE_URL ??=
  'postgresql://plantao:plantao@localhost:5432/plantao';
const { AppModule } = await import('./../src/app.module.js');

describe('API (e2e)', () => {
  let app: INestApplication<App>;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();
    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('GET /saude', () => {
    return request(app.getHttpServer())
      .get('/saude')
      .expect(200)
      .expect({ ok: true, servico: 'plantao-de-estudo-api' });
  });

  afterEach(async () => {
    await app.close();
  });
});
