"""
Cliente de integração com a Shopee Affiliate API.

Enquanto USE_MOCK_DATA=true (padrão, até você ter as credenciais reais
aprovadas), todas as funções retornam dados simulados de mock_data.py,
mas já no formato esperado da resposta real.

Quando USE_MOCK_DATA=false, as funções chamam a API real via GraphQL.

NOTA sobre os nomes de campos usados nas queries abaixo (productName,
priceMin, commissionRate, ratingStar, sales, offerLink): eles seguem a
documentação pública da Shopee Affiliate Open API, mas ainda não foram
validados contra uma resposta real. Se a Shopee devolver um erro de "campo
desconhecido" (visível na mensagem de erro impressa), ajuste o nome do
campo aqui conforme indicado — isso é esperado e normal na primeira
tentativa com a API real.
"""

import requests

from . import auth
from . import config
from . import mock_data


def _executar_graphql(query, variables=None):
    """Executa uma query/mutation GraphQL autenticada contra a Shopee Affiliate API."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    payload_str, headers = auth.montar_headers(payload)
    response = requests.post(
        config.SHOPEE_API_ENDPOINT, data=payload_str, headers=headers, timeout=20
    )
    response.raise_for_status()

    data = response.json()
    if "errors" in data:
        raise RuntimeError(f"Shopee API retornou erro: {data['errors']}")
    return data["data"]


def _mapear_produto(node):
    """Converte um item da resposta real da Shopee para o formato padronizado usado no resto do sistema."""
    price = float(node.get("priceMin") or node.get("price") or 0)
    return {
        "product_id": str(node.get("itemId")),
        "name": node.get("productName"),
        "category": "casa_construcao",
        "subcategory": None,
        "price": price,
        "original_price": price,
        "commission_rate": float(node.get("commissionRate") or 0),
        "rating": float(node.get("ratingStar") or 0),
        "total_sold": int(node.get("sales") or 0),
        # A Affiliate API não expõe status de frete grátis diretamente;
        # esse critério do blueprint não pode ser filtrado automaticamente
        # por enquanto.
        "free_shipping": None,
        "shop_name": node.get("shopName"),
        "image_url": node.get("imageUrl"),
        "product_url": node.get("offerLink"),
        # O link de afiliado já vem pronto (rastreável) na própria resposta
        # da busca de produtos — não é preciso outra chamada para gerá-lo.
        "affiliate_link": node.get("offerLink"),
    }


def buscar_produtos(subcategoria=None, min_comissao=None, keyword=None, limite=20):
    """
    Busca produtos da Shopee dentro do nicho casa e construção.

    Args:
        subcategoria: filtra por subcategoria (ex: "iluminacao", "cozinha",
            "organizacao", "ferramentas", "hidraulica"). None = todas.
            No modo real, é usado como termo de busca (keyword) se
            `keyword` não for informado.
        min_comissao: filtra produtos com comissão mínima (ex: 0.10 = 10%)
        keyword: termo de busca livre (só usado no modo real)
        limite: quantos produtos pedir à API (só usado no modo real)

    Returns:
        Lista de produtos no formato padronizado.
    """
    if config.USE_MOCK_DATA:
        produtos = mock_data.MOCK_PRODUCTS
        if subcategoria:
            produtos = [p for p in produtos if p["subcategory"] == subcategoria]
        if min_comissao is not None:
            produtos = [p for p in produtos if p["commission_rate"] >= min_comissao]
        return produtos

    query = """
    query BuscarProdutos($keyword: String, $limit: Int) {
      productOfferV2(keyword: $keyword, limit: $limit) {
        nodes {
          itemId
          productName
          commissionRate
          price
          priceMin
          priceMax
          sales
          ratingStar
          imageUrl
          shopName
          offerLink
        }
      }
    }
    """
    variables = {"keyword": keyword or subcategoria or "", "limit": limite}
    data = _executar_graphql(query, variables)
    nodes = (data.get("productOfferV2") or {}).get("nodes") or []
    produtos = [_mapear_produto(n) for n in nodes]

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
        # A taxa de comissão já vem junto de cada produto em buscar_produtos()
        # (campo "commission_rate") — use esse valor diretamente em vez de
        # chamar esta função no modo real.
        raise NotImplementedError(
            "obter_comissao não é necessário no modo real: use o campo "
            "'commission_rate' já retornado por buscar_produtos()."
        )


def obter_indicadores_vendas(product_id):
    """Retorna cliques/vendas dos últimos 7 dias e comissão acumulada de um produto."""
    if config.USE_MOCK_DATA:
        return mock_data.MOCK_SALES_INDICATORS.get(product_id)
    else:
        # Isso depende de um endpoint diferente da Shopee — relatório de
        # performance/conversão do próprio afiliado (cliques e vendas ao
        # longo do tempo), que é uma área separada da API de catálogo de
        # ofertas (productOfferV2). Ainda não foi mapeado; precisamos da
        # documentação/Postman Collection da Shopee sobre relatórios de
        # conversão para implementar isso com segurança.
        raise NotImplementedError(
            "Indicadores de vendas ainda não implementados para dados reais "
            "— depende do endpoint de relatório de conversão da Shopee, "
            "ainda não mapeado."
        )


def gerar_link_afiliado(product_id, produtos_cache=None):
    """
    Gera o link de afiliado de um produto específico.

    No modo real, o link rastreável já vem pronto no campo "affiliate_link"
    de cada produto devolvido por buscar_produtos() — não é necessário
    chamar esta função separadamente nesse caso.
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
        if produtos_cache:
            produto = next(
                (p for p in produtos_cache if p["product_id"] == str(product_id)),
                None,
            )
            if produto:
                return produto["affiliate_link"]
        raise NotImplementedError(
            "No modo real, use o campo 'affiliate_link' já presente no "
            "produto retornado por buscar_produtos() em vez de chamar esta "
            "função separadamente."
        )


def buscar_conversoes(purchase_time_start, purchase_time_end, limit=100, scroll_id=None):
    """
    Busca o relatório de conversões (vendas reais geradas pelos seus links
    de afiliado) num período, via a query conversionReport.

    Args:
        purchase_time_start: início do período, timestamp Unix (segundos)
        purchase_time_end: fim do período, timestamp Unix (segundos)
        limit: quantos registros pedir por página (a Shopee costuma limitar a 500)
        scroll_id: cursor de paginação devolvido pela página anterior

    Returns:
        dict com "nodes" (lista de conversões) e "pageInfo" (paginação)

    NOTA: validado parcialmente contra uma resposta real da Shopee em
    2026-08-30 — ela apontou dois ajustes (tipo Int64 nas variáveis de
    data, e o campo chama-se "conversionStatus", não "orderStatus" no
    nível da conversão) já corrigidos abaixo. O restante dos campos
    ainda não foi confirmado; se aparecer outro erro de "campo
    desconhecido", ajuste aqui conforme a mensagem indicar.
    """
    if config.USE_MOCK_DATA:
        raise NotImplementedError(
            "buscar_conversoes ainda não tem versão simulada — só funciona "
            "com USE_MOCK_DATA=false e credenciais reais."
        )

    query = """
    query BuscarConversoes($inicio: Int64, $fim: Int64, $limit: Int, $scrollId: String) {
      conversionReport(purchaseTimeStart: $inicio, purchaseTimeEnd: $fim, limit: $limit, scrollId: $scrollId) {
        nodes {
          conversionId
          purchaseTime
          conversionStatus
          totalCommission
          orders {
            orderId
            orderStatus
            items {
              itemId
              itemName
              itemTotalCommission
            }
          }
        }
        pageInfo {
          hasNextPage
          scrollId
        }
      }
    }
    """
    variables = {
        "inicio": purchase_time_start,
        "fim": purchase_time_end,
        "limit": limit,
        "scrollId": scroll_id,
    }
    data = _executar_graphql(query, variables)
    return data.get("conversionReport") or {"nodes": [], "pageInfo": {}}
