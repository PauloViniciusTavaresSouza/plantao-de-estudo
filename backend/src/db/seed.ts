/**
 * Importa a pasta base-ia para o Postgres: normas, livros, temáticas, provas e questões.
 * Pode rodar quantas vezes quiser: tudo é atualizado pelo id.
 *
 *   pnpm seed
 */
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { parse } from 'csv-parse/sync';
import { eq, sql } from 'drizzle-orm';
import { criarDb } from './client.js';
import * as s from './schema.js';

try {
  process.loadEnvFile();
} catch {
  // sem .env: usa as variáveis do ambiente
}

const BASE =
  process.env.BASE_IA_DIR ??
  join(import.meta.dirname, '..', '..', '..', 'base-ia');
const lerJson = <T>(...p: string[]): T =>
  JSON.parse(readFileSync(join(BASE, ...p), 'utf-8')) as T;
const lerCsv = (...p: string[]) =>
  parse(readFileSync(join(BASE, ...p), 'utf-8'), {
    columns: true,
    skip_empty_lines: true,
  }) as Record<string, string>[];
const vazio = (v?: string | null) => (v && v.trim() ? v.trim() : null);
const slug = (t: string) =>
  t
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
/** Atualiza todas as colunas informadas quando o id já existe. */
const atualizar = (dado: Record<string, unknown>) => ({ set: dado });

/** Áreas do filtro "Especialidade" e as palavras que ligam cada vaga do edital a uma área. */
export const AREAS: [string, string, string[]][] = [
  ['uti', 'Terapia Intensiva', ['terapia intensiva']],
  ['urg', 'Urgência e Emergência', ['urgência', 'emergência']],
  ['fam', 'Saúde da Família', ['saúde da família', 'atenção básica']],
  ['obs', 'Obstetrícia e Saúde da Mulher', ['obstetr', 'saúde da mulher']],
  ['neo', 'Neonatologia e Pediatria', ['neonat', 'pediatr', 'criança']],
  ['men', 'Saúde Mental', ['saúde mental']],
  ['onc', 'Oncologia', ['oncolog']],
  ['car', 'Cardiologia', ['cardiolog']],
  ['nef', 'Nefrologia', ['nefrolog']],
  ['cc', 'Centro Cirúrgico', ['centro cirúrgico']],
  ['ido', 'Saúde do Idoso', ['idoso']],
  ['inf', 'Infectologia e Infecção Hospitalar', ['infecção', 'infectolog']],
  ['vig', 'Vigilância e Saúde Coletiva', ['vigilância', 'saúde coletiva']],
  ['trab', 'Saúde do Trabalhador', ['trabalhador']],
  [
    'gest',
    'Gestão e Auditoria',
    ['gestão', 'gerenciamento', 'auditoria', 'home care'],
  ],
  ['hem', 'Hematologia e Hemoterapia', ['hematolog', 'hemoterapia']],
  ['neu', 'Neurologia', ['neurolog']],
  ['est', 'Estomaterapia e Dermatologia', ['estomaterapia', 'dermatológ']],
  ['tx', 'Transplantes', ['transplante']],
  ['ind', 'Saúde Indígena', ['indígena']],
  [
    'edu',
    'Educação e Pesquisa em Enfermagem',
    ['educação em enfermagem', 'pesquisa'],
  ],
];
const areaDe = (nome: string) => {
  const n = nome.toLowerCase();
  return AREAS.find(([, , ks]) => ks.some((k) => n.includes(k)))?.[0] ?? null;
};

const CATEGORIA = {
  enfermeiro: 'ENFERMEIRO',
  tecnico_enfermagem: 'TECNICO',
  auxiliar_enfermagem: 'AUXILIAR',
  multiprofissional: 'MULTIPROFISSIONAL',
} as const;
const STATUS = {
  rascunho: 'RASCUNHO',
  revisada: 'REVISADA',
  desatualizada: 'DESATUALIZADA',
} as const;

/** Órgão de cada prova, pelo começo do nome do arquivo em base-ia/provas. Acrescente aqui ao importar provas novas. */
const ORGAOS = [
  {
    prefixo: 'ebserh-',
    id: 'ebserh',
    nome: 'EBSERH',
    tipo: 'CONCURSO',
    esfera: 'Federal',
    uf: null,
  },
  {
    prefixo: 'enare-',
    id: 'enare',
    nome: 'ENARE',
    tipo: 'RESIDENCIA',
    esfera: 'Federal',
    uf: null,
  },
] as const;

type Manifesto = {
  banca: string;
  ano: number;
  cargo: string;
  categoria_profissional: keyof typeof CATEGORIA;
  grupo_prova?: string;
  tipo_prova?: string;
  data_prova?: string | null;
  url_prova?: string;
  url_gabarito?: string;
  gabarito_conferido?: string;
  especialidades?: string[];
  arquivo_questoes?: string;
};
type QuestaoBase = {
  id: string;
  origem: string;
  numero?: number | null;
  disciplina?: string | null;
  tema: string;
  subtema?: string | null;
  dificuldade?: number;
  texto_apoio?: string | null;
  enunciado: string;
  imagens?: string[];
  alternativas: { letra: string; texto: string }[];
  gabarito: string | null;
  anulada?: boolean;
  comentario?: string | null;
  status_revisao?: keyof typeof STATUS;
  revisor?: string | null;
  assuntos?: string[];
  fontes?: { documento_id: string; dispositivo?: string | null }[];
  referencias?: { referencia_id: string; onde?: string | null }[];
};

async function main() {
  if (!existsSync(BASE))
    throw new Error(`Pasta base-ia não encontrada em ${BASE}`);
  const { db, pool } = criarDb();

  await db.transaction(async (tx) => {
    // 1. Normas e livros
    const docs = lerCsv('fontes', 'catalogo_fontes.csv');
    for (const d of docs) {
      const dado = {
        titulo: d.titulo,
        tipo: d.tipo,
        numero: vazio(d.numero),
        ano: Number(d.ano) || null,
        orgao: vazio(d.orgao),
        tema: vazio(d.tema),
        prioridade: vazio(d.prioridade),
        formato: vazio(d.formato),
        urlOficial: vazio(d.url_oficial),
        observacao: vazio(d.observacao),
      };
      await tx
        .insert(s.documentos)
        .values({ id: d.id, ...dado })
        .onConflictDoUpdate({ target: s.documentos.id, ...atualizar(dado) });
    }
    const refs = lerCsv('fontes', 'referencias_bibliograficas.csv');
    for (const r of refs) {
      const dado = {
        tipo: r.tipo,
        autores: r.autores,
        titulo: r.titulo,
        editora: vazio(r.editora_ou_orgao),
        tema: vazio(r.tema),
        comoUsar: vazio(r.como_usar),
      };
      await tx
        .insert(s.referencias)
        .values({ id: r.id, ...dado })
        .onConflictDoUpdate({ target: s.referencias.id, ...atualizar(dado) });
    }

    // 2. Temáticas e assuntos
    const taxo = lerJson<
      { id: string; nome: string; assuntos: { id: string; nome: string }[] }[]
    >('esquemas', 'taxonomia.json');
    for (const [ordem, t] of taxo.entries()) {
      await tx
        .insert(s.tematicas)
        .values({ id: t.id, nome: t.nome, ordem })
        .onConflictDoUpdate({
          target: s.tematicas.id,
          set: { nome: t.nome, ordem },
        });
      for (const a of t.assuntos) {
        await tx
          .insert(s.assuntos)
          .values({ id: a.id, nome: a.nome, tematicaId: t.id })
          .onConflictDoUpdate({
            target: s.assuntos.id,
            set: { nome: a.nome, tematicaId: t.id },
          });
      }
    }

    // 3. Áreas de especialidade
    for (const [id, nome] of AREAS) {
      await tx
        .insert(s.areasEspecialidade)
        .values({ id, nome })
        .onConflictDoUpdate({ target: s.areasEspecialidade.id, set: { nome } });
    }

    // 4. Provas
    const provaDoArquivo = new Map<string, string>();
    for (const arq of readdirSync(join(BASE, 'provas'))
      .filter((f) => f.endsWith('.json'))
      .sort()) {
      const m = lerJson<Manifesto>('provas', arq);
      const org = ORGAOS.find((o) => arq.startsWith(o.prefixo));
      if (!org) {
        console.warn(
          `Pulei ${arq}: órgão não cadastrado em ORGAOS (src/db/seed.ts).`,
        );
        continue;
      }
      const { prefixo: _p, ...orgao } = org;
      await tx
        .insert(s.orgaos)
        .values(orgao)
        .onConflictDoUpdate({ target: s.orgaos.id, set: orgao });
      const bancaId = slug(m.banca);
      await tx
        .insert(s.bancas)
        .values({ id: bancaId, nome: m.banca })
        .onConflictDoNothing();

      const provaId = arq.replace(/\.json$/, '');
      const dado = {
        orgaoId: org.id,
        bancaId,
        ano: m.ano,
        cargo: m.cargo,
        categoria: CATEGORIA[m.categoria_profissional] ?? 'ENFERMEIRO',
        grupo: m.grupo_prova ?? null,
        tipoProva: m.tipo_prova ?? null,
        localidade: org.uf ?? 'Nacional',
        dataProva: m.data_prova ?? null,
        urlProva: m.url_prova ?? null,
        urlGabarito: m.url_gabarito ?? null,
        gabaritoConferido: m.gabarito_conferido ?? null,
      };
      await tx
        .insert(s.provas)
        .values({ id: provaId, ...dado })
        .onConflictDoUpdate({ target: s.provas.id, ...atualizar(dado) });

      await tx
        .delete(s.provaEspecialidades)
        .where(eq(s.provaEspecialidades.provaId, provaId));
      for (const nome of m.especialidades ?? []) {
        const id = slug(nome);
        await tx
          .insert(s.especialidades)
          .values({ id, nome, areaId: areaDe(nome) })
          .onConflictDoUpdate({
            target: s.especialidades.id,
            set: { nome, areaId: areaDe(nome) },
          });
        await tx
          .insert(s.provaEspecialidades)
          .values({ provaId, especialidadeId: id });
      }
      provaDoArquivo.set(m.arquivo_questoes ?? `questoes/${arq}`, provaId);
    }

    // 5. Questões
    const docsIds = new Set(docs.map((d) => d.id));
    const refsIds = new Set(refs.map((r) => r.id));
    let total = 0;
    for (const arq of readdirSync(join(BASE, 'questoes'))
      .filter((f) => f.endsWith('.json'))
      .sort()) {
      const provaId = provaDoArquivo.get(`questoes/${arq}`) ?? null;
      for (const q of lerJson<QuestaoBase[]>('questoes', arq)) {
        const dado = {
          origem:
            q.origem === 'prova'
              ? ('PROVA' as const)
              : q.origem === 'inedita'
                ? ('INEDITA' as const)
                : ('EXEMPLO' as const),
          provaId,
          numero: q.numero ?? null,
          disciplina: q.disciplina ?? null,
          temaBase: q.tema,
          subtema: q.subtema ?? null,
          dificuldade: q.dificuldade ?? 3,
          textoApoio: q.texto_apoio ?? null,
          enunciado: q.enunciado,
          imagens: q.imagens ?? [],
          gabarito: q.gabarito ?? null,
          anulada: q.anulada ?? false,
          comentario: q.comentario ?? null,
          statusRevisao: STATUS[q.status_revisao ?? 'rascunho'] ?? 'RASCUNHO',
          revisor: q.revisor ?? null,
          atualizadaEm: sql`now()`,
        };
        // As questões de exemplo vêm sempre com a certa na letra A: gira as alternativas de forma fixa por questão.
        if (
          dado.origem === 'EXEMPLO' &&
          q.gabarito === 'A' &&
          q.alternativas.length > 1
        ) {
          const giro =
            Array.from(q.id, (ch) => ch.charCodeAt(0)).reduce(
              (a, b) => a + b,
              0,
            ) % q.alternativas.length;
          const textos = q.alternativas.map((a) => a.texto);
          q.alternativas = textos.map((_, i) => ({
            letra: 'ABCDE'[i],
            texto: textos[(i - giro + textos.length) % textos.length],
          }));
          dado.gabarito = 'ABCDE'[giro];
        }
        await tx
          .insert(s.questoes)
          .values({ id: q.id, ...dado })
          .onConflictDoUpdate({ target: s.questoes.id, ...atualizar(dado) });

        // filhos: apaga e recria para refletir a base
        await tx
          .delete(s.alternativas)
          .where(eq(s.alternativas.questaoId, q.id));
        await tx.insert(s.alternativas).values(
          q.alternativas.map((a) => ({
            questaoId: q.id,
            letra: a.letra,
            texto: a.texto,
          })),
        );
        await tx
          .delete(s.questaoAssuntos)
          .where(eq(s.questaoAssuntos.questaoId, q.id));
        if (q.assuntos?.length)
          await tx
            .insert(s.questaoAssuntos)
            .values(
              q.assuntos.map((assuntoId) => ({ questaoId: q.id, assuntoId })),
            );
        await tx
          .delete(s.questaoFontes)
          .where(eq(s.questaoFontes.questaoId, q.id));
        const fontes = (q.fontes ?? []).filter((f) =>
          docsIds.has(f.documento_id),
        );
        if (fontes.length)
          await tx
            .insert(s.questaoFontes)
            .values(
              fontes.map((f) => ({
                questaoId: q.id,
                documentoId: f.documento_id,
                dispositivo: f.dispositivo ?? null,
              })),
            )
            .onConflictDoNothing();
        await tx
          .delete(s.questaoReferencias)
          .where(eq(s.questaoReferencias.questaoId, q.id));
        const rs = (q.referencias ?? []).filter((r) =>
          refsIds.has(r.referencia_id),
        );
        if (rs.length)
          await tx
            .insert(s.questaoReferencias)
            .values(
              rs.map((r) => ({
                questaoId: q.id,
                referenciaId: r.referencia_id,
                onde: r.onde ?? null,
              })),
            )
            .onConflictDoNothing();
        total++;
      }
    }

    // 6. Trechos das fichas (a fase da IA acrescenta os das normas baixadas)
    let nTrechos = 0;
    const pasta = join(BASE, 'dados', 'trechos');
    if (existsSync(pasta)) {
      for (const arq of readdirSync(pasta).filter((f) =>
        f.endsWith('.jsonl'),
      )) {
        for (const linha of readFileSync(join(pasta, arq), 'utf-8').split(
          '\n',
        )) {
          if (!linha.trim()) continue;
          const t = JSON.parse(linha) as {
            id: string;
            documento_id: string;
            dispositivo?: string;
            texto: string;
            tipo_conteudo?: string;
          };
          if (!docsIds.has(t.documento_id)) continue;
          const dado = {
            documentoId: t.documento_id,
            dispositivo: t.dispositivo ?? null,
            texto: t.texto,
            fonte: t.tipo_conteudo === 'resumo_proprio' ? 'ficha' : 'norma',
          };
          await tx
            .insert(s.trechos)
            .values({ id: t.id, ...dado })
            .onConflictDoUpdate({ target: s.trechos.id, ...atualizar(dado) });
          nTrechos++;
        }
      }
    }
    console.log(
      `Importados: ${docs.length} normas, ${refs.length} referências, ${taxo.length} temáticas, ${provaDoArquivo.size} provas, ${total} questões, ${nTrechos} trechos.`,
    );
  });
  await pool.end();
}

await main();
