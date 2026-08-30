# Cockpit de Afiliação IA-First — Papai Resolve (Fase 1)

## Comece aqui

Abra **`cockpit.html`** — é o único arquivo que você precisa abrir. Ele
tem um menu fixo no topo; clicar em cada aba troca o conteúdo ali
mesmo, sem precisar abrir outro arquivo. A aba **Chat** é uma conversa
de verdade com o coach (veja "O chat com IA" abaixo pra colocar no ar).

## As partes do sistema

- **`cockpit.html`** — arquivo único de entrada (abre os outros por dentro)
- **`index.html`** — visão geral do fluxo completo ("o que fazer hoje")
- **`chat.html`** — chat de verdade com o coach (usa `api/chat.js`)
- **`painel.html`** — produtos do dia (gerado automaticamente todo dia
  às 9h), com foto, seleção e roteiro pronto pra esteira de conteúdo
- **`importar.html`** — formulário simples pra registrar investimento em
  campanha e vendas confirmadas
- **`painel_roi.html`** — progresso da meta mensal e ROI por produto
- `buscar_leva_lancamento.py` — busca os produtos reais na Shopee
- `gerar_roi.py` — calcula o ROI a partir dos arquivos em `financeiro/`
  e também escreve `financeiro/resumo.json` (o chat lê esse arquivo)
- `sincronizar_vendas.py` — tenta puxar vendas reais direto da Shopee
  (experimental, ainda sendo validado contra a API)
- `financeiro/` — onde ficam os dados de investimento e vendas
  (`README.md` ali explica o formato)
- `produtos_manuais.txt` / `produtos_excluir.txt` — ajustes finos da
  curadoria automática
- `api/chat.js` — função serverless (Vercel) que fala com a Anthropic

## O chat com IA

O chat precisa de um servidor rodando `api/chat.js` — não funciona
abrindo `chat.html` direto do computador. O jeito mais simples é a
Vercel (gratuita pra esse uso):

1. Entre em [vercel.com](https://vercel.com) e faça login com sua conta
   do GitHub.
2. "Add New" → "Project" → escolha o repositório `AGENTE-SHOPEE`.
3. Em "Root Directory", clique em "Edit" e selecione a pasta
   `cockpit-shopee`.
4. Em "Environment Variables", adicione uma variável chamada
   `ANTHROPIC_API_KEY` com o valor da sua chave (pegue em
   [console.anthropic.com](https://console.anthropic.com), em "API
   Keys"). **Nunca** coloque essa chave em nenhum arquivo do
   repositório — só aqui, na Vercel.
5. Clique em "Deploy". Em ~1 minuto a Vercel te dá uma URL (algo como
   `agente-shopee.vercel.app`) — é ela que você abre no lugar do
   `cockpit.html` local a partir de agora, porque só nela o chat
   funciona.

Depois do primeiro deploy, toda vez que o robô diário (GitHub Actions)
atualizar o repositório, a Vercel republica sozinha.

## Automação

Um workflow do GitHub Actions (`.github/workflows/leva-diaria.yml`)
roda `buscar_leva_lancamento.py` e `gerar_roi.py` todo dia de manhã,
usando as credenciais guardadas como Secrets do repositório.

## Testar localmente

```bash
pip install -r requirements.txt
python buscar_leva_lancamento.py   # busca produtos (precisa de USE_MOCK_DATA=false + credenciais)
python gerar_roi.py                # gera o painel de ROI
python demo.py                     # demonstração com dados simulados
```
