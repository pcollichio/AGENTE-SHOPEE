"""
Função serverless (Vercel, runtime Python) que busca um produto específico
na Shopee, ao vivo, a pedido de quem está usando o painel — pra achar algo
que não apareceu na leva automática do dia.

Aceita tanto uma descrição/nome quanto um link da Shopee (curto ou da
página do produto) — nesse caso segue o link e extrai o nome/itemId do
produto (mesma lógica de `buscar_um_produto.py`, em
`shopee_integration/link_resolver.py`). Pedido do usuário em 02/09: "o
fluxo mais fácil vai ser achar o produto no app Shopee e trazer pro
agente" — colar o link direto no painel, sem precisar passar pelo chat.

Reaproveita o mesmo cliente já validado contra a API real
(shopee_integration/client.py) em vez de reimplementar a assinatura da
Shopee em JavaScript — reduz o risco de bugs de assinatura.

Precisa das mesmas variáveis de ambiente da automação diária, configuradas
na Vercel: SHOPEE_APP_ID, SHOPEE_APP_SECRET e USE_MOCK_DATA=false.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shopee_integration import client, config, link_resolver  # noqa: E402

TICKET_BAIXO_MAX = 50.0
TICKET_MEDIO_MAX = 150.0


def _classificar_tier(preco):
    if preco <= TICKET_BAIXO_MAX:
        return "baixo"
    if preco <= TICKET_MEDIO_MAX:
        return "medio"
    return "alto"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        entrada = (query.get("q") or [""])[0].strip()

        if not entrada:
            self._responder(400, {"erro": "Informe uma descrição ou um link do produto para buscar (parâmetro q)."})
            return

        if config.USE_MOCK_DATA:
            self._responder(500, {
                "erro": "Busca ainda não configurada neste servidor — faltam "
                        "SHOPEE_APP_ID, SHOPEE_APP_SECRET e USE_MOCK_DATA=false "
                        "nas variáveis de ambiente da Vercel."
            })
            return

        item_id_alvo = None
        termo = entrada
        veio_de_link = link_resolver.eh_link(entrada)
        if veio_de_link:
            try:
                url_final = link_resolver.resolver_link(entrada)
            except Exception as e:
                self._responder(502, {"erro": f"Não consegui abrir esse link: {e}"})
                return
            termo, item_id_alvo = link_resolver.extrair_info_link(url_final)
            if not termo:
                self._responder(400, {"erro": link_resolver.MENSAGEM_LINK_SEM_NOME})
                return

        try:
            produtos = client.buscar_produtos(keyword=termo, limite=8)
        except Exception as e:
            self._responder(502, {"erro": f"Não consegui buscar na Shopee agora: {e}"})
            return

        for p in produtos:
            p["tier"] = _classificar_tier(p["price"])

        if item_id_alvo:
            exato = next((p for p in produtos if p["product_id"] == item_id_alvo), None)
            if exato:
                self._responder(200, {"produtos": [exato], "correspondencia_exata": True})
                return

        resposta = {"produtos": produtos}
        if veio_de_link:
            resposta["termo_usado"] = termo
        self._responder(200, resposta)

    def _responder(self, status, corpo):
        payload = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
