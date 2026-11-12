# Guia técnico: IA do Plantão de Estudo

Objetivo: um assistente que explica questões e tira dúvidas de enfermagem **respondendo só com base na base de conhecimento**, citando a lei, o artigo ou a ficha usada, e dizendo "não encontrei" quando a base não cobre o assunto. A técnica é chamada de RAG, ou geração com busca: antes de responder, o sistema busca os trechos mais relevantes e entrega só eles ao modelo.

## 1. Fluxo

1. **Coleta:** `baixar_fontes.py` baixa as normas do catálogo e divide por artigo. `fichas_para_trechos.py` faz o mesmo com os resumos próprios.
2. **Validação:** `validar.py` confere esquemas, ids repetidos e fontes inexistentes.
3. **Carga:** os trechos entram na tabela `trechos`, com um vetor de embedding por trecho. As questões entram em `questoes`.
4. **Pergunta do usuário:** o sistema busca de 5 a 8 trechos parecidos, combinando busca por significado (vetor) e por palavra (texto), e filtrando os revogados.
5. **Resposta:** o modelo recebe a pergunta, os trechos e as regras do assistente, e responde citando o dispositivo.

## 2. Banco de dados sugerido (Postgres no Supabase, com pgvector)

```sql
create extension if not exists vector;

create table documentos (
  id text primary key,              -- igual ao catalogo_fontes.csv
  titulo text not null,
  tipo text, numero text, ano int, orgao text, tema text,
  prioridade text, url_oficial text, observacao text,
  atualizado_em timestamptz default now()
);

create table trechos (
  id text primary key,
  documento_id text references documentos(id),
  dispositivo text not null,
  texto text not null,
  tipo_conteudo text check (tipo_conteudo in ('texto_oficial','resumo_proprio')),
  situacao text check (situacao in ('vigente','alterado','revogado','verificar')),
  url_fonte text, data_coleta date, temas text[],
  embedding vector(1536),           -- ajustar ao tamanho do modelo de embedding escolhido
  busca tsvector generated always as (to_tsvector('portuguese', texto)) stored
);
create index on trechos using hnsw (embedding vector_cosine_ops);
create index on trechos using gin (busca);

create table questoes (
  id text primary key,
  origem text, banca text, ano int, orgao text, cargo text, tipo text,
  tema text, subtema text, dificuldade int,
  enunciado text not null, alternativas jsonb not null, gabarito text not null,
  anulada boolean default false, comentario text,
  data_referencia date, status_revisao text, revisor text
);

create table questao_fontes (
  questao_id text references questoes(id),
  documento_id text references documentos(id),
  dispositivo text
);
```

Só questões com `status_revisao = 'revisada'` e `anulada = false` aparecem para os alunos.

## 3. Regras do assistente (instruções de sistema)

Sugestão de base, para ajustar:

```
Você é o assistente de estudos do Plantão de Estudo, para profissionais de enfermagem que estudam para residência e concursos.
Responda SOMENTE com base nos trechos fornecidos em <fontes>. Cite o documento e o dispositivo (ex.: "Lei 7.498/1986, art. 11").
Se os trechos não bastarem para responder, diga que não encontrou na base e sugira consultar a fonte oficial. Não invente artigos, números ou prazos.
Se um trecho estiver com situação "verificar", avise que o conteúdo ainda está em revisão.
Explique de forma clara e curta, como um colega de plantão experiente.
Você é uma ferramenta de estudo: não dê orientação de conduta para um paciente real. Se a pergunta for sobre um caso real, oriente seguir o protocolo da instituição e a equipe responsável.
```

## 4. Recursos do app que usam essa base

- **Explicar a questão:** busca os trechos ligados em `questao_fontes`, mais os trechos parecidos com o enunciado.
- **Por que errei:** recebe a alternativa marcada e a correta e explica a diferença citando a fonte.
- **Gerar questão parecida:** usa os mesmos trechos para criar uma questão nova, que entra como `inedita` e `rascunho` até alguém revisar.
- **Alerta de legislação desatualizada:** quando um documento é atualizado, as questões ligadas a ele com `data_referencia` anterior viram `desatualizada` para revisão.

## 5. Atualização

- **Mensal:** rodar `baixar_fontes.py`, comparar com a versão anterior e revisar o que mudou.
- **A cada nova resolução do Cofen ou portaria relevante:** incluir no catálogo e rodar de novo.
- **Anual:** calendário de vacinação e lista de notificação compulsória.
- Guardar as versões anteriores dos trechos, para saber a partir de quando um gabarito mudou.

## 6. Problemas conhecidos

- **O site do Planalto pode bloquear acesso automático,** e bloqueou nos testes feitos a partir de um servidor. Alternativas oficiais: o portal de normas do Senado (normas.leg.br, que identifica as leis por URN do LexML) e a base de legislação da Câmara. Também dá para salvar a página no navegador e processar o arquivo local.
- **PDFs escaneados** não têm texto. Nesse caso, é preciso OCR, por exemplo com Tesseract em português, e uma revisão manual.
- **Leis que alteram outras** repetem números de artigo. O script marca as repetições com sufixo, mas vale conferir.

## 7. Qualidade da IA

Montar um conjunto de 50 perguntas de teste com a resposta esperada e a fonte certa, escritas por você. A cada mudança na base ou nas instruções, rodar as 50 e medir: quantas citam a fonte certa, quantas dizem "não encontrei" quando deveriam, e quantas inventam algo. Meta: zero invenções.
