"""
Gera o esteira.html — a lista viva dos produtos selecionados, com status
calculado cruzando com o financeiro (investido/vendido).

Rode com: python gerar_esteira.py
"""

from shopee_integration import esteira


def main():
    caminho = esteira.salvar_painel()
    print(f"Esteira salva em: {caminho}")


if __name__ == "__main__":
    main()
