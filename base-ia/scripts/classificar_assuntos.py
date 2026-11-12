"""Classifica as questões em temáticas e assuntos (filtro fino do app e da IA).

Uso:
    python scripts/classificar_assuntos.py            # grava "assuntos" em questoes/*.json
A taxonomia fica em esquemas/taxonomia.json. A classificação é automática, por palavras-chave:
o revisor confere e corrige no campo "assuntos" de cada questão.
"""
import glob, json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# grupo: (nome, [(id, nome, palavras-chave)])
TAXONOMIA = {
    "sus": ("SUS e Políticas de Saúde", [
        ("sus-leis", "Legislação do SUS", ["8.080", "8080", "8.142", "8142", "7.508", "7508", "lei orgânica", "constituição", "seguridade", "universalidade", "integralidade", "coap", "contrato organizativo", "regionaliza", "comissão intergestores", "comissão tripartite", "cib", "cit", "princípios do sus", "princípio do sus"]),
        ("sus-politicas", "Políticas de saúde", ["política nacional", "pnab", "atenção básica", "saúde da família", "humaniza", "pnh", "rede de atenção", "redes de atenção", "ras", "equidade de gênero", "lgbt", "orientação sexual", "saúde do homem", "tabagismo", "pessoa com deficiência", "modelo assistencial", "modelos assistenciais", "1.526", "determinantes sociais"]),
        ("sus-controle", "Controle social", ["conselho de saúde", "conselhos de saúde", "conselho nacional de saúde", "conferência de saúde", "participação social", "participação da comunidade", "controle social", "carta dos direitos", "cisttão"]),
        ("sus-financ", "Financiamento e saúde suplementar", ["financiamento", "complementar nº 141", "141/2012", "fundo de saúde", "saúde suplementar", "planos de saúde", "operadoras"]),
        ("sus-historia", "História das políticas de saúde", ["história das políticas", "história da saúde", "movimento sanitário", "reforma sanitária", "conferência nacional de saúde", "revolta da vacina", "inamps", "santas casas"]),
    ]),
    "vig": ("Vigilância em Saúde", [
        ("vig-epi", "Vigilância epidemiológica", ["epidemiológ", "notificação", "sinan", "incidência", "prevalência", "indicador", "surto", "dengue", "arbovir", "hanseníase", "leavell", "história natural", "cievs", "agravo", "febre", "malária"]),
        ("vig-sanit", "Vigilância sanitária", ["vigilância sanitária", "anvisa", "rdc", "notivisa", "boas práticas de funcionamento", "tecnovigilância", "farmacovigilância", "produtos que estão sob"]),
        ("vig-amb", "Vigilância ambiental", ["ambiental", "agrotóx", "barragem", "rejeito", "climát", "clima", "enchente", "ondas de calor", "peçonhent", "desastre"]),
        ("vig-trab", "Saúde do trabalhador", ["trabalhador", "ocupacion", "nr-", "norma regulamentadora", "acidente de trabalho", "acidentes do trabalho", "acidentes de trabalho", "ler/dort", "dort", "ergonom", "cipa", "sesmt", "epi", "clt", "consolidação das leis do trabalho", "oit", "pnsst", "fundacentro", "higiene ocupacional"]),
        ("vig-imun", "Imunização", ["vacin", "imuniz", "calendário", "caderneta vacinal", "pni", "tétano", "imunobiológ"]),
        ("vig-pnvs", "Política de Vigilância em Saúde", ["política nacional de vigilância", "pnvs"]),
    ]),
    "gest": ("Gestão e Gerência", [
        ("gest-enf", "Gerenciamento em enfermagem", ["gestão", "gerenc", "dimensionamento", "liderança", "planejamento", "blockchain", "avaliação normativa", "avaliação em saúde"]),
        ("gest-aud", "Auditoria", ["auditoria", "auditor"]),
        ("gest-qual", "Qualidade e segurança do paciente", ["segurança do paciente", "evento adverso", "eventos adversos", "qualidade", "incidente", "núcleo de segurança", "classificação internacional de segurança", "boas práticas"]),
        ("gest-edu", "Educação permanente e em saúde", ["educação permanente", "educação em saúde", "pneps"]),
    ]),
    "leg": ("Ética e Legislação", [
        ("leg-prof", "Exercício profissional e ética", ["7.498", "7498", "94.406", "código de ética", "ética", "cofen", "coren", "exercício de enfermagem", "exercício profissional", "bioética", "beneficência", "maleficência"]),
        ("leg-pe", "Processo de enfermagem", ["processo de enfermagem", "sistematização", "diagnóstico de enfermagem", "diagnósticos de enfermagem", "nanda", "implementação de enfermagem", "plano de cuidado"]),
        ("leg-ebserh", "Legislação da EBSERH", ["ebserh", "12.550", "estatuto social", "regimento interno", "regulamento de pessoal", "conselho consultivo"]),
    ]),
    "urg": ("Urgência e Emergência", [
        ("urg-rcp", "Parada cardiorrespiratória e RCP", ["rcp", "reanimação", "parada cardior", "pcr", "desfibril", "suporte básico", "suporte avançado", "ressuscita"]),
        ("urg-trauma", "Trauma e primeiros socorros", ["trauma", "tce", "cranioencef", "queimad", "primeiros socorros", "pré-hospitalar", "fratura", "glasgow", "ferimento", "acidentes com animais"]),
        ("urg-clin", "Emergências clínicas e choque", ["choque", "dor torácica", "coronariana", "infarto", "avc", "hipovolêm", "sepse", "anafila", "desidrata", "intoxicação"]),
        ("urg-org", "Organização da urgência", ["pronto-socorro", "pronto socorro", "classificação de risco", "samu", "upa", "urgência e emergência", "emergência e urgência", "conceitos de emergência"]),
    ]),
    "cri": ("Saúde da Criança", [
        ("cri-ped", "Pediatria", ["criança", "pediatr", "adolescente", "8.069", "puericult", "caderneta da criança", "infância"]),
        ("cri-neo", "Neonatologia", ["neonat", "recém-nascido", "apgar", "prematur", "bebê"]),
        ("cri-alei", "Aleitamento materno", ["amament", "aleitamento", "mamada", "pega"]),
    ]),
    "mul": ("Saúde da Mulher", [
        ("mul-obs", "Obstetrícia e parto", ["parto", "gestante", "gestação", "pré-natal", "obstétr", "puerpér", "gravidez", "trabalho de parto"]),
        ("mul-gin", "Ginecologia e prevenção", ["colo do útero", "hpv", "mama", "mamár", "papanicolau", "citopatológ", "planejamento familiar", "contracep", "climatério"]),
    ]),
    "cli": ("Clínica Médica e Cirúrgica", [
        ("cli-cir", "Centro cirúrgico e perioperatório", ["operatór", "cirúrg", "asa", "sedação", "anestes", "recuperação pós"]),
        ("cli-card", "Cardiologia", ["cardía", "cardio", "hipertens", "ausculta cardíaca", "insuficiência venosa", "vascular periférico"]),
        ("cli-resp", "Respiratório e oxigenoterapia", ["respirat", "oxigen", "dpoc", "pulmon", "ventila", "ruídos adventícios", "tórax"]),
        ("cli-nef", "Nefrologia e diálise", ["renal", "diálise", "hemodiálise", "fístula arteriovenosa", "drc", "trato urinário", "hiperfosfatemia"]),
        ("cli-hemo", "Hemoterapia", ["transfus", "hemocomponente", "hemoderivado", "abo", "tipo sanguíneo"]),
        ("cli-feridas", "Feridas e lesão por pressão", ["ferida", "lesão por pressão", "lesões por pressão", "curativo", "pressão negativa", "lesões de pele", "lesão de pele", "úlcera"]),
        ("cli-cron", "Doenças crônicas", ["diabet", "obesidade", "crônic", "dcnt", "insulina"]),
        ("cli-infec", "Doenças infecciosas e IST", ["ist", "sífilis", "hiv", "sexualmente transmiss", "trato urinário", "infectocontag", "tuberculose", "hanseníase", "dengue"]),
        ("cli-neuro", "Neurologia", ["neurológ", "avc", "convuls", "glasgow", "tce"]),
    ]),
    "fund": ("Fundamentos de Enfermagem", [
        ("fund-semio", "Semiologia e exame físico", ["exame físico", "anamnese", "percussão", "ausculta", "inspeção", "palpação", "estado mental", "edema", "cianose", "lesões elementares", "marcos anatômicos", "padrões respiratórios", "força muscular"]),
        ("fund-ssvv", "Sinais vitais", ["sinais vitais", "temperatura corporal", "termorregula", "pressão arterial", "manguito", "pulso"]),
        ("fund-proc", "Procedimentos de enfermagem", ["sonda", "coleta", "punção", "acesso venoso", "flebite", "terapia intravenosa", "infusão", "nutrição", "disfagia", "aspiração", "urina de 24", "exames de sangue"]),
    ]),
    "farm": ("Farmacologia e Cálculo", [
        ("farm-calc", "Cálculo de medicação", ["cálculo", "gotas", "microgotas", "ml/h", "diluição", "unidades de insulina", "medidas domésticas", "medidas caseiras", "colher", "converter unidades"]),
        ("farm-adm", "Administração de medicamentos", ["medicament", "fármaco", "antipsicót", "frasco-ampola", "bolus", "dipirona", "intramuscular", "endovenos", "intravenosa"]),
    ]),
    "bio": ("Biossegurança e Infecção", [
        ("bio-prec", "Precauções e isolamento", ["precauç", "isolamento", "aerossó", "gotícula", "infecção hospitalar", "iras"]),
        ("bio-proc", "Processamento de produtos", ["esteriliz", "desinfec", "rdc nº 15", "rdc 15", "spaulding", "produtos para a saúde", "produtos para saúde", "cme"]),
        ("bio-resid", "Resíduos, NR 32 e exposição", ["resíduo", "perfurocortante", "nr-32", "nr 32", "biossegurança", "material biológico"]),
    ]),
    "men": ("Saúde Mental", [
        ("men-pol", "Políticas de saúde mental", ["10.216", "caps", "raps", "reforma psiquiátrica", "internação involuntária", "internação psiquiátrica"]),
        ("men-clin", "Transtornos e cuidado", ["delirium", "psicót", "transtorno", "antipsic", "neuroléptic", "comunicação terapêutica", "extrapiramidal", "depress", "suicíd", "saúde mental"]),
    ]),
    "ido": ("Saúde do Idoso", [
        ("ido-geral", "Saúde do idoso", ["idoso", "envelhec", "geriátr", "10.741"]),
    ]),
    "port": ("Língua Portuguesa", [
        ("port-texto", "Interpretação de texto", ["texto", "fragmento", "parágrafo", "argument", "inferir", "infere", "interlocutor"]),
        ("port-gram", "Gramática", ["pronome", "pontuação", "grafia", "verbo", "oração", "reticências", "concordância", "regência", "crase", "vocábulo", "sublinhada", "reescrever", "interrogação"]),
    ]),
}
FALLBACK = {"sus": "sus-politicas", "vigilancia": "vig-epi", "gestao": "gest-enf", "etica": "leg-prof",
            "legislacao_institucional": "leg-ebserh", "urg": "urg-clin", "crianca": "cri-ped", "mulher": "mul-gin",
            "clinica": "cli-cron", "fund": "fund-proc", "calc": "farm-calc", "bio": "bio-prec", "mental": "men-clin",
            "idoso": "ido-geral", "imunizacao": "vig-imun", "seguranca": "gest-qual", "saude_trabalhador": "vig-trab",
            "portugues": "port-texto", "outros": "fund-proc"}
# temas que limitam os grupos possíveis (evita que palavras soltas puxem a questão para outro grupo)
TRAVA = {"portugues": {"port"}, "legislacao_institucional": {"leg"}}

ITENS = [(g, sid, nome, kws) for g, (_, subs) in TAXONOMIA.items() for sid, nome, kws in subs]
GRUPO = {sid: g for g, sid, _, _ in ITENS}


def _rx(k):
    k = re.escape(k.lower())
    return re.compile(r"\b" + k + r"\b") if len(k) <= 4 else re.compile(k)


REGRAS = [(sid, [_rx(k) for k in kws]) for _, sid, _, kws in ITENS]


def classificar(tema, subtema, enunciado):
    sub = (subtema or "").lower()
    enu = (enunciado or "").lower()[:400]
    trava = TRAVA.get(tema)
    pont = {}
    for sid, rxs in REGRAS:
        if trava and GRUPO[sid] not in trava:
            continue
        if GRUPO[sid] == "port" and tema != "portugues":
            continue
        p = sum(3 for r in rxs if r.search(sub)) + sum(1 for r in rxs if r.search(enu))
        if p:
            pont[sid] = p
    fortes = [s for s, p in sorted(pont.items(), key=lambda x: -x[1]) if p >= 3][:3]
    if not fortes:
        fortes = [s for s, p in sorted(pont.items(), key=lambda x: -x[1]) if p >= 1][:2]
    if tema == "portugues" and not fortes:
        fortes = ["port-texto"]
    if not fortes:
        fortes = [FALLBACK.get(tema, "fund-proc")]
    return fortes


def taxonomia_json():
    return [{"id": g, "nome": n, "assuntos": [{"id": s, "nome": sn} for s, sn, _ in subs]} for g, (n, subs) in TAXONOMIA.items()]


def main():
    json.dump(taxonomia_json(), open(os.path.join(RAIZ, "esquemas", "taxonomia.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    sp = os.path.join(RAIZ, "esquemas", "questao.schema.json")
    s = json.load(open(sp, encoding="utf-8"))
    s["properties"]["assuntos"] = {"type": "array", "items": {"enum": [sid for _, sid, _, _ in ITENS]},
                                   "description": "Assuntos finos da questão (esquemas/taxonomia.json). Cada assunto pertence a uma temática"}
    s["properties"]["localidade"] = {"type": ["string", "null"], "description": "UF da prova, ou Nacional"}
    json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    total = 0
    for arq in sorted(glob.glob(os.path.join(RAIZ, "questoes", "*.json"))):
        qs = json.load(open(arq, encoding="utf-8"))
        for q in qs:
            q["assuntos"] = classificar(q["tema"], q.get("subtema"), q["enunciado"])
            if "localidade" not in q:
                q["localidade"] = "Nacional" if q.get("origem") == "prova" else None
            total += 1
        json.dump(qs, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(total, "questões classificadas")


if __name__ == "__main__":
    main()
