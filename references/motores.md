# Motores e roteamento por formato

Ler quando: iniciar qualquer auditoria (define qual motor rodar) ou montar setup/preflight.

Regra de ouro: **motor determinístico primeiro, LLM depois** (para triar, deduplicar, explicar e julgar o que máquina não decide). LLM nunca é fonte primária de um achado marcado como `[motor]`.

## Matriz de roteamento

| Entrada | Núcleo (sempre) | Extras (se preflight OK) | Referência |
|---|---|---|---|
| URL viva | `npx @axe-core/cli` | Playwright p/ estados (modais, pós-login); IBM Equal Access (`npx achecker`) como 2º motor | esta página |
| HTML local / protótipo | `npx @axe-core/cli arquivo.html` + leitura do fonte pelo LLM | idem | esta página |
| PDF | triagem `pikepdf`/`pypdf` (MarkInfo, StructTreeRoot, Lang, Title) | `verapdf --flavour ua1 arquivo.pdf --format json` | `documentos.md` |
| docx / pptx / xlsx | `scripts/office_audit.py` | (não há; PAC/checker Office só em GUI, citar como passo manual) | `documentos.md` |
| Paleta / gráfico (código) | `scripts/cor.py paleta ...` + revisão do código de plot | DaltonLens p/ severidade parcial e tritanopia rigorosa | `cor-daltonismo.md` |
| Imagem raster (peça pronta) | leitura LLM + `cor.py` nas cores dominantes declaradas | DaltonLens + Pillow p/ simular a imagem inteira | `cor-daltonismo.md` |

Sempre rodar `scripts/preflight.py` antes da primeira auditoria da sessão; toda capacidade degradada entra na seção de cobertura do relatório.

## Comandos de referência

```bash
# web, mono-página (baixa o axe no primeiro uso)
npx @axe-core/cli <url> --tags wcag2a,wcag2aa,wcag21aa,wcag22aa --save axe.json

# segundo motor (regras genuinamente diferentes; aceita diretório de HTML local)
npx achecker <url-ou-diretório>

# multi-página: loop simples sobre lista de URLs com limite declarado (default 10)
# PDF/UA
verapdf --flavour ua1 arquivo.pdf --format json

# loop de correção (baseline → fix → prova)
python3 scripts/axe_diff.py baseline.json depois.json
```

Pegadinhas do axe-cli (aprendidas na prática):
- **Arquivo local**: passar URL `file:///caminho/absoluto.html`; caminho relativo vira `http://` e falha com ERR_NAME_NOT_RESOLVED.
- **ChromeDriver × Chrome dessincronizados** (erro "only supports Chrome version N"): rodar `npx browser-driver-manager install chrome` (instala o par casado em `~/.browser-driver-manager/`, sem tocar no Chrome do sistema) e passar `--chrome-path`/`--chromedriver-path` com os caminhos que ele imprime.
- **Extensão não-`.html`** (backups `.bak`, cópias): o Chrome serve como texto puro e o axe audita um DOM sintetizado vazio, gerando falsos achados (`document-title`). Auditar sempre uma cópia byte-idêntica renomeada para `.html` (conferir hash) e declarar isso na cobertura.
- **Auditoria nunca modifica o alvo**: em material de cliente, registrar hash antes/depois como prova.

## Buckets do axe (tratar diferente, nunca misturar)

- `violations` → achado `[motor]`, confiável (axe tem política de zero falso positivo).
- `incomplete` → **onde moram os problemas reais que pipelines ignoram**: triar item a item com o LLM (ex.: contraste sobre imagem de fundo) e reportar como `[incomplete → triado]` com o julgamento explicado.
- `passes`/`inapplicable` → só para estatística de cobertura.

## Honestidade de cobertura (obrigatória em todo relatório)

Ferramentas automáticas cobrem ~30-40% dos critérios WCAG (~57% do volume de issues, estudo Deque; melhor ferramenta isolada achou ~40% no benchmark GDS). O resto (teclado, ordem de leitura, qualidade de alt/rótulo/erro, uso real com leitor de tela) é julgamento: ver `checklist-manual.md`. O relatório declara os dois números e lista o que não foi verificado.

## Licenças (regra: invocar via CLI, nunca vendorizar)

| Ferramenta | Licença | Pode? |
|---|---|---|
| axe-core / @axe-core/cli | MPL-2.0 | invocar via npx: sim; copiar código pro repo: não |
| IBM Equal Access | Apache-2.0 | invocar: sim |
| veraPDF | GPLv3+/MPLv2 | invocar CLI: sim |
| Pa11y | LGPL-3.0 | invocar: sim; vendorizar: não (preferir axe direto) |
| apca-w3 | restrita (uso WCAG-web) | usar como guia conceitual; não redistribuir |
| Chartability | CC-BY-SA | citar e linkar; não copiar o workbook |
| Lighthouse | Apache-2.0 | não usar para a11y (subconjunto do axe; score confunde) |
| WAVE API | paga | fora; extensão citável como passo manual |

## Privacidade

Processamento 100% local: nenhum documento ou URL de cliente vai para API cloud de terceiros (nada de Adobe Auto-Tag e afins). Se um dia entrar rota cloud, é decisão explícita do usuário, nunca default.

Pós-login: quem autentica é o usuário (sessão/storage state fornecido por ele). A skill nunca solicita, armazena ou registra credenciais em log, baseline ou relatório.
