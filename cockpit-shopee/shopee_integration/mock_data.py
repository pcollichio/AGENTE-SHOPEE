"""
Dados simulados (mock) da Shopee Affiliate API.

Formato pensado para ficar o mais parecido possível com o que a API real
(GraphQL) deve retornar, para que trocar de mock -> API real no futuro
exija o mínimo de mudança possível no resto do código.
"""

from datetime import datetime, timedelta
import random

MOCK_PRODUCTS = [
    {
        "product_id": "shp_001",
        "name": "Fita LED 5m RGB com Controle Remoto",
        "category": "casa_construcao",
        "subcategory": "iluminacao",
        "price": 39.90,
        "original_price": 69.90,
        "commission_rate": 0.15,
        "rating": 4.7,
        "total_sold": 12500,
        "free_shipping": True,
        "shop_name": "LuzCasa Oficial",
        "image_url": "https://example.com/produtos/fita-led.jpg",
        "product_url": "https://shopee.com.br/product/000001",
    },
    {
        "product_id": "shp_002",
        "name": "Organizador de Panelas Extensível Inox",
        "category": "casa_construcao",
        "subcategory": "cozinha",
        "price": 54.90,
        "original_price": 89.90,
        "commission_rate": 0.12,
        "rating": 4.8,
        "total_sold": 8300,
        "free_shipping": True,
        "shop_name": "OrganizaCasa",
        "image_url": "https://example.com/produtos/organizador-panelas.jpg",
        "product_url": "https://shopee.com.br/product/000002",
    },
    {
        "product_id": "shp_003",
        "name": "Kit 10 Ganchos Adesivos para Parede",
        "category": "casa_construcao",
        "subcategory": "organizacao",
        "price": 19.90,
        "original_price": 34.90,
        "commission_rate": 0.18,
        "rating": 4.6,
        "total_sold": 21000,
        "free_shipping": True,
        "shop_name": "FixaFácil",
        "image_url": "https://example.com/produtos/ganchos.jpg",
        "product_url": "https://shopee.com.br/product/000003",
    },
    {
        "product_id": "shp_004",
        "name": "Furadeira Parafusadeira Elétrica 12V",
        "category": "casa_construcao",
        "subcategory": "ferramentas",
        "price": 149.90,
        "original_price": 229.90,
        "commission_rate": 0.10,
        "rating": 4.5,
        "total_sold": 3400,
        "free_shipping": False,
        "shop_name": "ToolMax",
        "image_url": "https://example.com/produtos/furadeira.jpg",
        "product_url": "https://shopee.com.br/product/000004",
    },
    {
        "product_id": "shp_005",
        "name": "Cabideiro Organizador de Pia Sanfonado",
        "category": "casa_construcao",
        "subcategory": "organizacao",
        "price": 29.90,
        "original_price": 49.90,
        "commission_rate": 0.14,
        "rating": 4.4,
        "total_sold": 6700,
        "free_shipping": True,
        "shop_name": "OrganizaCasa",
        "image_url": "https://example.com/produtos/cabideiro-pia.jpg",
        "product_url": "https://shopee.com.br/product/000005",
    },
    {
        "product_id": "shp_006",
        "name": "Luminária de Mesa LED Touch Regulável",
        "category": "casa_construcao",
        "subcategory": "iluminacao",
        "price": 45.90,
        "original_price": 79.90,
        "commission_rate": 0.16,
        "rating": 4.9,
        "total_sold": 9100,
        "free_shipping": True,
        "shop_name": "LuzCasa Oficial",
        "image_url": "https://example.com/produtos/luminaria-mesa.jpg",
        "product_url": "https://shopee.com.br/product/000006",
    },
    {
        "product_id": "shp_007",
        "name": "Torneira Extensora com Ducha Móvel para Cozinha",
        "category": "casa_construcao",
        "subcategory": "hidraulica",
        "price": 79.90,
        "original_price": 119.90,
        "commission_rate": 0.09,
        "rating": 4.3,
        "total_sold": 2100,
        "free_shipping": False,
        "shop_name": "HidroCasa",
        "image_url": "https://example.com/produtos/torneira.jpg",
        "product_url": "https://shopee.com.br/product/000007",
    },
    {
        "product_id": "shp_008",
        "name": "Prateleira Flutuante de Parede Kit 3 Peças",
        "category": "casa_construcao",
        "subcategory": "organizacao",
        "price": 59.90,
        "original_price": 99.90,
        "commission_rate": 0.13,
        "rating": 4.6,
        "total_sold": 5400,
        "free_shipping": True,
        "shop_name": "FixaFácil",
        "image_url": "https://example.com/produtos/prateleira.jpg",
        "product_url": "https://shopee.com.br/product/000008",
    },
]


def _generate_mock_sales_series(days=7, base=50):
    """Gera uma série temporal simulada de cliques/vendas dos últimos N dias."""
    series = []
    today = datetime.now()
    for i in range(days):
        date = today - timedelta(days=days - i - 1)
        clicks = base + random.randint(-15, 30)
        sales = max(0, int(clicks * random.uniform(0.02, 0.08)))
        series.append({
            "date": date.strftime("%Y-%m-%d"),
            "clicks": clicks,
            "sales": sales,
        })
    return series


MOCK_SALES_INDICATORS = {
    product["product_id"]: {
        "product_id": product["product_id"],
        "last_7_days": _generate_mock_sales_series(),
        "total_commission_earned": round(
            product["price"] * product["commission_rate"] * random.randint(1, 15), 2
        ),
    }
    for product in MOCK_PRODUCTS
}
