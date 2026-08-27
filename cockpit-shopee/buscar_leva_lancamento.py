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

ARQUIVO_PRODUTOS_MANUAIS = "produtos_manuais.txt"


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


def carregar_termos_manuais(caminho=ARQUIVO_PRODUTOS_MANUAIS):
    """Lê produtos_manuais.txt: uma palavra-chave por linha, ignorando
    linhas em branco e comentários (#)."""
    try:
        with open(caminho, encoding="utf-8") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        return []

    termos = []
    for linha in linhas:
        termo = linha.strip()
        if termo and not termo.startswith("#"):
            termos.append(termo)
    return termos


def buscar_produtos_manuais(termos, ids_ja_incluidos=None):
    """Busca produtos específicos pedidos manualmente (via
    produtos_manuais.txt). Ao contrário da leva automática, não aplica
    filtro de comissão/avaliação — o usuário pediu esse produto de
    propósito, então ele entra do jeito que a Shopee retornar."""
    ids_ja_incluidos = ids_ja_incluidos or set()
    encontrados = []
    vistos = set(ids_ja_incluidos)

    for termo in termos:
        try:
            produtos = client.buscar_produtos(keyword=termo, limite=5)
        except Exception as e:
            print(f"Aviso: busca manual por '{termo}' falhou: {e}")
            continue

        for p in produtos:
            if p["product_id"] in vistos:
                continue
            vistos.add(p["product_id"])
            encontrados.append({**p, "tier": _classificar_tier(p["price"]), "termo_busca": termo})

    return encontrados


def formatar_markdown(produtos, titulo="Leva de produtos do dia", extras=None):
    """Formata a leva de produtos (e, opcionalmente, os adicionados
    manualmente) como tabelas Markdown, prontas para ser salvas como
    histórico (legível tanto no terminal quanto no GitHub)."""
    faixa_label = {"baixo": "Baixo", "medio": "Médio", "alto": "Alto"}

    def _tabela(lista):
        linhas = [
            "| # | Produto | Faixa | Preço | Comissão | Avaliação | Vendidos | Link de afiliado |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for i, p in enumerate(lista, start=1):
            nome = (p["name"] or "(sem nome)").replace("|", "-")
            linhas.append(
                f"| {i} | {nome} | {faixa_label[p['tier']]} | R${p['price']:.2f} | "
                f"{p['commission_rate']*100:.0f}% | {p['rating']:.1f}⭐ | "
                f"{p['total_sold']} | [link]({p['affiliate_link']}) |"
            )
        return "\n".join(linhas)

    partes = [f"# {titulo} — {date.today().isoformat()}", "", _tabela(produtos)]

    if extras:
        partes += ["", "## Adicionados manualmente (produtos_manuais.txt)", "", _tabela(extras)]

    return "\n".join(partes)


def main():
    if config.USE_MOCK_DATA:
        print(
            "USE_MOCK_DATA está true — configure USE_MOCK_DATA=false no .env "
            "para buscar produtos reais."
        )
        return

    leva = montar_leva_variada()

    termos_manuais = carregar_termos_manuais()
    extras = buscar_produtos_manuais(
        termos_manuais, ids_ja_incluidos={p["product_id"] for p in leva}
    )

    if not leva and not extras:
        print(
            f"# Leva de produtos do dia — {date.today().isoformat()}\n\n"
            "Nenhum produto encontrado hoje. Pode ser que os termos de busca "
            "não retornaram resultados, que os nomes dos campos da API "
            "precisem de ajuste, ou que a Shopee tenha recusado a "
            "autenticação — veja os avisos acima (se houver) para o motivo "
            "exato."
        )
    else:
        print(formatar_markdown(leva, extras=extras))

    # Sempre salva o painel, mesmo com a leva vazia (ex: falha temporária na
    # API), para o passo seguinte do workflow sempre ter um arquivo pra
    # commitar e não quebrar a automação.
    caminho_painel = painel.salvar_painel(leva, "painel.html", extras=extras)
    print(f"Painel visual salvo em: {caminho_painel}", file=sys.stderr)


if __name__ == "__main__":
    main()
