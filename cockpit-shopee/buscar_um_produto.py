"""
Busca um produto específico na Shopee, sob demanda — não é a leva
automática do dia. Pensado pra ser disparado manualmente (pelo GitHub
Actions, geralmente a pedido no chat com o Claude) quando você quiser
achar algo fora da leva.

Aceita tanto um nome/termo de busca quanto um link da Shopee (link
curto s.shopee.com.br ou o link completo do produto) — nesse caso,
segue o link, extrai o nome do produto a partir da URL e busca por ele
(pedido do usuário em 2026-08-31: "olhar o produto no app e entregar o
link pra relacionar").

Rode com:
    python buscar_um_produto.py "nome do produto"
    python buscar_um_produto.py "https://s.shopee.com.br/xxxxxxxx"
"""

import sys

from shopee_integration import client, config, link_resolver


def main():
    if len(sys.argv) < 2:
        print('Uso: python buscar_um_produto.py "termo de busca ou link da Shopee"')
        return

    entrada = " ".join(sys.argv[1:]).strip()

    if config.USE_MOCK_DATA:
        print(
            "USE_MOCK_DATA está true — configure USE_MOCK_DATA=false no .env "
            "para buscar produtos reais."
        )
        return

    item_id_alvo = None
    if link_resolver.eh_link(entrada):
        try:
            url_final = link_resolver.resolver_link(entrada)
        except Exception as e:
            print(f"Não consegui abrir o link: {e}")
            return
        print(f"Link resolvido: {url_final}")
        termo, item_id_alvo = link_resolver.extrair_info_link(url_final)
        if not termo:
            print(f"\n{link_resolver.MENSAGEM_LINK_SEM_NOME}")
            return
        print(f'Buscando por: "{termo}"' + (f" (item {item_id_alvo})" if item_id_alvo else ""))
        print()
    else:
        termo = entrada

    try:
        produtos = client.buscar_produtos(keyword=termo, limite=8)
    except Exception as e:
        print(f"Erro ao buscar: {e}")
        return

    if not produtos:
        print(f'Nenhum produto encontrado para "{termo}".')
        return

    if item_id_alvo:
        exato = next((p for p in produtos if p["product_id"] == item_id_alvo), None)
        if exato:
            print("# Produto encontrado (correspondência exata pelo link)\n")
            produtos = [exato]
        else:
            print(f'# Não achei correspondência exata pelo link — resultados mais prováveis para "{termo}"\n')
    else:
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
