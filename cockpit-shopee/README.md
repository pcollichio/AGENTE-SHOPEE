# Cockpit de Afiliação IA-First — Papai Resolve (Fase 1)

## Comece aqui

Abra **`index.html`** — é o painel central que mostra o fluxo inteiro,
o que já é automático e o que ainda depende de você, com link pra cada
parte.

## As partes do sistema

- **`index.html`** — visão geral do fluxo completo
- **`painel.html`** — produtos do dia (gerado automaticamente todo dia
  às 9h), com seleção e roteiro pronto pra esteira de conteúdo
- **`importar.html`** — formulário simples pra registrar investimento em
  campanha e vendas confirmadas
- **`painel_roi.html`** — progresso da meta mensal e ROI por produto
- `buscar_leva_lancamento.py` — busca os produtos reais na Shopee
- `gerar_roi.py` — calcula o ROI a partir dos arquivos em `financeiro/`
- `sincronizar_vendas.py` — tenta puxar vendas reais direto da Shopee
  (experimental, ainda sendo validado contra a API)
- `financeiro/` — onde ficam os dados de investimento e vendas
  (`README.md` ali explica o formato)
- `produtos_manuais.txt` / `produtos_excluir.txt` — ajustes finos da
  curadoria automática

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
