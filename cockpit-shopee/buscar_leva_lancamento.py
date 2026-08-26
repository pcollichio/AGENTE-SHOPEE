"""
Busca produtos reais da Shopee no nicho casa e construção e monta uma leva
de 20 oportunidades para @papairesolve_br escolher o que divulgar,
distribuídas entre ticket baixo, médio e alto (para dar variedade de preço,
não só produtos de compra por impulso).

Critérios de qualidade (blueprint, seção 5):
  - Comissão acima de 10-12%
  - Avaliação acima de 4,5 estrelas

Rode com: python buscar_leva_lancamento.py

IMPORTANTE: precisa de acesso real à internet e das credenciais reais
configuradas no .env (USE_MOCK_DATA=false). Não funciona em sandboxes sem
acesso externo — rode no seu computador ou no Google Colab, como fizemos
no teste de conexão.

NOTA: a Shopee Affiliate API não expõe o status de frete grátis nem uma
categoria oficial "casa e construção" (ainda não temos a lista de
categorias da Shopee) — por isso a busca é feita por palavra-chave,
cobrindo os principais subnichos da casa.
"""

import sys
from datetime import date

from shopee_integration import client, config, curadoria, painel

# Palavras-chave para cobrir bem o nicho "casa e construção" (sem depender
# de um código de categoria oficial da Shopee, que ainda não temos)
SUBCATEGORIAS_CASA_CONSTRUCAO = [
    "ferramentas",
    "organizacao",
    "iluminacao",
    "hidraulica",
    "decoracao",
    "cozinha",
    "banheiro",
    "jardim",
    "eletrica",
    "pintura",
    "limpeza",
    "moveis",
]

# Faixas de ticket médio (em reais)
TICKET_BAIXO_MAX = 50.0
TICKET_MEDIO_MAX = 150.0

QUANTIDADE_TOTAL = 20


def _classificar_tier(preco):
    if preco <= TICKET_BAIXO_MAX:
        return "baixo"
    if preco <= TICKET_MEDIO_MAX:
        return "medio"
    return "alto"


def buscar_produtos_do_nicho():
    """Busca produtos em todas as palavras-chave do nicho e remove duplicados."""
    todos_produtos = []
    for termo in SUBCATEGORIAS_CASA_CONSTRUCAO:
        try:
            produtos = client.buscar_produtos(
                keyword=termo, min_comissao=curadoria.COMISSAO_MINIMA, limite=20
            )
            todos_produtos.extend(produtos)
        except Exception as e:
            print(f"Aviso: busca por '{termo}' falhou: {e}")

    vistos = set()
    produtos_unicos = []
    for p in todos_produtos:
        if p["product_id"] not in vistos:
            vistos.add(p["product_id"])
            produtos_unicos.append(p)
    return produtos_unicos


def montar_leva_variada(quantidade_total=QUANTIDADE_TOTAL):
    """Busca produtos do nicho e seleciona os melhores, distribuídos entre
    ticket baixo/médio/alto, para dar opções de preço variadas."""
    produtos = buscar_produtos_do_nicho()

    # Critério mínimo de qualidade (comissão e avaliação); sem filtro de
    # preço aqui, pois é justamente a variação de preço que queremos.
    qualificados = [
        {**p, "tier": _classificar_tier(p["price"]), "score": curadoria.calcular_score(p)}
        for p in produtos
        if p["commission_rate"] >= curadoria.COMISSAO_MINIMA
        and p["rating"] >= curadoria.AVALIACAO_MINIMA
    ]

    por_tier = {"baixo": [], "medio": [], "alto": []}
    for p in qualificados:
        por_tier[p["tier"]].append(p)
    for tier in por_tier:
        por_tier[tier].sort(key=lambda p: p["score"], reverse=True)

    # Distribui a quantidade igualmente entre as 3 faixas (com sobra pros
    # dois primeiros tiers), pegando o que houver disponível em cada uma
    base = quantidade_total // 3
    metas = {"baixo": base + 1, "medio": base + 1, "alto": base}

    selecionados = []
    for tier, meta in metas.items():
        selecionados.extend(por_tier[tier][:meta])

    # Se alguma faixa não tinha produtos suficientes, completa com o
    # restante disponível (de qualquer faixa), até atingir a quantidade
    if len(selecionados) < quantidade_total:
        ja_selecionados_ids = {p["product_id"] for p in selecionados}
        restantes = sorted(
            (p for p in qualificados if p["product_id"] not in ja_selecionados_ids),
            key=lambda p: p["score"],
            reverse=True,
        )
        faltam = quantidade_total - len(selecionados)
        selecionados.extend(restantes[:faltam])

    selecionados.sort(key=lambda p: p["score"], reverse=True)
    return selecionados


def formatar_markdown(produtos):
    """Formata a leva de produtos como uma tabela Markdown, pronta para ser
    salva como histórico (legível tanto no terminal quanto no GitHub)."""
    linhas = [
        f"# Leva de produtos do dia — {date.today().isoformat()}",
        "",
        "| # | Produto | Faixa | Preço | Comissão | Avaliação | Vendidos | Link de afiliado |",
        "|---|---|---|---|---|---|---|---|",
    ]
    faixa_label = {"baixo": "Baixo", "medio": "Médio", "alto": "Alto"}
    for i, p in enumerate(produtos, start=1):
        nome = (p["name"] or "(sem nome)").replace("|", "-")
        linhas.append(
            f"| {i} | {nome} | {faixa_label[p['tier']]} | R${p['price']:.2f} | "
            f"{p['commission_rate']*100:.0f}% | {p['rating']:.1f}⭐ | "
            f"{p['total_sold']} | [link]({p['affiliate_link']}) |"
        )
    return "\n".join(linhas)


def main():
    if config.USE_MOCK_DATA:
        print(
            "USE_MOCK_DATA está true — configure USE_MOCK_DATA=false no .env "
            "para buscar produtos reais."
        )
        return

    leva = montar_leva_variada()

    if not leva:
        print(
            f"# Leva de produtos do dia — {date.today().isoformat()}\n\n"
            "Nenhum produto encontrado com os critérios atuais. Pode ser que "
            "os termos de busca não retornaram resultados, ou que os nomes "
            "dos campos da API precisem de ajuste (veja os comentários em "
            "shopee_integration/client.py)."
        )
        return

    print(formatar_markdown(leva))

    caminho_painel = painel.salvar_painel(leva, "painel.html")
    print(f"Painel visual salvo em: {caminho_painel}", file=sys.stderr)


if __name__ == "__main__":
    main()
