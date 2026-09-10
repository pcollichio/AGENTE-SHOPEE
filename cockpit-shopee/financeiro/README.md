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

## `vendas_shopee.csv` e `vendas_pendentes.csv` — importados de relatório (não editar à mão)

Desde 10/09, rodando `python importar_extratos.py caminho/do/relatorio.csv`
com o **relatório de comissões de afiliado** exportado do painel da
Shopee (Portal de Afiliados → Relatórios → Comissão), o sistema separa
os pedidos por status:

- **Concluído** → vira venda de verdade em `vendas_shopee.csv` (conta
  no ROI e na meta mensal).
- **Pendente** → vai pra `vendas_pendentes.csv` (só aparece como "R$X
  pendente" no Dashboard — ainda pode ser cancelado, então não conta
  no ROI nem na meta até aparecer como Concluído num relatório futuro).
- **Cancelado** → ignorado.

Rodar de novo com um relatório mais recente (que repete pedidos
antigos) não duplica nada — o script usa o ID do pedido como chave.
Esses dois arquivos são **separados** do `vendas.csv` de propósito —
assim a importação nunca apaga o que você digitou manualmente. O
painel de ROI soma `vendas.csv` + `vendas_shopee.csv` (não soma
`vendas_pendentes.csv`, que é só informativo).

(`sincronizar_vendas.py`, uma tentativa anterior de puxar vendas direto
da API em vez de relatório exportado, continua no repositório mas
nunca foi validada contra uma resposta real — o caminho do relatório
exportado funcionou de primeira e é o que está em uso.)

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
