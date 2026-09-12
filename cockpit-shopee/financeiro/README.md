# Como preencher esses arquivos

Dois arquivos de planilha simples (CSV — abre até no Excel/Google Sheets,
mas também dá pra editar direto aqui no GitHub, clicando no lápis).

**Dica para editar no GitHub:** abra o arquivo, clique no lápis (editar),
adicione uma linha nova seguindo o mesmo formato das outras, e clique em
"Commit changes" no final da página.

## `investimentos.csv` — quanto você gastou divulgando

Uma linha por vez que você impulsionar algo (post do Instagram, anúncio etc).

```
data,produto,valor_investido,observacao
2026-08-28,Sifão Ajustável Universal,20.00,Impulsionamento post Instagram
```

- **data**: no formato AAAA-MM-DD (ano-mês-dia)
- **produto**: nome do produto ou campanha (não precisa ser exato, só pra você reconhecer)
- **valor_investido**: só o número, com ponto para casas decimais (ex: 20.00, não R$20,00)
- **observacao**: opcional, qualquer nota que ajude a lembrar

## `vendas.csv` — quanto você realmente vendeu/recebeu de comissão (manual)

Preencha conferindo no seu painel de afiliado da Shopee (a comissão de
verdade que caiu pra você, não a comissão "possível" que o painel mostra
antes de vender).

```
data,produto,comissao_recebida,observacao
2026-08-28,Sifão Ajustável Universal,15.50,Confirmado no painel Shopee
```

Mesmas regras de formato do arquivo acima.

## `vendas_shopee.csv` e `vendas_pendentes.csv` — automático + manual (não editar à mão)

Esses dois arquivos são alimentados por **duas fontes que convivem**,
sem duplicar:

1. **Automática (desde 12/09)**: `sincronizar_vendas.py` roda sozinho
   todo dia (dentro de `leva-diaria.yml`, antes do ROI ser
   recalculado), buscando direto na API da Shopee.
2. **Manual**: rodando `python importar_extratos.py caminho/do/relatorio.csv`
   com o **relatório de comissões de afiliado** exportado do painel da
   Shopee (Portal de Afiliados → Relatórios → Comissão) — via upload em
   `importar.html`. Continua disponível pra puxar histórico de antes de
   12/09, ou se a sincronização automática ficar fora do ar.

As duas fontes separam os pedidos pelo mesmo critério de status:

- **Concluído/Confirmado** → vira venda de verdade em `vendas_shopee.csv`
  (conta no ROI e na meta mensal).
- **Pendente** → vai pra `vendas_pendentes.csv` (só aparece como "R$X
  pendente" no Dashboard — ainda pode ser cancelado, então não conta
  no ROI nem na meta até confirmar). Se um pedido pendente depois vira
  confirmado, ele some da conta de "pendente" automaticamente (o
  cálculo do ROI ignora, em `vendas_pendentes.csv`, qualquer pedido que
  já apareça confirmado em `vendas_shopee.csv`) — não precisa apagar a
  linha antiga à mão.
- **Cancelado/Rejeitado** → ignorado.

Rodar de novo (manual ou automático, em qualquer ordem) não duplica
nada — os dois usam o ID do pedido (`conversion_id`) como chave.
Ambos os arquivos são **separados** do `vendas.csv` de propósito —
assim nem a importação nem a sincronização apagam o que você digitou
manualmente. O painel de ROI soma `vendas.csv` + `vendas_shopee.csv`
(não soma `vendas_pendentes.csv`, que é só informativo).

## Gasto com anúncios — importado do gerenciador da Meta

Rodando `python importar_extratos.py caminho/do/relatorio.xlsx` com o
relatório exportado do Gerenciador de Anúncios (Meta Ads Manager,
formato .xlsx), o sistema acrescenta uma linha em `investimentos.csv`
por conjunto de anúncios (cada um corresponde, normalmente, a um post
impulsionado). Também idempotente — rodar de novo não duplica.

## O que acontece com esses dados

O painel de ROI (`painel_roi.html`) lê todos esses arquivos
automaticamente (rodando `python gerar_roi.py`, ou pela automação
diária do GitHub Actions) e calcula:

- Quanto você já investiu x quanto já recebeu de comissão
- O ROI de cada produto/campanha (meta: 3x — cada R$1 investido deve
  voltar R$3 em comissão)
- O progresso da meta mensal de R$10.000 em comissão
