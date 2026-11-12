import { Module } from '@nestjs/common';
import { FiltrosController } from './filtros.controller.js';
import { FiltrosService } from './filtros.service.js';
import { QuestoesController } from './questoes.controller.js';
import { QuestoesService } from './questoes.service.js';

@Module({
  controllers: [QuestoesController, FiltrosController],
  providers: [QuestoesService, FiltrosService],
})
export class QuestoesModule {}
