# Cockpit Shopee — Integração inicial (Fase 1)

## O que já está pronto

- `shopee_integration/config.py` — gerencia credenciais (usa dados mockados
  automaticamente até você configurar a API real)
- `shopee_integration/mock_data.py` — 8 produtos simulados do nicho casa e
  construção, no formato esperado da API real
- `shopee_integration/client.py` — funções de busca de produtos, comissão,
  indicadores de venda e geração de link de afiliado
- `shopee_integration/curadoria.py` — aplica os critérios do blueprint
  (comissão, avaliação, vendas, faixa de preço, frete grátis) e ranqueia
  os melhores produtos do dia
- `demo.py` — script pronto para rodar e ver tudo funcionando

## Como rodar

```bash
python demo.py
```

Isso vai imprimir os 5 melhores produtos do dia (por enquanto com dados
simulados), já com o link de afiliado pronto para colar no Creatify.

## Quando a Shopee aprovar sua API

1. Crie um arquivo `.env` na raiz do projeto com:
   ```
   SHOPEE_APP_ID=seu_app_id_real
   SHOPEE_APP_SECRET=seu_app_secret_real
   USE_MOCK_DATA=false
   ```
2. Rode `pip install python-dotenv` (para carregar o `.env` automaticamente)
3. Em `shopee_integration/client.py`, procure os comentários `# TODO:` —
   é ali que entra a chamada real à API GraphQL da Shopee, substituindo os
   dados mockados

Nenhuma outra parte do código precisa mudar — a curadoria e o resto do
sistema já foram construídos para funcionar igual, seja com dados mockados
ou reais.

## Próximo passo sugerido

- Ajustar `curadoria.py` se quiser mudar os pesos dos critérios de score
- Pegar os links de afiliado gerados pelo `demo.py` e testar no Creatify
- Depois: começar o dashboard web que exibe isso visualmente (ao invés de
  só imprimir no terminal)
