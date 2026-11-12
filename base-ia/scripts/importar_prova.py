"""Converte questões em texto para o formato do banco (questao.schema.json).

Formato de entrada: um bloco por questão, separados por uma linha com ---

    Banca: FGV | Ano: 2024 | Órgão: Prefeitura X | Cargo: Enfermeiro | Tipo: Concurso | Tema: SUS | Dificuldade: 3
    Fonte: lei-8080-1990, art. 7
    Enunciado da questão.
    A) alternativa
    B) alternativa
    C) alternativa
    D) alternativa
    E) alternativa
    Gabarito: C
    Comentário: explicação (opcional, pode ter várias linhas)

Uso:
    python scripts/importar_prova.py entrada.txt questoes/saida.json
"""
import json
import re
import sys
import unicodedata

TEMAS = {
    "sus": ["sus", "saude publica", "saude coletiva", "politicas", "legislacao do sus"],
    "etica": ["etica", "legislacao profissional", "exercicio profissional", "cofen", "processo de enfermagem", "sae"],
    "fund": ["fundamentos", "semiologia", "semiotecnica", "procedimentos"],
    "calc": ["calculo", "farmacologia", "medicacao", "medicamentos"],
    "urg": ["urgencia", "emergencia", "rcp", "trauma", "uti", "terapia intensiva"],
    "mulher": ["mulher", "obstetricia", "pre-natal", "prenatal", "ginecologia", "gestante"],
    "crianca": ["crianca", "pediatria", "neonatal", "neonatologia", "adolescente"],
    "bio": ["biosseguranca", "infeccao", "precaucoes", "residuos", "esterilizacao", "cme"],
    "mental": ["mental", "psiquiatria", "caps", "raps"],
    "idoso": ["idoso", "geriatria", "gerontologia"],
    "vigilancia": ["vigilancia", "epidemiologia", "notificacao"],
    "imunizacao": ["imunizacao", "vacina", "vacinacao", "pni"],
    "seguranca": ["seguranca do paciente"],
    "gestao": ["gestao", "gerenciamento", "administracao", "lideranca"],
    "clinica": ["clinica", "medico-cirurgica", "cirurgica", "cronicas"],
    "portugues": ["portugues", "lingua portuguesa", "interpretacao de texto"],
    "legislacao_institucional": ["legislacao ebserh", "legislacao institucional", "regimento", "estatuto"],
}

CATEGORIAS = {"enfermeiro": "enfermeiro", "enfermagem": "enfermeiro", "tecnico": "tecnico_enfermagem",
              "auxiliar": "auxiliar_enfermagem", "multiprofissional": "multiprofissional"}


def categoria_de(texto):
    t = sem_acento(texto)
    for chave, valor in CATEGORIAS.items():
        if chave in t:
            return valor
    return None


def lista(texto):
    return [x.strip() for x in (texto or "").split(";") if x.strip()]


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").lower().strip()


def tema_de(texto):
    t = sem_acento(texto)
    if not t:
        return "outros"
    for chave, palavras in TEMAS.items():
        if t == chave or any(p in t for p in palavras):
            return chave
    return "outros"


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", sem_acento(s)).strip("-")
    return s or "x"


def ler_cabecalho(linha):
    meta = {}
    for parte in linha.split("|"):
        if ":" in parte:
            k, v = parte.split(":", 1)
            meta[sem_acento(k)] = v.strip()
    return meta


def converter(texto):
    questoes, erros = [], []
    ultimo_meta = {}
    blocos = re.split(r"\n\s*-{3,}\s*\n", texto.strip())
    for n, bloco in enumerate(blocos, 1):
        linhas = [l.rstrip() for l in bloco.strip().splitlines() if l.strip()]
        if not linhas:
            continue
        meta = {}
        if re.match(r"^\s*banca\s*:", linhas[0], re.I):
            meta = ler_cabecalho(linhas.pop(0))
            ultimo_meta.clear()
            ultimo_meta.update(meta)
        else:
            meta = dict(ultimo_meta)  # sem cabeçalho: herda o da questão anterior
        numero = None
        m_num = re.match(r"^\s*quest[aã]o\s*(\d+)\s*$", linhas[0], re.I) if linhas else None
        if m_num:
            numero = int(m_num.group(1))
            linhas.pop(0)
        fontes = []
        enunciado, alts, gabarito, comentario = [], [], None, []
        em_comentario = False
        for l in linhas:
            l_strip = l.strip()
            m_fonte = re.match(r"^fonte\s*:\s*(.+)$", l_strip, re.I)
            m_alt = re.match(r"^([A-Ea-e])\s*[\)\.\-]\s*(.+)$", l_strip)
            m_gab = re.match(r"^gabarito\s*:\s*([A-Ea-e])\b", l_strip, re.I)
            m_com = re.match(r"^coment[aá]rio\s*:\s*(.*)$", l_strip, re.I)
            if m_fonte and not alts:
                for item in m_fonte.group(1).split(";"):
                    doc, _, disp = item.partition(",")
                    fontes.append({"documento_id": doc.strip(), "dispositivo": disp.strip() or None})
            elif m_gab:
                gabarito = m_gab.group(1).upper()
            elif m_com:
                em_comentario = True
                if m_com.group(1):
                    comentario.append(m_com.group(1))
            elif em_comentario:
                comentario.append(l_strip)
            elif m_alt and gabarito is None:
                alts.append({"letra": m_alt.group(1).upper(), "texto": m_alt.group(2).strip()})
            elif not alts:
                enunciado.append(l_strip)
        letras = [a["letra"] for a in alts]
        problema = None
        if not enunciado:
            problema = "sem enunciado"
        elif len(alts) < 2:
            problema = "menos de 2 alternativas"
        elif letras != list("ABCDE"[: len(letras)]):
            problema = "alternativas fora de ordem: " + ",".join(letras)
        elif gabarito not in letras:
            problema = "gabarito ausente ou fora das alternativas"
        if problema:
            erros.append(f"bloco {n}: {problema}")
            continue
        ano = int(meta["ano"]) if meta.get("ano", "").isdigit() else None
        banca = meta.get("banca") or None
        tipo = "residencia" if "resid" in sem_acento(meta.get("tipo", "")) else "concurso"
        dif = int(meta["dificuldade"]) if meta.get("dificuldade", "").isdigit() and 1 <= int(meta["dificuldade"]) <= 5 else 3
        base_id = "-".join(x for x in [slug(banca or "sem-banca"), str(ano or ""), slug(meta["orgao"])[:30] if meta.get("orgao") else ""] if x)
        grupo = meta.get("grupo") or None
        tipo_prova = meta.get("tipo de prova") or meta.get("tipo prova") or None
        sufixo = f"{slug(grupo)}-" if grupo else ""
        questoes.append({
            "id": f"{base_id}-{sufixo}q{(numero or n):03d}",
            "origem": "prova",
            "banca": banca,
            "ano": ano,
            "orgao": meta.get("orgao") or None,
            "cargo": meta.get("cargo") or None,
            "categoria_profissional": categoria_de(meta.get("categoria") or meta.get("cargo") or ""),
            "especialidades": lista(meta.get("especialidades")),
            "unidades": lista(meta.get("unidades")),
            "grupo_prova": grupo,
            "tipo_prova": tipo_prova,
            "numero": numero,
            "disciplina": meta.get("disciplina") or None,
            "tipo": tipo,
            "tema": tema_de(meta.get("tema", "")),
            "subtema": None,
            "dificuldade": dif,
            "enunciado": " ".join(enunciado),
            "alternativas": alts,
            "gabarito": gabarito,
            "anulada": False,
            "comentario": " ".join(comentario) or None,
            "fontes": fontes,
            "data_referencia": None,
            "status_revisao": "rascunho",
            "revisor": None,
        })
    return questoes, erros


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        qs, errs = converter(f.read())
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, indent=2)
    print(f"{len(qs)} questões convertidas para {sys.argv[2]}")
    for e in errs:
        print("Aviso:", e)
