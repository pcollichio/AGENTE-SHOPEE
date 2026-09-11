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

from shopee_integration import client, config, link_resolver, segmentos  # noqa: E402

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
        link_rastreavel_direto = None
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
            # Gera o link rastreável direto da URL colada (mutation
            # generateShortLink — ver NOTA em client.py), em vez de depender
            # só de achar esse mesmo item de novo na busca por palavra-chave
            # abaixo. Best-effort: se falhar (mutation ainda não validada
            # contra a API real, ou erro de rede), segue com o link que a
            # busca por palavra-chave trouxer, como já funcionava antes.
            try:
                link_rastreavel_direto = client.gerar_link_rastreavel(url_final)
            except Exception as e:
                print(f"Aviso: gerar_link_rastreavel falhou: {e}", file=sys.stderr)

        try:
            produtos = client.buscar_produtos(keyword=termo, limite=8)
        except Exception as e:
            self._responder(502, {"erro": f"Não consegui buscar na Shopee agora: {e}"})
            return

        for p in produtos:
            p["tier"] = _classificar_tier(p["price"])
            p["segmento"] = segmentos.inferir_segmento(p["name"])

        if item_id_alvo:
            exato = next((p for p in produtos if p["product_id"] == item_id_alvo), None)
            if exato:
                if link_rastreavel_direto:
                    exato["affiliate_link"] = link_rastreavel_direto
                self._responder(200, {"produtos": [exato], "correspondencia_exata": True})
                return
            if link_rastreavel_direto:
                # Não achamos os detalhes (nome/preço/foto) do produto colado
                # entre os resultados da busca por palavra-chave, mas
                # conseguimos gerar o link rastreável exato da URL — devolve
                # ele separado, pra não perder essa garantia mesmo sem os
                # detalhes visuais.
                self._responder(200, {
                    "produtos": produtos,
                    "termo_usado": termo,
                    "link_rastreavel_sem_correspondencia": link_rastreavel_direto,
                })
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
