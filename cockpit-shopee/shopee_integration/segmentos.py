"""
Classificador de segmento de produto (beleza, casa & construção, moda
etc.), por palavras-chave no nome.

Por quê por palavras-chave, e não pela categoria oficial da Shopee: a
Affiliate API (productOfferV2) não devolve nenhum campo de categoria do
produto (ver NOTA em client.py — `category`/`subcategory` vêm sempre
`None` no mapeamento real). Pedido do usuário em 11/09: um filtro por
segmento no painel, agora que a leva traz produtos de qualquer
categoria. Sem campo de categoria vindo da API, a única forma viável é
inferir pelo nome do produto — não é perfeito (nome comercial nem
sempre é claro, e um produto pode encaixar em mais de um segmento), mas
cobre bem a maioria dos casos reais observados na leva.
"""

import unicodedata


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).lower()


# Ordem importa: a primeira lista cujo termo bater no nome vence — por
# isso termos mais específicos vêm antes dos mais genéricos.
_SEGMENTOS = [
    ("beleza", [
        "maquiagem", "batom", "base facial", "skincare", "hidratante facial",
        "serum", "shampoo", "condicionador", "escova de cabelo",
        "secador de cabelo", "prancha de cabelo", "chapinha", "perfume",
        "esmalte", "delineador", "rimel", "mascara de cilios",
        "protetor solar", "creme facial", "sabonete facial", "depilador",
        "pinca de sobrancelha", "gloss labial", "primer facial",
    ]),
    ("casa_construcao", [
        "torneira", "sifao", "chuveiro", "mangueira", "furadeira",
        "impermeabilizante", "argamassa", "vedante", "vedacit", "parafuso",
        "luminaria", "lampada", "organizador", "prateleira", "cortina",
        "tapete", "panela", "louca", "colher", "talher", "prato", "copo",
        "utensilio de cozinha", "faqueiro", "jogo de cama", "edredom",
        "toalha de banho", "painel ripado", "rodape", "decoracao",
        "quadro decorativo", "esfregador", "vassoura", "rodo",
        "escova de limpeza", "aspirador", "porta temperos",
        "prendedor de roupa", "varal",
    ]),
    ("moda", [
        "vestido", "camiseta", "camisa", "calca", "shorts", "saia",
        "jaqueta", "sutia", "lingerie", "baby doll", "biquini",
        "sandalia", "tenis", "bolsa feminina", "bolsa transversal",
        "carteira", "cinto", "oculos de sol", "moletom",
        "conjunto academia", "top fitness", "legging", "meia calca",
        "regata feminina",
    ]),
    ("eletronicos", [
        "fone de ouvido", "fone bluetooth", "carregador", "cabo usb",
        "power bank", "smartwatch", "caixa de som", "mouse", "teclado",
        "webcam", "hd externo", "pendrive", "capinha", "pelicula",
        "suporte de celular", "adaptador", "smartband",
    ]),
    ("pet", [
        "racao", "coleira", "guia para cachorro", "brinquedo pet",
        "arranhador", "caminha para cachorro", "comedouro pet",
        "aquario",
    ]),
    ("infantil", [
        "brinquedo infantil", "boneca", "carrinho de bebe", "fralda",
        "mamadeira", "chupeta", "body infantil", "roupa de bebe",
    ]),
    ("esporte_lazer", [
        "halter", "elastico de exercicio", "corda de pular", "colchonete",
        "bicicleta", "bola de futebol", "luva de treino", "squeeze",
    ]),
    ("saude", [
        "vitamina", "suplemento", "termometro", "mascara facial",
        "oximetro", "colageno",
    ]),
    ("papelaria_escritorio", [
        "caderno", "caneta", "mochila escolar", "estojo escolar",
        "organizador de mesa", "planner", "adesivo escolar",
    ]),
    ("automotivo", [
        "capa de carro", "tapete automotivo", "aromatizante de carro",
        "suporte veicular", "carregador veicular",
    ]),
]

# Ordem de exibição no filtro do painel (só entram as que tiverem pelo
# menos um produto na leva do dia — ver painel.py).
ORDEM_EXIBICAO = [chave for chave, _ in _SEGMENTOS] + ["outros"]

SEGMENTO_LABELS = {
    "beleza": "Beleza",
    "casa_construcao": "Casa & Construção",
    "moda": "Moda",
    "eletronicos": "Eletrônicos",
    "pet": "Pet",
    "infantil": "Infantil",
    "esporte_lazer": "Esporte & Lazer",
    "saude": "Saúde",
    "papelaria_escritorio": "Papelaria & Escritório",
    "automotivo": "Automotivo",
    "outros": "Outros",
}

_TERMOS_NORMALIZADOS = [
    (chave, [_normalizar(termo) for termo in termos]) for chave, termos in _SEGMENTOS
]


def inferir_segmento(nome_produto):
    """Classifica o produto num segmento a partir de palavras-chave no
    nome (heurística — ver módulo). Retorna 'outros' quando nenhuma
    palavra-chave bate."""
    nome_normalizado = _normalizar(nome_produto)
    for chave, termos in _TERMOS_NORMALIZADOS:
        if any(termo in nome_normalizado for termo in termos):
            return chave
    return "outros"
