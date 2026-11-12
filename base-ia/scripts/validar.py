"""Confere se os arquivos de questões e trechos seguem os esquemas e se as fontes citadas existem no catálogo.

Uso:
    python scripts/validar.py
"""
import csv
import glob
import json
import os
import sys

from jsonschema import Draft202012Validator

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def main():
    v_q = Draft202012Validator(carregar(os.path.join(RAIZ, "esquemas", "questao.schema.json")))
    v_t = Draft202012Validator(carregar(os.path.join(RAIZ, "esquemas", "trecho.schema.json")))
    with open(os.path.join(RAIZ, "fontes", "catalogo_fontes.csv"), encoding="utf-8") as f:
        catalogo = {linha["id"] for linha in csv.DictReader(f)}
    with open(os.path.join(RAIZ, "fontes", "referencias_bibliograficas.csv"), encoding="utf-8") as f:
        referencias = {linha["id"] for linha in csv.DictReader(f)}
    problemas, total_q, total_t, ids = [], 0, 0, set()

    for arq in sorted(glob.glob(os.path.join(RAIZ, "questoes", "*.json"))):
        for q in carregar(arq):
            total_q += 1
            for e in v_q.iter_errors(q):
                problemas.append(f"{os.path.basename(arq)} {q.get('id')}: {e.message}")
            if q.get("id") in ids:
                problemas.append(f"id repetido: {q.get('id')}")
            ids.add(q.get("id"))
            for fonte in q.get("fontes", []):
                if fonte["documento_id"] not in catalogo:
                    problemas.append(f"{q.get('id')}: fonte fora do catálogo: {fonte['documento_id']}")
            for ref in q.get("referencias", []):
                if ref["referencia_id"] not in referencias:
                    problemas.append(f"{q.get('id')}: referência fora da lista: {ref['referencia_id']}")

    for arq in sorted(glob.glob(os.path.join(RAIZ, "dados", "trechos", "*.jsonl"))):
        with open(arq, encoding="utf-8") as f:
            for n, linha in enumerate(f, 1):
                if not linha.strip():
                    continue
                total_t += 1
                t = json.loads(linha)
                for e in v_t.iter_errors(t):
                    problemas.append(f"{os.path.basename(arq)} linha {n}: {e.message}")

    total_p = 0
    for arq in sorted(glob.glob(os.path.join(RAIZ, "provas", "*.json"))):
        prova = carregar(arq)
        total_p += 1
        numeros = [q["numero"] for q in prova.get("questoes", [])]
        if numeros != list(range(1, len(numeros) + 1)):
            problemas.append(f"{os.path.basename(arq)}: numeração das questões com falha")
        for q in prova.get("questoes", []):
            if not q.get("anulada") and q.get("gabarito") not in list("ABCDE"):
                problemas.append(f"{os.path.basename(arq)} questão {q['numero']}: gabarito inválido")
            for doc in q.get("normas", []):
                if doc not in catalogo:
                    problemas.append(f"{os.path.basename(arq)} questão {q['numero']}: norma fora do catálogo: {doc}")

    print(f"{total_q} questões, {total_t} trechos e {total_p} provas conferidos.")
    for p in problemas:
        print("Problema:", p)
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
