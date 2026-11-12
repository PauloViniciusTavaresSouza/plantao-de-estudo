"use client";

import { useEffect, useMemo, useState } from "react";
import { LIMITE_GRATIS, UFS } from "@/lib/alvos";
import { buscarOpcoes, buscarQuestoes, FILTROS_VAZIOS, type Filtros, type Opcoes, type Questao } from "@/lib/api";
import { Resolver } from "./Resolver";
import s from "./Estudo.module.css";

const hoje = () => new Date().toLocaleDateString("sv-SE"); // AAAA-MM-DD no fuso do aparelho
const CHAVE = "plantao-de-estudo:dia";

/** Questões respondidas hoje. Fica no navegador até existir login; depois o servidor controla. */
function lerRespondidasHoje(): number {
  try {
    const d = JSON.parse(localStorage.getItem(CHAVE) ?? "null") as { data: string; n: number } | null;
    return d && d.data === hoje() ? d.n : 0;
  } catch {
    return 0;
  }
}
function gravarRespondidasHoje(n: number) {
  try {
    localStorage.setItem(CHAVE, JSON.stringify({ data: hoje(), n }));
  } catch {
    // armazenamento bloqueado: o contador vale só para esta visita
  }
}

export function Estudo() {
  const [opcoes, setOpcoes] = useState<Opcoes | null>(null);
  const [filtros, setFiltros] = useState<Filtros>(FILTROS_VAZIOS);
  const [total, setTotal] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [sessao, setSessao] = useState<Questao[] | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [respondidas, setRespondidas] = useState(0);

  // Opções dos filtros, contador do dia e filtro vindo do link (?orgao=enare)
  useEffect(() => {
    buscarOpcoes().then(setOpcoes).catch(() => setErro("Não consegui falar com a API. Confira se o backend está rodando."));
    // Depois da primeira pintura, para o HTML do servidor e o do navegador começarem iguais.
    queueMicrotask(() => {
      setRespondidas(lerRespondidasHoje());
      const orgao = new URLSearchParams(window.location.search).get("orgao");
      if (orgao) setFiltros((f) => ({ ...f, orgao }));
    });
  }, []);

  // Contagem das questões que batem com os filtros
  useEffect(() => {
    let vivo = true;
    buscarQuestoes(filtros, { limite: 1 })
      .then((p) => vivo && setTotal(p.total))
      .catch(() => vivo && setTotal(null));
    return () => {
      vivo = false;
    };
  }, [filtros]);

  const restantes = Math.max(0, LIMITE_GRATIS - respondidas);
  const orgaoAtual = opcoes?.orgaos.find((o) => o.id === filtros.orgao);
  const orgaosVisiveis = useMemo(() => (opcoes?.orgaos ?? []).filter((o) => !filtros.tipo || o.tipo === filtros.tipo), [opcoes, filtros.tipo]);
  const ativos =
    filtros.tematica.length + filtros.assunto.length + (["orgao", "banca", "ano", "categoria", "area", "uf"] as const).filter((k) => filtros[k]).length;

  const mudar = (parte: Partial<Filtros>) => setFiltros((f) => ({ ...f, ...parte }));

  function alternarTematica(id: string) {
    setFiltros((f) => {
      if (!f.tematica.includes(id)) return { ...f, tematica: [...f.tematica, id] };
      const doGrupo = new Set(opcoes?.tematicas.find((t) => t.id === id)?.assuntos.map((a) => a.id));
      return { ...f, tematica: f.tematica.filter((t) => t !== id), assunto: f.assunto.filter((a) => !doGrupo.has(a)) };
    });
  }
  const alternarAssunto = (id: string) =>
    setFiltros((f) => ({ ...f, assunto: f.assunto.includes(id) ? f.assunto.filter((a) => a !== id) : [...f.assunto, id] }));

  async function comecar() {
    if (!restantes) return;
    setCarregando(true);
    try {
      const p = await buscarQuestoes(filtros, { limite: restantes, semente: String(Date.now()) });
      setSessao(p.itens);
    } catch {
      setErro("Não consegui carregar as questões. Tente de novo.");
    } finally {
      setCarregando(false);
    }
  }

  if (sessao) {
    return (
      <Resolver
        questoes={sessao}
        aoResponder={() =>
          setRespondidas((n) => {
            gravarRespondidasHoje(n + 1);
            return n + 1;
          })
        }
        aoSair={() => setSessao(null)}
      />
    );
  }

  return (
    <>
      <div className={s.titulo}>
        <h1>Questões</h1>
        <p>Escolha o concurso ou a residência, a especialidade da vaga e a temática, e treine com as provas reais.</p>
      </div>

      {erro && <p className={s.erro}>{erro}</p>}

      <section className={s.cartao}>
        <div className={s.seg} role="group" aria-label="Tipo de prova">
          {(
            [
              ["", "Todas"],
              ["CONCURSO", "Concursos"],
              ["RESIDENCIA", "Residências"],
            ] as const
          ).map(([valor, nome]) => (
            <button
              key={valor}
              type="button"
              aria-pressed={filtros.tipo === valor}
              onClick={() => mudar({ tipo: valor, orgao: orgaoAtual && valor && orgaoAtual.tipo !== valor ? "" : filtros.orgao })}
            >
              {nome}
            </button>
          ))}
        </div>

        <div className={s.grade3}>
          <label className={s.campo}>
            <span>{filtros.tipo === "CONCURSO" ? "Órgão ou concurso" : filtros.tipo === "RESIDENCIA" ? "Programa de residência" : "Órgão ou programa"}</span>
            <select
              value={filtros.orgao}
              onChange={(e) => {
                const o = opcoes?.orgaos.find((x) => x.id === e.target.value);
                mudar({ orgao: e.target.value, tipo: o ? o.tipo : filtros.tipo });
              }}
            >
              <option value="">Todos</option>
              {orgaosVisiveis.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.nome} ({o.questoes})
                </option>
              ))}
            </select>
          </label>
          <label className={s.campo}>
            <span>Banca</span>
            <select value={filtros.banca} onChange={(e) => mudar({ banca: e.target.value })}>
              <option value="">Todas</option>
              {opcoes?.bancas.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.nome}
                </option>
              ))}
            </select>
          </label>
          <label className={s.campo}>
            <span>Ano</span>
            <select value={filtros.ano} onChange={(e) => mudar({ ano: e.target.value })}>
              <option value="">Todos</option>
              {opcoes?.anos.map((a) => (
                <option key={a.ano} value={a.ano}>
                  {a.ano}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className={s.grade3}>
          <label className={s.campo}>
            <span>Categoria profissional</span>
            <select value={filtros.categoria} onChange={(e) => mudar({ categoria: e.target.value as Filtros["categoria"] })}>
              <option value="">Todas</option>
              <option value="ENFERMEIRO">Enfermeiro</option>
              <option value="TECNICO">Técnico</option>
              <option value="AUXILIAR">Auxiliar</option>
            </select>
          </label>
          <label className={s.campo}>
            <span>Especialidade da enfermagem</span>
            <select value={filtros.area} onChange={(e) => mudar({ area: e.target.value })}>
              <option value="">Todas</option>
              {opcoes?.areas.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.nome}
                </option>
              ))}
            </select>
          </label>
          <label className={s.campo}>
            <span>Localidade</span>
            <select value={filtros.uf} onChange={(e) => mudar({ uf: e.target.value })}>
              <option value="">Todas</option>
              <option value="Nacional">Só provas nacionais</option>
              {UFS.map(([regiao, ufs]) => (
                <optgroup key={regiao} label={regiao}>
                  {ufs.map((uf) => (
                    <option key={uf}>{uf}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </label>
        </div>

        <div className={s.campo}>
          <span>Temática</span>
          <div className={s.chips}>
            {opcoes?.tematicas.map((t) => (
              <button key={t.id} type="button" className={s.chip} aria-pressed={filtros.tematica.includes(t.id)} onClick={() => alternarTematica(t.id)}>
                {t.nome}
              </button>
            ))}
          </div>
          <small className={s.dica}>Marque uma temática para escolher os assuntos dela. Nenhuma marcada = todas.</small>
        </div>

        {opcoes?.tematicas
          .filter((t) => filtros.tematica.includes(t.id))
          .map((t) => (
            <div key={t.id} className={s.assuntos}>
              <b>{t.nome}</b>
              <div className={s.chips}>
                {t.assuntos.map((a) => (
                  <button
                    key={a.id}
                    type="button"
                    className={`${s.chip} ${s.menor}`}
                    aria-pressed={filtros.assunto.includes(a.id)}
                    disabled={!a.questoes}
                    onClick={() => alternarAssunto(a.id)}
                  >
                    {a.nome} <span className={s.conta}>{a.questoes}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}

        {filtros.uf && filtros.uf !== "Nacional" && (
          <p className={s.dica}>Provas nacionais, como EBSERH e ENARE, valem para todos os estados e aparecem junto com as de {filtros.uf}.</p>
        )}
        {filtros.area && <p className={s.dica}>Provas únicas para todas as especialidades, como a do ENARE, também aparecem neste filtro.</p>}

        <div className={s.rodape}>
          <b>{total === null ? "Contando..." : `${total} questões encontradas`}</b>
          <div className={s.acoes}>
            <button type="button" className={s.secundario} disabled={!ativos && !filtros.tipo} onClick={() => setFiltros(FILTROS_VAZIOS)}>
              Limpar filtros{ativos ? ` (${ativos})` : ""}
            </button>
            <button type="button" className={s.primario} disabled={!total || !restantes || carregando} onClick={comecar}>
              {carregando ? "Carregando..." : "Resolver questões"}
            </button>
          </div>
        </div>
        <p className={s.dica}>
          {restantes
            ? `Plano grátis: você ainda pode resolver ${restantes} de ${LIMITE_GRATIS} questões hoje.`
            : `Você usou as ${LIMITE_GRATIS} questões grátis de hoje. Volte amanhã ou conheça o Premium.`}
        </p>
      </section>
    </>
  );
}
