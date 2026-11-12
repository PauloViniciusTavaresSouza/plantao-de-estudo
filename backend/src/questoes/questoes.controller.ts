import {
  Body,
  Controller,
  Get,
  HttpCode,
  Param,
  Post,
  Query,
} from '@nestjs/common';
import {
  listarQuestoesSchema,
  responderSchema,
  type ListarQuestoes,
  type Responder,
} from './questoes.schema.js';
import { QuestoesService } from './questoes.service.js';

@Controller('questoes')
export class QuestoesController {
  constructor(private readonly questoes: QuestoesService) {}

  /** GET /questoes?tipo=RESIDENCIA&orgao=enare&tematica=vig&assunto=vig-sanit&uf=DF&pagina=1&limite=10 */
  @Get()
  listar(@Query({ schema: listarQuestoesSchema }) filtros: ListarQuestoes) {
    return this.questoes.listar(filtros);
  }

  @Get(':id')
  buscar(@Param('id') id: string) {
    return this.questoes.buscar(id);
  }

  /** POST /questoes/:id/resposta { "letra": "B" } -> diz se acertou, o gabarito e onde estudar */
  @Post(':id/resposta')
  @HttpCode(200)
  responder(
    @Param('id') id: string,
    @Body({ schema: responderSchema }) corpo: Responder,
  ) {
    return this.questoes.responder(id, corpo.letra);
  }
}
