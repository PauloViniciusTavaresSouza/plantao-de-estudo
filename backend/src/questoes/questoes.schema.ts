import { z } from 'zod';

/** "a,b,c" ou parâmetro repetido -> ['a','b','c'] */
const lista = z
  .union([z.string(), z.array(z.string())])
  .optional()
  .transform((v) =>
    v === undefined
      ? []
      : (Array.isArray(v) ? v : v.split(','))
          .map((x) => x.trim())
          .filter(Boolean),
  );

export const listarQuestoesSchema = z.object({
  /** CONCURSO ou RESIDENCIA */
  tipo: z.enum(['CONCURSO', 'RESIDENCIA']).optional(),
  /** id do órgão ou programa (ex.: ebserh, enare) */
  orgao: z.string().trim().optional(),
  banca: z.string().trim().optional(),
  ano: z.coerce.number().int().min(1990).max(2100).optional(),
  categoria: z
    .enum(['ENFERMEIRO', 'TECNICO', 'AUXILIAR', 'MULTIPROFISSIONAL'])
    .optional(),
  /** área de especialidade (ex.: uti, obs) */
  area: z.string().trim().optional(),
  /** "Nacional" ou sigla da UF. Com uma UF, as provas nacionais também entram. */
  uf: z.string().trim().max(8).optional(),
  /** ids de temáticas (ex.: vig,urg) */
  tematica: lista,
  /** ids de assuntos (ex.: vig-sanit). Refinam a temática a que pertencem. */
  assunto: lista,
  origem: z.enum(['PROVA', 'INEDITA', 'EXEMPLO']).optional(),
  /** "aleatoria" embaralha de forma estável para a mesma `semente` */
  ordem: z.enum(['prova', 'aleatoria']).default('prova'),
  semente: z.string().max(40).default('plantao'),
  pagina: z.coerce.number().int().min(1).default(1),
  limite: z.coerce.number().int().min(1).max(50).default(10),
});
export type ListarQuestoes = z.infer<typeof listarQuestoesSchema>;

export const responderSchema = z.object({
  letra: z.enum(['A', 'B', 'C', 'D', 'E']),
});
export type Responder = z.infer<typeof responderSchema>;
