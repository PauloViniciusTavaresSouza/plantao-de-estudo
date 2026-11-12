import { Injectable } from '@nestjs/common';
import { asc, eq, sql } from 'drizzle-orm';
import type { Db } from '../db/client.js';
import { InjectDb } from '../db/database.module.js';
import {
  areasEspecialidade,
  assuntos,
  bancas,
  orgaos,
  provas,
  questaoAssuntos,
  questoes,
  tematicas,
} from '../db/schema.js';

const n = sql<number>`count(distinct ${questoes.id})::int`;

/** Opções de cada filtro, com o número de questões válidas (não anuladas) em cada uma. */
@Injectable()
export class FiltrosService {
  constructor(@InjectDb() private readonly db: Db) {}

  async opcoes() {
    const validas = eq(questoes.anulada, false);
    const [total, orgs, bcs, anos, cats, ufs, areas, tems, asss] =
      await Promise.all([
        this.db
          .select({ total: sql<number>`count(*)::int` })
          .from(questoes)
          .where(validas),
        this.db
          .select({
            id: orgaos.id,
            nome: orgaos.nome,
            tipo: orgaos.tipo,
            esfera: orgaos.esfera,
            uf: orgaos.uf,
            questoes: n,
          })
          .from(orgaos)
          .leftJoin(provas, eq(provas.orgaoId, orgaos.id))
          .leftJoin(
            questoes,
            sql`${questoes.provaId} = ${provas.id} and ${validas}`,
          )
          .groupBy(orgaos.id)
          .orderBy(asc(orgaos.nome)),
        this.db
          .select({ id: bancas.id, nome: bancas.nome, questoes: n })
          .from(bancas)
          .leftJoin(provas, eq(provas.bancaId, bancas.id))
          .leftJoin(
            questoes,
            sql`${questoes.provaId} = ${provas.id} and ${validas}`,
          )
          .groupBy(bancas.id)
          .orderBy(asc(bancas.nome)),
        this.db
          .select({ ano: provas.ano, questoes: n })
          .from(provas)
          .innerJoin(
            questoes,
            sql`${questoes.provaId} = ${provas.id} and ${validas}`,
          )
          .groupBy(provas.ano)
          .orderBy(sql`${provas.ano} desc`),
        this.db
          .select({ id: provas.categoria, questoes: n })
          .from(provas)
          .innerJoin(
            questoes,
            sql`${questoes.provaId} = ${provas.id} and ${validas}`,
          )
          .groupBy(provas.categoria),
        this.db
          .select({ id: provas.localidade, questoes: n })
          .from(provas)
          .innerJoin(
            questoes,
            sql`${questoes.provaId} = ${provas.id} and ${validas}`,
          )
          .groupBy(provas.localidade),
        this.db
          .select()
          .from(areasEspecialidade)
          .orderBy(asc(areasEspecialidade.nome)),
        this.db.select().from(tematicas).orderBy(asc(tematicas.ordem)),
        this.db
          .select({
            id: assuntos.id,
            nome: assuntos.nome,
            tematicaId: assuntos.tematicaId,
            questoes: n,
          })
          .from(assuntos)
          .leftJoin(questaoAssuntos, eq(questaoAssuntos.assuntoId, assuntos.id))
          .leftJoin(
            questoes,
            sql`${questoes.id} = ${questaoAssuntos.questaoId} and ${validas}`,
          )
          .groupBy(assuntos.id)
          .orderBy(asc(assuntos.id)),
      ]);
    const NOMES_CATEGORIA = {
      ENFERMEIRO: 'Enfermeiro',
      TECNICO: 'Técnico',
      AUXILIAR: 'Auxiliar',
      MULTIPROFISSIONAL: 'Multiprofissional',
    };
    return {
      total: total[0].total,
      orgaos: orgs,
      bancas: bcs,
      anos,
      categorias: cats.map((c) => ({ ...c, nome: NOMES_CATEGORIA[c.id] })),
      localidades: ufs,
      areas,
      tematicas: tems.map((t) => {
        const filhos = asss
          .filter((a) => a.tematicaId === t.id)
          .map(({ tematicaId: _t, ...a }) => a);
        return { id: t.id, nome: t.nome, assuntos: filhos };
      }),
    };
  }
}
