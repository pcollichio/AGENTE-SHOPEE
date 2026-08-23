"""
Módulo de curadoria de produtos.

Aplica os critérios definidos no blueprint do cockpit para ranquear
produtos e sugerir os melhores candidatos do dia para virar conteúdo.

Critérios (ver blueprint-cockpit-afiliado-ia.md):
  1. Comissão acima de 10-12%
  2. Avaliação acima de 4,5 estrelas
  3. Volume de vendas relevante
  4. Faixa de preço R$40-100 (compra por impulso)
  5. Frete grátis (aumenta conversão)
"""

from . import client

COMISSAO_MINIMA = 0.10
AVALIACAO_MINIMA = 4.5
PRECO_MIN_IMPULSO = 40.0
PRECO_MAX_IMPULSO = 100.0


def calcular_score(produto):
    """
    Calcula uma pontuação (0 a 100) de quão bom é o produto como candidato
    a virar conteúdo, com base nos critérios do blueprint.
    """
    score = 0

    # Comissão (peso alto - é o que gera receita)
    if produto["commission_rate"] >= COMISSAO_MINIMA:
        score += min(produto["commission_rate"] * 100, 30)  # até 30 pontos

    # Avaliação
    if produto["rating"] >= AVALIACAO_MINIMA:
        score += 20
    elif produto["rating"] >= 4.0:
        score += 10

    # Volume de vendas (normalizado, capando em 20 pontos)
    score += min(produto["total_sold"] / 1000, 20)

    # Faixa de preço ideal para compra por impulso
    if PRECO_MIN_IMPULSO <= produto["price"] <= PRECO_MAX_IMPULSO:
        score += 20

    # Frete grátis
    if produto["free_shipping"]:
        score += 10

    return round(min(score, 100), 1)


def sugerir_produtos_do_dia(quantidade=5, subcategoria=None):
    """
    Retorna os melhores produtos do dia, ranqueados por score, já prontos
    para virar conteúdo (com link de afiliado gerado).
    """
    produtos = client.buscar_produtos(subcategoria=subcategoria)

    ranqueados = []
    for produto in produtos:
        score = calcular_score(produto)
        ranqueados.append({**produto, "score": score})

    ranqueados.sort(key=lambda p: p["score"], reverse=True)
    selecionados = ranqueados[:quantidade]

    # Já anexa o link de afiliado pronto para cada um
    for produto in selecionados:
        produto["affiliate_link"] = client.gerar_link_afiliado(produto["product_id"])

    return selecionados
