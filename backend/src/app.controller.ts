import { Controller, Get } from '@nestjs/common';

@Controller()
export class AppController {
  /** GET /saude -> usado para conferir se a API está no ar */
  @Get('saude')
  saude() {
    return { ok: true, servico: 'plantao-de-estudo-api' };
  }
}
