"""
Script de demonstração da integração com a Shopee (com dados mockados).

Rode com: python demo.py
"""

from shopee_integration import curadoria, client


def main():
    print("=" * 60)
    print("COCKPIT SHOPEE — CURADORIA DIÁRIA DE PRODUTOS (dados simulados)")
    print("=" * 60)

    produtos_do_dia = curadoria.sugerir_produtos_do_dia(quantidade=5)

    for i, produto in enumerate(produtos_do_dia, start=1):
        print(f"\n#{i} — {produto['name']}")
        print(f"    Score de curadoria: {produto['score']}/100")
        print(f"    Preço: R${produto['price']:.2f}  |  "
              f"Comissão: {produto['commission_rate']*100:.0f}%  |  "
              f"Avaliação: {produto['rating']}⭐  |  "
              f"Vendidos: {produto['total_sold']}")
        print(f"    Frete grátis: {'Sim' if produto['free_shipping'] else 'Não'}")
        print(f"    Link de afiliado: {produto['affiliate_link']}")

        indicadores = client.obter_indicadores_vendas(produto["product_id"])
        if indicadores:
            print(f"    Comissão acumulada (simulada): "
                  f"R${indicadores['total_commission_earned']:.2f}")

    print("\n" + "=" * 60)
    print("Próximo passo: pegar o 'Link de afiliado' de cada produto acima")
    print("e colar no Creatify para gerar o vídeo automaticamente.")
    print("=" * 60)


if __name__ == "__main__":
    main()
