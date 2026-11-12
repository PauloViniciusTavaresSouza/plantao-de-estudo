import { Controller, Get } from '@nestjs/common';
import { FiltrosService } from './filtros.service.js';

@Controller('filtros')
export class FiltrosController {
  constructor(private readonly filtros: FiltrosService) {}

  /** GET /filtros -> órgãos, bancas, anos, categorias, localidades, áreas e temáticas com contagem */
  @Get()
  opcoes() {
    return this.filtros.opcoes();
  }
}
