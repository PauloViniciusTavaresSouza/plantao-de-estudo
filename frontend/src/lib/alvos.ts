/**
 * Vitrine da página inicial: áreas de concurso e programas de residência.
 * `orgaoId` liga o cartão ao órgão no banco (quando já temos provas dele).
 */
export type Alvo = {
  nome: string;
  inst: string;
  local: string;
  banca: string;
  cor: `--h${1 | 2 | 3 | 4 | 5 | 6}`;
  forma: "hosp" | "uni" | "city";
  orgaoId?: string;
};

export const CONCURSOS: Alvo[] = [
  { nome: "EBSERH", inst: "Hospitais universitários federais", local: "Federal", banca: "FGV e IBFC", cor: "--h5", forma: "hosp", orgaoId: "ebserh" },
  { nome: "Secretarias Estaduais de Saúde", inst: "SES-DF, SES-SP, SES-GO e outras", local: "Estadual", banca: "Várias bancas", cor: "--h1", forma: "city" },
  { nome: "Prefeituras", inst: "Secretarias municipais, UBS, UPA e hospitais", local: "Municipal", banca: "Várias bancas", cor: "--h4", forma: "city" },
  { nome: "Forças Armadas", inst: "Marinha, Exército e Aeronáutica", local: "Federal · militar", banca: "Bancas próprias", cor: "--h3", forma: "uni" },
  { nome: "PM e Bombeiros", inst: "Quadros de saúde das corporações", local: "Estadual · militar", banca: "Várias bancas", cor: "--h6", forma: "uni" },
  { nome: "Institutos e órgãos federais", inst: "Ministério da Saúde, INCA, Fiocruz, INTO", local: "Federal", banca: "Várias bancas", cor: "--h2", forma: "hosp" },
  { nome: "Hospitais e universidades estaduais", inst: "HCs, fundações e universidades", local: "Estadual", banca: "Várias bancas", cor: "--h1", forma: "hosp" },
  { nome: "Fundações e consórcios", inst: "Fundações estatais e consórcios de saúde", local: "Regional", banca: "Várias bancas", cor: "--h4", forma: "city" },
];

export const RESIDENCIAS: Alvo[] = [
  { nome: "ENARE", inst: "HU Brasil e instituições parceiras", local: "Nacional", banca: "FGV", cor: "--h5", forma: "hosp", orgaoId: "enare" },
  { nome: "SES-DF", inst: "Residências da Fepecs", local: "DF", banca: "Iades", cor: "--h1", forma: "city" },
  { nome: "UERJ", inst: "Residência em Enfermagem", local: "RJ", banca: "CEPUERJ", cor: "--h2", forma: "uni" },
  { nome: "HCFMUSP", inst: "Hospital das Clínicas da USP", local: "SP", banca: "Vunesp", cor: "--h3", forma: "hosp" },
  { nome: "Unifesp", inst: "Residência Multiprofissional", local: "SP", banca: "Vunesp", cor: "--h4", forma: "uni" },
  { nome: "Sírio-Libanês", inst: "Uni e multiprofissional", local: "SP", banca: "Vunesp", cor: "--h6", forma: "city" },
  { nome: "HCPA", inst: "Hospital de Clínicas de Porto Alegre", local: "RS", banca: "FundMed", cor: "--h1", forma: "hosp" },
  { nome: "INCA", inst: "Residência em Oncologia", local: "RJ", banca: "INCA", cor: "--h2", forma: "uni" },
];

export const UFS: [string, string[]][] = [
  ["Norte", ["AC", "AM", "AP", "PA", "RO", "RR", "TO"]],
  ["Nordeste", ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]],
  ["Centro-Oeste", ["DF", "GO", "MS", "MT"]],
  ["Sudeste", ["ES", "MG", "RJ", "SP"]],
  ["Sul", ["PR", "RS", "SC"]],
];

/** Limite do plano grátis. Por enquanto fica no navegador; passa para o servidor quando houver login. */
export const LIMITE_GRATIS = 5;
