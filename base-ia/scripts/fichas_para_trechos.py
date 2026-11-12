"""Transforma as fichas em Markdown (pasta fichas/) em trechos para a IA (dados/trechos/fichas.jsonl).

Cada seção "## ..." de uma ficha vira um trecho do tipo resumo_proprio, ligado ao documento_id do cabeçalho.
O dispositivo é tirado do título da seção quando ele cita artigos, por exemplo "(art. 11, I)".

Uso:
    python scripts/fichas_para_trechos.py
"""
import datetime
import glob
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ler_ficha(caminho):
    texto = open(caminho, encoding="utf-8").read()
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if m:
        for linha in m.group(1).splitlines():
            if ":" in linha:
                k, v = linha.split(":", 1)
                meta[k.strip()] = v.strip()
        texto = texto[m.end():]
    secoes = re.split(r"^## ", texto, flags=re.M)[1:]
    return meta, [s.split("\n", 1) for s in secoes]


def main():
    hoje = datetime.date.today().isoformat()
    saida = os.path.join(RAIZ, "dados", "trechos", "fichas.jsonl")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    total = 0
    with open(saida, "w", encoding="utf-8") as f:
        for caminho in sorted(glob.glob(os.path.join(RAIZ, "fichas", "*.md"))):
            meta, secoes = ler_ficha(caminho)
            doc = meta.get("documento_id") or os.path.splitext(os.path.basename(caminho))[0]
            revisada = "conferid" in meta.get("status", "")
            for n, (titulo, corpo) in enumerate(secoes):
                titulo = titulo.strip()
                m = re.search(r"\((arts?\.[^)]*)\)", titulo)
                f.write(json.dumps({
                    "id": f"ficha-{doc}#{n:02d}",
                    "documento_id": doc,
                    "dispositivo": m.group(1) if m else titulo,
                    "texto": f"{titulo}. " + " ".join(corpo.split()),
                    "tipo_conteudo": "resumo_proprio",
                    "situacao": "vigente" if revisada else "verificar",
                    "url_fonte": None,
                    "data_coleta": hoje,
                    "temas": [],
                }, ensure_ascii=False) + "\n")
                total += 1
    print(f"{total} trechos de fichas gravados em {saida}")


if __name__ == "__main__":
    main()
