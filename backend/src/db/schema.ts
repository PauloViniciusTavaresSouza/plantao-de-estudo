/**
 * Banco do Plantão de Estudo: provas, questões, temáticas e a base de normas que a IA cita.
 * Mudou algo aqui? Rode `pnpm db:generate` para criar a migração e `pnpm db:migrate` para aplicar.
 */
import { relations } from 'drizzle-orm';
import {
  boolean,
  date,
  index,
  integer,
  pgEnum,
  pgTable,
  primaryKey,
  text,
  timestamp,
} from 'drizzle-orm/pg-core';

export const tipoSelecao = pgEnum('tipo_selecao', ['CONCURSO', 'RESIDENCIA']);
export const categoria = pgEnum('categoria', [
  'ENFERMEIRO',
  'TECNICO',
  'AUXILIAR',
  'MULTIPROFISSIONAL',
]);
export const origemQuestao = pgEnum('origem_questao', [
  'PROVA',
  'INEDITA',
  'EXEMPLO',
]);
export const statusRevisao = pgEnum('status_revisao', [
  'RASCUNHO',
  'REVISADA',
  'DESATUALIZADA',
]);

/** Instituição que faz a prova (FGV, Vunesp, Instituto AOCP...). */
export const bancas = pgTable('bancas', {
  id: text().primaryKey(),
  nome: text().notNull().unique(),
});

/** Quem seleciona: um concurso (EBSERH, prefeitura) ou um programa de residência (ENARE, SES-DF). */
export const orgaos = pgTable('orgaos', {
  id: text().primaryKey(),
  nome: text().notNull(),
  tipo: tipoSelecao().notNull(),
  esfera: text(), // Federal, Estadual, Municipal, Militar
  uf: text(), // sigla, ou null quando é nacional
});

/** Área usada no filtro "Especialidade" do app (Terapia Intensiva, Obstetrícia...). */
export const areasEspecialidade = pgTable('areas_especialidade', {
  id: text().primaryKey(),
  nome: text().notNull(),
});

/** Vaga ou especialidade como aparece no edital. */
export const especialidades = pgTable('especialidades', {
  id: text().primaryKey(),
  nome: text().notNull().unique(),
  areaId: text('area_id').references(() => areasEspecialidade.id),
});

export const provas = pgTable(
  'provas',
  {
    id: text().primaryKey(),
    orgaoId: text('orgao_id')
      .notNull()
      .references(() => orgaos.id),
    bancaId: text('banca_id')
      .notNull()
      .references(() => bancas.id),
    ano: integer().notNull(),
    dataProva: date('data_prova'),
    cargo: text().notNull(),
    categoria: categoria().notNull(),
    grupo: text(),
    tipoProva: text('tipo_prova'),
    localidade: text().notNull().default('Nacional'), // "Nacional" ou a sigla da UF
    urlProva: text('url_prova'),
    urlGabarito: text('url_gabarito'),
    gabaritoConferido: text('gabarito_conferido'),
  },
  (t) => [index('provas_orgao_ano_idx').on(t.orgaoId, t.ano)],
);

/** Especialidades de cada prova. Prova sem nenhuma = vale para todas. */
export const provaEspecialidades = pgTable(
  'prova_especialidades',
  {
    provaId: text('prova_id')
      .notNull()
      .references(() => provas.id, { onDelete: 'cascade' }),
    especialidadeId: text('especialidade_id')
      .notNull()
      .references(() => especialidades.id),
  },
  (t) => [primaryKey({ columns: [t.provaId, t.especialidadeId] })],
);

export const tematicas = pgTable('tematicas', {
  id: text().primaryKey(),
  nome: text().notNull(),
  ordem: integer().notNull().default(0),
});

export const assuntos = pgTable('assuntos', {
  id: text().primaryKey(),
  nome: text().notNull(),
  tematicaId: text('tematica_id')
    .notNull()
    .references(() => tematicas.id),
});

export const questoes = pgTable(
  'questoes',
  {
    id: text().primaryKey(),
    origem: origemQuestao().notNull(),
    provaId: text('prova_id').references(() => provas.id),
    numero: integer(),
    disciplina: text(),
    temaBase: text('tema_base').notNull(), // tema amplo antigo da base; as temáticas finas ficam em questao_assuntos
    subtema: text(),
    dificuldade: integer().notNull().default(3),
    textoApoio: text('texto_apoio'),
    enunciado: text().notNull(),
    imagens: text().array().notNull().default([]),
    gabarito: text(), // letra A-E; null quando anulada
    anulada: boolean().notNull().default(false),
    comentario: text(),
    statusRevisao: statusRevisao('status_revisao')
      .notNull()
      .default('RASCUNHO'),
    revisor: text(),
    criadaEm: timestamp('criada_em').notNull().defaultNow(),
    atualizadaEm: timestamp('atualizada_em').notNull().defaultNow(),
  },
  (t) => [index('questoes_prova_idx').on(t.provaId, t.numero)],
);

export const alternativas = pgTable(
  'alternativas',
  {
    questaoId: text('questao_id')
      .notNull()
      .references(() => questoes.id, { onDelete: 'cascade' }),
    letra: text().notNull(),
    texto: text().notNull(),
  },
  (t) => [primaryKey({ columns: [t.questaoId, t.letra] })],
);

export const questaoAssuntos = pgTable(
  'questao_assuntos',
  {
    questaoId: text('questao_id')
      .notNull()
      .references(() => questoes.id, { onDelete: 'cascade' }),
    assuntoId: text('assunto_id')
      .notNull()
      .references(() => assuntos.id),
  },
  (t) => [
    primaryKey({ columns: [t.questaoId, t.assuntoId] }),
    index('questao_assuntos_assunto_idx').on(t.assuntoId),
  ],
);

/** Normas oficiais (leis, portarias, resoluções). Podem entrar inteiras na base da IA. */
export const documentos = pgTable('documentos', {
  id: text().primaryKey(),
  titulo: text().notNull(),
  tipo: text().notNull(),
  numero: text(),
  ano: integer(),
  orgao: text(),
  tema: text(),
  prioridade: text(),
  formato: text(),
  urlOficial: text('url_oficial'),
  observacao: text(),
});

/** Livros e manuais. Livros têm direitos autorais: só citação e resumo próprio. */
export const referencias = pgTable('referencias', {
  id: text().primaryKey(),
  tipo: text().notNull(),
  autores: text().notNull(),
  titulo: text().notNull(),
  editora: text(),
  tema: text(),
  comoUsar: text('como_usar'),
});

export const questaoFontes = pgTable(
  'questao_fontes',
  {
    questaoId: text('questao_id')
      .notNull()
      .references(() => questoes.id, { onDelete: 'cascade' }),
    documentoId: text('documento_id')
      .notNull()
      .references(() => documentos.id),
    dispositivo: text(),
  },
  (t) => [primaryKey({ columns: [t.questaoId, t.documentoId] })],
);

export const questaoReferencias = pgTable(
  'questao_referencias',
  {
    questaoId: text('questao_id')
      .notNull()
      .references(() => questoes.id, { onDelete: 'cascade' }),
    referenciaId: text('referencia_id')
      .notNull()
      .references(() => referencias.id),
    onde: text(),
  },
  (t) => [primaryKey({ columns: [t.questaoId, t.referenciaId] })],
);

/** Trecho de norma ou ficha que a IA busca e cita. O vetor de busca (pgvector) entra na fase da IA. */
export const trechos = pgTable('trechos', {
  id: text().primaryKey(),
  documentoId: text('documento_id')
    .notNull()
    .references(() => documentos.id),
  dispositivo: text(),
  texto: text().notNull(),
  fonte: text(), // "norma" ou "ficha"
});

// Relações, para consultas com `db.query.*.findFirst({ with: ... })`
export const questoesRel = relations(questoes, ({ one, many }) => ({
  prova: one(provas, { fields: [questoes.provaId], references: [provas.id] }),
  alternativas: many(alternativas),
  assuntos: many(questaoAssuntos),
  fontes: many(questaoFontes),
  referencias: many(questaoReferencias),
}));
export const provasRel = relations(provas, ({ one, many }) => ({
  orgao: one(orgaos, { fields: [provas.orgaoId], references: [orgaos.id] }),
  banca: one(bancas, { fields: [provas.bancaId], references: [bancas.id] }),
  especialidades: many(provaEspecialidades),
  questoes: many(questoes),
}));
export const alternativasRel = relations(alternativas, ({ one }) => ({
  questao: one(questoes, {
    fields: [alternativas.questaoId],
    references: [questoes.id],
  }),
}));
export const questaoAssuntosRel = relations(questaoAssuntos, ({ one }) => ({
  questao: one(questoes, {
    fields: [questaoAssuntos.questaoId],
    references: [questoes.id],
  }),
  assunto: one(assuntos, {
    fields: [questaoAssuntos.assuntoId],
    references: [assuntos.id],
  }),
}));
export const assuntosRel = relations(assuntos, ({ one }) => ({
  tematica: one(tematicas, {
    fields: [assuntos.tematicaId],
    references: [tematicas.id],
  }),
}));
export const questaoFontesRel = relations(questaoFontes, ({ one }) => ({
  questao: one(questoes, {
    fields: [questaoFontes.questaoId],
    references: [questoes.id],
  }),
  documento: one(documentos, {
    fields: [questaoFontes.documentoId],
    references: [documentos.id],
  }),
}));
export const questaoReferenciasRel = relations(
  questaoReferencias,
  ({ one }) => ({
    questao: one(questoes, {
      fields: [questaoReferencias.questaoId],
      references: [questoes.id],
    }),
    referencia: one(referencias, {
      fields: [questaoReferencias.referenciaId],
      references: [referencias.id],
    }),
  }),
);
export const provaEspecialidadesRel = relations(
  provaEspecialidades,
  ({ one }) => ({
    prova: one(provas, {
      fields: [provaEspecialidades.provaId],
      references: [provas.id],
    }),
    especialidade: one(especialidades, {
      fields: [provaEspecialidades.especialidadeId],
      references: [especialidades.id],
    }),
  }),
);
export const especialidadesRel = relations(especialidades, ({ one }) => ({
  area: one(areasEspecialidade, {
    fields: [especialidades.areaId],
    references: [areasEspecialidade.id],
  }),
}));
