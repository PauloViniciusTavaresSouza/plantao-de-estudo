# Plantão de Estudo · Base de conhecimento da IA

Este pacote é o ponto de partida do banco de questões e da base de documentos que a IA do site vai consultar. O assistente usa esse material para responder com base em leis, resoluções e comentários revisados, sempre citando a fonte, em vez de responder "de cabeça".

## O que tem aqui

| Pasta ou arquivo | O que é |
| --- | --- |
| `fontes/catalogo_fontes.csv` | 84 documentos cobrados em provas de enfermagem (leis, decretos, resoluções do Cofen, portarias, RDCs, NR 32, manuais), com link oficial, tema e prioridade |
| `fontes/referencias_bibliograficas.csv` | 44 livros e manuais de referência (enfermagem, saúde coletiva, saúde do trabalhador e português). Os livros têm direitos autorais: entram só como citação e resumo próprio. Os manuais do Ministério da Saúde são de acesso livre |
| `scripts/vincular_referencias.py` | Liga cada questão da EBSERH 2025 aos livros e manuais que embasam a resposta (campo `referencias`) |
| `esquemas/questao.schema.json` | Formato de cada questão: banca, ano, órgão, tipo, tema, dificuldade, alternativas, gabarito, comentário, fontes legais e status de revisão |
| `esquemas/trecho.schema.json` | Formato de cada trecho de documento que a IA busca e cita (um artigo de lei, ou uma seção de ficha) |
| `questoes/questoes_exemplo.json` | As 56 questões do protótipo no formato novo, 19 já ligadas à lei correspondente |
| `fichas/*.md` | Resumos próprios das 6 normas que mais caem: Lei 7.498, Lei 8.080, Lei 8.142, Lei 10.216, Código de Ética e Resolução 736/2024 |
| `scripts/baixar_fontes.py` | Baixa as normas do catálogo, tira o texto revogado e divide por artigo |
| `scripts/fichas_para_trechos.py` | Converte as fichas em trechos para a IA |
| `scripts/importar_prova.py` | Converte questões de prova em texto para o formato do banco |
| `scripts/validar.py` | Confere se tudo segue os esquemas e se as fontes citadas existem no catálogo |
| `GUIA_TECNICO.md` | Arquitetura da IA, banco de dados e rotina de atualização, para o programador |
| `provas/` | Manifestos da EBSERH Nacional 2025 (FGV): gabarito definitivo, anuladas, assunto e normas de cada questão, para os Grupos 4 (enfermeiro, todas as especialidades), 15 (técnico) e 16 (técnico, saúde do trabalhador) |
| `questoes/ebserh-2025-*.json` | As 180 questões dessas três provas com enunciado, alternativas, texto de apoio e gabarito, prontas para os filtros do app. Status: rascunho até a revisão |
| `fontes/ebserh_unidades.csv` | Hospitais e unidades da EBSERH com vagas, por macrorregião, conforme o edital |

## Filtros do app

Cada questão tem `categoria_profissional` (enfermeiro, técnico, auxiliar), `cargo`, `especialidades`, `unidades`, `banca`, `ano`, `orgao`, `tipo` (concurso ou residência), `grupo_prova`, `disciplina` e `tema`. Na EBSERH, a mesma prova vale para todas as especialidades e todas as unidades do grupo: por isso a questão guarda a lista inteira de especialidades e `unidades: ["Todas"]`. Assim, quem filtrar por "Enfermeiro · Terapia Intensiva" ou por um hospital específico encontra as questões certas.

## Como usar (em ordem)

```bash
pip install requests beautifulsoup4 pdfplumber jsonschema
python scripts/baixar_fontes.py          # baixa e divide as normas por artigo
python scripts/fichas_para_trechos.py    # transforma as fichas em trechos
python scripts/importar_prova.py prova.txt questoes/fgv-2024-x.json   # para cada prova
python scripts/validar.py                # confere tudo antes de subir para o banco
```

## Status de revisão

Nada aqui deve ir para o app sem revisão de um enfermeiro.

- **Questões:** todas entram como `rascunho`. Só viram `revisada` depois que vocês conferirem gabarito, comentário e fonte. Quando uma lei mudar, as questões afetadas passam para `desatualizada`.
- **Fichas:** a ficha da Resolução 736/2024 teve as etapas e os arts. 6º, 7º e 14 conferidos no PDF oficial do Cofen. As demais estão em rascunho e devem ser conferidas contra o texto oficial.
- **Catálogo:** os links foram montados a partir dos padrões dos sites oficiais. Rode o script e corrija os que falharem. Os itens sem link, como calendário vacinal e lista de notificação compulsória, mudam com frequência e precisam ser buscados na versão vigente.

## Cuidados legais

- Leis, decretos e resoluções oficiais não têm proteção de direito autoral no Brasil e podem entrar inteiros na base.
- Livros, a classificação NANDA-I e as diretrizes da AHA têm direitos autorais. Use só citações e resumos escritos por vocês.
- Questões de provas de bancas: consulte um advogado antes de usá-las no produto pago. Questões inéditas e comentários próprios são de vocês.
