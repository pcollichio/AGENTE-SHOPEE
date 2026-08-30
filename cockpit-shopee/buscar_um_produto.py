"""
Busca um produto específico na Shopee, sob demanda — não é a leva
automática do dia. Pensado pra ser disparado manualmente (pelo GitHub
Actions, geralmente a pedido no chat com o Claude) quando você quiser
achar algo fora da leva.

Rode com: python buscar_um_produto.py "nome do produto"
"""

import sys

from shopee_integration import client, config


def main():
    if len(sys.argv) < 2:
        print('Uso: python buscar_um_produto.py "termo de busca"')
        return

    termo = " ".join(sys.argv[1:])

    if config.USE_MOCK_DATA:
        print(
            "USE_MOCK_DATA está true — configure USE_MOCK_DATA=false no .env "
            "para buscar produtos reais."
        )
        return

    try:
        produtos = client.buscar_produtos(keyword=termo, limite=8)
    except Exception as e:
        print(f"Erro ao buscar: {e}")
        return

    if not produtos:
        print(f'Nenhum produto encontrado para "{termo}".')
        return

    print(f'# Resultados para "{termo}"\n')
    for i, p in enumerate(produtos, start=1):
        print(f"{i}. {p['name']}")
        print(
            f"   Preço: R${p['price']:.2f} | Comissão: {p['commission_rate']*100:.0f}% | "
            f"Avaliação: {p['rating']:.1f}⭐ | Vendidos: {p['total_sold']}"
        )
        print(f"   Link: {p['affiliate_link']}")
        print()


if __name__ == "__main__":
    main()
