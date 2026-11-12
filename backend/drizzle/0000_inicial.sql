CREATE TYPE "public"."categoria" AS ENUM('ENFERMEIRO', 'TECNICO', 'AUXILIAR', 'MULTIPROFISSIONAL');--> statement-breakpoint
CREATE TYPE "public"."origem_questao" AS ENUM('PROVA', 'INEDITA', 'EXEMPLO');--> statement-breakpoint
CREATE TYPE "public"."status_revisao" AS ENUM('RASCUNHO', 'REVISADA', 'DESATUALIZADA');--> statement-breakpoint
CREATE TYPE "public"."tipo_selecao" AS ENUM('CONCURSO', 'RESIDENCIA');--> statement-breakpoint
CREATE TABLE "alternativas" (
	"questao_id" text NOT NULL,
	"letra" text NOT NULL,
	"texto" text NOT NULL,
	CONSTRAINT "alternativas_questao_id_letra_pk" PRIMARY KEY("questao_id","letra")
);
--> statement-breakpoint
CREATE TABLE "areas_especialidade" (
	"id" text PRIMARY KEY NOT NULL,
	"nome" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "assuntos" (
	"id" text PRIMARY KEY NOT NULL,
	"nome" text NOT NULL,
	"tematica_id" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "bancas" (
	"id" text PRIMARY KEY NOT NULL,
	"nome" text NOT NULL,
	CONSTRAINT "bancas_nome_unique" UNIQUE("nome")
);
--> statement-breakpoint
CREATE TABLE "documentos" (
	"id" text PRIMARY KEY NOT NULL,
	"titulo" text NOT NULL,
	"tipo" text NOT NULL,
	"numero" text,
	"ano" integer,
	"orgao" text,
	"tema" text,
	"prioridade" text,
	"formato" text,
	"url_oficial" text,
	"observacao" text
);
--> statement-breakpoint
CREATE TABLE "especialidades" (
	"id" text PRIMARY KEY NOT NULL,
	"nome" text NOT NULL,
	"area_id" text,
	CONSTRAINT "especialidades_nome_unique" UNIQUE("nome")
);
--> statement-breakpoint
CREATE TABLE "orgaos" (
	"id" text PRIMARY KEY NOT NULL,
	"nome" text NOT NULL,
	"tipo" "tipo_selecao" NOT NULL,
	"esfera" text,
	"uf" text
);
--> statement-breakpoint
CREATE TABLE "prova_especialidades" (
	"prova_id" text NOT NULL,
	"especialidade_id" text NOT NULL,
	CONSTRAINT "prova_especialidades_prova_id_especialidade_id_pk" PRIMARY KEY("prova_id","especialidade_id")
);
--> statement-breakpoint
CREATE TABLE "provas" (
	"id" text PRIMARY KEY NOT NULL,
	"orgao_id" text NOT NULL,
	"banca_id" text NOT NULL,
	"ano" integer NOT NULL,
	"data_prova" date,
	"cargo" text NOT NULL,
	"categoria" "categoria" NOT NULL,
	"grupo" text,
	"tipo_prova" text,
	"localidade" text DEFAULT 'Nacional' NOT NULL,
	"url_prova" text,
	"url_gabarito" text,
	"gabarito_conferido" text
);
--> statement-breakpoint
CREATE TABLE "questao_assuntos" (
	"questao_id" text NOT NULL,
	"assunto_id" text NOT NULL,
	CONSTRAINT "questao_assuntos_questao_id_assunto_id_pk" PRIMARY KEY("questao_id","assunto_id")
);
--> statement-breakpoint
CREATE TABLE "questao_fontes" (
	"questao_id" text NOT NULL,
	"documento_id" text NOT NULL,
	"dispositivo" text,
	CONSTRAINT "questao_fontes_questao_id_documento_id_pk" PRIMARY KEY("questao_id","documento_id")
);
--> statement-breakpoint
CREATE TABLE "questao_referencias" (
	"questao_id" text NOT NULL,
	"referencia_id" text NOT NULL,
	"onde" text,
	CONSTRAINT "questao_referencias_questao_id_referencia_id_pk" PRIMARY KEY("questao_id","referencia_id")
);
--> statement-breakpoint
CREATE TABLE "questoes" (
	"id" text PRIMARY KEY NOT NULL,
	"origem" "origem_questao" NOT NULL,
	"prova_id" text,
	"numero" integer,
	"disciplina" text,
	"tema_base" text NOT NULL,
	"subtema" text,
	"dificuldade" integer DEFAULT 3 NOT NULL,
	"texto_apoio" text,
	"enunciado" text NOT NULL,
	"imagens" text[] DEFAULT '{}' NOT NULL,
	"gabarito" text,
	"anulada" boolean DEFAULT false NOT NULL,
	"comentario" text,
	"status_revisao" "status_revisao" DEFAULT 'RASCUNHO' NOT NULL,
	"revisor" text,
	"criada_em" timestamp DEFAULT now() NOT NULL,
	"atualizada_em" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "referencias" (
	"id" text PRIMARY KEY NOT NULL,
	"tipo" text NOT NULL,
	"autores" text NOT NULL,
	"titulo" text NOT NULL,
	"editora" text,
	"tema" text,
	"como_usar" text
);
--> statement-breakpoint
CREATE TABLE "tematicas" (
	"id" text PRIMARY KEY NOT NULL,
	"nome" text NOT NULL,
	"ordem" integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "trechos" (
	"id" text PRIMARY KEY NOT NULL,
	"documento_id" text NOT NULL,
	"dispositivo" text,
	"texto" text NOT NULL,
	"fonte" text
);
--> statement-breakpoint
ALTER TABLE "alternativas" ADD CONSTRAINT "alternativas_questao_id_questoes_id_fk" FOREIGN KEY ("questao_id") REFERENCES "public"."questoes"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "assuntos" ADD CONSTRAINT "assuntos_tematica_id_tematicas_id_fk" FOREIGN KEY ("tematica_id") REFERENCES "public"."tematicas"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "especialidades" ADD CONSTRAINT "especialidades_area_id_areas_especialidade_id_fk" FOREIGN KEY ("area_id") REFERENCES "public"."areas_especialidade"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prova_especialidades" ADD CONSTRAINT "prova_especialidades_prova_id_provas_id_fk" FOREIGN KEY ("prova_id") REFERENCES "public"."provas"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prova_especialidades" ADD CONSTRAINT "prova_especialidades_especialidade_id_especialidades_id_fk" FOREIGN KEY ("especialidade_id") REFERENCES "public"."especialidades"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "provas" ADD CONSTRAINT "provas_orgao_id_orgaos_id_fk" FOREIGN KEY ("orgao_id") REFERENCES "public"."orgaos"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "provas" ADD CONSTRAINT "provas_banca_id_bancas_id_fk" FOREIGN KEY ("banca_id") REFERENCES "public"."bancas"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "questao_assuntos" ADD CONSTRAINT "questao_assuntos_questao_id_questoes_id_fk" FOREIGN KEY ("questao_id") REFERENCES "public"."questoes"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "questao_assuntos" ADD CONSTRAINT "questao_assuntos_assunto_id_assuntos_id_fk" FOREIGN KEY ("assunto_id") REFERENCES "public"."assuntos"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "questao_fontes" ADD CONSTRAINT "questao_fontes_questao_id_questoes_id_fk" FOREIGN KEY ("questao_id") REFERENCES "public"."questoes"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "questao_fontes" ADD CONSTRAINT "questao_fontes_documento_id_documentos_id_fk" FOREIGN KEY ("documento_id") REFERENCES "public"."documentos"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "questao_referencias" ADD CONSTRAINT "questao_referencias_questao_id_questoes_id_fk" FOREIGN KEY ("questao_id") REFERENCES "public"."questoes"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "questao_referencias" ADD CONSTRAINT "questao_referencias_referencia_id_referencias_id_fk" FOREIGN KEY ("referencia_id") REFERENCES "public"."referencias"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "questoes" ADD CONSTRAINT "questoes_prova_id_provas_id_fk" FOREIGN KEY ("prova_id") REFERENCES "public"."provas"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "trechos" ADD CONSTRAINT "trechos_documento_id_documentos_id_fk" FOREIGN KEY ("documento_id") REFERENCES "public"."documentos"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "provas_orgao_ano_idx" ON "provas" USING btree ("orgao_id","ano");--> statement-breakpoint
CREATE INDEX "questao_assuntos_assunto_idx" ON "questao_assuntos" USING btree ("assunto_id");--> statement-breakpoint
CREATE INDEX "questoes_prova_idx" ON "questoes" USING btree ("prova_id","numero");