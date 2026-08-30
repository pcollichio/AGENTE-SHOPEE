"""
Gera o index.html — o cockpit central, com as recomendações do dia (o
"agente coach") calculadas a partir do financeiro e do ROI.

Rode com: python gerar_index.py
"""

from shopee_integration import chat_page, painel_index


def main():
    caminho = painel_index.salvar_painel("index.html")
    print(f"Cockpit central salvo em: {caminho}")

    caminho_chat = chat_page.salvar_painel("chat.html")
    print(f"Página de chat salva em: {caminho_chat}")


if __name__ == "__main__":
    main()
