#!/usr/bin/env python3
"""axe_diff.py — diff de auditorias axe-core (baseline vs. pós-fix).

Fecha o loop de correção do cão-guia: todo fix aplicado precisa de prova de
que resolveu a violação sem criar violação nova. Compara dois JSON do
@axe-core/cli (ou de axe.run()) e reporta corrigidas / novas / persistentes.

Uso:
  npx @axe-core/cli <url-ou-arquivo> --save baseline.json
  # ... aplica os fixes aprovados ...
  npx @axe-core/cli <url-ou-arquivo> --save depois.json
  python3 axe_diff.py baseline.json depois.json [--json]

Sai com código 2 se houver violação NOVA (fix criou problema), 0 caso contrário.
"""

import json
import sys


def carregar_violacoes(caminho):
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    # @axe-core/cli grava uma lista de resultados; axe.run() grava um objeto
    resultados = dados if isinstance(dados, list) else [dados]
    chaves = {}
    for res in resultados:
        for v in res.get("violations", []):
            for node in v.get("nodes", []):
                alvo = "|".join(str(t) for t in node.get("target", []))
                chaves[(v["id"], alvo)] = {
                    "regra": v["id"], "impacto": v.get("impact"),
                    "alvo": alvo, "ajuda": v.get("help", "")}
    return chaves


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    antes, depois = carregar_violacoes(args[0]), carregar_violacoes(args[1])
    corrigidas = [antes[k] for k in antes.keys() - depois.keys()]
    novas = [depois[k] for k in depois.keys() - antes.keys()]
    persistentes = [depois[k] for k in antes.keys() & depois.keys()]
    saida = {"corrigidas": corrigidas, "novas": novas,
             "persistentes": persistentes,
             "resumo": {"corrigidas": len(corrigidas), "novas": len(novas),
                        "persistentes": len(persistentes)}}
    if "--json" in sys.argv:
        print(json.dumps(saida, ensure_ascii=False, indent=2))
    else:
        r = saida["resumo"]
        print(f"corrigidas: {r['corrigidas']} · novas: {r['novas']} "
              f"· persistentes: {r['persistentes']}")
        for v in novas:
            print(f"  NOVA: {v['regra']} em {v['alvo']} ({v['impacto']})")
        for v in persistentes:
            print(f"  persiste: {v['regra']} em {v['alvo']}")
    sys.exit(2 if novas else 0)


if __name__ == "__main__":
    main()
