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
  Issues. O botão "Salvar seleção agora" no `painel.html` grava a
  seleção instantaneamente em `cockpit-shopee/selecao_atual.json`
  (via `api/selecionar.js`, que escreve no GitHub usando um
  `GITHUB_TOKEN`). O Claude lê esse arquivo pra saber o que foi
  selecionado, sem precisar que o usuário digite de novo no chat.
- Chat (`chat.html` + `api/chat.js`) e busca ao vivo no site
  (`api/buscar_produto.py`) também rodam na Vercel — todos os três
  (chat, busca, seleção) dependem do deploy estar ativo.

## Onde as coisas estão

- `cockpit-shopee/README.md` — visão geral técnica de cada arquivo e
  workflow.
- `cockpit-shopee/leva_do_dia.md` — leva de produtos do dia (atualizada
  às 9h por `leva-diaria.yml`).
- `cockpit-shopee/financeiro/` — investimento e vendas (import manual,
  não automatizado — ver decisão em `HISTORICO.md`).
- `cockpit-shopee/financeiro/resumo.json` — resumo do ROI em JSON.
- `cockpit-shopee/selecao_atual.json` — última seleção de produtos
  feita no painel (leia antes de gerar roteiro, se o usuário mencionar
  que já selecionou algo no painel).
- Links publicados: GitHub Pages em
  `https://pcollichio.github.io/AGENTE-SHOPEE/cockpit-shopee/cockpit.html`
  (e `/painel.html`, `/painel_roi.html`, etc.)

## Segurança

Nunca commitar `.env` nem qualquer credencial (Shopee, Anthropic) em
nenhum arquivo do repositório — só como Secret do GitHub ou variável de
ambiente na Vercel.
