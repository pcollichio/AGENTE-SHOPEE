# Cockpit de Afiliação IA-First — Papai Resolve (Fase 1)

## Comece aqui

Por enquanto (MVP), o jeito principal de usar o cockpit é **conversando
com o Claude** — veja "Como usar agora: o agente dentro do Claude"
logo abaixo. Além disso, `cockpit.html` é o painel visual: um arquivo
único com um menu fixo no topo, pra ver os produtos do dia, o ROI e
importar dados, sem precisar abrir outro arquivo.

## Como usar agora: o agente dentro do Claude (MVP)

Não é necessário publicar nada na Vercel pra começar a usar. O "agente"
do cockpit, por enquanto, é o próprio Claude, numa conversa com você:

- **Pergunte o que fazer hoje** — o Claude lê os dados reais do
  projeto (leva do dia, ROI, financeiro) e te diz.
- **Peça pra buscar um produto específico** — ex: "busca torneira de
  cozinha pra mim". O Claude dispara o workflow
  `.github/workflows/busca-manual.yml` (que roda `buscar_um_produto.py`
  com acesso real à API da Shopee) e te traz os resultados na hora.
- **Peça uma leitura do ROI, um roteiro pra um produto, ajuda com
  qualquer parte do fluxo** — o Claude já tem contexto de todo o
  projeto.

Essa abordagem existe porque a sessão do Claude, por segurança, não
acessa a API da Shopee diretamente — só o GitHub Actions tem esse
acesso real. Por isso a busca de produto passa por um workflow, não
por uma chamada direta.

O `chat.html` e a busca ao vivo no site (`api/`) continuam existindo,
prontos pra quando/se você quiser um chat que funcione sozinho, sem
precisar de mim na conversa — veja "Opcional: colocar o site no ar com
Chat" mais abaixo. Não é necessário pro MVP.

## As partes do sistema

- **`cockpit.html`** — arquivo único de entrada (abre os outros por dentro)
- **`index.html`** — visão geral do fluxo completo ("o que fazer hoje")
- **`chat.html`** — chat de verdade com o coach (usa `api/chat.js`)
- **`painel.html`** — produtos do dia (gerado automaticamente todo dia
  às 9h), com foto, seleção, roteiro pronto pra esteira de conteúdo e
  uma busca ao vivo (por nome) pra achar um produto específico que não
  apareceu na leva (usa `api/buscar_produto.py`)
- **`importar.html`** — formulário simples pra registrar investimento em
  campanha e vendas confirmadas
- **`painel_roi.html`** — progresso da meta mensal e ROI por produto
- `buscar_leva_lancamento.py` — busca os produtos reais na Shopee (leva do dia)
- `buscar_um_produto.py` — busca um produto específico sob demanda
  (usado pelo workflow `busca-manual.yml`, a pedido no chat com o Claude)
- `gerar_roi.py` — calcula o ROI a partir dos arquivos em `financeiro/`
  e também escreve `financeiro/resumo.json` (o chat lê esse arquivo)
- `sincronizar_vendas.py` — tenta puxar vendas reais direto da Shopee
  (experimental, ainda sendo validado contra a API)
- `financeiro/` — onde ficam os dados de investimento e vendas
  (`README.md` ali explica o formato)
- `produtos_manuais.txt` / `produtos_excluir.txt` — ajustes finos da
  curadoria automática
- `api/chat.js` — função serverless (Vercel) que fala com a Anthropic
- `api/buscar_produto.py` — função serverless (Vercel) que busca um
  produto específico direto na Shopee

## Opcional: colocar o site no ar com Chat (Vercel)

**Não é necessário pro MVP** — veja "Como usar agora" no topo deste
arquivo. Isso aqui só é preciso se um dia você quiser um chat que
funcione sozinho no site, sem precisar de mim na conversa. O chat e a
busca de produto específico do site só funcionam depois de publicar o
cockpit num servidor — não funcionam abrindo os arquivos direto do
computador. O jeito mais simples é a Vercel (gratuita pra esse uso):

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

   **Nunca** coloque nenhum desses valores em nenhum arquivo do
   repositório — só aqui, nas variáveis de ambiente da Vercel.
5. Clique em "Deploy". Em ~1 minuto a Vercel te dá uma URL (algo como
   `agente-shopee.vercel.app`) — é ela que você abre no lugar do
   `cockpit.html` local a partir de agora, porque só nela o chat e a
   busca funcionam.

Depois do primeiro deploy, toda vez que o robô diário (GitHub Actions)
atualizar o repositório, a Vercel republica sozinha.

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
