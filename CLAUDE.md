# Cockpit de Afiliação IA-First — Papai Resolve

Contexto que toda sessão do Claude neste repositório deve carregar
primeiro. Leia isto e `HISTORICO.md` antes de responder qualquer coisa
sobre o projeto — evita reexplicar do zero a cada conversa nova.

## O que é

Cockpit de afiliação pra @papairesolve_br (Shopee, nicho casa &
construção). Meta: R$10.000/mês de comissão, ROI mínimo 3x. O usuário
(dono do projeto) não é técnico, usa celular/navegador, prefere resolver
tudo puxando o Claude em vez de mexer em código ou infraestrutura.

## Como trabalhamos (modelo operacional — confirmado pelo usuário em 30/08)

- **Conversa, decisão e "o que fazer agora"**: aqui, com o Claude, numa
  sessão de chat. O Claude é a cabeça pensante — mantém o histórico e
  guia o passo a passo de forma objetiva.
- **Tudo visual/interativo** (fotos de produto, marcar seleção, gráfico
  de ROI): fica no `painel.html` e nas outras páginas do
  `cockpit-shopee/`, publicadas no GitHub Pages, tudo versionado no
  GitHub. O Claude não tenta recriar isso em texto — aponta pro link.
- **Regra explícita (usuário, 31/08): a relação/lista de produtos
  NUNCA é exibida em texto/tabela no chat.** Quando o usuário pedir pra
  ver os produtos (da leva, de uma busca, etc.), a resposta é sempre o
  link do `painel.html` (ou da página relevante) — nunca listar item a
  item aqui. Pode comentar destaques pontuais (ex: "o #7 tem prova
  social forte") sem recriar a lista inteira.
- **Toda decisão e marco importante entra em `HISTORICO.md`**, com
  data. Ao começar uma sessão nova, releia esse arquivo antes de agir.
- A sessão do Claude tem uma restrição de rede: não acessa a API da
  Shopee nem carrega imagens externas diretamente. Pra buscar um
  produto específico sob demanda, dispare o workflow
  `.github/workflows/busca-manual.yml` (via `actions_run_trigger`,
  input `termo`) e leia o resultado nos logs do job.
- **Decisão de 31/08: o cockpit roda na Vercel.** O usuário pediu uma
  conexão de verdade entre o painel (onde ele seleciona produtos) e o
  Claude — decidiu usar a Vercel em vez do fluxo manual por GitHub
  Issues. O botão "Salvar seleção agora" no `painel.html` acrescenta
  (não sobrescreve) a seleção em `cockpit-shopee/esteira.json` (via
  `api/selecionar.js`, que escreve no GitHub usando um `GITHUB_TOKEN`).
  `esteira.html` mostra o status de cada produto (selecionado /
  impulsionado / vendido), calculado cruzando com o financeiro.
- Chat (`chat.html` + `api/chat.js`) e busca ao vivo no site
  (`api/buscar_produto.py`) também rodam na Vercel — todos os três
  (chat, busca, seleção) dependem do deploy estar ativo.
- `importar.html` tem um campo de **upload de arquivo** (relatório de
  vendas Shopee, extrato/print do Meta Ads) — envia pro GitHub em
  `financeiro/importados/` via `api/importar_arquivo.js`, sem tentar
  parsear automaticamente (formato varia demais). Quando o usuário
  avisar que subiu um arquivo, leia-o de lá e converta pros CSVs de
  `financeiro/` (investimentos.csv / vendas.csv) você mesmo.

## Onde as coisas estão

- `cockpit-shopee/README.md` — visão geral técnica de cada arquivo e
  workflow.
- `cockpit-shopee/leva_do_dia.md` — leva de produtos do dia (atualizada
  às 9h por `leva-diaria.yml`).
- `cockpit-shopee/financeiro/` — investimento e vendas (import manual,
  não automatizado — ver decisão em `HISTORICO.md`).
- `cockpit-shopee/financeiro/resumo.json` — resumo do ROI em JSON.
- `cockpit-shopee/esteira.json` — lista viva (acumulada, não
  sobrescrita) de todos os produtos já selecionados no painel; leia
  antes de gerar roteiro ou responder sobre o que já foi selecionado.
  Cada item tem dois eixos de status independentes: financeiro
  (selecionado/impulsionado/vendido, calculado sozinho cruzando com o
  financeiro) e `etapa_conteudo` (roteiro_pronto/em_producao/publicado,
  atualizado manualmente pelo usuário no seletor de `esteira.html`, via
  `api/atualizar_esteira.js`). Desde 01/09 cada item também guarda
  `narracao` e `legenda` (o texto pronto pra gravação e pra legenda do
  post, gerados no momento da seleção — ver "Padrão de narração e
  legenda dos Reels" abaixo).
- `cockpit-shopee/esteira.html` — visão da esteira com status financeiro
  calculado automaticamente (selecionado / impulsionado / vendido),
  cruzando `esteira.json` com o financeiro, mais um seletor manual de
  etapa de conteúdo por produto, os textos de narração/legenda prontos
  pra copiar ("Ver textos"), um botão pra excluir produto ainda não
  publicado (`api/excluir_esteira.js`, bloqueado no servidor pra produto
  já publicado) e um guia embutido do processo
  roteiro→gravação→edição→publicação→avaliação (deixa claro que gravar,
  editar e publicar são passos manuais do usuário — o Claude não grava
  vídeo nem publica sozinho, não há integração com API do Meta/TikTok
  configurada).
- Pedido do usuário em 01/09: o filtro de qualidade (comissão mínima,
  avaliação mínima) não corta mais produto do nicho antes da leva — a
  leva traz todos os produtos do nicho casa & construção, e o filtro
  acontece interativamente no painel, no momento da seleção (selects de
  comissão mínima / avaliação mínima em `painel.html`, combináveis com o
  filtro de faixa de preço). Pedido em 02/09: revertido o "todos" por
  volume — a leva agora traz só os **50 melhores** do nicho, por score
  de curadoria (`LIMITE_LEVA` em `buscar_leva_lancamento.py`); o filtro
  de qualidade continua interativo, no painel.
- Pedido do usuário em 02/09: "o fluxo mais fácil vai ser achar o
  produto no app Shopee e trazer pro agente" — a busca por descrição
  **ou link colado** do produto (usa `shopee_integration/link_resolver.py`,
  compartilhado com `buscar_um_produto.py`) subiu pro topo do
  `painel.html`, acima da leva do dia, em vez de ficar embaixo da
  tabela. Todo produto marcado — venha da leva, da busca por link ou
  por descrição, ou de `produtos_manuais.txt` — usa os mesmos
  `montarRoteiro()`/`montarLegenda()` no momento de salvar, então
  sempre sai com narração e legenda prontas na esteira, sem exceção.
- Links publicados: GitHub Pages em
  `https://pcollichio.github.io/AGENTE-SHOPEE/cockpit-shopee/cockpit.html`
  (e `/painel.html`, `/painel_roi.html`, etc.)

## Padrão de narração e legenda dos Reels (fixado em 31/08, legenda em 01/09)

Todo roteiro gerado (pelo painel ou a pedido no chat) segue este modelo:
**narração em voz de jovem** (nem criança, nem adolescente), sempre
abrindo com a frase fixa "Meu papai sempre resolve tudo aqui em casa!",
depois a dor de um problema de casa, a solução com o produto, fechando
com call to action. Estrutura de 5 blocos (~24s, ajustada em 01/09):
Abertura (frase fixa) → Dor → Solução (o Papai acha o produto) → Prova
(visual, sem falar) → Call to action. Implementado em `GANCHOS_ROTEIRO`
e `montarRoteiro()` em `shopee_integration/painel.py` — se o usuário
pedir um roteiro pontual no chat, siga esse mesmo modelo.

A **legenda do post** segue o mesmo padrão de abertura, gerada junto com
o roteiro a partir do mesmo `GANCHOS_ROTEIRO` (mesma dor/motivo): (1) a
frase fixa "Meu papai sempre resolve tudo aqui em casa!"; (2) dor, em
uma linha, com emoji 😩; (3) solução citando o produto pelo nome, com
emoji ✅; (4) call to action pedindo pra comentar "QUERO" ou ir no link
da bio, com emoji 🛒; (5) hashtags fixas (`#papairesolve
#casaeconstrucao #achadosdashopee #dicasdecasa #paisdeplantao`).
Implementado em `montarLegenda()`, ao lado de `montarRoteiro()`, no
mesmo arquivo.

Desde 01/09, tanto a narração quanto a legenda são salvas por produto em
`esteira.json` (campos `narracao`/`legenda`) no momento da seleção no
painel, e ficam visíveis (com botão de copiar) em `esteira.html`, em "Ver
textos" na linha do produto — fecha o ciclo criar → publicar → avaliar
sem precisar digitar o texto de novo. Um produto que ainda não foi
publicado (`etapa_conteudo` != `publicado`) pode ser removido da esteira
por lá; a checagem que impede excluir produto já publicado é feita no
servidor (`api/excluir_esteira.js`), não só na tela.

## Segurança

Nunca commitar `.env` nem qualquer credencial (Shopee, Anthropic) em
nenhum arquivo do repositório — só como Secret do GitHub ou variável de
ambiente na Vercel.
