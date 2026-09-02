"""
Resolve links da Shopee (curtos, tipo s.shopee.com.br, ou o link completo
da página do produto) pra extrair um termo de busca e o itemId, quando
presente. Usado tanto por `buscar_um_produto.py` (busca manual via
GitHub Actions, a pedido no chat) quanto por `api/buscar_produto.py` (a
busca ao vivo, direto do painel) — mesma lógica, um lugar só.
"""

import re

import requests


def eh_link(texto):
    return texto.startswith("http://") or texto.startswith("https://")


def resolver_link(url):
    """Segue redirecionamentos (caso de link curto s.shopee.com.br) e
    devolve a URL final do produto."""
    resposta = requests.get(url, allow_redirects=True, timeout=15)
    return resposta.url


def extrair_info_link(url):
    """Tenta extrair um termo de busca (a partir do slug da URL) e o
    itemId do produto, quando presente — em dois formatos possíveis:
    .../nome-do-produto-i.<shopId>.<itemId> (link de página de produto,
    o formato normal quando você copia o link direto do app) ou
    .../product/<shopId>/<itemId> (formato sem nome, comum em links de
    afiliado/rastreamento — nesse caso não tem nome pra extrair)."""
    item_id = None

    m = re.search(r"-i\.(\d+)\.(\d+)", url)
    if m:
        item_id = m.group(2)
    else:
        m = re.search(r"/product/(\d+)/(\d+)", url)
        if m:
            item_id = m.group(2)

    caminho = url.split("?")[0].rstrip("/")
    slug = caminho.rsplit("/", 1)[-1]
    slug = re.sub(r"-i\.\d+\.\d+$", "", slug)
    termo = re.sub(r"[-_]+", " ", slug).strip()

    # Slug puramente numérico (ou vazio) não é um nome de produto —
    # normalmente é um link de rastreamento/afiliado, sem nome na URL.
    if not termo or termo.isdigit():
        termo = None

    return termo, item_id


MENSAGEM_LINK_SEM_NOME = (
    "Esse link não tem o nome do produto na URL — parece ser um link de "
    "rastreamento/afiliado, não o link da página do produto. Copie o link "
    "direto de dentro do app da Shopee, na página do produto (compartilhar "
    "> copiar link), ou digite o nome do produto."
)
