# Plantão de Estudo

Site e app de estudo para concursos e residências de enfermagem: questões de provas reais com gabarito oficial, filtros por órgão, banca, especialidade, localidade e temática, e uma base de leis e livros que respalda cada resposta.

## Pastas

| Pasta | O que é |
| --- | --- |
| `frontend/` | Next.js 16 + TypeScript (App Router), estilos com CSS Modules |
| `backend/` | NestJS 12 + Drizzle ORM (API das questões e dos filtros) |
| `base-ia/` | Banco de questões, provas, normas, livros e temáticas em arquivos (a fonte dos dados) |
| `docker-compose.yml` | Postgres 16 com pgvector |

## O que instalar

- Node.js 22 ou mais novo
- pnpm (`npm i -g pnpm`)
- Docker Desktop (para o Postgres)

## Rodar pela primeira vez

```bash
# 1. Banco
docker compose up -d

# 2. API (porta 3001)
cd backend
cp .env.example .env
pnpm install
pnpm db:migrate     # cria as tabelas
pnpm seed           # importa a pasta base-ia para o banco
pnpm start:dev

# 3. Site (porta 3000), em outro terminal
cd frontend
pnpm install
pnpm dev
```

Abra http://localhost:3000. A tela de questões fica em http://localhost:3000/questoes.

No Windows, troque `cp` por `copy`.

## Dia a dia

| Quero | Comando (dentro de `backend/`) |
| --- | --- |
| Atualizar o banco depois de mexer em `base-ia/` | `pnpm seed` (pode rodar quantas vezes quiser) |
| Mudar uma tabela | edite `src/db/schema.ts`, depois `pnpm db:generate` e `pnpm db:migrate` |
| Ver as tabelas no navegador | `pnpm db:studio` |
| Rodar os testes | `pnpm test` e `pnpm test:e2e` |

## API

| Rota | O que faz |
| --- | --- |
| `GET /saude` | Confere se a API está no ar |
| `GET /filtros` | Opções de cada filtro, com o número de questões |
| `GET /questoes` | Lista questões. Filtros: `tipo`, `orgao`, `banca`, `ano`, `categoria`, `area`, `uf`, `tematica`, `assunto`, `pagina`, `limite`, `ordem`, `semente` |
| `GET /questoes/:id` | Uma questão (sem o gabarito) |
| `POST /questoes/:id/resposta` | Recebe `{ "letra": "B" }` e devolve se acertou, o gabarito e onde estudar |
| `GET /imagens/arquivo.png` | Figuras das questões |

O gabarito nunca vai na listagem: o site só o recebe depois de responder.

## Como entram provas novas

1. A prova e o gabarito oficial viram arquivos em `base-ia/provas/` e `base-ia/questoes/` (veja `base-ia/LEIA-ME.md`).
2. Se o órgão for novo, acrescente uma linha em `ORGAOS`, no arquivo `backend/src/db/seed.ts`.
3. Rode `pnpm seed`.

## Próximos passos

- Login, perfil e plano (o limite de 5 questões por dia hoje fica só no navegador)
- Pagamento da assinatura
- Simulados, revisão dos erros e desempenho por temática
- Comentário de cada questão e assistente de IA que cita a lei (usando `trechos` e pgvector)

## Cuidados

- Todas as questões estão como **rascunho**: tema, assunto e fontes precisam da revisão de um enfermeiro.
- Leis e normas oficiais podem entrar inteiras na base. Livros têm direitos autorais: só citação e resumo próprio.
- Antes de vender acesso a questões de bancas, consulte um advogado.
