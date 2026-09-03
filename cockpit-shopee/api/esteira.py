"""
Função serverless (Vercel, runtime Python) que devolve o estado atual da
esteira (produtos selecionados, já cruzados com o financeiro) como JSON.

Existe porque `esteira.html` era só um retrato estático, gerado apenas
quando o workflow `leva-diaria.yml` roda (uma vez por dia) — então um
produto selecionado, uma etapa mudada ou uma venda registrada só
apareciam na página no dia seguinte. Esse endpoint deixa a página
sempre buscar o estado mais recente ao abrir, sem depender do próximo
horário da leva (usuário reportou em 03/09: "a esteira não está
atualizando").

Reaproveita a mesma lógica de cálculo de `shopee_integration/esteira.py`
(carregar_esteira + calcular_status), sem duplicar nada em JavaScript —
os arquivos (esteira.json, financeiro/*.csv) fazem parte do deploy da
Vercel, então já estão atualizados a cada novo commit/redeploy.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shopee_integration import esteira as esteira_calc, roi as roi_calc  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            itens = esteira_calc.carregar_esteira()
            investimentos = roi_calc.carregar_investimentos()
            vendas = roi_calc.carregar_vendas()
            calculada = esteira_calc.calcular_status(itens, investimentos, vendas)
        except Exception as e:
            self._responder(500, {"erro": f"Não consegui calcular a esteira agora: {e}"})
            return

        self._responder(200, {"itens": calculada})

    def _responder(self, status, corpo):
        payload = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
