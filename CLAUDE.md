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
- **Toda decisão e marco importante entra em `HISTORICO.md`**, com
  data. Ao começar uma sessão nova, releia esse arquivo antes de agir.
- A sessão do Claude tem uma restrição de rede: não acessa a API da
  Shopee nem carrega imagens externas diretamente. Pra buscar um
  produto específico sob demanda, dispare o workflow
  `.github/workflows/busca-manual.yml` (via `actions_run_trigger`,
  input `termo`) e leia o resultado nos logs do job.
- Chat/busca "ao vivo" no próprio site (`chat.html`, `api/`) existem
  mas são **opcionais**, hospedados via Vercel — só fazem sentido se o
  usuário um dia quiser um chat que funcione sem o Claude na conversa.
  Não é o modo de operação atual.

## Onde as coisas estão

- `cockpit-shopee/README.md` — visão geral técnica de cada arquivo e
  workflow.
- `cockpit-shopee/leva_do_dia.md` — leva de produtos do dia (atualizada
  às 9h por `leva-diaria.yml`).
- `cockpit-shopee/financeiro/` — investimento e vendas (import manual,
  não automatizado — ver decisão em `HISTORICO.md`).
- `cockpit-shopee/financeiro/resumo.json` — resumo do ROI em JSON.
- Links publicados: GitHub Pages em
  `https://pcollichio.github.io/AGENTE-SHOPEE/cockpit-shopee/cockpit.html`
  (e `/painel.html`, `/painel_roi.html`, etc.)

## Segurança

Nunca commitar `.env` nem qualquer credencial (Shopee, Anthropic) em
nenhum arquivo do repositório — só como Secret do GitHub ou variável de
ambiente na Vercel.
