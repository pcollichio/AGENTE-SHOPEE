"""
Gera o painel de ROI (painel_roi.html) a partir dos arquivos preenchidos
manualmente em financeiro/investimentos.csv e financeiro/vendas.csv.

Rode com: python gerar_roi.py

Veja financeiro/README.md para o formato de preenchimento dos arquivos.
"""

from shopee_integration import painel_roi, roi


def main():
    investimentos = roi.carregar_investimentos()
    vendas = roi.carregar_vendas()

    caminho = painel_roi.salvar_painel(investimentos, vendas, "painel_roi.html")
    print(f"Painel de ROI salvo em: {caminho}")

    caminho_json = roi.exportar_resumo_json()
    print(f"Resumo em JSON salvo em: {caminho_json}")

    resumo = roi.calcular_resumo(investimentos, vendas)
    roi_texto = f"{resumo['roi_medio']:.1f}x" if resumo["roi_medio"] is not None else "sem dados ainda"
    print(f"Investido: R${resumo['total_investido']:.2f} | "
          f"Comissão: R${resumo['total_comissao']:.2f} | ROI médio: {roi_texto}")
    print(f"Meta do mês: R${resumo['comissao_mes_atual']:.2f} de R${resumo['meta_mensal']:.0f} "
          f"({resumo['progresso_meta']*100:.0f}%)")


if __name__ == "__main__":
    main()
