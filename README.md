# cão-guia 🦮

Skill do Claude Code que **valida, verifica, sugere, ajusta e audita acessibilidade visual** (baixa visão, cegueira e daltonismo) em material com interface visual, com o contexto normativo brasileiro embutido.

O nome diz o método: guiar o material até ficar acessível, no modelo social (a barreira está no material, nunca na pessoa).

## O que ela cobre

| Entrada | Motor |
|---|---|
| Web: URL viva ou HTML local/protótipo | axe-core (+ IBM Equal Access como 2º motor) |
| Documentos: PDF, docx, pptx, xlsx | veraPDF/Matterhorn + checks OOXML próprios |
| Data viz, paletas e peças estáticas | pipeline próprio de cor (contraste WCAG + simulação de daltonismo Machado 2009 + veredito ΔE) |

Fora de escopo: mobile nativo, vídeo/audiodescrição, EPUB e e-mail HTML.

## O que a diferencia

- **Motor primeiro, LLM depois**: todo achado carrega proveniência (`[motor]`, `[incomplete → triado]`, `[heurística LLM]`).
- **Honestidade de cobertura**: o relatório declara que varredura automática cobre só ~30-40% dos critérios WCAG e lista o que não foi verificado.
- **Brasil por default**: LBI art. 63, ABNT NBR 17225:2025 (mapeamento autoral), WCAG 2.2 pt-BR, ramo eMAG para `.gov.br`, números do IBGE com fonte e ano.
- **Correção com prova**: diagnóstico → lote aprovado → aplicar → re-scan com diff vs. baseline. Gate duro em cor de marca e mudança estrutural.
- **Não emite laudo**: auditoria assistida com disclaimer fixo; certificação de conformidade não existe aqui.

## Como invocar

A skill **sugere sempre, mas só executa quando chamada**:

- `/cao-guia` ou nominalmente: "usa o cão-guia nesse deck", "manda o cão-guia auditar https://…";
- por regra de projeto que você declarar ("neste projeto, revisão de acessibilidade é com a cao-guia");
- por plano aprovado que cite a skill.

Pedidos genéricos de acessibilidade não a disparam; o Claude apenas menciona que ela existe.

## Instalação

```bash
git clone https://github.com/beralzir/cao-guia ~/.claude/skills/cao-guia
```

Núcleo funciona só com `node`/`npx` + Python 3 (sem dependências). Extras opcionais (o preflight informa o que falta e o que fica degradado):

```bash
python3 ~/.claude/skills/cao-guia/scripts/preflight.py
pip install python-docx python-pptx openpyxl   # documentos Office
pip install daltonlens pillow                   # CVD avançado + imagem raster
# veraPDF (Java) para PDF/UA: https://verapdf.org
```

## Arquivos

- `SKILL.md`: fluxo, modos (auditar/sugerir/ajustar), escopo e regras.
- `references/`: motores e roteamento, normas BR, cor/daltonismo, documentos, checklist manual, contrato do relatório.
- `scripts/`: utilitários de apoio (preflight de ambiente, cor/contraste, auditoria de documentos Office, diff de re-scan).
- `assets/template-relatorio.html`: template do relatório acessível (claro/escuro/print, zero JS).

## Licença

MIT. Os motores externos (axe-core, IBM Equal Access, veraPDF) são invocados via CLI e mantêm suas próprias licenças; nada é vendorizado neste repo.
