# Documentos: PDF, Word, PowerPoint, Excel

Ler quando: a entrada for PDF ou arquivo Office.

## PDF

**Triagem fail-fast** (pikepdf/pypdf, barata, sempre que o extra existir): o PDF tem `/MarkInfo` (é taggeado?), `/StructTreeRoot` (árvore de tags existe?), `/Lang` definido, `Title` preenchido + `DisplayDocTitle`? PDF sem tags já reprova na triagem: **a rota confiável é consertar o documento-fonte** (Word/PPT com estilos corretos) e re-exportar com "Document structure tags"; não existe auto-tagger open source decente e a skill não usa APIs cloud.

**Validação PDF/UA** (extra veraPDF): `verapdf --flavour ua1 arquivo.pdf --format json`. Parsear o JSON e mapear cada falha ao checkpoint do **Matterhorn Protocol 1.1** (31 checkpoints, 136 condições de falha; documento gratuito da PDF Association, é a espinha metodológica).

**Divisão máquina × humano do Matterhorn** (usar na estrutura do relatório): ~89 condições são verificáveis por máquina (delegar ao veraPDF e reportar como `[motor]`); ~45 exigem julgamento (qualidade de alt-text, ordem de leitura lógica, semântica de headings e TH/TD): fluxo assistido, com o LLM lendo o dump da tag tree (`pikepdf` ou `pdftl dump_tags`) e emitindo julgamento marcado `[heurística LLM]` para confirmação humana.

Tabelas em PDF: cabeçalhos como TH com `Scope` (Row/Column); mescladas exigem ColSpan/RowSpan espelhando o layout; ordem das tags segue a leitura visual.

## Office (docx/pptx/xlsx)

Motor: `scripts/office_audit.py` (reimplementa o subconjunto machine-checkable das regras públicas do checker da Microsoft; o checker oficial não tem CLI). Taxonomia erro/aviso/dica igual à da Microsoft. O que o script NÃO decide (e vira triagem LLM): qualidade do alt-text, ordem de leitura real, contraste dentro de temas do Office (fraco em toda ferramenta; marcar como verificação manual).

Regras-âncora por formato:
- **Word**: alt-text em toda imagem informativa (ou marcar decorativa); tabelas com "Repetir linha de cabeçalho"; headings sem salto de nível; título nos metadados.
- **PowerPoint**: título único e descritivo por slide (é o heading de navegação do leitor de tela); usar layouts embutidos (placeholders garantem ordem); ordem de leitura = ordem no spTree (conferir no Painel de Seleção, de baixo para cima); alt-text em imagens; tabela com header row ligado.
- **Excel**: abas com nome descritivo; dados em Tabelas reais com header row; evitar mescladas e linhas/colunas em branco; título em A1.

## Alt-text (árvore de decisão W3C/WAI, vale para tudo)

1. **Informativa** → alt objetivo, ≤ ~125 caracteres (ATs truncam), sem "imagem de".
2. **Decorativa** → alt vazio / "marcar como decorativa" / Artifact no PDF.
3. **Funcional** (imagem-link/botão) → descrever a ação, não a aparência.
4. **Complexa** (gráfico, infográfico) → alt curto com a mensagem + descrição longa adjacente (tabela de dados).

LLM gera alt como **rascunho, sempre**: 2 variantes (curta/longa) usando o contexto do documento, marcado `[heurística LLM]`, com aprovação humana antes de aplicar. O mesmo gráfico pede alt diferente em contextos diferentes.

## Correção em OOXML (modo ajustar)

Aplicável direto no XML: setar `descr` (alt), marcar decorativa, ligar header row, renomear abas, preencher título. **Roundtrip obrigatório**: depois de editar, reabrir o arquivo com a mesma lib e re-rodar o `office_audit.py`; se o arquivo não abre ou o achado persiste, reverter e reportar. Nunca editar OOXML de cliente sem backup do original ao lado (`arquivo.bak-caoguia`).
