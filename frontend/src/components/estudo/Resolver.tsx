"use client";

import { useState } from "react";
import { responder, urlImagem, type Letra, type Questao, type Resultado } from "@/lib/api";
import s from "./Estudo.module.css";

type Props = { questoes: Questao[]; aoResponder: () => void; aoSair: () => void };

/** Uma questão por vez: escolhe, responde, vê o gabarito oficial e onde estudar. */
export function Resolver({ questoes, aoResponder, aoSair }: Props) {
  const [i, setI] = useState(0);
  const [escolha, setEscolha] = useState<Letra | null>(null);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [acertos, setAcertos] = useState(0);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  if (i >= questoes.length) {
    return (
      <section className={s.cartao}>
        <h1 className={s.resumo}>
          {acertos} de {questoes.length} acertos
        </h1>
        <p>Sessão concluída. Volte aos filtros para escolher outro assunto.</p>
        <div className={s.acoes}>
          <button type="button" className={s.primario} onClick={aoSair}>
            Voltar aos filtros
          </button>
        </div>
      </section>
    );
  }

  const q = questoes[i];
  const estudar = resultado ? [...resultado.fontes.map((f) => f.titulo), ...resultado.referencias.map((r) => `${r.autores}. ${r.titulo}`)] : [];

  async function confirmar() {
    if (!escolha) return;
    setEnviando(true);
    setErro("");
    try {
      const r = await responder(q.id, escolha);
      setResultado(r);
      if (r.correta) setAcertos((n) => n + 1);
      aoResponder();
    } catch {
      setErro("Não consegui conferir a resposta. Tente de novo.");
    } finally {
      setEnviando(false);
    }
  }

  function proxima() {
    setI((n) => n + 1);
    setEscolha(null);
    setResultado(null);
  }

  return (
    <>
      <div className={s.titulo}>
        <small className={s.dica}>Modo estudo</small>
        <h1>
          Questão {i + 1} de {questoes.length}
        </h1>
      </div>
      <div className={s.barra}>
        <i style={{ width: `${((i + (resultado ? 1 : 0)) / questoes.length) * 100}%` }} />
      </div>

      <section className={s.cartao}>
        <div className={s.meta}>
          <span className={s.tag}>{q.assuntos[0] ? `${q.assuntos[0].tematica} · ${q.assuntos[0].nome}` : (q.disciplina ?? "Questão")}</span>
          <span className={s.pilula}>
            {q.prova ? `${q.prova.orgao} · ${q.prova.banca} · ${q.prova.ano}${q.numero ? ` · Q${q.numero}` : ""}` : "Questão de exemplo"}
          </span>
        </div>

        {q.textoApoio && (
          <details className={s.apoio}>
            <summary>Texto de apoio</summary>
            <p>{q.textoApoio}</p>
          </details>
        )}
        {q.imagens.map((src) => (
          // eslint-disable-next-line @next/next/no-img-element -- figura servida pela API, com tamanho variável
          <img key={src} className={s.figura} src={urlImagem(src)} alt={`Figura da questão ${q.numero ?? ""}`} loading="lazy" />
        ))}

        <p className={s.enunciado}>{q.enunciado}</p>

        <div className={s.alternativas}>
          {q.alternativas.map((a) => {
            const certa = resultado && a.letra === resultado.gabarito;
            const errada = resultado && a.letra === escolha && !resultado.correta;
            return (
              <button
                key={a.letra}
                type="button"
                className={`${s.alt} ${certa ? s.certa : ""} ${errada ? s.errada : ""}`}
                aria-pressed={!resultado && escolha === a.letra}
                disabled={!!resultado}
                onClick={() => setEscolha(a.letra)}
              >
                <b>{a.letra}</b>
                <span>{a.texto}</span>
              </button>
            );
          })}
        </div>

        {erro && <p className={s.erro}>{erro}</p>}

        {resultado && (
          <div className={s.comentario}>
            <b className={resultado.correta ? s.acertou : s.errou}>{resultado.correta ? "Você acertou!" : `Resposta: ${resultado.gabarito}`}</b>
            <p>{resultado.comentario ?? `Gabarito oficial da banca: letra ${resultado.gabarito}. O comentário do professor está em revisão.`}</p>
            {estudar.length > 0 && (
              <>
                <b>Onde estudar</b>
                <ul>
                  {estudar.slice(0, 4).map((t) => (
                    <li key={t}>{t}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}

        <div className={s.rodape}>
          <button type="button" className={s.secundario} onClick={aoSair}>
            Encerrar
          </button>
          {resultado ? (
            <button type="button" className={s.primario} onClick={proxima}>
              {i < questoes.length - 1 ? "Próxima questão" : "Ver resumo"}
            </button>
          ) : (
            <button type="button" className={s.primario} disabled={!escolha || enviando} onClick={confirmar}>
              {enviando ? "Conferindo..." : "Responder"}
            </button>
          )}
        </div>
      </section>
    </>
  );
}
