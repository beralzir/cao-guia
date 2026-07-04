#!/usr/bin/env python3
"""cor.py — pipeline de cor do cão-guia (Python puro, sem dependências).

Faz três coisas:
  contraste  razão de contraste WCAG 2.x entre duas cores + vereditos AA/AAA/UI
  paleta     simula daltonismo sobre uma paleta e mede distinguibilidade (ΔE)
  paletas    imprime as paletas seguras embutidas (Okabe-Ito, Paul Tol)

Uso:
  python3 cor.py contraste "#333333" "#FFFFFF"
  python3 cor.py paleta "#E69F00" "#56B4E9" "#009E73" [--json]
  python3 cor.py paletas

Decisões de engenharia (citar em qualquer relatório que use este script):
- A simulação opera em RGB LINEAR: linearização sRGB antes das matrizes e
  reencode depois. Pular esse passo é o erro nº 1 das implementações abertas
  (cores escuras demais).
- Matrizes de Machado et al. (2009) em severidade 1.0 (dicromacia). Para
  severidade parcial (tricromacia anômala, o caso mais comum na prática) e
  para tritanopia rigorosa (só Brettel 1997 é válido), use o extra
  DaltonLens/colorspacious (ver preflight.py). A simulação de tritanopia
  daqui é aproximada e está marcada como tal na saída.
- Distinguibilidade sob CVD: ΔE (CIE76, espaço Lab) entre cada par de cores
  na versão simulada. Threshold fixado pela skill (não existe padrão de
  mercado): ΔE < 10 = COLISÃO, 10 a 20 = ALERTA, ≥ 20 = OK.
- WCAG 2.x é o critério de conformidade legal. APCA/Lc é só guia de design e
  tem licença restrita; não é implementado aqui de propósito.
"""

import json
import sys

# Machado et al. 2009, severidade 1.0, aplicadas em RGB linear
MACHADO_10 = {
    "protanopia": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deuteranopia": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    # Aproximação: para tritanopia rigorosa use Brettel 1997 (extra DaltonLens)
    "tritanopia~": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}

DELTA_E_COLISAO = 10.0
DELTA_E_ALERTA = 20.0

PALETAS_SEGURAS = {
    "okabe-ito": {
        "descricao": "8 cores categóricas, padrão recomendado pela Nature Methods",
        "cores": ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
                  "#0072B2", "#D55E00", "#CC79A7", "#000000"],
    },
    "tol-bright": {
        "descricao": "Paul Tol, qualitativa bright (7 cores)",
        "cores": ["#4477AA", "#EE6677", "#228833", "#CCBB44",
                  "#66CCEE", "#AA3377", "#BBBBBB"],
    },
    "tol-muted": {
        "descricao": "Paul Tol, qualitativa muted (10 cores)",
        "cores": ["#332288", "#88CCEE", "#44AA99", "#117733", "#999933",
                  "#DDCC77", "#CC6677", "#882255", "#AA4499", "#DDDDDD"],
    },
    # Contínuo: usar viridis/cividis da própria lib de plot (matplotlib,
    # plotly, d3-scale-chromatic); não faz sentido embutir stops aqui.
}


def hex_to_rgb(hexstr):
    h = hexstr.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"cor inválida: {hexstr!r} (esperado #RRGGBB)")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02X}" for c in rgb)


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def luminancia(rgb):
    r, g, b = (srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def razao_contraste(rgb1, rgb2):
    l1, l2 = sorted((luminancia(rgb1), luminancia(rgb2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def vereditos_wcag(ratio):
    return {
        "texto_normal_AA (4.5:1)": ratio >= 4.5,
        "texto_normal_AAA (7:1)": ratio >= 7.0,
        "texto_grande_AA (3:1)": ratio >= 3.0,
        "texto_grande_AAA (4.5:1)": ratio >= 4.5,
        "ui_nao_texto_AA (3:1)": ratio >= 3.0,
    }


def simular_cvd(rgb, tipo):
    lin = [srgb_to_linear(c) for c in rgb]
    m = MACHADO_10[tipo]
    sim = [sum(m[i][j] * lin[j] for j in range(3)) for i in range(3)]
    return tuple(linear_to_srgb(c) for c in sim)


def rgb_to_lab(rgb):
    r, g, b = (srgb_to_linear(c) for c in rgb)
    x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
    xn, yn, zn = 0.95047, 1.0, 1.08883

    def f(t):
        return t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e76(rgb1, rgb2):
    l1, l2 = rgb_to_lab(rgb1), rgb_to_lab(rgb2)
    return sum((a - b) ** 2 for a, b in zip(l1, l2)) ** 0.5


def cmd_contraste(args):
    rgb1, rgb2 = hex_to_rgb(args[0]), hex_to_rgb(args[1])
    ratio = razao_contraste(rgb1, rgb2)
    print(f"contraste {args[0]} sobre {args[1]}: {ratio:.2f}:1")
    for nome, ok in vereditos_wcag(ratio).items():
        print(f"  {'PASSA ' if ok else 'REPROVA'} {nome}")


def avaliar_paleta(cores_hex):
    """Retorna o dict de resultado da paleta (usado pelo modo humano e --json)."""
    rgbs = [hex_to_rgb(c) for c in cores_hex]
    resultado = {"cores": cores_hex, "thresholds": {
        "colisao": DELTA_E_COLISAO, "alerta": DELTA_E_ALERTA,
        "metrica": "deltaE CIE76 sobre simulação Machado 2009 sev 1.0 em RGB linear"},
        "simulacoes": {}, "veredito": "OK"}
    cenarios = {"visao_tipica": None}
    cenarios.update({t: t for t in MACHADO_10})
    for nome, tipo in cenarios.items():
        sims = rgbs if tipo is None else [simular_cvd(rgb, tipo) for rgb in rgbs]
        pares = []
        for i in range(len(sims)):
            for j in range(i + 1, len(sims)):
                de = delta_e76(sims[i], sims[j])
                status = ("COLISAO" if de < DELTA_E_COLISAO
                          else "ALERTA" if de < DELTA_E_ALERTA else "ok")
                pares.append({"par": [cores_hex[i], cores_hex[j]],
                              "simulados": [rgb_to_hex(sims[i]), rgb_to_hex(sims[j])],
                              "deltaE": round(de, 1), "status": status})
        resultado["simulacoes"][nome] = pares
        if any(p["status"] == "COLISAO" for p in pares):
            resultado["veredito"] = "REPROVADA"
        elif resultado["veredito"] != "REPROVADA" and any(
                p["status"] == "ALERTA" for p in pares):
            resultado["veredito"] = "ALERTA"
    return resultado


def cmd_paleta(args):
    as_json = "--json" in args
    cores = [a for a in args if not a.startswith("--")]
    if len(cores) < 2:
        sys.exit("paleta exige ao menos 2 cores")
    resultado = avaliar_paleta(cores)
    if as_json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return
    print(f"paleta ({len(cores)} cores) — veredito: {resultado['veredito']}")
    print(f"thresholds declarados: colisão ΔE<{DELTA_E_COLISAO}, "
          f"alerta ΔE<{DELTA_E_ALERTA} (CIE76; decisão da skill, sem padrão de mercado)")
    for cenario, pares in resultado["simulacoes"].items():
        ruins = [p for p in pares if p["status"] != "ok"]
        print(f"  {cenario}: {len(pares) - len(ruins)}/{len(pares)} pares ok"
              + (" (tritanopia aproximada; rigor = Brettel/DaltonLens)"
                 if cenario.startswith("tritanopia") else ""))
        for p in ruins:
            print(f"    {p['status']}: {p['par'][0]} × {p['par'][1]} "
                  f"(ΔE {p['deltaE']}, vistos como {p['simulados'][0]} × {p['simulados'][1]})")


def cmd_paletas(_args):
    for nome, info in PALETAS_SEGURAS.items():
        print(f"{nome}: {info['descricao']}")
        print(f"  {' '.join(info['cores'])}")
    print("contínuo: viridis/cividis (nativos em matplotlib/plotly/d3)")


def main():
    cmds = {"contraste": cmd_contraste, "paleta": cmd_paleta, "paletas": cmd_paletas}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
