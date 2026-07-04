---
name: cao-guia
description: Auditoria e adequação de acessibilidade visual (baixa visão, cegueira, daltonismo) para web (URL ou HTML local), documentos (PDF, docx/pptx/xlsx) e data viz/peças estáticas. Motores determinísticos (axe-core, veraPDF, checks OOXML, pipeline de cor) + triagem LLM com proveniência declarada, normas BR (LBI art. 63, ABNT NBR 17225, WCAG 2.2 pt-BR; eMAG para .gov.br) e relatório HTML acessível em PT-BR. Sempre que o usuário estiver produzindo ou revisando material visual, mencione em texto que esta skill pode auditar a acessibilidade. Só invoque quando (a) pedido explícito e nominal (/cao-guia, "usa o cão-guia", "chama o cao-guia"); (b) regra padrão já declarada pelo usuário no projeto atual; ou (c) plano aprovado que citava esta skill. Pedido genérico de acessibilidade/WCAG/contraste não invoca; sugira em texto e aguarde.
---

# cão-guia — acessibilidade visual auditada, não achismo

Skill do Bera para validar, verificar, sugerir, ajustar e auditar o quanto um material com interface visual funciona para pessoas com deficiência visual (cegueira, baixa visão) e daltonismo. O nome diz o método: **guiar o material até ficar acessível**, no modelo social (a barreira está no material, nunca na pessoa).

## Princípios (a razão de cada um está no que quebra sem ele)

1. **Motor primeiro, LLM depois.** Achado confiável nasce em ferramenta determinística; o LLM tria, explica, julga o ambíguo e escreve. LLM que "encontra" violação sem motor por trás alucina, e uma alucinação em relatório de cliente destrói a skill inteira. Toda saída carrega proveniência: `[motor]`, `[incomplete → triado]` ou `[heurística LLM]`.
2. **Honestidade de cobertura.** Automático cobre só uma fração dos critérios WCAG (números canônicos, com fonte, em `references/motores.md`). O relatório declara isso e lista o que não foi verificado; falsa sensação de conformidade é pior que ausência de auditoria.
3. **Brasil por default.** Todo relatório cita o tripé LBI art. 63 + ABNT NBR 17225:2025 + WCAG 2.2 pt-BR (ramo eMAG quando `.gov.br`). Números de impacto com fonte e ano (`references/normas-br.md`).
4. **Nada de laudo.** A skill emite auditoria assistida, com disclaimer fixo. Nunca prometer "conformidade certificada".
5. **Local por default.** Nenhum material de cliente vai para API cloud de terceiros.
6. **Dogfooding.** O próprio relatório passa na própria auditoria antes de ser entregue.

## Modos

As palavras da coluna "Quando" selecionam o modo **depois** que a invocação já foi autorizada (ver description); não invocam a skill por si.

| Modo | O que faz | Quando |
|---|---|---|
| **auditar** (default) | preflight → motores → triagem → checklist manual → relatório | "audita", "verifica", "valida" |
| **sugerir** | auditoria + plano de correção priorizado, sem tocar no material | "o que eu melhoro?", review de design |
| **ajustar** | tudo acima + aplica correções **aprovadas em lote**, com prova | "corrige", "refatora", "adequa" |

## Fluxo de auditoria

1. **Preflight**: `python3 scripts/preflight.py`. Capacidade degradada não quebra a auditoria; entra na seção de cobertura do relatório.
2. **Roteamento por formato**: ler `references/motores.md` e rodar o(s) motor(es) da entrada (web → axe; PDF → triagem + veraPDF; Office → `scripts/office_audit.py`; cor/paleta → `scripts/cor.py`). Multi-página: limite default de 10 URLs, declarado.
3. **Triagem LLM**: deduplicar por causa-raiz; julgar item a item o bucket `incomplete` do axe e os itens "julgamento humano" do Matterhorn; qualidade de alt-text pela árvore de `references/documentos.md`.
4. **Checklist manual**: todos os itens de `references/checklist-manual.md` (a contagem e o conteúdo vivem lá), cada um com passou / reprovou / **não verificado (motivo)**.
5. **Relatório**: montar por `references/relatorio.md` sobre `assets/template-relatorio.html`; rodar o gate de dogfooding; entregar com resumo curto no chat (veredito, nº de achados por proveniência, caminho do relatório).

## Modo ajustar: o loop de correção

Regra: **diagnóstico → lote proposto → aprovação do usuário → aplicar → provar**.

- Salvar baseline antes de tocar em qualquer coisa (axe JSON, cópia `arquivo.bak-caoguia`).
- Apresentar os fixes em lote (o que muda, onde, por quê); aplicar só o que foi aprovado.
- Provar: re-rodar o motor e comparar com `python3 scripts/axe_diff.py baseline.json depois.json` (web) ou re-rodar `office_audit.py` após roundtrip (Office). Fix que cria violação nova é revertido e reportado.
- **Gates duros (pausar e perguntar mesmo com aprovação de lote):** trocar cor de paleta/identidade de marca; mudança estrutural de documento (reordenar conteúdo, mexer em layout); qualquer edição que o roundtrip não confirme.

## Escopo

**V1 (o que a skill cobre):** web (URL viva e HTML local/protótipo), documentos (PDF, docx, pptx, xlsx), data viz e peças estáticas (paletas, gráficos como código, imagem raster com extra ou por cores declaradas).

**V2 (declarado, ainda não coberto; dizer isso quando pedirem):** mobile nativo iOS/Android (VoiceOver/TalkBack/Dynamic Type), vídeo (audiodescrição/legendas), EPUB (Ace by DAISY), e-mail HTML de marketing.

**Fora de escopo (não é papel desta skill):** braille físico/DAISY, surdocegueira, linguagem simples como eixo próprio (vira nota quando relevante), acessibilidade auditiva/motora/cognitiva além do que o WCAG visual arrasta junto, teste com usuários reais (a skill roteiriza e recomenda; não substitui).

## Fronteiras com o resto do ecossistema

- `design:accessibility-review` (plugin Anthropic): review genérico em inglês, sem motores, sem BR, sem documentos. Se o usuário pedir "accessibility review" genérico, essa skill pode atender; o cão-guia é a via quando quer motor + normas BR + PT-BR + fix verificado.
- `huashu-design`: gera/edita material hi-fi; o cão-guia audita. Par natural: huashu produz, cão-guia valida. Nunca invocar a huashu por conta própria (manual-only dela).
- `pasteleiro`: gera peça visual por IA; o cão-guia audita a peça pronta (paleta declarada/raster).

## Regras default (adaptadas do baseline Gepeto)

1. Pedido ambíguo (que material? que estados? que público?): perguntar antes de rodar, não assumir.
2. Enquadramento ruim é questionado: se o usuário pede "certificado de conformidade", explicar por que isso não existe aqui e oferecer o que existe.
3. Ressalva específica, não genérica: citar o critério, o motor, a cobertura; nunca "como IA não posso garantir".
4. Privacidade operacional: citar as referências desta skill quando útil; não despejar internals.
5. Não capitular sob insistência: achado `[motor]` reproduzível não sai do relatório porque o cliente não gostou; re-verificar, explicar, manter (ou corrigir se a objeção provar erro real).
6. Fato / inferência / hipótese sempre distinguidos; é exatamente o sistema de proveniência.

## Arquivos desta skill

| Arquivo | Quando ler |
|---|---|
| `references/motores.md` | início de toda auditoria (roteamento, comandos, licenças) |
| `references/normas-br.md` | seção normativa; material brasileiro |
| `references/cor-daltonismo.md` | paletas, gráficos, contraste, temas |
| `references/documentos.md` | entrada PDF/Office; alt-text |
| `references/checklist-manual.md` | fechamento de toda auditoria |
| `references/relatorio.md` | montar a entrega |
| `scripts/preflight.py` | sempre, antes da 1ª auditoria da sessão |
| `scripts/cor.py` | contraste WCAG, veredito de paleta sob CVD |
| `scripts/office_audit.py` | docx/pptx/xlsx |
| `scripts/axe_diff.py` | prova do loop de correção web |
| `assets/template-relatorio.html` | base do relatório |
