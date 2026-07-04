#!/usr/bin/env python3
"""preflight.py — inventário de dependências do cão-guia com degradação declarada.

A skill tem um núcleo leve (npx + Python puro) e extras opcionais. Este script
diz o que a máquina atual cobre e o que fica de fora. A regra da skill: nunca
quebrar por falta de extra; declarar no relatório o que não foi verificado.

Uso: python3 preflight.py [--json]
"""

import importlib.util
import json
import shutil
import sys


def which(binario):
    return shutil.which(binario) is not None


def modulo(nome):
    return importlib.util.find_spec(nome) is not None


def montar():
    node = which("node") and which("npx")
    java = which("java")
    verapdf = which("verapdf")
    caps = []

    caps.append({
        "capacidade": "Web núcleo (axe-core em URL/HTML local)",
        "ok": node,
        "requisito": "node + npx (axe baixa no primeiro uso: npx @axe-core/cli)",
        "degradacao": "sem node: auditoria web fica só na leitura estática do HTML pelo LLM, marcada como [heurística LLM]",
    })
    caps.append({
        "capacidade": "Web SPA / estados dinâmicos (Playwright)",
        "ok": node and modulo("playwright"),
        "requisito": "pip install playwright && playwright install chromium",
        "degradacao": "sem Playwright: audita só o estado inicial da página; estados (modais, pós-login) ficam declarados como não cobertos",
    })
    caps.append({
        "capacidade": "Data viz núcleo (contraste WCAG + paleta CVD)",
        "ok": True,
        "requisito": "nenhum (scripts/cor.py é Python puro)",
        "degradacao": "n/a",
    })
    caps.append({
        "capacidade": "CVD avançado (severidade parcial, tritanopia rigorosa, imagem raster)",
        "ok": modulo("daltonlens") and modulo("PIL"),
        "requisito": "pip install daltonlens pillow (colorspacious opcional p/ severidade)",
        "degradacao": "sem extra: paleta usa Machado sev 1.0 do cor.py (tritanopia aproximada); imagem raster não é simulada",
    })
    caps.append({
        "capacidade": "PDF (PDF/UA via veraPDF)",
        "ok": java and verapdf,
        "requisito": "java + veraPDF CLI (https://verapdf.org; ou docker verapdf/cli)",
        "degradacao": "sem veraPDF: triagem só com pikepdf/pypdf se instalados (MarkInfo/StructTree/Lang) ou leitura LLM; conformidade PDF/UA fica não verificada",
    })
    caps.append({
        "capacidade": "PDF triagem leve (tags/idioma/título)",
        "ok": modulo("pikepdf") or modulo("pypdf"),
        "requisito": "pip install pikepdf (ou pypdf)",
        "degradacao": "sem lib: triagem estrutural de PDF indisponível",
    })
    caps.append({
        "capacidade": "Office (docx/pptx/xlsx via office_audit.py)",
        "ok": modulo("docx") and modulo("pptx") and modulo("openpyxl"),
        "requisito": "pip install python-docx python-pptx openpyxl",
        "degradacao": "sem libs: checagem OOXML indisponível; recomenda o checker manual do Office",
    })
    return {
        "capacidades": caps,
        "binarios": {"node": which("node"), "npx": which("npx"),
                     "java": java, "verapdf": verapdf},
    }


def main():
    dados = montar()
    if "--json" in sys.argv:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        return
    print("cão-guia · preflight de dependências\n")
    for c in dados["capacidades"]:
        status = "OK       " if c["ok"] else "DEGRADADO"
        print(f"[{status}] {c['capacidade']}")
        if not c["ok"]:
            print(f"           instalar: {c['requisito']}")
            print(f"           sem isso: {c['degradacao']}")
    faltando = [c for c in dados["capacidades"] if not c["ok"]]
    print(f"\n{len(dados['capacidades']) - len(faltando)}/"
          f"{len(dados['capacidades'])} capacidades disponíveis.")
    if faltando:
        print("Toda capacidade degradada DEVE aparecer na seção de cobertura do relatório.")


if __name__ == "__main__":
    main()
