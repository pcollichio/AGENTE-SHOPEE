"""
Autenticação da Shopee Affiliate Open API.

A Shopee exige que cada requisição seja assinada, no formato:

    Authorization: SHA256 Credential={AppId}, Timestamp={timestamp}, Signature={signature}

Onde:
    signature = SHA256( AppId + Timestamp + Payload + Secret )   (em hexadecimal)

- Timestamp: segundos Unix (não milissegundos), com janela de validade de
  cerca de 5 minutos — se o relógio da máquina estiver muito errado, a
  Shopee vai rejeitar a requisição.
- Payload: o corpo (body) exato da requisição GraphQL, como string JSON,
  sem espaços extras além dos que o json.dumps já gera.

Referência: painel "Open API" da Shopee > Guia de Usuário.
"""

import hashlib
import time
import json

from . import config


def _gerar_assinatura(payload_str: str, timestamp: int) -> str:
    base = f"{config.SHOPEE_APP_ID}{timestamp}{payload_str}{config.SHOPEE_APP_SECRET}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def montar_headers(payload_dict: dict):
    """
    Monta o payload (como string) e os headers de autenticação exigidos
    pela Shopee para uma requisição GraphQL.

    Returns:
        (payload_str, headers) — ambos prontos para passar no requests.post
    """
    payload_str = json.dumps(payload_dict, separators=(",", ":"))
    timestamp = int(time.time())
    signature = _gerar_assinatura(payload_str, timestamp)

    headers = {
        "Content-Type": "application/json",
        "Authorization": (
            f"SHA256 Credential={config.SHOPEE_APP_ID}, "
            f"Timestamp={timestamp}, Signature={signature}"
        ),
    }
    return payload_str, headers
