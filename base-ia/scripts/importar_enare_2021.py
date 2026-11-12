"""Importa o ENARE 2021/2022 (Instituto AOCP), prova de Enfermagem Tipo 01.

Uso:
    python scripts/importar_enare_2021.py <questoes_extraidas.json> <gabarito_definitivo.txt>
"""
import csv, json, os, re, shutil, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NOVAS_FONTES = [
    ["lei-9782-1999", "Sistema Nacional de Vigilância Sanitária e criação da Anvisa", "lei", "9.782", "1999", "Presidência da República", "vigilancia", "alta", "html", "https://www.planalto.gov.br/ccivil_03/leis/l9782.htm", ""],
    ["portaria-2836-2011", "Política Nacional de Saúde Integral de Lésbicas, Gays, Bissexuais, Travestis e Transexuais", "portaria", "2.836", "2011", "Ministério da Saúde", "sus", "media", "html", "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2011/prt2836_01_12_2011.html", "Consolidada na Portaria de Consolidação nº 2/2017"],
    ["res-cofen-358-2009", "Processo de Enfermagem (revogada)", "resolucao", "358", "2009", "Cofen", "fund", "media", "html", "", "Revogada pela Resolução Cofen 736/2024. Serve só para entender questões antigas"],
    ["portaria-158-2016", "Regulamento técnico de procedimentos hemoterápicos", "portaria", "158", "2016", "Ministério da Saúde", "clinica", "alta", "html", "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2016/prt0158_04_02_2016.html", "Consolidada na Portaria de Consolidação nº 5/2017"],
]

PE = ["res-cofen-736-2024", "res-cofen-358-2009"]
# numero: (tema, subtema, fontes, referencias)
MAPA = {
    1: ("sus", "História das políticas de saúde no Brasil", [], ["ref-paim"]),
    2: ("sus", "Movimento sanitário", [], ["ref-paim"]),
    3: ("sus", "8ª Conferência Nacional de Saúde", [], ["ref-paim"]),
    4: ("sus", "Instâncias de pactuação do SUS (CIB e CIT)", ["lei-8080-1990", "decreto-7508-2011"], []),
    5: ("sus", "Participação social: Lei 8.142/1990", ["lei-8142-1990", "lei-8080-1990"], []),
    6: ("sus", "Contrato Organizativo da Ação Pública (COAP)", ["decreto-7508-2011"], []),
    7: ("sus", "Regionalização", ["decreto-7508-2011"], []),
    8: ("sus", "Redes de Atenção à Saúde", ["portaria-4279-2010"], ["ref-mendes-ras"]),
    9: ("vigilancia", "Indicadores: incidência", [], ["ref-rouquayrol"]),
    10: ("vigilancia", "Rede Cievs", ["guia-vigilancia-saude"], ["ref-rouquayrol"]),
    11: ("vigilancia", "Competências da Anvisa", ["lei-9782-1999"], []),
    12: ("sus", "História natural da doença (Leavell e Clark)", [], ["ref-rouquayrol"]),
    13: ("sus", "Política Nacional de Atenção Básica", ["portaria-2436-2017"], []),
    14: ("gestao", "Educação permanente em saúde", ["portaria-1996-2007"], []),
    15: ("mental", "Trabalho interdisciplinar em saúde mental", ["portaria-3088-2011"], ["ref-townsend"]),
    16: ("sus", "Política de Saúde Integral LGBT", ["portaria-2836-2011"], []),
    17: ("gestao", "Avaliação em saúde: estrutura, processo e resultado", [], ["ref-kurcgant"]),
    18: ("seguranca", "Classificação Internacional de Segurança do Paciente (OMS)", ["portaria-529-2013", "rdc-36-2013"], []),
    19: ("sus", "Modelos assistenciais", [], ["ref-paim"]),
    20: ("etica", "Princípios da bioética", [], ["ref-beauchamp"]),
    21: ("fund", "Processo de enfermagem: diagnóstico", PE, ["ref-potter"]),
    22: ("fund", "Anamnese: avaliação da dor", [], ["ref-barros", "ref-potter"]),
    23: ("fund", "Percussão", [], ["ref-barros", "ref-posso"]),
    24: ("fund", "Sistema vascular periférico", [], ["ref-barros", "ref-porto"]),
    25: ("fund", "Exame vascular dos membros inferiores", [], ["ref-barros"]),
    26: ("fund", "Termorregulação", [], ["ref-potter"]),
    27: ("fund", "Exame do estado mental", [], ["ref-barros"]),
    28: ("fund", "Ausculta cardíaca", [], ["ref-barros", "ref-porto"]),
    29: ("fund", "Aferição da pressão arterial: tamanho do manguito", ["diretrizes-has-2020"], ["ref-potter"]),
    30: ("fund", "Cianose", [], ["ref-barros"]),
    31: ("fund", "Lesões elementares de pele", [], ["ref-barros", "ref-posso"]),
    32: ("fund", "Ruídos adventícios pulmonares", [], ["ref-barros"]),
    33: ("fund", "Marcos anatômicos do tórax", [], ["ref-barros"]),
    34: ("clinica", "Insuficiência venosa e arterial", [], ["ref-brunner", "ref-barros"]),
    35: ("fund", "Avaliação do edema (cacifo)", [], ["ref-barros"]),
    36: ("fund", "Riscos nutricionais na internação", [], ["ref-potter"]),
    37: ("clinica", "Disfagia e risco de aspiração", [], ["ref-potter", "ref-brunner"]),
    38: ("calc", "Apresentações de medicamentos", [], ["ref-clayton", "ref-giovani"]),
    39: ("calc", "Medidas caseiras e conversão de doses", [], ["ref-giovani"]),
    40: ("fund", "Avaliação de feridas", [], ["ref-potter"]),
    41: ("clinica", "Terapia de feridas por pressão negativa", [], ["ref-potter"]),
    42: ("seguranca", "Locais de lesão por pressão", ["portaria-529-2013"], ["ref-potter"]),
    43: ("fund", "Escala de flebite", [], ["ref-potter"]),
    44: ("fund", "Fatores que alteram a velocidade de infusão", [], ["ref-potter", "ref-giovani"]),
    45: ("clinica", "Compatibilidade ABO na transfusão", ["portaria-158-2016"], ["ref-brunner"]),
    46: ("clinica", "Controle da transfusão de hemocomponentes", ["portaria-158-2016"], ["ref-brunner"]),
    47: ("clinica", "Classificação ASA e sedação", [], ["ref-sobecc", "ref-brunner"]),
    48: ("clinica", "Cuidados pós-operatórios", [], ["ref-sobecc", "ref-brunner"]),
    49: ("mental", "Efeitos extrapiramidais de antipsicóticos", [], ["ref-townsend"]),
    50: ("mental", "Delirium", [], ["ref-townsend", "ref-brunner"]),
    51: ("mental", "Síndrome neuroléptica maligna", [], ["ref-townsend"]),
    52: ("clinica", "Infecção do trato urinário", [], ["ref-brunner"]),
    53: ("fund", "Preparo para exames de sangue", [], ["ref-potter"]),
    54: ("bio", "Biossegurança hospitalar", ["nr-32"], []),
    55: ("fund", "Diagnósticos de enfermagem NANDA-I: domínios", PE, ["ref-nanda"]),
    56: ("mulher", "Cistos mamários", [], ["ref-cab-13", "ref-ricci"]),
    57: ("etica", "Análise ética na enfermagem", ["res-cofen-564-2017"], []),
    58: ("fund", "Processo de enfermagem: implementação", PE, ["ref-potter"]),
    59: ("mental", "Comunicação terapêutica", [], ["ref-townsend"]),
    60: ("fund", "Modelo transteórico de mudança de comportamento", [], ["ref-potter"]),
}

CORRECOES = {  # erros de extração conferidos no PDF
    (10, "A"): "Cievs.",
}


def gabarito(txt):
    linhas = open(txt, encoding="utf-8").read().splitlines()
    i = linhas.index("ENFERMAGEM - PROVA 1")
    r = []
    for k in (2, 4, 6):
        r += linhas[i + k].split()
    assert len(r) == 60
    return r


def main():
    extraidas, gab_txt = sys.argv[1], sys.argv[2]
    gab = gabarito(gab_txt)
    cat = os.path.join(RAIZ, "fontes", "catalogo_fontes.csv")
    with open(cat, encoding="utf-8") as f:
        existentes = {l["id"] for l in csv.DictReader(f)}
    with open(cat, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows([r for r in NOVAS_FONTES if r[0] not in existentes])

    sp = os.path.join(RAIZ, "esquemas", "questao.schema.json")
    s = json.load(open(sp, encoding="utf-8"))
    s["properties"]["imagens"] = {"type": "array", "items": {"type": "string"},
                                  "description": "Figuras da questão, caminhos relativos à pasta base-ia (ex.: imagens/enare-2021-enf-q031-0.png)"}
    json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    pasta_img = os.path.join(RAIZ, "imagens")
    os.makedirs(pasta_img, exist_ok=True)
    origem_img = os.path.join(os.path.dirname(os.path.abspath(extraidas)), "img")
    imgs = {}
    for nome in sorted(os.listdir(origem_img)):
        if nome.startswith("enare-2021-enf-"):
            shutil.copy(os.path.join(origem_img, nome), os.path.join(pasta_img, nome))
            n = int(re.search(r"q(\d{3})", nome).group(1))
            imgs.setdefault(n, []).append(f"imagens/{nome}")

    base = dict(origem="prova", banca="Instituto AOCP", ano=2021,
                orgao="EBSERH, ENARE 2021/2022 (Edital 2/2021), residência multiprofissional e uniprofissional",
                cargo="Residência em área profissional da saúde · Enfermagem",
                categoria_profissional="enfermeiro", especialidades=[], unidades=["Todas"],
                grupo_prova="Enfermagem", tipo_prova="Tipo 01", tipo="residencia")
    saida, manifesto = [], []
    for q in json.load(open(extraidas, encoding="utf-8")):
        n = q["numero"]
        tema, sub, fontes, refs = MAPA[n]
        alts = []
        for a in q["alternativas"]:
            t = re.sub(r"\s*Competências \(Conhecimentos, habilidades, atitudes\) Específicas\s*$", "", a["texto"])
            alts.append({"letra": a["letra"], "texto": CORRECOES.get((n, a["letra"]), t)})
        g = gab[n - 1]
        anulada = g not in list("ABCDE")
        disc = "Competências comuns" if n <= 20 else "Competências específicas de Enfermagem"
        saida.append({
            "id": f"aocp-2021-enare-enf-q{n:03d}", **base, "numero": n, "disciplina": disc,
            "tema": tema, "subtema": sub, "dificuldade": 3, "texto_apoio": None,
            "enunciado": q["enunciado"], "imagens": imgs.get(n, []), "alternativas": alts,
            "gabarito": None if anulada else g, "anulada": anulada, "comentario": None,
            "fontes": [{"documento_id": d, "dispositivo": None} for d in fontes],
            "referencias": [{"referencia_id": r, "onde": None} for r in refs],
            "data_referencia": None, "status_revisao": "rascunho", "revisor": None,
        })
        manifesto.append({"numero": n, "disciplina": disc, "tema": tema, "assunto": sub,
                          "gabarito": "X" if anulada else g, "anulada": anulada, "normas": fontes})
    nome = "enare-2021-enfermagem-tipo1.json"
    json.dump(saida, open(os.path.join(RAIZ, "questoes", nome), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    man = {**{k: v for k, v in base.items() if k != "origem"}, "data_prova": None,
           "fonte_gabarito": "gabarito definitivo ENARE 2021/2022 (Ebserh/Instituto AOCP), enviado pelo usuário",
           "gabarito_conferido": "Lido do PDF do gabarito definitivo: Enfermagem, Prova 1",
           "status": "texto das questões importado (rascunho, falta revisão)",
           "arquivo_questoes": f"questoes/{nome}", "questoes": manifesto}
    json.dump(man, open(os.path.join(RAIZ, "provas", nome), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(len(saida), "questões; anuladas:", [q["numero"] for q in saida if q["anulada"]],
          "; com figura:", sorted(imgs))


if __name__ == "__main__":
    main()
