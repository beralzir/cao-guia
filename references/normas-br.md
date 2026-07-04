# Normas e contexto Brasil

Ler quando: montar a seção normativa de qualquer relatório, ou quando o material auditado for brasileiro (default do cão-guia).

## O tripé normativo (citar nos três em todo relatório BR)

1. **LBI, Lei 13.146/2015, art. 63**: acessibilidade é obrigatória em sites "mantidos por empresas com sede ou representação comercial no País ou por órgãos de governo". O §1º exige exibição do símbolo de acessibilidade em destaque. Atenção à honestidade jurídica: o art. 63 **não foi regulamentado** (não há nível mínimo oficial, órgão fiscalizador nem multa administrativa automática); o enforcement real acontece via ação civil pública do MP e ações individuais. Nunca escrever "multa de X pela LBI" sem processo citável.
2. **ABNT NBR 17225:2025** (março/2025): primeira norma técnica brasileira de acessibilidade web, ~150 requisitos/recomendações baseados na WCAG 2.2, com níveis de conformidade próprios. A norma é **paga e protegida por copyright**: o mapeamento requisito↔WCAG usado pelo cão-guia é autoral e aproximado; nunca transcrever trechos da norma no relatório ou no repo. Quando precisar do texto exato, apontar o usuário para a loja da ABNT.
3. **WCAG 2.2 (W3C, out/2023)** com a tradução autorizada pt-BR: base técnica de tudo. Todo achado sai com critério de sucesso (número + nome em pt-BR + nível A/AA/AAA). URLs estáveis: `w3.org/TR/WCAG22/` e `w3.org/Translations/WCAG22-pt-BR/`.

Alvo de conformidade default do relatório: **WCAG 2.2 AA**, com nota de equivalência para WCAG 2.1 AA (exigido por EAA/EN 301 549 na UE e ADA Title II nos EUA) quando o material tiver público internacional.

## Ramo órgão público (.gov.br)

Ativar automaticamente quando o domínio for `.gov.br` (ou o usuário sinalizar órgão público). Somar ao tripé:
- **eMAG 3.1** (2014, base WCAG 2.0): formalmente obrigatório nos sites do governo federal (SISP) pela Portaria nº 3/2007; tecnicamente defasado, juridicamente vigente. Declarar o conflito eMAG × NBR 17225 em vez de escolher em silêncio.
- Decreto 5.296/2004 art. 47; LAI (Lei 12.527/2011) art. 8º §3º VIII; Acórdão TCU 2.099/2025 (auditoria de acessibilidade em 288 órgãos) como precedente de cobrança.

## Itens que nenhuma ferramenta internacional cobre (checar sempre em material BR)

- Símbolo de acessibilidade em destaque (LBI art. 63 §1º).
- Libras: presença/qualidade de VLibras ou equivalente quando o público exigir (Lei 10.436/2002). Nota: Libras é pauta de deficiência auditiva; registrar como observação, não como achado do escopo visual.
- Conteúdo, rótulos e mensagens de erro em pt-BR corretos (leitor de tela em português pronuncia mal texto em inglês não marcado com `lang`).

## Números de impacto (com fonte e ano; verificados em 2026-07)

- Censo IBGE 2022 (divulgação amostra, mai/2025): **14,4 mi de pessoas com deficiência** (7,3% da população 2+); dificuldade de enxergar é a mais comum, **~7,9 mi**.
- Réguas não-somáveis (anéis concêntricos, nunca somar): 7,9 mi funcional (IBGE) ≠ ~1,5 mi cegos + ~6 mi baixa visão (clínico CBO/OMS) ≠ 144 mi com problema de visão corrigível (TAM óptico ABIÓPTICA).
- Daltonismo: **~8% dos homens e ~0,5% das mulheres** (estimativa OMS; não há dado oficial IBGE). Deuteranomalia é o tipo mais comum.
- Analfabetismo entre PcD: 21,3% (4× a taxa de quem não tem deficiência) — reforça linguagem clara e voz, embora "linguagem simples" esteja fora do escopo V1 (registrar como nota quando relevante).
- Benchmark nacional: só **2,9% dos sites brasileiros** passaram em todos os testes automáticos (BigDataCorp + Movimento Web para Todos, edição 2024). Bom para calibrar expectativa e dar peso ao relatório.

## Validade dos fatos

Esta página embute fatos datados (status do art. 63, edição do benchmark, divulgações IBGE). Antes de citar em relatório para cliente, conferir se o fato mais sensível ainda vale (busca rápida); se este arquivo tiver mais de ~12 meses desde "verificados em", propor atualização ao usuário em vez de citar no automático.
