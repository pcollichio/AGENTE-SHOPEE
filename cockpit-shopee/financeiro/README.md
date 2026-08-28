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

## `vendas.csv` — quanto você realmente vendeu/recebeu de comissão

Preencha conferindo no seu painel de afiliado da Shopee (a comissão de
verdade que caiu pra você, não a comissão "possível" que o painel mostra
antes de vender).

```
data,produto,comissao_recebida,observacao
2026-08-28,Sifão Ajustável Universal,15.50,Confirmado no painel Shopee
```

Mesmas regras de formato do arquivo acima.

## O que acontece com esses dados

O painel de ROI (`painel_roi.html`) lê os dois arquivos automaticamente
(rodando `python gerar_roi.py`, ou pela automação diária do GitHub
Actions) e calcula:

- Quanto você já investiu x quanto já recebeu de comissão
- O ROI de cada produto/campanha (meta: 3x — cada R$1 investido deve
  voltar R$3 em comissão)
- O progresso da meta mensal de R$10.000 em comissão
