"""Monta a lista de referências bibliográficas e liga cada questão da EBSERH 2025 sem norma aos livros e manuais que embasam a resposta.

Uso:
    python scripts/vincular_referencias.py
"""
import csv, json, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVRO = "Livro com direitos autorais: citar e escrever resumo próprio, sem copiar trechos."
PUBLICO = "Publicação oficial de acesso livre: pode entrar na base de trechos da IA citando a fonte."

# id, tipo, autores, titulo, editora_ou_orgao, area, como_usar
REFERENCIAS = [
    # Fundamentos e semiologia
    ("ref-potter", "livro", "Potter; Perry; Stockert; Hall", "Fundamentos de Enfermagem", "Elsevier", "fund", LIVRO),
    ("ref-taylor", "livro", "Taylor; Lynn; Bartlett", "Fundamentos de Enfermagem: a arte e a ciência do cuidado de enfermagem", "Artmed", "fund", LIVRO),
    ("ref-posso", "livro", "Posso, M. B. S.", "Semiologia e Semiotécnica de Enfermagem", "Atheneu", "fund", LIVRO),
    ("ref-barros", "livro", "Barros, A. L. B. L. (org.)", "Anamnese e Exame Físico: avaliação diagnóstica de enfermagem no adulto", "Artmed", "fund", LIVRO),
    ("ref-porto", "livro", "Porto, C. C.", "Semiologia Médica", "Guanabara Koogan", "fund", LIVRO),
    ("ref-giovani", "livro", "Giovani, A. M. M.", "Enfermagem: cálculo e administração de medicamentos", "Scrinium", "calc", LIVRO),
    ("ref-clayton", "livro", "Clayton; Willihnganz", "Farmacologia na Prática de Enfermagem", "Elsevier", "calc", LIVRO),
    ("ref-nanda", "livro", "NANDA International", "Diagnósticos de Enfermagem da NANDA-I: definições e classificação", "Artmed", "fund", "Títulos e definições são protegidos e licenciados. Usar só com licença ou citar sem reproduzir."),
    # Clínica, cirurgia, urgência
    ("ref-brunner", "livro", "Hinkle; Cheever (Brunner & Suddarth)", "Tratado de Enfermagem Médico-Cirúrgica", "Guanabara Koogan", "clinica", LIVRO),
    ("ref-sobecc", "livro", "SOBECC", "Diretrizes de Práticas em Enfermagem Cirúrgica e Processamento de Produtos para a Saúde", "SOBECC / Manole", "clinica", LIVRO),
    ("ref-fermi", "livro", "Fermi, M. R. V.", "Diálise para Enfermagem: guia prático", "Guanabara Koogan", "clinica", LIVRO),
    ("ref-phtls", "livro", "NAEMT", "PHTLS: Atendimento Pré-hospitalar ao Traumatizado", "Artmed / Jones & Bartlett", "urg", LIVRO),
    ("ref-gold", "diretriz", "Global Initiative for Chronic Obstructive Lung Disease", "Relatório GOLD: estratégia global para DPOC", "GOLD", "clinica", "Relatório de acesso livre com direitos autorais: citar a edição e resumir."),
    ("ref-cdc-isolamento", "diretriz", "Siegel; Rhinehart; Jackson; Chiarello (CDC/HICPAC)", "Guideline for Isolation Precautions (2007, atualizado)", "CDC", "bio", PUBLICO),
    # Mulher, criança, idoso, mental
    ("ref-ricci", "livro", "Ricci, S. S.", "Enfermagem Materno-Neonatal e Saúde da Mulher", "Guanabara Koogan", "mulher", LIVRO),
    ("ref-rezende", "livro", "Montenegro; Rezende Filho", "Rezende Obstetrícia Fundamental", "Guanabara Koogan", "mulher", LIVRO),
    ("ref-wong", "livro", "Hockenberry; Wilson (Wong)", "Wong Fundamentos de Enfermagem Pediátrica", "Elsevier", "crianca", LIVRO),
    ("ref-eliopoulos", "livro", "Eliopoulos, C.", "Enfermagem Gerontológica", "Artmed", "idoso", LIVRO),
    ("ref-townsend", "livro", "Townsend, M. C.", "Enfermagem em Saúde Mental e Psiquiátrica", "Guanabara Koogan", "mental", LIVRO),
    # Gestão, ética, saúde coletiva
    ("ref-kurcgant", "livro", "Kurcgant, P. (coord.)", "Gerenciamento em Enfermagem", "Guanabara Koogan", "gestao", LIVRO),
    ("ref-motta", "livro", "Motta, A. L. C.", "Auditoria de Enfermagem nos Hospitais e Operadoras de Planos de Saúde", "Iátria", "gestao", LIVRO),
    ("ref-beauchamp", "livro", "Beauchamp; Childress", "Princípios de Ética Biomédica", "Loyola", "etica", LIVRO),
    ("ref-rouquayrol", "livro", "Rouquayrol; Gurgel", "Epidemiologia & Saúde", "MedBook", "vigilancia", LIVRO),
    ("ref-paim", "livro", "Paim; Almeida-Filho (org.)", "Saúde Coletiva: Teoria e Prática", "MedBook", "sus", LIVRO),
    ("ref-mendes-ras", "livro", "Mendes, E. V.", "As Redes de Atenção à Saúde", "OPAS", "sus", "Publicação da OPAS de acesso livre: citar e resumir."),
    # Saúde do trabalhador
    ("ref-mendes-patologia", "livro", "Mendes, R. (org.)", "Patologia do Trabalho", "Atheneu", "saude_trabalhador", LIVRO),
    ("ref-kendall", "livro", "Kendall; McCreary; Provance", "Músculos: provas e funções", "Manole", "saude_trabalhador", LIVRO),
    ("ref-ms-doencas-trabalho", "manual oficial", "Ministério da Saúde; OPAS", "Doenças Relacionadas ao Trabalho: manual de procedimentos para os serviços de saúde", "Ministério da Saúde", "saude_trabalhador", PUBLICO),
    ("ref-ms-ler-dort", "manual oficial", "Ministério da Saúde", "Dor relacionada ao trabalho: LER/DORT (Saúde do Trabalhador, Protocolos de Complexidade Diferenciada)", "Ministério da Saúde", "saude_trabalhador", PUBLICO),
    ("ref-ms-agrotoxicos", "manual oficial", "Ministério da Saúde", "Diretrizes Brasileiras para o Diagnóstico e Tratamento de Intoxicações por Agrotóxicos", "Ministério da Saúde", "saude_trabalhador", PUBLICO),
    # Manuais do Ministério da Saúde por linha de cuidado
    ("ref-cab-23", "manual oficial", "Ministério da Saúde", "Caderno de Atenção Básica nº 23: Saúde da criança, aleitamento materno e alimentação complementar", "Ministério da Saúde", "crianca", PUBLICO),
    ("ref-cab-13", "manual oficial", "Ministério da Saúde", "Caderno de Atenção Básica nº 13: Controle dos cânceres do colo do útero e da mama", "Ministério da Saúde", "mulher", PUBLICO),
    ("ref-cab-19", "manual oficial", "Ministério da Saúde", "Caderno de Atenção Básica nº 19: Envelhecimento e saúde da pessoa idosa", "Ministério da Saúde", "idoso", PUBLICO),
    ("ref-cab-38", "manual oficial", "Ministério da Saúde", "Caderno de Atenção Básica nº 38: Estratégias para o cuidado da pessoa com doença crônica, obesidade", "Ministério da Saúde", "clinica", PUBLICO),
    ("ref-pcdt-ist", "manual oficial", "Ministério da Saúde", "PCDT para Atenção Integral às Pessoas com Infecções Sexualmente Transmissíveis", "Ministério da Saúde", "clinica", PUBLICO),
    ("ref-plano-dant", "manual oficial", "Ministério da Saúde", "Plano de Ações Estratégicas para o Enfrentamento das Doenças Crônicas e Agravos Não Transmissíveis no Brasil 2021-2030", "Ministério da Saúde", "clinica", PUBLICO),
    ("ref-diretriz-parto", "manual oficial", "Ministério da Saúde; Conitec", "Diretrizes Nacionais de Assistência ao Parto Normal", "Ministério da Saúde", "mulher", PUBLICO),
    ("ref-pnaish", "manual oficial", "Ministério da Saúde", "Política Nacional de Atenção Integral à Saúde do Homem: princípios e diretrizes", "Ministério da Saúde", "clinica", PUBLICO),
    ("ref-anvisa-notivisa", "manual oficial", "Anvisa", "Notivisa: Sistema de Notificações em Vigilância Sanitária (orientações oficiais)", "Anvisa", "vigilancia", PUBLICO),
    # Língua Portuguesa
    ("ref-bechara", "livro", "Bechara, E.", "Moderna Gramática Portuguesa", "Nova Fronteira", "portugues", LIVRO),
    ("ref-cunha-cintra", "livro", "Cunha; Cintra", "Nova Gramática do Português Contemporâneo", "Lexikon", "portugues", LIVRO),
    ("ref-garcia", "livro", "Garcia, O. M.", "Comunicação em Prosa Moderna", "FGV Editora", "portugues", LIVRO),
    ("ref-koch", "livro", "Koch, I. V.", "A Coesão Textual", "Contexto", "portugues", LIVRO),
    ("ref-volp", "manual oficial", "Academia Brasileira de Letras", "Vocabulário Ortográfico da Língua Portuguesa (VOLP)", "ABL", "portugues", "Consulta oficial de grafia: citar."),
]

NOVAS_FONTES = [
    ["lei-8213-1991", "Planos de Benefícios da Previdência Social (definição de acidente de trabalho, arts. 19 a 21)", "lei", "8.213", "1991", "Presidência da República", "saude_trabalhador", "alta", "html", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm", "Cobrar arts. 19 a 23"],
    ["portaria-1999-2023", "Lista de Doenças Relacionadas ao Trabalho (LDRT)", "portaria", "1.999", "2023", "Ministério da Saúde", "saude_trabalhador", "alta", "html", "", "Altera a Portaria de Consolidação nº 5/2017; buscar no Saúde Legis"],
    ["decreto-1254-1994", "Promulga a Convenção 155 da OIT (segurança e saúde dos trabalhadores)", "decreto", "1.254", "1994", "Presidência da República", "saude_trabalhador", "media", "html", "https://www.planalto.gov.br/ccivil_03/decreto/1990-1994/d1254.htm", "Conferir o link"],
    ["nr-5", "NR 5: Comissão Interna de Prevenção de Acidentes e de Assédio (CIPA)", "norma regulamentadora", "5", "", "Ministério do Trabalho", "saude_trabalhador", "alta", "pdf", "", "Buscar o texto vigente na página de NRs do gov.br"],
    ["portaria-2048-2002", "Regulamento Técnico dos Sistemas Estaduais de Urgência e Emergência", "portaria", "2.048", "2002", "Ministério da Saúde", "urg", "alta", "html", "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2002/prt2048_05_11_2002.html", "Conferir o link"],
    ["res-cfm-1451-1995", "Definições de urgência e emergência e estrutura do pronto-socorro", "resolucao", "1.451", "1995", "Conselho Federal de Medicina", "urg", "media", "html", "", "Buscar no portal do CFM"],
    ["lei-9656-1998", "Planos e seguros privados de assistência à saúde (saúde suplementar)", "lei", "9.656", "1998", "Presidência da República", "sus", "media", "html", "https://www.planalto.gov.br/ccivil_03/leis/l9656.htm", ""],
    ["res-cofen-266-2001", "Atividades do enfermeiro auditor", "resolucao", "266", "2001", "Cofen", "gestao", "media", "html", "", "Buscar no portal do Cofen"],
    ["portaria-1944-2009", "Política Nacional de Atenção Integral à Saúde do Homem (PNAISH)", "portaria", "1.944", "2009", "Ministério da Saúde", "clinica", "media", "html", "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2009/prt1944_27_08_2009.html", "Consolidada na Portaria de Consolidação nº 2/2017"],
]

PT_TEXTO = ["ref-garcia", "ref-koch"]
PT_GRAM = ["ref-bechara", "ref-cunha-cintra"]

# (referências, normas a acrescentar) por questão
G4 = {
    1: (PT_TEXTO, []), 2: (PT_TEXTO, []), 3: (PT_TEXTO, []), 4: (PT_TEXTO, []),
    5: (PT_GRAM, []), 6: (PT_GRAM, []), 7: (PT_TEXTO, []), 8: (PT_GRAM, []),
    9: (PT_TEXTO, []), 10: (PT_GRAM + PT_TEXTO, []),
    18: (["ref-paim"], []),
    20: (["ref-kurcgant"], []),
    21: (["ref-paim"], ["lei-9656-1998", "lei-8080-1990"]),
    22: (["ref-beauchamp"], []),
    28: (["ref-mendes-ras"], ["portaria-4279-2010"]),
    37: (["ref-ricci", "ref-rezende", "ref-diretriz-parto"], []),
    38: (["ref-cab-23", "ref-ricci"], []),
    40: (["ref-rouquayrol"], ["guia-vigilancia-saude"]),
    42: (["ref-motta", "ref-kurcgant"], ["res-cofen-266-2001"]),
    43: (["ref-phtls", "ref-brunner"], []),
    46: (["ref-fermi", "ref-brunner"], []),
    47: (["ref-brunner"], ["diretriz-rcp-aha"]),
    53: (["ref-sobecc", "ref-brunner"], []),
    54: (["ref-barros", "ref-potter", "ref-posso"], []),
    55: (["ref-fermi", "ref-brunner"], []),
    57: (["ref-cdc-isolamento"], ["anvisa-caderno-iras-2017"]),
    59: (["ref-eliopoulos", "ref-cab-19"], []),
    60: (["ref-barros", "ref-porto"], []),
}
COMUM_TEC = {  # questões 1 a 30, iguais nos Grupos 15 e 16
    1: (PT_TEXTO, []), 2: (PT_TEXTO, []), 3: (PT_GRAM, []), 4: (PT_TEXTO, []),
    5: (PT_GRAM, []), 6: (PT_GRAM, []), 7: (PT_GRAM, []), 8: (PT_GRAM, []),
    9: (PT_GRAM, []), 10: (["ref-volp", "ref-bechara"], []),
    25: (["ref-anvisa-notivisa", "ref-rouquayrol"], []),
}
G15 = {**COMUM_TEC,
    33: (["ref-cab-13", "ref-ricci"], ["calendario-vacinacao"]),
    34: (["ref-pcdt-ist", "ref-brunner"], []),
    37: (["ref-pnaish", "ref-brunner"], ["portaria-1944-2009"]),
    38: (["ref-cab-23", "ref-ricci"], []),
    39: (["ref-mendes-patologia", "ref-ms-doencas-trabalho"], ["lei-8213-1991"]),
    43: (["ref-plano-dant", "ref-brunner"], []),
    45: (["ref-phtls", "ref-brunner"], []),
    46: (["ref-brunner"], ["portaria-2048-2002", "res-cfm-1451-1995"]),
    49: (["ref-cab-38", "ref-brunner"], []),
    54: (["ref-potter", "ref-posso"], []),
    56: (["ref-phtls", "ref-brunner"], []),
    57: (["ref-brunner", "ref-gold"], []),
    59: (["ref-potter", "ref-taylor"], []),
    60: (["ref-sobecc", "ref-brunner"], []),
}
G16 = {**COMUM_TEC,
    31: (["ref-giovani", "ref-potter"], []),
    33: (["ref-ms-agrotoxicos", "ref-mendes-patologia"], []),
    36: (["ref-rouquayrol", "ref-mendes-patologia"], ["guia-vigilancia-saude"]),
    37: (["ref-kendall", "ref-barros"], []),
    38: (["ref-ms-ler-dort", "ref-mendes-patologia"], ["portaria-1999-2023"]),
    45: (["ref-mendes-patologia"], ["lei-8080-1990", "res-cns-453-2012"]),
    47: (["ref-mendes-patologia"], ["decreto-1254-1994"]),
    49: (["ref-mendes-patologia"], ["nr-5"]),
    50: (["ref-giovani", "ref-potter"], []),
    52: (["ref-ms-doencas-trabalho", "ref-townsend"], ["portaria-1999-2023"]),
    53: (["ref-potter", "ref-brunner"], []),
    58: (["ref-giovani", "ref-clayton"], []),
}
EXTRAS_COM_NORMA = {  # questões que já tinham norma e ganham também um livro de apoio
    "g16": {56: ["ref-ms-doencas-trabalho", "ref-mendes-patologia"], 59: ["ref-brunner"], 55: ["ref-brunner"],
            57: ["ref-barros"], 35: ["ref-ms-ler-dort"], 41: ["ref-mendes-patologia"]},
    "g15": {48: ["ref-potter", "ref-posso"], 55: ["ref-brunner"], 58: ["ref-giovani", "ref-potter"],
            44: ["ref-brunner"], 36: ["ref-potter"], 41: ["ref-mendes-patologia"], 51: ["ref-sobecc"],
            52: ["ref-sobecc"], 53: ["ref-sobecc"], 42: ["ref-brunner"], 47: ["ref-brunner"], 50: ["ref-phtls"]},
}

ARQS = [("ebserh-2025-enfermeiro-grupo4-tipo1.json", "g4", G4),
        ("ebserh-2025-tecnico-grupo15-tipo1.json", "g15", G15),
        ("ebserh-2025-tecnico-saude-trabalhador-grupo16-tipo1.json", "g16", G16)]


def main():
    # 1. lista de referências
    with open(os.path.join(RAIZ, "fontes", "referencias_bibliograficas.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "tipo", "autores", "titulo", "editora_ou_orgao", "tema", "como_usar"])
        w.writerows(REFERENCIAS)
    ids_ref = {r[0] for r in REFERENCIAS}
    # 2. novas normas no catálogo
    cat = os.path.join(RAIZ, "fontes", "catalogo_fontes.csv")
    with open(cat, encoding="utf-8") as f:
        existentes = {l["id"] for l in csv.DictReader(f)}
    with open(cat, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows([r for r in NOVAS_FONTES if r[0] not in existentes])
    # 3. esquema: campo referencias
    sp = os.path.join(RAIZ, "esquemas", "questao.schema.json")
    s = json.load(open(sp, encoding="utf-8"))
    s["properties"]["referencias"] = {
        "type": "array",
        "description": "Livros e manuais que embasam a resposta (ids de fontes/referencias_bibliograficas.csv)",
        "items": {"type": "object", "required": ["referencia_id"], "additionalProperties": False,
                  "properties": {"referencia_id": {"type": "string"},
                                 "onde": {"type": ["string", "null"], "description": "Capítulo ou seção, preenchido na revisão"}}},
    }
    json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    # 4. questões
    resumo = []
    for nome, sigla, mapa in ARQS:
        p = os.path.join(RAIZ, "questoes", nome)
        qs = json.load(open(p, encoding="utf-8"))
        for q in qs:
            refs, normas = mapa.get(q["numero"], ([], []))
            refs = refs + EXTRAS_COM_NORMA.get(sigla, {}).get(q["numero"], [])
            assert all(r in ids_ref for r in refs), (nome, q["numero"], refs)
            q["referencias"] = [{"referencia_id": r, "onde": None} for r in dict.fromkeys(refs)]
            ja = {f["documento_id"] for f in q["fontes"]}
            q["fontes"] += [{"documento_id": d, "dispositivo": None} for d in normas if d not in ja]
        json.dump(qs, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        sem = [q["numero"] for q in qs if not q["fontes"] and not q["referencias"]]
        resumo.append((nome, sum(bool(q["referencias"]) for q in qs), sum(bool(q["fontes"]) for q in qs), sem))
    for r in resumo:
        print(r)


if __name__ == "__main__":
    main()
