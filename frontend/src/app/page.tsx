import Link from "next/link";
import { ArteAlvo, ArteCapa, Logo } from "@/components/Ilustracoes";
import { CONCURSOS, LIMITE_GRATIS, RESIDENCIAS, type Alvo } from "@/lib/alvos";
import s from "./page.module.css";

function Cartao({ alvo }: { alvo: Alvo }) {
  return (
    <article className={s.alvo}>
      <div className={s.arte} style={{ background: `color-mix(in srgb, var(${alvo.cor}) 16%, var(--surface))` }}>
        <ArteAlvo alvo={alvo} />
      </div>
      <h3>{alvo.nome}</h3>
      <p className={s.pequeno}>{alvo.inst}</p>
      <div className={s.pilulas}>
        <span className={s.pilula}>{alvo.banca}</span>
        <span className={s.pilula}>{alvo.local}</span>
      </div>
      {alvo.orgaoId ? (
        <Link className={s.disponivel} href={`/questoes?orgao=${alvo.orgaoId}`}>
          Questões disponíveis
        </Link>
      ) : (
        <span className={s.embreve}>Em breve</span>
      )}
    </article>
  );
}

const RECURSOS = [
  ["Filtros do jeito da sua prova", "Órgão ou programa, banca, ano, cargo, especialidade, estado e temática, até o assunto."],
  ["Gabarito com a fonte", "Depois de responder, veja o gabarito oficial e a lei ou o livro onde estudar o assunto."],
  ["Simulados cronometrados", "Monte provas de 10 a 40 questões, com tempo de prova real. Em breve."],
  ["Revisão dos seus erros", "As questões que você errou voltam até você acertar. Em breve."],
];

export default function Inicio() {
  return (
    <>
      <header className={s.nav}>
        <div className={`container ${s.navIn}`}>
          <Link className={s.logo} href="/">
            <Logo />
          </Link>
          <nav className={s.links}>
            <a href="#concursos">Concursos</a>
            <a href="#residencias">Residências</a>
            <a href="#planos">Planos</a>
            <Link className={`${s.btn} ${s.primario} ${s.btnNav}`} href="/questoes">
              Entrar
            </Link>
          </nav>
        </div>
      </header>

      <main>
        <section className={`container ${s.hero}`}>
          <div>
            <span className={s.tag}>Concursos e residências de enfermagem</span>
            <h1>
              Seu concurso ou sua residência começam no <em>plantão de estudo</em>
            </h1>
            <p className={s.lead}>
              Questões de provas reais com gabarito oficial, para enfermeiros e técnicos. Filtre por concurso, programa de
              residência, especialidade e banca, e estude entre um plantão e outro.
            </p>
            <div className={s.ctas}>
              <Link className={`${s.btn} ${s.primario}`} href="/questoes">
                Começar grátis
              </Link>
              <a className={`${s.btn} ${s.secundario}`} href="#concursos">
                Ver concursos e residências
              </a>
            </div>
            <ul className={s.confianca}>
              <li>Questões de provas reais</li>
              <li>Gabarito oficial da banca</li>
              <li>Sem cartão para começar</li>
            </ul>
          </div>
          <div className={s.capa}>
            <ArteCapa />
          </div>
        </section>

        <section className={`container ${s.secao}`} id="concursos">
          <div className={s.cabeca}>
            <span className={s.tag}>Concursos</span>
            <h2>Do hospital federal à prefeitura da sua cidade</h2>
            <p>Questões para enfermeiro, técnico e auxiliar de enfermagem, em todas as esferas: federal, estadual, municipal e militar.</p>
          </div>
          <div className={s.grade}>
            {CONCURSOS.map((a) => (
              <Cartao key={a.nome} alvo={a} />
            ))}
          </div>
        </section>

        <section className={`container ${s.secao}`} id="residencias">
          <div className={s.cabeca}>
            <span className={s.tag}>Residências</span>
            <h2>Treine com a prova do programa que você quer</h2>
            <p>Cada questão traz o programa, a banca e o ano. Filtre e treine só com o estilo da sua prova.</p>
          </div>
          <div className={s.grade}>
            {RESIDENCIAS.map((a) => (
              <Cartao key={a.nome} alvo={a} />
            ))}
          </div>
        </section>

        <section className={`container ${s.secao}`}>
          <div className={s.cabeca}>
            <span className={s.tag}>Recursos</span>
            <h2>Tudo o que você precisa entre um plantão e outro</h2>
          </div>
          <div className={s.grade}>
            {RECURSOS.map(([titulo, texto]) => (
              <article key={titulo} className={s.recurso}>
                <h3>{titulo}</h3>
                <p>{texto}</p>
              </article>
            ))}
          </div>
        </section>

        <section className={`container ${s.secao}`} id="planos">
          <div className={s.cabeca}>
            <span className={s.tag}>Planos</span>
            <h2>Comece grátis. Assine quando quiser ir além.</h2>
          </div>
          <div className={s.planos}>
            <article className={s.plano}>
              <h3>Grátis</h3>
              <div className={s.preco}>R$ 0</div>
              <ul>
                <li>{LIMITE_GRATIS} questões por dia</li>
                <li>Todos os filtros</li>
                <li>Gabarito oficial e onde estudar</li>
              </ul>
              <Link className={`${s.btn} ${s.secundario}`} href="/questoes">
                Começar grátis
              </Link>
            </article>
            <article className={`${s.plano} ${s.destaque}`}>
              <h3>Premium Anual</h3>
              <div className={s.preco}>
                R$ 239,90 <small>/ano</small>
              </div>
              <ul>
                <li>Questões ilimitadas</li>
                <li>Simulados e revisão dos erros</li>
                <li>Equivale a R$ 19,99 por mês</li>
              </ul>
              <span className={s.embreve}>Assinatura em breve</span>
            </article>
            <article className={s.plano}>
              <h3>Premium Mensal</h3>
              <div className={s.preco}>
                R$ 29,90 <small>/mês</small>
              </div>
              <ul>
                <li>Questões ilimitadas</li>
                <li>Simulados e revisão dos erros</li>
                <li>Cancele quando quiser</li>
              </ul>
              <span className={s.embreve}>Assinatura em breve</span>
            </article>
          </div>
        </section>
      </main>

      <footer className={`container ${s.rodape}`}>
        <span className={s.logo}>
          <Logo />
        </span>
        <p className={s.pequeno}>Não somos afiliados a nenhuma banca nem programa de residência.</p>
      </footer>
    </>
  );
}
