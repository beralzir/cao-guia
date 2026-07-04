# Cor, contraste e daltonismo

Ler quando: auditar ou ajustar paletas, gráficos, temas, peças estáticas, ou qualquer achado de contraste.

## Política de contraste (fixa; declarar no relatório)

- **Critério de conformidade: WCAG 2.x** (razão de luminância): texto normal ≥ 4,5:1 (AA) / 7:1 (AAA); texto grande (≥ 18pt ou 14pt bold) ≥ 3:1 (AA) / 4,5:1 (AAA); componentes de UI e gráficos não-textuais ≥ 3:1 (SC 1.4.11). Calcular com `scripts/cor.py contraste`.
- **APCA/Lc é só guia de design** (WCAG 3 candidato; sensível a tamanho, peso e polaridade; licença restrita a uso WCAG-web). Quando um par passa WCAG e "parece ruim" (ou o inverso), explicar a divergência citando APCA conceitualmente, sem transformar Lc em veredito de conformidade. Exemplo real das divergências: `#B0B0B0` sobre `#1E1E1E` passa AAA (7,69:1) e reprova no APCA; branco sobre `#777777` reprova AA (4,48:1) e passa no APCA.
- WCAG 2 ignora polaridade e fonte: usar isso como argumento para o dual-track, não para afrouxar o gate.

## Simulação de daltonismo

- Motor embutido: `scripts/cor.py paleta` (Machado 2009 sev 1.0, **em RGB linear**; a linearização sRGB é inegociável, pular gamma é o erro nº 1 das libs abertas).
- Tritanopia do cor.py é aproximada (marcada `tritanopia~`); rigor exige Brettel 1997 → extra DaltonLens.
- Severidade parcial (tricromacia anômala, o caso mais comum na prática) exige Machado com severidade → extra colorspacious/DaltonLens.
- Imagem raster inteira: só com extra (DaltonLens + Pillow). Sem o extra, não emitir veredito de cor sobre screenshot: medir pixel em raster é instável (antialiasing, gradiente, subpixel). Quando o usuário fornecer as cores da paleta (hex), auditar as cores declaradas e dizer que foi isso que se auditou.
- Threshold de distinguibilidade: ΔE CIE76 sobre pares simulados; < 10 colisão, 10-20 alerta, ≥ 20 ok. Decisão de engenharia da skill (não há padrão de mercado); citar sempre.

## Prevalência (para dimensionar impacto no relatório)

~8% dos homens, ~0,5% das mulheres (vermelho-verde, ligado ao X). Deuteranomalia é o tipo mais comum; tritanopia é raríssima (mas barata de checar junto). Fonte OMS; sem dado IBGE.

## Paletas seguras embutidas

`scripts/cor.py paletas`: Okabe-Ito (categórico, padrão Nature Methods), Paul Tol bright/muted. Contínuo: viridis/cividis (nativos nas libs de plot; cividis é otimizado para deuteranopia). Divergente: RdBu do ColorBrewer ou Tol sunset. Proibir escalas vermelho-verde para divergente.

## Regra de redundância (SC 1.4.1, auditável sempre)

Cor nunca é o único canal. Toda distinção por cor precisa de segundo canal: forma/marcador, padrão/hachura (`hatch` no matplotlib, `pattern_shape` no plotly), tracejado, espessura, ou rótulo direto. Mesmo paleta segura falha em gráfico denso; a redundância é o que segura. Nenhuma ferramenta automatiza esse julgamento: é checagem LLM marcada `[heurística LLM]` + confirmação humana.

## Defaults ao GERAR ou corrigir material visual

- Categórico: Okabe-Ito (máx. 8 categorias; acima disso, repensar o gráfico).
- Corpo de texto 16px+, eixos/ticks ≥ 12px (matplotlib default 10pt é pequeno), line-height 1.5.
- Todo gráfico com alternativa não-visual: tabela de dados adjacente + `aria-label` com a mensagem do gráfico (não a descrição literal dos marks).
- Foco visível (`:focus-visible` com outline ≥ 2px e contraste 3:1), nunca `outline: none` sem substituto.
- Animação sempre dentro de `@media (prefers-reduced-motion: reduce)` com estado final estático idêntico.
- Dark mode: superfície ~`#121212` (não preto puro), texto off-white (não `#FFF` puro), séries dessaturadas; revalidar contraste no tema escuro (não herda do claro).
- Reflow: HTML utilizável a 320px de largura sem scroll horizontal (SC 1.4.10); conteúdo largo em container próprio com `overflow-x: auto`.
