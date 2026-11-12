import {
  Global,
  Inject,
  Module,
  type OnApplicationShutdown,
} from '@nestjs/common';
import type { Pool } from 'pg';
import { criarDb } from './client.js';

export const DB = Symbol('DB');
const POOL = Symbol('POOL');

/** Use `@InjectDb() private readonly db: Db` nos serviços. */
export const InjectDb = () => Inject(DB);

const conexao = { valor: undefined as ReturnType<typeof criarDb> | undefined };
const obter = () => (conexao.valor ??= criarDb());

@Global()
@Module({
  providers: [
    { provide: POOL, useFactory: () => obter().pool },
    { provide: DB, useFactory: () => obter().db },
  ],
  exports: [DB],
})
export class DatabaseModule implements OnApplicationShutdown {
  constructor(@Inject(POOL) private readonly pool: Pool) {}

  async onApplicationShutdown() {
    await this.pool.end();
  }
}
