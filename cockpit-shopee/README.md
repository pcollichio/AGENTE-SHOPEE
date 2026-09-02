# Cockpit de Afiliação IA-First — Papai Resolve (Fase 1)

## Comece aqui

O cockpit tem duas partes que trabalham junto: você **conversa com o
Claude** pra decisão, roteiro e "o que fazer agora", e usa o
**`cockpit.html`** (publicado na Vercel — veja "Colocar o cockpit no
ar" abaixo) pra tudo visual: produtos do dia com foto, seleção, ROI e
importar dados. O `cockpit.html` tem um menu lateral fixo (Início,
Produtos, Esteira, Importar, ROI) e um painel de chat fixo à direita
— o chat conversa com a mesma IA de sempre, sempre visível, sem
precisar trocar de aba pra perguntar algo.

Desde 31/08, todo produto que você seleciona no painel e salva (botão
"Salvar seleção agora") entra numa lista viva, a **esteira**
(`esteira.html`) — é assim que o Claude sabe o que você já escolheu ao
longo do tempo, sem precisar digitar de novo no chat. O status de cada
produto (selecionado / impulsionado / vendido) é calculado sozinho,
cruzando com o financeiro.

## O agente dentro do Claude

- **Pergunte o que fazer hoje** — o Claude lê os dados reais do
  projeto (leva do dia, ROI, financeiro, sua última seleção salva) e
  te diz.
- **Peça pra buscar um produto específico** — por nome ("busca
  torneira de cozinha pra mim") ou **colando o link do produto que
  você viu no app da Shopee**. O Claude dispara o workflow
  `.github/workflows/busca-manual.yml` (que roda `buscar_um_produto.py`
  com acesso real à API da Shopee — segue o link, identifica o produto
  e busca) e te traz os resultados na hora. Na prática, o mais rápido é
  colar o link direto na busca do topo do `painel.html` — funciona sem
  passar pelo chat.
- **Peça o roteiro de um produto que você selecionou no painel** — o
  Claude lê `esteira.json` (salvo pelo botão do painel) e já monta o
  texto pronto pra gravação.
- **Pergunte o que está na esteira** — o Claude sabe quais produtos
  já foram selecionados, quais já foram impulsionados e quais já
  venderam.

Essa abordagem existe porque a sessão do Claude, por segurança, não
acessa a API da Shopee diretamente — só o GitHub Actions tem esse
acesso real. Por isso a busca de produto passa por um workflow, não
por uma chamada direta.

## As partes do sistema

- **`cockpit.html`** — arquivo único de entrada (abre os outros por dentro)
- **`index.html`** — visão geral do fluxo completo ("o que fazer hoje")
- **`chat.html`** — chat de verdade com o coach (usa `api/chat.js`)
- **`painel.html`** — os 50 melhores produtos do dia no nicho (gerado
  automaticamente todo dia às 9h, por score de curadoria, sem filtro de
  comissão/avaliação — isso é filtro interativo, no painel), com foto,
  seleção, roteiro e legenda prontos pra esteira. No topo, uma busca ao
  vivo aceita tanto uma descrição quanto um link colado direto do app
  da Shopee — pra trazer qualquer produto pro agente sem esperar a leva
  do dia (usa `api/buscar_produto.py`, mesma lógica de resolver link do
  `buscar_um_produto.py`)
- **`esteira.html`** — a lista viva de produtos selecionados, com
  status financeiro automático (selecionado / impulsionado / vendido),
  etapa de conteúdo manual (roteiro pronto / em produção / publicado),
  o texto de narração e de legenda prontos pra copiar por produto, um
  botão pra excluir produto que ainda não foi publicado, e um guia do
  processo de gravação/edição/publicação/avaliação
- **`importar.html`** — formulário simples pra registrar investimento em
  campanha e vendas confirmadas
- **`painel_roi.html`** — progresso da meta mensal e ROI por produto
- `buscar_leva_lancamento.py` — busca os produtos reais na Shopee e
  devolve os 50 melhores do nicho, por score (leva do dia)
- `buscar_um_produto.py` — busca um produto específico sob demanda, por
  nome ou link (usado pelo workflow `busca-manual.yml`, a pedido no
  chat com o Claude) — mesma lógica de link de `api/buscar_produto.py`,
  compartilhada via `shopee_integration/link_resolver.py`
- `gerar_roi.py` — calcula o ROI a partir dos arquivos em `financeiro/`
  e também escreve `financeiro/resumo.json` (o chat lê esse arquivo)
- `gerar_esteira.py` — recalcula o status da esteira (`esteira.html`)
  cruzando `esteira.json` com o financeiro
- `sincronizar_vendas.py` — tenta puxar vendas reais direto da Shopee
  (experimental, ainda sendo validado contra a API)
- `financeiro/` — onde ficam os dados de investimento e vendas
  (`README.md` ali explica o formato)
- `produtos_manuais.txt` / `produtos_excluir.txt` — ajustes finos da
  curadoria automática
- `api/chat.js` — função serverless (Vercel) que fala com a Anthropic
- `api/buscar_produto.py` — função serverless (Vercel) que busca um
  produto específico direto na Shopee, por descrição ou por link
  colado do app
- `api/selecionar.js` — função serverless (Vercel) que acrescenta a
  seleção do painel em `esteira.json`, direto no GitHub
- `api/importar_arquivo.js` — função serverless (Vercel) que recebe um
  arquivo enviado em `importar.html` (relatório de vendas, Meta Ads
  etc.) e salva em `financeiro/importados/`, direto no GitHub
- `api/atualizar_esteira.js` — função serverless (Vercel) que salva a
  etapa de conteúdo (roteiro pronto/em produção/publicado) de um
  produto na esteira, usada pelo seletor em `esteira.html`
- `api/excluir_esteira.js` — função serverless (Vercel) que remove um
  produto da esteira, usada pelo botão "Excluir" em `esteira.html`;
  recusa excluir produto com etapa "Publicado" (checagem no servidor)
- `esteira.json` — todos os produtos já selecionados no painel ao
  longo do tempo (escrito pelo botão "Baixar roteiro e salvar na
  esteira", já com o texto de narração e de legenda prontos; é o que
  o Claude e o `esteira.html` leem)

## Colocar o cockpit no ar (Vercel)

O chat, a busca de produto específico e o botão "Salvar seleção agora"
só funcionam depois de publicar o cockpit num servidor — não funcionam
abrindo os arquivos direto do computador. O jeito mais simples é a
Vercel (gratuita pra esse uso):

1. Entre em [vercel.com](https://vercel.com) e faça login com sua conta
   do GitHub.
2. "Add New" → "Project" → escolha o repositório `AGENTE-SHOPEE`.
3. Em "Root Directory", clique em "Edit" e selecione a pasta
   `cockpit-shopee`.
4. Em "Environment Variables", adicione:
   - `ANTHROPIC_API_KEY` — sua chave da Anthropic (pegue em
     [console.anthropic.com](https://console.anthropic.com), em "API
     Keys"). Usada pelo chat.
   - `SHOPEE_APP_ID` e `SHOPEE_APP_SECRET` — as mesmas credenciais que
     já estão nos Secrets do GitHub (usadas pela automação diária).
     Usadas pela busca de produto específico.
   - `USE_MOCK_DATA` com o valor `false`.
   - `GITHUB_TOKEN` — um token de acesso pessoal do GitHub, só pra
     este repositório, com permissão de escrever conteúdo. Veja como
     criar logo abaixo. Usado pelo botão "Salvar seleção agora".

   **Nunca** coloque nenhum desses valores em nenhum arquivo do
   repositório — só aqui, nas variáveis de ambiente da Vercel.
5. Clique em "Deploy". Em ~1 minuto a Vercel te dá uma URL (algo como
   `agente-shopee.vercel.app`) — é ela que você abre no lugar do
   `cockpit.html` local a partir de agora, porque só nela o chat, a
   busca e o salvamento de seleção funcionam.

Depois do primeiro deploy, toda vez que o robô diário (GitHub Actions)
atualizar o repositório, a Vercel republica sozinha.

### Criando o `GITHUB_TOKEN`

1. No GitHub, vá em **Settings** (da sua conta, não do repositório) →
   **Developer settings** → **Personal access tokens** →
   **Fine-grained tokens** → **Generate new token**.
2. Em "Repository access", escolha **Only select repositories** e
   selecione `AGENTE-SHOPEE`.
3. Em "Permissions" → "Repository permissions", ache **Contents** e
   mude de "No access" pra **Read and write**.
4. Gere o token e copie o valor (começa com `github_pat_...`) — só
   aparece uma vez.
5. Cole esse valor como a variável `GITHUB_TOKEN` na Vercel (passo 4
   acima).

## Automação

- `.github/workflows/leva-diaria.yml` — roda `buscar_leva_lancamento.py`
  e `gerar_roi.py` todo dia de manhã, usando as credenciais guardadas
  como Secrets do repositório.
- `.github/workflows/busca-manual.yml` — roda sob demanda (não tem
  horário fixo), com um termo de busca como entrada. É o que o Claude
  dispara quando você pede pra buscar um produto específico na conversa.

## Testar localmente

```bash
pip install -r requirements.txt
python buscar_leva_lancamento.py   # busca produtos (precisa de USE_MOCK_DATA=false + credenciais)
python gerar_roi.py                # gera o painel de ROI
python demo.py                     # demonstração com dados simulados
```
