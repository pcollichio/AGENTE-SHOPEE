"""
Busca produtos reais da Shopee (nicho casa e construção) que atendem aos
critérios da campanha de lançamento @papairesolve_br (blueprint, seção 5):

  - Comissão acima de 10-12%
  - Avaliação acima de 4,5 estrelas
  - Preço entre R$40 e R$100 (compra por impulso)
  - Prioridade para: ferramentas, organização, iluminação, hidráulica

Rode com: python buscar_leva_lancamento.py

IMPORTANTE: precisa de acesso real à internet e das credenciais reais
configuradas no .env (USE_MOCK_DATA=false). Não funciona em sandboxes sem
acesso externo — rode no seu computador ou no Google Colab, como fizemos
no teste de conexão.

NOTA: a Shopee Affiliate API não expõe o status de frete grátis, então
esse critério do blueprint não é filtrado automaticamente aqui.
"""

from shopee_integration import client, config, curadoria

SUBCATEGORIAS_PRIORITARIAS = ["ferramentas", "organizacao", "iluminacao", "hidraulica"]


def buscar_leva():
    todos_produtos = []
    for termo in SUBCATEGORIAS_PRIORITARIAS:
        try:
            produtos = client.buscar_produtos(
                keyword=termo, min_comissao=curadoria.COMISSAO_MINIMA, limite=20
            )
            todos_produtos.extend(produtos)
        except Exception as e:
            print(f"Aviso: busca por '{termo}' falhou: {e}")

    # Remove produtos duplicados (podem aparecer em mais de uma busca)
    vistos = set()
    produtos_unicos = []
    for p in todos_produtos:
        if p["product_id"] not in vistos:
            vistos.add(p["product_id"])
            produtos_unicos.append(p)

    # Aplica os critérios do blueprint
    filtrados = [
        p
        for p in produtos_unicos
        if p["commission_rate"] >= curadoria.COMISSAO_MINIMA
        and p["rating"] >= curadoria.AVALIACAO_MINIMA
        and curadoria.PRECO_MIN_IMPULSO <= p["price"] <= curadoria.PRECO_MAX_IMPULSO
    ]

    ranqueados = sorted(
        ({**p, "score": curadoria.calcular_score(p)} for p in filtrados),
        key=lambda p: p["score"],
        reverse=True,
    )
    return ranqueados[:10]


def main():
    if config.USE_MOCK_DATA:
        print(
            "USE_MOCK_DATA está true — configure USE_MOCK_DATA=false no .env "
            "para buscar produtos reais."
        )
        return

    top10 = buscar_leva()

    if not top10:
        print(
            "Nenhum produto encontrado com os critérios atuais. Pode ser que "
            "os termos de busca não retornaram resultados, ou que os nomes "
            "dos campos da API precisem de ajuste (veja os comentários em "
            "shopee_integration/client.py)."
        )
        return

    print(
        f"{'Produto':<40} {'Preço':>9} {'Comissão':>9} {'Avaliação':>10} "
        f"{'Vendidos':>9}  Link de afiliado"
    )
    print("-" * 140)
    for p in top10:
        nome = (p["name"] or "(sem nome)")[:38]
        print(
            f"{nome:<40} R${p['price']:>6.2f} {p['commission_rate']*100:>7.0f}% "
            f"{p['rating']:>9.1f}⭐ {p['total_sold']:>9}  {p['affiliate_link']}"
        )


if __name__ == "__main__":
    main()
