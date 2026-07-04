# Checklist do não-automatizável (o complemento do que os motores cobrem; números em `motores.md`)

Ler quando: fechar qualquer auditoria. Os motores param em ~30-40% dos critérios WCAG; o que está aqui é o resto. Para cada item: o LLM pré-julga com a evidência que tiver (DOM, fonte, dump de tags) e marca `[heurística LLM]`; o que exigir interação real vira "confirmar com humano/AT" no relatório. Nunca omitir um item: passou, reprovou ou **não verificado** (com motivo).

## Interação e navegação
1. **Teclado ponta-a-ponta** (2.1.1/2.1.2): tudo alcançável e operável por Tab/Enter/Esc; sem armadilha de foco. LLM checa `tabindex`, handlers só-mouse; interação real = humano.
2. **Ordem de foco** (2.4.3) e **foco visível** (2.4.7): sequência lógica, indicador com contraste ≥ 3:1.
3. **WCAG 2.2 novos, que os motores cobrem mal**: 2.4.11 foco não obscurecido (sticky headers/banners por cima do foco); 2.5.7 arrastar tem alternativa de clique; 2.5.8 alvo ≥ 24×24 px (medir bounding box via DOM quando houver browser); 3.2.6 ajuda consistente; 3.3.7 sem re-digitação de dado já informado; 3.3.8 login sem teste cognitivo.

## Conteúdo e semântica
4. **Qualidade de alt-text** (1.1.1): pertinente ao contexto? (a presença o motor pega; a qualidade não). Ver árvore em `documentos.md`.
5. **Propósito do link** (2.4.4): nada de "clique aqui"/"saiba mais" soltos.
6. **Ordem de leitura** (1.3.2): DOM/tag tree/spTree na ordem visual.
7. **Mensagens de erro** (3.3.1/3.3.3): identificam o campo e dizem como corrigir.
8. **Idioma** (3.1.1/3.1.2): `lang="pt-BR"` no raiz e marcação de trechos em outro idioma.
9. **Sentido só por cor no contexto** (1.4.1): "campos em vermelho são obrigatórios" sem outro canal.

## Baixa visão (além de contraste)
10. **Zoom/reflow** (1.4.4/1.4.10): 200% sem perda; utilizável a 320px de largura sem scroll 2D. Exige browser renderizando; sem browser, marcar não verificado.
11. **Text spacing** (1.4.12): nada quebra com line-height 1.5×, letter-spacing 0.12×, word-spacing 0.16×, parágrafo 2×.
12. **Movimento** (2.2.2/2.3.3): autoplay > 5s tem pausa; animações respeitam `prefers-reduced-motion`.
13. **Modos do SO**: comportamento decente sob `prefers-contrast` e `forced-colors` (checagem de CSS; teste real = humano).

## Data viz (metodologia inspirada no Chartability, citado e linkado, não copiado)
14. Título/mensagem do gráfico em texto; tabela de dados adjacente; eixos e unidades legíveis (≥ 12px); redundância além da cor em toda série; legenda perto dos dados (ou rótulo direto); interativo navegável por teclado. Referência: Chartability (Frank Elavsky), github.com/Chartability/POUR-CAF.

## Teste assistivo real (sempre recomendado, nunca simulado)
15. Roteiro mínimo VoiceOver em pt-BR (macOS: Cmd+F5; navegar por headings VO+Cmd+H, formulários, imagens): a skill **recomenda e roteiriza**, não finge ter feito. Padrão-ouro: teste com usuários reais cegos/baixa visão ("nada sobre nós sem nós"); registrar como recomendação no relatório de material de alto impacto.
