"""
Configuração de credenciais da Shopee Affiliate API.

IMPORTANTE: nunca coloque suas credenciais reais direto no código.
Quando a Shopee aprovar seu acesso, crie um arquivo chamado `.env`
nesta mesma pasta (ele NÃO deve ser commitado no git) com o seguinte
conteúdo:

    SHOPEE_APP_ID=seu_app_id_aqui
    SHOPEE_APP_SECRET=seu_app_secret_aqui
    USE_MOCK_DATA=false

Enquanto a aprovação não chega, deixe USE_MOCK_DATA=true (ou simplesmente
não crie o .env ainda) e o sistema vai usar dados simulados automaticamente.
"""

import os

# Tenta carregar variáveis de um arquivo .env, se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv é opcional; sem ele, só lê variáveis de ambiente do sistema

SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID", "")
SHOPEE_APP_SECRET = os.getenv("SHOPEE_APP_SECRET", "")

# Endpoint oficial da Shopee Affiliate API (GraphQL) para o Brasil.
# Confirme esta URL no Postman Collection / documentação vinculada no seu
# painel "Open API" caso alguma chamada retorne erro de endpoint inválido.
SHOPEE_API_ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"

# Se não houver credenciais reais configuradas, o sistema usa dados mockados
# automaticamente — não precisa fazer nada manual para isso funcionar.
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true" or not (
    SHOPEE_APP_ID and SHOPEE_APP_SECRET
)
