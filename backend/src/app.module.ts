import { Module } from '@nestjs/common';
import { AppController } from './app.controller.js';
import { DatabaseModule } from './db/database.module.js';
import { QuestoesModule } from './questoes/questoes.module.js';

@Module({
  imports: [DatabaseModule, QuestoesModule],
  controllers: [AppController],
})
export class AppModule {}
