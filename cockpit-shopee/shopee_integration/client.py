"""
Cliente de integração com a Shopee Affiliate API.

Enquanto USE_MOCK_DATA=true (padrão, até você ter as credenciais reais
aprovadas), todas as funções retornam dados simulados de mock_data.py,
mas já no formato esperado da resposta real.

Quando a API real for liberada, o TODO em cada função indica exatamente
onde entra a chamada GraphQL de verdade.
"""

from . import config
from . import mock_data


def buscar_produtos(subcategoria=None, min_comissao=None):
    """
    Busca produtos da Shopee dentro do nicho casa e construção.

    Args:
        subcategoria: filtra por subcategoria (ex: "iluminacao", "cozinha",
            "organizacao", "ferramentas", "hidraulica"). None = todas.
        min_comissao: filtra produtos com comissão mínima (ex: 0.10 = 10%)

    Returns:
        Lista de produtos no formato padronizado.
    """
    if config.USE_MOCK_DATA:
        produtos = mock_data.MOCK_PRODUCTS
    else:
        # TODO: substituir por chamada real à Shopee Affiliate API (GraphQL)
        # Exemplo de estrutura da requisição (ajustar conforme documentação
        # oficial recebida no e-mail de aprovação):
        #
        # query = """
        #   query GetProducts($category: String!) {
        #     productOfferV2(categoryId: $category) {
        #       nodes { itemId, productName, price, commissionRate, ... }
        #     }
        #   }
        # """
        # response = _executar_graphql(query, {"category": "casa_construcao"})
        # produtos = _parse_produtos(response)
        raise NotImplementedError(
            "Credenciais reais da Shopee ainda não configuradas. "
            "Configure SHOPEE_APP_ID e SHOPEE_APP_SECRET no .env, "
            "ou mantenha USE_MOCK_DATA=true para continuar testando."
        )

    if subcategoria:
        produtos = [p for p in produtos if p["subcategory"] == subcategoria]
    if min_comissao is not None:
        produtos = [p for p in produtos if p["commission_rate"] >= min_comissao]

    return produtos


def obter_comissao(product_id):
    """Retorna os dados de comissão de um produto específico."""
    if config.USE_MOCK_DATA:
        produto = next(
            (p for p in mock_data.MOCK_PRODUCTS if p["product_id"] == product_id),
            None,
        )
        if not produto:
            return None
        return {
            "product_id": product_id,
            "commission_rate": produto["commission_rate"],
            "commission_value_estimate": round(
                produto["price"] * produto["commission_rate"], 2
            ),
        }
    else:
        # TODO: chamada real à API
        raise NotImplementedError("Credenciais reais da Shopee ainda não configuradas.")


def obter_indicadores_vendas(product_id):
    """Retorna cliques/vendas dos últimos 7 dias e comissão acumulada de um produto."""
    if config.USE_MOCK_DATA:
        return mock_data.MOCK_SALES_INDICATORS.get(product_id)
    else:
        # TODO: chamada real à API
        raise NotImplementedError("Credenciais reais da Shopee ainda não configuradas.")


def gerar_link_afiliado(product_id):
    """
    Gera o link de afiliado de um produto específico.

    Em produção, a Shopee normalmente exige uma chamada de API para gerar
    o link rastreável (com seu ID de afiliado embutido), não é só concatenar
    texto. Por isso isso já está isolado em sua própria função.
    """
    if config.USE_MOCK_DATA:
        produto = next(
            (p for p in mock_data.MOCK_PRODUCTS if p["product_id"] == product_id),
            None,
        )
        if not produto:
            return None
        # Simulação simples de link rastreável
        return f"{produto['product_url']}?af_id=SEU_ID_AFILIADO&mock=true"
    else:
        # TODO: chamada real à API para gerar o deep link rastreável
        raise NotImplementedError("Credenciais reais da Shopee ainda não configuradas.")
