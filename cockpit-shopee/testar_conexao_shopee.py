"""
Script para testar se as credenciais reais da Shopee estão funcionando.

Rode com: python testar_conexao_shopee.py

IMPORTANTE: este teste faz uma chamada de rede real para a API da Shopee.
Se você estiver rodando isso num ambiente sem acesso à internet externa
(como alguns sandboxes de execução de código), ele vai falhar por conexão,
não por credencial errada. Rode localmente no seu computador para um teste
confiável.
"""

import requests
from shopee_integration import config, auth


def testar_conexao():
    if config.USE_MOCK_DATA:
        print("USE_MOCK_DATA está true — configure USE_MOCK_DATA=false no "
              ".env para testar a API real.")
        return

    # Query simples só para validar autenticação (ajustar nome do campo
    # conforme o schema real, visível no Postman Collection da Shopee)
    query = """
    query {
      shopeeOfferV2 {
        nodes {
          offerName
        }
      }
    }
    """
    payload = {"query": query}
    payload_str, headers = auth.montar_headers(payload)

    print(f"Testando conexão em: {config.SHOPEE_API_ENDPOINT}")
    print(f"App ID usado: {config.SHOPEE_APP_ID}")

    try:
        response = requests.post(
            config.SHOPEE_API_ENDPOINT,
            data=payload_str,
            headers=headers,
            timeout=15,
        )
        print(f"\nStatus HTTP: {response.status_code}")
        print(f"Resposta:\n{response.text[:1000]}")

        if response.status_code == 200 and "errors" not in response.json():
            print("\n✅ Conexão e autenticação funcionando!")
        else:
            print("\n⚠️ A Shopee respondeu, mas com erro — veja a mensagem "
                  "acima. Pode ser nome de campo errado na query (isso é "
                  "normal, só ajustar) ou credencial/timestamp.")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("Se você estiver rodando isso num sandbox sem acesso à "
              "internet externa, rode este script no seu computador local "
              "em vez daqui.")


if __name__ == "__main__":
    testar_conexao()
