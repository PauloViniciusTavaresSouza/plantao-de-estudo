"""Baixa os documentos do catálogo e divide o texto em trechos, um por artigo.

Para cada linha de fontes/catalogo_fontes.csv com url_oficial preenchida:
  1. baixa a página (HTML) ou o PDF
  2. tira o texto revogado, que o Planalto marca como riscado
  3. divide por artigo ("Art. 1º", "Art. 2º"...) e grava em dados/trechos/<id>.jsonl

Uso:
    python scripts/baixar_fontes.py            # todos os documentos
    python scripts/baixar_fontes.py lei-8080-1990 lei-8142-1990

Depende de: requests, beautifulsoup4, pdfplumber
Sempre confira por amostragem o texto gerado contra a página oficial.
"""
import csv
import datetime
import io
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "dados", "trechos")
CABECALHOS = {"User-Agent": "Mozilla/5.0 (base de estudos Plantao de Estudos)"}

RE_ARTIGO = re.compile(r"^\s*Art\.\s*(\d+)\s*(?:º|°|o)?\s*(?:-\s*([A-Z]))?[\s\.\-–]", re.M)


def texto_de_html(conteudo, encoding):
    html = conteudo.decode(encoding or "utf-8", errors="replace")
    sopa = BeautifulSoup(html, "html.parser")
    # O Planalto mostra a redação revogada riscada: ela não deve entrar na base
    for tag in sopa.find_all(["strike", "s", "del", "script", "style"]):
        tag.decompose()
    for tag in sopa.find_all(style=re.compile(r"line-through", re.I)):
        tag.decompose()
    for br in sopa.find_all("br"):
        br.replace_with("\n")
    linhas = []
    for bloco in sopa.find_all(["p", "div", "li", "h1", "h2", "h3", "h4", "td"]):
        if bloco.find(["p", "div", "li", "td"]):
            continue
        t = " ".join(bloco.get_text(" ").split())
        if t:
            linhas.append(t)
    return "\n".join(linhas) if linhas else sopa.get_text("\n")


def texto_de_pdf(conteudo):
    import pdfplumber
    paginas = []
    with pdfplumber.open(io.BytesIO(conteudo)) as pdf:
        for p in pdf.pages:
            paginas.append(p.extract_text() or "")
    return "\n".join(paginas)


def dividir_por_artigo(texto):
    """Devolve lista de (dispositivo, texto). O que vem antes do art. 1º vira 'ementa'."""
    marcas = list(RE_ARTIGO.finditer(texto))
    if not marcas:
        return [("documento", texto.strip())] if texto.strip() else []
    partes = []
    inicio = texto[: marcas[0].start()].strip()
    if inicio:
        partes.append(("ementa", inicio))
    vistos = {}
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        numero = m.group(1) + (f"-{m.group(2)}" if m.group(2) else "")
        disp = f"art. {numero}"
        # Artigos repetidos (ex.: lei que altera outra) ganham sufixo para não colidir
        vistos[disp] = vistos.get(disp, 0) + 1
        if vistos[disp] > 1:
            disp = f"{disp} ({vistos[disp]})"
        partes.append((disp, " ".join(texto[m.start():fim].split())))
    return partes


def situacao_de(trecho):
    t = trecho.lower()
    if re.search(r"\(revogad[oa]", t) and len(t) < 200:
        return "revogado"
    if "redação dada" in t or "incluído pela" in t or "incluída pela" in t:
        return "alterado"
    return "vigente"


def processar(linha):
    url = (linha.get("url_oficial") or "").strip()
    if not url:
        return f"{linha['id']}: sem URL no catálogo, pulei"
    r = requests.get(url, headers=CABECALHOS, timeout=60)
    r.raise_for_status()
    eh_pdf = url.lower().endswith(".pdf") or "pdf" in r.headers.get("Content-Type", "")
    texto = texto_de_pdf(r.content) if eh_pdf else texto_de_html(r.content, r.apparent_encoding)
    hoje = datetime.date.today().isoformat()
    temas = [linha["tema"]] if linha.get("tema") else []
    caminho = os.path.join(SAIDA, f"{linha['id']}.jsonl")
    partes = dividir_por_artigo(texto)
    with open(caminho, "w", encoding="utf-8") as f:
        for n, (disp, t) in enumerate(partes):
            f.write(json.dumps({
                "id": f"{linha['id']}#{n:04d}",
                "documento_id": linha["id"],
                "dispositivo": disp,
                "texto": t,
                "tipo_conteudo": "texto_oficial",
                "situacao": situacao_de(t),
                "url_fonte": url,
                "data_coleta": hoje,
                "temas": temas,
            }, ensure_ascii=False) + "\n")
    return f"{linha['id']}: {len(partes)} trechos"


def main(filtro):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(RAIZ, "fontes", "catalogo_fontes.csv"), encoding="utf-8") as f:
        linhas = [l for l in csv.DictReader(f) if not filtro or l["id"] in filtro]
    for linha in linhas:
        try:
            print(processar(linha))
        except Exception as e:  # segue para o próximo documento
            print(f"{linha['id']}: ERRO {e}")
        time.sleep(1)  # não sobrecarregar os sites oficiais


if __name__ == "__main__":
    main(set(sys.argv[1:]))
