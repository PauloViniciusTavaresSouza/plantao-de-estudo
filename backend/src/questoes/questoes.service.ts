import { Injectable, NotFoundException } from '@nestjs/common';
import { and, asc, eq, inArray, sql, type SQL } from 'drizzle-orm';
import type { Db } from '../db/client.js';
import { InjectDb } from '../db/database.module.js';
import {
  alternativas,
  assuntos,
  bancas,
  documentos,
  especialidades,
  orgaos,
  provaEspecialidades,
  provas,
  questaoAssuntos,
  questaoFontes,
  questaoReferencias,
  questoes,
  referencias,
  tematicas,
} from '../db/schema.js';
import type { ListarQuestoes } from './questoes.schema.js';

@Injectable()
export class QuestoesService {
  constructor(@InjectDb() private readonly db: Db) {}

  /** Monta o WHERE a partir dos filtros. Usado pela listagem e pela contagem de filtros. */
  async condicoes(f: Partial<ListarQuestoes>): Promise<SQL | undefined> {
    const c: (SQL | undefined)[] = [eq(questoes.anulada, false)];
    if (f.origem) c.push(eq(questoes.origem, f.origem));
    if (f.tipo) c.push(eq(orgaos.tipo, f.tipo));
    if (f.orgao) c.push(eq(provas.orgaoId, f.orgao));
    if (f.banca) c.push(eq(provas.bancaId, f.banca));
    if (f.ano) c.push(eq(provas.ano, f.ano));
    if (f.categoria) c.push(eq(provas.categoria, f.categoria));
    if (f.uf) {
      c.push(
        f.uf === 'Nacional'
          ? eq(provas.localidade, 'Nacional')
          : sql`${provas.localidade} in (${f.uf}, 'Nacional')`,
      );
    }
    if (f.area) {
      // Prova sem especialidades vale para todas; senão, precisa ter uma especialidade da área.
      c.push(sql`${questoes.provaId} is not null and (
        not exists (select 1 from ${provaEspecialidades} pe where pe.prova_id = ${questoes.provaId})
        or exists (select 1 from ${provaEspecialidades} pe join ${especialidades} e on e.id = pe.especialidade_id
                   where pe.prova_id = ${questoes.provaId} and e.area_id = ${f.area}))`);
    }
    const tems = f.tematica ?? [];
    const asss = f.assunto ?? [];
    if (tems.length || asss.length) {
      // Dentro de uma temática com assuntos marcados, vale só o assunto; nas outras, a temática inteira.
      const doAssunto = asss.length
        ? await this.db
            .select({ id: assuntos.id, tematicaId: assuntos.tematicaId })
            .from(assuntos)
            .where(inArray(assuntos.id, asss))
        : [];
      const refinadas = new Set(doAssunto.map((a) => a.tematicaId));
      const inteiras = tems.filter((t) => !refinadas.has(t));
      const partes: SQL[] = [];
      if (inteiras.length)
        partes.push(
          sql`a.tematica_id in (${sql.join(
            inteiras.map((t) => sql`${t}`),
            sql`, `,
          )})`,
        );
      if (doAssunto.length)
        partes.push(
          sql`a.id in (${sql.join(
            doAssunto.map((a) => sql`${a.id}`),
            sql`, `,
          )})`,
        );
      c.push(
        partes.length
          ? sql`exists (select 1 from ${questaoAssuntos} qa join ${assuntos} a on a.id = qa.assunto_id
                        where qa.questao_id = ${questoes.id} and (${sql.join(partes, sql` or `)}))`
          : sql`false`,
      );
    }
    return and(...c);
  }

  async listar(f: ListarQuestoes) {
    const where = await this.condicoes(f);
    const base = () =>
      this.db
        .select({ id: questoes.id })
        .from(questoes)
        .leftJoin(provas, eq(provas.id, questoes.provaId))
        .leftJoin(orgaos, eq(orgaos.id, provas.orgaoId));

    const [{ total }] = await this.db
      .select({ total: sql<number>`count(*)::int` })
      .from(questoes)
      .leftJoin(provas, eq(provas.id, questoes.provaId))
      .leftJoin(orgaos, eq(orgaos.id, provas.orgaoId))
      .where(where);

    const ordem =
      f.ordem === 'aleatoria'
        ? [sql`md5(${questoes.id} || ${f.semente})`]
        : [asc(questoes.provaId), asc(questoes.numero), asc(questoes.id)];
    const ids = await base()
      .where(where)
      .orderBy(...ordem)
      .limit(f.limite)
      .offset((f.pagina - 1) * f.limite);
    const itens = await this.detalhar(ids.map((x) => x.id));
    return {
      total,
      pagina: f.pagina,
      limite: f.limite,
      paginas: Math.ceil(total / f.limite),
      itens,
    };
  }

  async buscar(id: string) {
    const [q] = await this.detalhar([id]);
    if (!q) throw new NotFoundException('Questão não encontrada.');
    return q;
  }

  /** Confere a resposta e devolve o gabarito, o comentário e onde estudar. */
  async responder(id: string, letra: string) {
    const [q] = await this.db
      .select({
        gabarito: questoes.gabarito,
        anulada: questoes.anulada,
        comentario: questoes.comentario,
      })
      .from(questoes)
      .where(eq(questoes.id, id));
    if (!q || q.anulada || !q.gabarito)
      throw new NotFoundException('Questão não encontrada.');
    const fontes = await this.db
      .select({
        id: documentos.id,
        titulo: documentos.titulo,
        url: documentos.urlOficial,
        dispositivo: questaoFontes.dispositivo,
      })
      .from(questaoFontes)
      .innerJoin(documentos, eq(documentos.id, questaoFontes.documentoId))
      .where(eq(questaoFontes.questaoId, id));
    const refs = await this.db
      .select({
        id: referencias.id,
        autores: referencias.autores,
        titulo: referencias.titulo,
        onde: questaoReferencias.onde,
      })
      .from(questaoReferencias)
      .innerJoin(
        referencias,
        eq(referencias.id, questaoReferencias.referenciaId),
      )
      .where(eq(questaoReferencias.questaoId, id));
    return {
      correta: letra === q.gabarito,
      gabarito: q.gabarito,
      comentario: q.comentario,
      fontes,
      referencias: refs,
    };
  }

  /** Questões prontas para a tela, na ordem dos ids recebidos. Nunca inclui o gabarito. */
  private async detalhar(ids: string[]) {
    if (!ids.length) return [];
    const linhas = await this.db
      .select({
        id: questoes.id,
        origem: questoes.origem,
        numero: questoes.numero,
        disciplina: questoes.disciplina,
        subtema: questoes.subtema,
        textoApoio: questoes.textoApoio,
        enunciado: questoes.enunciado,
        imagens: questoes.imagens,
        provaId: provas.id,
        ano: provas.ano,
        cargo: provas.cargo,
        categoria: provas.categoria,
        localidade: provas.localidade,
        orgaoId: orgaos.id,
        orgao: orgaos.nome,
        tipo: orgaos.tipo,
        banca: bancas.nome,
      })
      .from(questoes)
      .leftJoin(provas, eq(provas.id, questoes.provaId))
      .leftJoin(orgaos, eq(orgaos.id, provas.orgaoId))
      .leftJoin(bancas, eq(bancas.id, provas.bancaId))
      .where(inArray(questoes.id, ids));
    const alts = await this.db
      .select()
      .from(alternativas)
      .where(inArray(alternativas.questaoId, ids))
      .orderBy(asc(alternativas.letra));
    const ass = await this.db
      .select({
        questaoId: questaoAssuntos.questaoId,
        id: assuntos.id,
        nome: assuntos.nome,
        tematicaId: tematicas.id,
        tematica: tematicas.nome,
      })
      .from(questaoAssuntos)
      .innerJoin(assuntos, eq(assuntos.id, questaoAssuntos.assuntoId))
      .innerJoin(tematicas, eq(tematicas.id, assuntos.tematicaId))
      .where(inArray(questaoAssuntos.questaoId, ids));

    const porId = new Map(linhas.map((l) => [l.id, l]));
    return ids.flatMap((id) => {
      const l = porId.get(id);
      if (!l) return [];
      const {
        provaId,
        ano,
        cargo,
        categoria,
        localidade,
        orgaoId,
        orgao,
        tipo,
        banca,
        ...q
      } = l;
      return [
        {
          ...q,
          prova: provaId
            ? {
                id: provaId,
                orgaoId,
                orgao,
                tipo,
                banca,
                ano,
                cargo,
                categoria,
                localidade,
              }
            : null,
          alternativas: alts
            .filter((a) => a.questaoId === id)
            .map(({ letra, texto }) => ({ letra, texto })),
          assuntos: ass
            .filter((a) => a.questaoId === id)
            .map(({ questaoId: _q, ...a }) => a),
        },
      ];
    });
  }
}
