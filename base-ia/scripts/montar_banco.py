"""Junta o texto extraído dos PDFs com os manifestos (gabarito, tema, normas) e gera os arquivos do banco."""
import csv, json, re, sys, os

BASE = sys.argv[1]  # pasta base-ia
AQUI = os.path.dirname(os.path.abspath(__file__))

NOVAS_FONTES = [
    ["portaria-230-2023", "Programa Nacional de Equidade de Gênero, Raça e Valorização das Trabalhadoras no SUS", "portaria", "230", "2023", "Ministério da Saúde", "sus", "media", "html", "", "Buscar no Saúde Legis (bvsms.saude.gov.br)"],
    ["res-cns-453-2012", "Diretrizes para os Conselhos de Saúde", "resolucao", "453", "2012", "Conselho Nacional de Saúde", "sus", "alta", "html", "https://bvsms.saude.gov.br/bvs/saudelegis/cns/2012/res0453_10_05_2012.html", "Conferir o link"],
    ["rdc-63-2011", "RDC 63/2011: Boas Práticas de Funcionamento dos serviços de saúde", "rdc", "63", "2011", "Anvisa", "seguranca", "alta", "html", "https://bvsms.saude.gov.br/bvs/saudelegis/anvisa/2011/rdc0063_25_11_2011.html", "Conferir o link"],
    ["portaria-4279-2010", "Diretrizes para a organização da Rede de Atenção à Saúde (RAS)", "portaria", "4.279", "2010", "Ministério da Saúde", "sus", "alta", "html", "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2010/prt4279_30_12_2010.html", "Consolidada na Portaria de Consolidação nº 3/2017"],
    ["portaria-1526-2023", "Portaria GM/MS 1.526/2023: altera as Portarias de Consolidação 2, 3 e 6 (Política Nacional de Atenção Integral à Saúde da Pessoa com Deficiência)", "portaria", "1.526", "2023", "Ministério da Saúde", "sus", "media", "html", "", "Buscar no Saúde Legis e conferir o tema"],
    ["res-cns-588-2018", "Política Nacional de Vigilância em Saúde (PNVS)", "resolucao", "588", "2018", "Conselho Nacional de Saúde", "vigilancia", "alta", "pdf", "https://conselho.saude.gov.br/resolucoes/2018/Reso588.pdf", "Conferir o link"],
    ["portaria-1996-2007", "Política Nacional de Educação Permanente em Saúde (PNEPS)", "portaria", "1.996", "2007", "Ministério da Saúde", "gestao", "media", "html", "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2007/prt1996_20_08_2007.html", "Conferir alterações posteriores"],
    ["portaria-502-2023", "Programa Nacional de Controle do Tabagismo (PNCT)", "portaria", "502", "2023", "Ministério da Saúde", "sus", "media", "html", "", "Buscar no Saúde Legis"],
    ["decreto-7602-2011", "Política Nacional de Segurança e Saúde no Trabalho (PNSST)", "decreto", "7.602", "2011", "Presidência da República", "saude_trabalhador", "alta", "html", "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/decreto/d7602.htm", ""],
    ["clt", "Consolidação das Leis do Trabalho (Decreto-Lei 5.452/1943), capítulo de segurança e medicina do trabalho", "decreto-lei", "5.452", "1943", "Presidência da República", "saude_trabalhador", "media", "html", "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm", "Cobrar só os arts. 154 a 201"],
    ["nr-4", "NR 4: Serviços Especializados em Segurança e Medicina do Trabalho (SESMT)", "norma regulamentadora", "4", "", "Ministério do Trabalho", "saude_trabalhador", "alta", "pdf", "", "Buscar o texto vigente na página de NRs do gov.br"],
    ["nr-6", "NR 6: Equipamento de Proteção Individual (EPI)", "norma regulamentadora", "6", "", "Ministério do Trabalho", "saude_trabalhador", "alta", "pdf", "", "Buscar o texto vigente na página de NRs do gov.br"],
    ["nr-9", "NR 9: Avaliação e controle das exposições ocupacionais a agentes físicos, químicos e biológicos", "norma regulamentadora", "9", "", "Ministério do Trabalho", "saude_trabalhador", "alta", "pdf", "", "Texto de 2020 substituiu o PPRA pelo PGR (NR 1); conferir a versão vigente"],
    ["nr-17", "NR 17: Ergonomia", "norma regulamentadora", "17", "", "Ministério do Trabalho", "saude_trabalhador", "alta", "pdf", "", "Buscar o texto vigente na página de NRs do gov.br"],
    ["nho-fundacentro", "Normas de Higiene Ocupacional (NHO) da Fundacentro", "norma tecnica", "", "", "Fundacentro", "saude_trabalhador", "baixa", "pdf", "", "Conferir direitos de uso antes de incluir o texto"],
    ["diretrizes-has-2020", "Diretrizes Brasileiras de Hipertensão Arterial 2020", "diretriz", "", "2020", "Sociedade Brasileira de Cardiologia", "clinica", "alta", "pdf", "", "Material com direitos autorais: usar só resumo próprio e citar a edição"],
]

# tema, assunto, normas. 1 a 30 valem para os Grupos 15 e 16.
T_BASICO = {
    11: ("legislacao_institucional", "Regulamento de Pessoal da Ebserh", ["ebserh-regulamento-pessoal"]),
    12: ("legislacao_institucional", "Lei 12.550/2011: criação e regras da Ebserh", ["lei-12550-2011"]),
    13: ("legislacao_institucional", "Estatuto Social da Ebserh (Decreto 7.661/2011)", ["ebserh-estatuto-social"]),
    14: ("legislacao_institucional", "Conselho Consultivo da Ebserh", ["ebserh-estatuto-social"]),
    15: ("legislacao_institucional", "Código de Ética e Conduta da Ebserh", ["ebserh-codigo-etica"]),
    16: ("sus", "Programa de Equidade de Gênero e Raça no SUS", ["portaria-230-2023"]),
    17: ("sus", "Conselhos de Saúde", ["res-cns-453-2012", "lei-8142-1990"]),
    18: ("seguranca", "Boas Práticas de Funcionamento dos serviços de saúde", ["rdc-63-2011"]),
    19: ("sus", "Estratégia Saúde da Família", ["portaria-2436-2017"]),
    20: ("sus", "Política Nacional de Atenção Básica", ["portaria-2436-2017"]),
    21: ("sus", "Financiamento: LC 141/2012", ["lc-141-2012"]),
    22: ("sus", "Redes de Atenção à Saúde", ["portaria-4279-2010"]),
    23: ("sus", "Portaria GM/MS 1.526/2023", ["portaria-1526-2023"]),
    24: ("vigilancia", "Política Nacional de Vigilância em Saúde", ["res-cns-588-2018"]),
    25: ("vigilancia", "Vigilância de eventos adversos de produtos (Notivisa)", []),
    26: ("gestao", "Educação Permanente em Saúde", ["portaria-1996-2007"]),
    27: ("sus", "Decreto 7.508/2011", ["decreto-7508-2011"]),
    28: ("sus", "Seguridade social na Constituição", ["cf-1988-saude"]),
    29: ("seguranca", "Boas Práticas de Funcionamento (RDC 63)", ["rdc-63-2011"]),
    30: ("sus", "Carta dos direitos e deveres da pessoa usuária", ["res-cns-553-2017"]),
}
T_G15 = {
    31: ("etica", "Lei do exercício profissional", ["lei-7498-1986", "decreto-94406-1987"]),
    32: ("etica", "Código de Ética dos Profissionais de Enfermagem", ["res-cofen-564-2017"]),
    33: ("mulher", "HPV e câncer do colo do útero", []),
    34: ("clinica", "Infecções sexualmente transmissíveis", []),
    35: ("crianca", "Acidentes e violências na infância e adolescência", ["lei-8069-1990"]),
    36: ("imunizacao", "Sala de vacina e caderneta vacinal", ["manual-vacinacao", "calendario-vacinacao"]),
    37: ("clinica", "Saúde do homem: câncer de pênis", []),
    38: ("mulher", "Amamentação: pega correta", []),
    39: ("saude_trabalhador", "Acidentes de trabalho", []),
    40: ("vigilancia", "Notificação compulsória (Sinan)", ["lista-notificacao-compulsoria"]),
    41: ("saude_trabalhador", "Ergonomia", ["nr-17"]),
    42: ("vigilancia", "Hanseníase e tuberculose", ["guia-vigilancia-saude"]),
    43: ("clinica", "Doenças crônicas não transmissíveis", []),
    44: ("urg", "Diretrizes de RCP", ["diretriz-rcp-aha"]),
    45: ("urg", "Choque hipovolêmico", []),
    46: ("urg", "Urgência, emergência e pronto-socorro", []),
    47: ("vigilancia", "Dengue e arboviroses", ["guia-vigilancia-saude"]),
    48: ("fund", "Aferição da pressão arterial", ["diretrizes-has-2020"]),
    49: ("clinica", "Obesidade", []),
    50: ("urg", "Acidentes com animais peçonhentos", ["guia-vigilancia-saude"]),
    51: ("bio", "Classificação de produtos para saúde (Spaulding)", ["rdc-15-2012"]),
    52: ("bio", "Níveis de desinfecção", ["rdc-15-2012"]),
    53: ("bio", "Processamento de produtos para saúde (RDC 15/2012)", ["rdc-15-2012"]),
    54: ("fund", "Temperatura corporal", []),
    55: ("bio", "Precauções para tuberculose", ["anvisa-caderno-iras-2017"]),
    56: ("urg", "Primeiros socorros em acidentes", []),
    57: ("clinica", "Oxigenoterapia no paciente com DPOC", []),
    58: ("seguranca", "Medicação intravenosa em bolus", ["portaria-529-2013"]),
    59: ("fund", "Coleta de urina de 24 horas", []),
    60: ("clinica", "Cuidados perioperatórios", []),
}
T_G16 = {
    31: ("fund", "Preparo de medicamento em frasco-ampola", []),
    32: ("etica", "Código de Ética dos Profissionais de Enfermagem", ["res-cofen-564-2017"]),
    33: ("vigilancia", "Vigilância em saúde ambiental", []),
    34: ("sus", "Programa Nacional de Controle do Tabagismo", ["portaria-502-2023"]),
    35: ("saude_trabalhador", "Ergonomia e postura", ["nr-17"]),
    36: ("vigilancia", "Desastres e exposição a rejeitos de mineração", []),
    37: ("saude_trabalhador", "Avaliação da força muscular", []),
    38: ("saude_trabalhador", "LER/DORT", []),
    39: ("saude_trabalhador", "Doenças infectocontagiosas no trabalho", ["nr-32"]),
    40: ("saude_trabalhador", "Condições ambientais de trabalho", ["nr-17"]),
    41: ("saude_trabalhador", "NR 4: SESMT", ["nr-4"]),
    42: ("saude_trabalhador", "NR 6: EPI", ["nr-6"]),
    43: ("saude_trabalhador", "CLT: segurança e medicina do trabalho", ["clt"]),
    44: ("saude_trabalhador", "NR 9: exposições ocupacionais", ["nr-9"]),
    45: ("saude_trabalhador", "Controle social em saúde do trabalhador (Cisttão/CNS)", []),
    46: ("saude_trabalhador", "NR 9 e PPRA", ["nr-9"]),
    47: ("saude_trabalhador", "Organização Internacional do Trabalho", []),
    48: ("saude_trabalhador", "Normas de Higiene Ocupacional da Fundacentro", ["nho-fundacentro"]),
    49: ("saude_trabalhador", "Prevenção de acidentes", []),
    50: ("fund", "Administração intramuscular de dipirona", []),
    51: ("saude_trabalhador", "Política Nacional de Segurança e Saúde no Trabalho", ["decreto-7602-2011"]),
    52: ("mental", "Transtornos mentais relacionados ao trabalho", []),
    53: ("clinica", "Desidratação", []),
    54: ("saude_trabalhador", "NR 32: prevenção de riscos", ["nr-32"]),
    55: ("imunizacao", "Ferimento e profilaxia do tétano", ["calendario-vacinacao"]),
    56: ("saude_trabalhador", "Dermatoses ocupacionais", ["lista-notificacao-compulsoria"]),
    57: ("fund", "Pressão arterial", ["diretrizes-has-2020"]),
    58: ("calc", "Cálculo e mistura de insulinas", []),
    59: ("bio", "Exposição a material biológico", ["pcdt-pep", "nr-32"]),
    60: ("vigilancia", "Febre após viagem: doenças de notificação", ["guia-vigilancia-saude"]),
}

def disciplina(n):
    return ("Língua Portuguesa" if n <= 10 else "Legislação EBSERH" if n <= 15
            else "Políticas Públicas de Saúde e Educação" if n <= 30 else "Conhecimentos Específicos")

def limpar(t):
    return re.sub(r"\s*Realiz\s*zação\s*$", "", t).strip()

PROVAS = [
    ("ebserh-2025-enfermeiro-grupo4-tipo1.json", "grupo4_parsed.json", "g4", None),
    ("ebserh-2025-tecnico-grupo15-tipo1.json", "grupo15_parsed.json", "g15", {**T_BASICO, **T_G15}),
    ("ebserh-2025-tecnico-saude-trabalhador-grupo16-tipo1.json", "grupo16_parsed.json", "g16", {**T_BASICO, **T_G16}),
]

def main():
    # 1. catálogo
    cat = os.path.join(BASE, "fontes", "catalogo_fontes.csv")
    with open(cat, encoding="utf-8") as f:
        existentes = {l["id"] for l in csv.DictReader(f)}
    novas = [r for r in NOVAS_FONTES if r[0] not in existentes]
    with open(cat, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(novas)
    # 2. esquema: tema saude_trabalhador
    sp = os.path.join(BASE, "esquemas", "questao.schema.json")
    s = json.load(open(sp, encoding="utf-8"))
    if "saude_trabalhador" not in s["properties"]["tema"]["enum"]:
        s["properties"]["tema"]["enum"].insert(-1, "saude_trabalhador")
    if None not in s["properties"]["gabarito"]["enum"]:
        s["properties"]["gabarito"]["enum"].append(None)
        s["properties"]["gabarito"]["description"] = "null só quando a questão foi anulada sem gabarito"
    json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    resumo = []
    for man_nome, parsed_nome, sigla, mapa in PROVAS:
        mp = os.path.join(BASE, "provas", man_nome)
        man = json.load(open(mp, encoding="utf-8"))
        texto = {q["numero"]: q for q in json.load(open(os.path.join(AQUI, parsed_nome), encoding="utf-8"))}
        saida = []
        for mq in man["questoes"]:
            n = mq["numero"]
            if mapa and n in mapa:
                mq["tema"], mq["assunto"], mq["normas"] = mapa[n]
            mq["disciplina"] = mq.get("disciplina") or disciplina(n)
            if not mq.get("tema"):
                mq["tema"] = "portugues" if n <= 10 else "outros"
            t = texto[n]
            alts = [{"letra": a["letra"], "texto": limpar(a["texto"])} for a in t["alternativas"]]
            anulada = bool(mq.get("anulada")) or mq.get("gabarito") not in list("ABCDE")
            saida.append({
                "id": f"fgv-2025-ebserh-{sigla}-q{n:03d}",
                "origem": "prova", "banca": "FGV", "ano": man["ano"], "orgao": man["orgao"],
                "cargo": man["cargo"], "categoria_profissional": man["categoria_profissional"],
                "especialidades": man["especialidades"], "unidades": man["unidades"],
                "grupo_prova": man["grupo_prova"], "tipo_prova": man["tipo_prova"], "numero": n,
                "disciplina": mq["disciplina"], "tipo": "concurso", "tema": mq["tema"],
                "subtema": mq.get("assunto"), "dificuldade": 3,
                "texto_apoio": t.get("texto_apoio"),
                "enunciado": limpar(t["enunciado"]), "alternativas": alts,
                "gabarito": mq["gabarito"] if mq.get("gabarito") in list("ABCDE") else None,
                "anulada": anulada, "comentario": None,
                "fontes": [{"documento_id": d, "dispositivo": None} for d in mq.get("normas", [])],
                "data_referencia": man["data_prova"], "status_revisao": "rascunho", "revisor": None,
            })
            if anulada:
                mq["anulada"] = True
        man["status"] = "texto das questões importado (rascunho, falta revisão)"
        man["arquivo_questoes"] = f"questoes/{man_nome}"
        json.dump(man, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        json.dump(saida, open(os.path.join(BASE, "questoes", man_nome), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        resumo.append((man_nome, len(saida), [q["numero"] for q in saida if q["anulada"]], sum(bool(q["fontes"]) for q in saida)))
    print("novas fontes:", len(novas))
    for r in resumo:
        print(r)

main()
