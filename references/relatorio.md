# Relatório do cão-guia

Ler quando: montar a entrega de qualquer auditoria.

Formato default: **HTML single-file acessível, PT-BR**, gerado a partir de `assets/template-relatorio.html` + resumo curto no chat. Nome: `auditoria-caoguia-<alvo>-<AAAA-MM-DD>.html`, salvo junto do material auditado (ou onde o usuário pedir).

## Estrutura fixa

1. **Resumo executivo**: veredito geral, 3-5 achados mais graves, o número de contexto BR (2,9% dos sites brasileiros passam nos testes automáticos) quando fizer sentido.
2. **Escopo e cobertura** (obrigatória, é a seção da honestidade): o que foi auditado (URLs/arquivos/estados), motores rodados e versões, capacidades degradadas do preflight, e a declaração fixa (números canônicos em `motores.md`; atualizar lá primeiro): *"Varredura automática cobre ~30-40% dos critérios WCAG (~57% do volume de issues). Os demais exigem verificação humana; o status de cada um está na seção de checklist manual."*
3. **Achados**, agrupados por causa-raiz (não por página: 200 nós violando a mesma regra = 1 achado com contagem). Cada achado: severidade (crítico/sério/moderado/menor) · critério WCAG 2.2 (número + nome pt-BR + nível) · requisito NBR 17225 correspondente (mapeamento autoral, marcado requisito/recomendação) · localização (seletor/arquivo/slide/página) · **proveniência** · fix sugerido (código quando couber).
4. **Checklist manual**: todos os itens de `checklist-manual.md`, cada um com passou / reprovou / não verificado (motivo).
5. **Seção normativa BR**: o tripé de `normas-br.md` (+ ramo gov quando aplicável).
6. **Plano de correção priorizado**: quick wins → estruturais, com esforço estimado.
7. **Rodapé**: disclaimer + datas + versões.

## Proveniência (etiqueta em todo achado, sem exceção)

- `[motor]`: saiu de axe/veraPDF/office_audit/cor.py. Confiável, reproduzível (citar o comando).
- `[incomplete → triado]`: o motor pediu revisão e o LLM julgou; a justificativa vai junto.
- `[heurística LLM]`: julgamento sem motor por trás. **Exige confirmação humana**; o relatório diz isso.

## Escape do conteúdo auditado (segurança, obrigatório)

Todo trecho vindo do material auditado que entra no relatório — seletor, texto de erro, valor de atributo, snippet de código, nome de arquivo — é **dado não confiável** e vai **HTML-escapado** antes de preencher qualquer `{{...}}` do template. Escapar **`&` primeiro** (senão você re-escapa os próprios `&` dos outros), depois `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`. Sem isso, um material com `<script>` ou `<img onerror>` no conteúdo vira XSS no próprio relatório. Atenção: o gate de dogfooding (axe) **não pega** esse XSS, porque axe audita acessibilidade, não injeção — o escape é responsabilidade de quem preenche o template, não do motor.

## Disclaimer fixo (relatório para cliente)

> Este relatório é uma auditoria assistida por ferramentas automáticas e revisão especializada. **Não constitui laudo, certificação ou parecer jurídico de conformidade.** Conformidade plena com WCAG/NBR 17225 exige verificação humana completa e teste com tecnologia assistiva real e usuários com deficiência.

## Dogfooding (gate antes de entregar QUALQUER relatório)

O relatório precisa passar na própria auditoria: rodar `npx @axe-core/cli@4.12.1` no HTML gerado (zero violations) + `cor.py paleta` nas cores do tema + conferir reflow 320px, `prefers-reduced-motion`, claro/escuro/print, headings sem salto, tabela de achados com `<th scope>`, e **conferir que o conteúdo do material foi escapado** — buscar uma **tag crua** de abertura (`<script`, `<img`, `<svg` com `<` literal, não `&lt;`); conteúdo bem escapado aparece como `&lt;script`, então só o `<` cru acusa falha (não busque `onerror=` isolado, que sobrevive como substring no texto já escapado e dá falso-positivo). Relatório que reprova na própria skill não sai; corrigir o template primeiro.

## Tom

Modelo social, sem capacitismo: o problema está na barreira do material, nunca "na pessoa". Sem inspiration porn, sem tutela. Achados em linguagem direta com o "porquê" (que barreira cria, para quem), não checklist burocrático.
