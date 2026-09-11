"""
Busca os produtos mais vendidos da Shopee via API (sortType "mais
vendidos", sem restringir por nicho/categoria) e traz os melhores 50
(por score de curadoria) pra selecionar direto no painel — que tem os
filtros (faixa de preço, comissão mínima, avaliação mínima, vendidos
mínimo) pra aplicar no momento da escolha, não antes.

Histórico da fonte de produtos: 31/08 "traga todos e deixe que eu faça
a seleção" (ainda restrito ao nicho casa & construção, por
palavra-chave) → 01/09 filtro de qualidade virou interativo no painel →
02/09 teto de 50 → 10/09 "não quero mais que filtre só casa e
construção, quero os mais vendidos da Shopee via API" — removida a
busca por palavra-chave de nicho, agora é uma chamada só à API pedindo
os mais vendidos em geral (ver HISTORICO.md).

Rode com: python buscar_leva_lancamento.py

IMPORTANTE: precisa de acesso real à internet e das credenciais reais
configuradas no .env (USE_MOCK_DATA=false). Não funciona em sandboxes sem
acesso externo — rode no seu computador ou no Google Colab, como fizemos
no teste de conexão.

NOTA: o parâmetro sortType usado aqui pra pedir "mais vendidos" ainda
não foi validado contra uma resposta real da Shopee — se ela recusar o
campo, ajuste em shopee_integration/client.py (ver nota lá no topo).
"""

import sys
import unicodedata
from datetime import date

from shopee_integration import client, config, curadoria, painel, segmentos

# Faixas de ticket médio (em reais)
TICKET_BAIXO_MAX = 50.0
TICKET_MEDIO_MAX = 150.0

# Teto da leva diária — só os melhores, não tudo que a busca encontrar.
LIMITE_LEVA = 50

# A Shopee recusa mais de 50 itens por página (erro 11001, validado
# contra resposta real em 10/09) — então pedimos várias páginas de 50
# em vez de um limite maior numa chamada só.
PAGINAS_BUSCA_API = 2

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
    """Lê produtos_excluir.txt: uma lista de bloqueio manual — palavras
    que, se aparecerem no nome do produto, tiram ele da leva automática,
    mesmo estando entre os mais vendidos (ex: categorias que você não
    quer promover)."""
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


def _produto_excluido(nome, termos_excluidos):
    nome_normalizado = _normalizar(nome)
    return any(termo in nome_normalizado for termo in termos_excluidos)


def buscar_mais_vendidos():
    """Busca os produtos mais vendidos da Shopee via API (sortType
    "sales"), sem restringir por nicho/categoria, paginando (a Shopee
    limita a 50 por página) até PAGINAS_BUSCA_API, e descarta os que
    batem com produtos_excluir.txt (bloqueio manual)."""
    termos_excluidos = carregar_termos_excluidos()

    produtos = []
    for pagina in range(1, PAGINAS_BUSCA_API + 1):
        try:
            produtos_pagina = client.buscar_produtos(
                limite=client.LIMITE_MAXIMO_POR_PAGINA, sort_type="sales", pagina=pagina
            )
        except Exception as e:
            print(f"Aviso: busca dos mais vendidos (página {pagina}) falhou: {e}")
            break
        if not produtos_pagina:
            break
        produtos.extend(produtos_pagina)
        if len(produtos_pagina) < client.LIMITE_MAXIMO_POR_PAGINA:
            break  # última página (veio menos que o máximo)

    vistos = set()
    produtos_unicos = []
    for p in produtos:
        if p["product_id"] in vistos:
            continue
        if _produto_excluido(p["name"], termos_excluidos):
            continue
        vistos.add(p["product_id"])
        produtos_unicos.append(p)
    return produtos_unicos


def montar_leva_variada():
    """Busca os produtos mais vendidos da Shopee (sem filtro de
    comissão/avaliação — isso é interativo, no painel), classifica por
    faixa de preço, ordena por score e devolve só os LIMITE_LEVA
    melhores."""
    produtos = buscar_mais_vendidos()

    todos = [
        {
            **p,
            "tier": _classificar_tier(p["price"]),
            "score": curadoria.calcular_score(p),
            "segmento": segmentos.inferir_segmento(p["name"]),
        }
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
            encontrados.append({
                **p,
                "tier": _classificar_tier(p["price"]),
                "termo_busca": termo,
                "segmento": segmentos.inferir_segmento(p["name"]),
            })

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
