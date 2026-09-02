"""
Busca produtos reais da Shopee no nicho casa e construção e traz os
melhores 50 (por score de curadoria, sem filtro de comissão, avaliação
ou vendas) pra @papairesolve_br selecionar direto no painel — que tem
os filtros (faixa de preço, comissão mínima, avaliação mínima) pra
aplicar no momento da escolha, não antes.

Pedido do usuário (31/08, 01/09 e 02/09): primeiro "traga todos e deixe
que eu faça a seleção", depois "todos que fazem parte do nicho de casa
e construção... o filtro no momento das escolhas dos produtos", depois
"vamos trazer apenas 50 produtos do nosso nicho" — ou seja, o único
corte por volume é o teto de 50 (os melhores por score); qualidade
(comissão, avaliação) continua sendo filtro interativo no painel, não
um corte na busca.

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
import unicodedata
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

# Teto da leva diária — pedido do usuário em 02/09: só os 50 melhores
# (por score de curadoria) do nicho, não todos os que a busca encontrar.
LIMITE_LEVA = 50

ARQUIVO_PRODUTOS_MANUAIS = "produtos_manuais.txt"
ARQUIVO_PRODUTOS_EXCLUIR = "produtos_excluir.txt"


def _classificar_tier(preco):
    if preco <= TICKET_BAIXO_MAX:
        return "baixo"
    if preco <= TICKET_MEDIO_MAX:
        return "medio"
    return "alto"


def _normalizar(texto):
    """Remove acentos e caixa alta, para comparar texto sem depender de
    acentuação exata (ex: 'balão' e 'balao' batem igual)."""
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).lower()


def carregar_termos_excluidos(caminho=ARQUIVO_PRODUTOS_EXCLUIR):
    """Lê produtos_excluir.txt: palavras que, se aparecerem no nome do
    produto, tiram ele da leva automática (a busca por palavra-chave da
    Shopee é ampla e às vezes traz produtos fora do nicho, ex: brinquedos,
    itens pet, peças de carro)."""
    try:
        with open(caminho, encoding="utf-8") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        return []

    termos = []
    for linha in linhas:
        termo = linha.strip()
        if termo and not termo.startswith("#"):
            termos.append(_normalizar(termo))
    return termos


def _produto_fora_do_nicho(nome, termos_excluidos):
    nome_normalizado = _normalizar(nome)
    return any(termo in nome_normalizado for termo in termos_excluidos)


def buscar_produtos_do_nicho():
    """Busca produtos em todas as palavras-chave do nicho, remove duplicados
    e descarta os que batem com produtos_excluir.txt (fora do nicho)."""
    termos_excluidos = carregar_termos_excluidos()

    todos_produtos = []
    for termo in SUBCATEGORIAS_CASA_CONSTRUCAO:
        try:
            # Sem filtro de comissão aqui — trazemos todo mundo do nicho,
            # o filtro de qualidade é interativo, no painel. Limite alto
            # (50) só pra dar mais opções de produto por palavra-chave.
            produtos = client.buscar_produtos(keyword=termo, limite=50)
            for p in produtos:
                p["termo_busca"] = termo
            todos_produtos.extend(produtos)
        except Exception as e:
            print(f"Aviso: busca por '{termo}' falhou: {e}")

    vistos = set()
    produtos_unicos = []
    for p in todos_produtos:
        if p["product_id"] in vistos:
            continue
        if _produto_fora_do_nicho(p["name"], termos_excluidos):
            continue
        vistos.add(p["product_id"])
        produtos_unicos.append(p)
    return produtos_unicos


def montar_leva_variada():
    """Busca produtos do nicho (sem filtro de comissão/avaliação — só o
    filtro de nicho já aplicado em buscar_produtos_do_nicho), classifica
    por faixa de preço, ordena por score e devolve só os LIMITE_LEVA
    melhores. Pedido do usuário em 01/09: o filtro de qualidade
    (comissão, avaliação) acontece no momento da seleção, no painel —
    não antes; pedido em 02/09: limitar a leva aos 50 melhores, não
    trazer o nicho inteiro."""
    produtos = buscar_produtos_do_nicho()

    todos = [
        {**p, "tier": _classificar_tier(p["price"]), "score": curadoria.calcular_score(p)}
        for p in produtos
    ]

    todos.sort(key=lambda p: p["score"], reverse=True)
    return todos[:LIMITE_LEVA]


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
