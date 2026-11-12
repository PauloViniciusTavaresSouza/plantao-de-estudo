/** Cliente da API do Plantão de Estudo (backend NestJS). */
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001";

export type Tipo = "CONCURSO" | "RESIDENCIA";
export type Categoria = "ENFERMEIRO" | "TECNICO" | "AUXILIAR" | "MULTIPROFISSIONAL";
export type Letra = "A" | "B" | "C" | "D" | "E";

export type Questao = {
  id: string;
  origem: "PROVA" | "INEDITA" | "EXEMPLO";
  numero: number | null;
  disciplina: string | null;
  subtema: string | null;
  textoApoio: string | null;
  enunciado: string;
  imagens: string[];
  prova: {
    id: string;
    orgaoId: string;
    orgao: string;
    tipo: Tipo;
    banca: string;
    ano: number;
    cargo: string;
    categoria: Categoria;
    localidade: string;
  } | null;
  alternativas: { letra: Letra; texto: string }[];
  assuntos: { id: string; nome: string; tematicaId: string; tematica: string }[];
};

export type Pagina = { total: number; pagina: number; limite: number; paginas: number; itens: Questao[] };

export type Resultado = {
  correta: boolean;
  gabarito: Letra;
  comentario: string | null;
  fontes: { id: string; titulo: string; url: string | null; dispositivo: string | null }[];
  referencias: { id: string; autores: string; titulo: string; onde: string | null }[];
};

export type Opcoes = {
  total: number;
  orgaos: { id: string; nome: string; tipo: Tipo; esfera: string | null; uf: string | null; questoes: number }[];
  bancas: { id: string; nome: string; questoes: number }[];
  anos: { ano: number; questoes: number }[];
  categorias: { id: Categoria; nome: string; questoes: number }[];
  localidades: { id: string; questoes: number }[];
  areas: { id: string; nome: string }[];
  tematicas: { id: string; nome: string; assuntos: { id: string; nome: string; questoes: number }[] }[];
};

/** Filtros da tela de questões. String vazia = sem filtro. */
export type Filtros = {
  tipo: "" | Tipo;
  orgao: string;
  banca: string;
  ano: string;
  categoria: "" | Categoria;
  area: string;
  uf: string;
  tematica: string[];
  assunto: string[];
};

export const FILTROS_VAZIOS: Filtros = {
  tipo: "",
  orgao: "",
  banca: "",
  ano: "",
  categoria: "",
  area: "",
  uf: "",
  tematica: [],
  assunto: [],
};

async function pedir<T>(caminho: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API_URL}${caminho}`, init);
  if (!r.ok) throw new Error(`A API respondeu ${r.status} em ${caminho}`);
  return (await r.json()) as T;
}

export const buscarOpcoes = () => pedir<Opcoes>("/filtros");

export function buscarQuestoes(f: Filtros, extra: { pagina?: number; limite?: number; semente?: string } = {}) {
  const q = new URLSearchParams();
  for (const k of ["tipo", "orgao", "banca", "ano", "categoria", "area", "uf"] as const) if (f[k]) q.set(k, f[k]);
  if (f.tematica.length) q.set("tematica", f.tematica.join(","));
  if (f.assunto.length) q.set("assunto", f.assunto.join(","));
  q.set("pagina", String(extra.pagina ?? 1));
  q.set("limite", String(extra.limite ?? 10));
  if (extra.semente) {
    q.set("ordem", "aleatoria");
    q.set("semente", extra.semente);
  }
  return pedir<Pagina>(`/questoes?${q}`);
}

export const responder = (id: string, letra: Letra) =>
  pedir<Resultado>(`/questoes/${encodeURIComponent(id)}/resposta`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ letra }),
  });

/** Caminho "imagens/x.png" da base -> URL servida pela API. */
export const urlImagem = (caminho: string) => `${API_URL}/${caminho.replace(/^\//, "")}`;
