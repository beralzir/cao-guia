#!/usr/bin/env python3
"""preflight.py: inventário de dependências do cão-guia com degradação declarada.

A skill tem um núcleo leve (npx + Python puro) e extras opcionais. Este script
diz o que a máquina atual cobre e o que fica de fora. A regra da skill: nunca
quebrar por falta de extra; declarar no relatório o que não foi verificado.

Binário se testa executando, não por presença: o macOS tem um /usr/bin/java que
só pede para instalar o Java, e uma extração truncada deixa a pasta sem binário.

Uso: python3 preflight.py [--json]
     CAOGUIA_BDM_DIR aponta outra pasta do browser-driver-manager
     (padrão ~/.browser-driver-manager).
"""

import glob
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

# Layout do @puppeteer/browsers, que o browser-driver-manager usa por baixo:
# <pasta>/<chrome|chromedriver>/<plataforma>-<versão>/<pacote>/<binário>
CHROME_BINARIOS = (
    "*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
    "*/chrome",
    "*/chrome.exe",
)
DRIVER_BINARIOS = ("*/chromedriver", "*/chromedriver.exe")


def which(binario):
    return shutil.which(binario) is not None


def modulo(nome):
    return importlib.util.find_spec(nome) is not None


def executa(cmd, timeout=20):
    """Saída do comando (stdout + stderr) se ele sair com 0; None se não roda."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    return (r.stdout + r.stderr) if r.returncode == 0 else None


def _chave_versao(pasta):
    m = re.search(r"(\d+(?:\.\d+)+)$", os.path.basename(pasta))
    return tuple(int(n) for n in m.group(1).split(".")) if m else ()


def _mais_nova(base, tipo, padroes):
    """(binário, pasta) da versão mais nova de `tipo`; binário None se a pasta está incompleta."""
    pastas = [p for p in glob.glob(os.path.join(base, tipo, "*-*")) if os.path.isdir(p)]
    if not pastas:
        return None, None
    pasta = max(pastas, key=_chave_versao)
    for padrao in padroes:
        achados = glob.glob(os.path.join(pasta, padrao))
        if achados:
            return achados[0], pasta
    return None, pasta


def par_axe():
    """Par Chrome for Testing + ChromeDriver do browser-driver-manager.

    Opcional: sem ele, o axe usa o Chrome do sistema. Mas par presente e quebrado
    derruba o axe com os caminhos que a skill manda passar. Em 27/09/2026, com
    Node 26, o bdm 2.0.1 saiu com código 0 no meio da extração, deixando o driver
    sem binário e o Chrome sem framework (ver references/motores.md).
    """
    base = os.path.expanduser(os.environ.get("CAOGUIA_BDM_DIR", "~/.browser-driver-manager"))
    par = {"pasta": base, "estado": "ausente", "chrome": None, "chromedriver": None,
           "versao_chrome": None, "versao_driver": None, "problemas": []}
    chrome, pasta_chrome = _mais_nova(base, "chrome", CHROME_BINARIOS)
    driver, pasta_driver = _mais_nova(base, "chromedriver", DRIVER_BINARIOS)
    if pasta_chrome is None and pasta_driver is None:
        return par
    par["chrome"], par["chromedriver"] = chrome, driver
    for rotulo, binario, pasta, chave in (
            ("Chrome for Testing", chrome, pasta_chrome, "versao_chrome"),
            ("ChromeDriver", driver, pasta_driver, "versao_driver")):
        if pasta is None:
            par["problemas"].append(rotulo + " não instalado")
            continue
        if binario is None:
            par["problemas"].append(rotulo + " incompleto: a pasta não tem o binário")
            continue
        versao = re.search(r"\d+\.\d+\.\d+\.\d+", executa([binario, "--version"]) or "")
        if versao is None:
            par["problemas"].append(rotulo + " não executa (--version falhou)")
        else:
            par[chave] = versao.group(0)
    vc, vd = par["versao_chrome"], par["versao_driver"]
    if vc and vd and vc.split(".")[0] != vd.split(".")[0]:
        par["problemas"].append("Chrome %s e driver %s dessincronizados" % (vc, vd))
    par["estado"] = "quebrado" if par["problemas"] else "ok"
    return par


def montar():
    node = which("node") and which("npx")
    java = executa(["java", "-version"]) is not None
    verapdf = executa(["verapdf", "--version"]) is not None
    caps = []

    caps.append({
        "capacidade": "Web núcleo (axe-core em URL/HTML local)",
        "ok": node,
        "requisito": "node + npx (axe pinado: npx @axe-core/cli@4.12.1)",
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
        "ok": verapdf,
        "requisito": "veraPDF CLI que execute (Homebrew: brew install verapdf, já traz o Java; ou https://verapdf.org; ou docker verapdf/cli)",
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
        "par_axe": par_axe(),
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

    par = dados["par_axe"]
    print()
    if par["estado"] == "ok":
        print("Par Chrome/driver do axe: OK (" + par["versao_chrome"] + "). Passar ao axe:")
        print('  --chrome-path "%s" --chromedriver-path "%s"' % (par["chrome"], par["chromedriver"]))
    elif par["estado"] == "quebrado":
        print("Par Chrome/driver do axe: QUEBRADO em " + par["pasta"])
        for problema in par["problemas"]:
            print("  - " + problema)
        print("  Não passar esses caminhos ao axe. Ver as pegadinhas do axe-cli em references/motores.md.")
    else:
        print("Par Chrome/driver do axe: não instalado. Opcional: só é preciso se o axe")
        print("acusar Chrome e ChromeDriver dessincronizados (ver references/motores.md).")


if __name__ == "__main__":
    main()
