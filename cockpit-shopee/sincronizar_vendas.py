"""
Puxa as vendas/comissões reais dos últimos N dias direto da Shopee
(via a query conversionReport) e salva em financeiro/vendas_shopee.csv —
um arquivo SEPARADO do financeiro/vendas.csv que você preenche à mão, pra
nunca sobrescrever o que você digitou manualmente.

Rode com: python sincronizar_vendas.py

IMPORTANTE: precisa de acesso real à internet e das credenciais reais no
.env (USE_MOCK_DATA=false). Rode no seu computador ou no Google Colab.

NOTA: o schema desta busca ainda não foi validado contra uma resposta real
da Shopee (veja o comentário em shopee_integration/client.py). Se der
erro, me manda a mensagem de erro completa que eu ajusto o nome do campo.
"""

import csv
import sys
import time
from datetime import datetime, timedelta

from shopee_integration import client, config

DIAS_PARA_TRAS = 30
CAMINHO_SAIDA = "financeiro/vendas_shopee.csv"

# Considera "venda confirmada" qualquer status que contenha um destes
# termos (case-insensitive) — ajuste aqui se os valores reais da Shopee
# forem diferentes (ex: "COMPLETED", "PAID", "SETTLED").
STATUS_CONFIRMADOS = ["complet", "paid", "settle", "success"]


def _status_confirmado(status):
    status = (status or "").lower()
    return any(termo in status for termo in STATUS_CONFIRMADOS)


def buscar_todas_conversoes(inicio_ts, fim_ts):
    conversoes = []
    scroll_id = None
    while True:
        pagina = client.buscar_conversoes(
            inicio_ts, fim_ts, limit=100, scroll_id=scroll_id
        )
        nodes = pagina.get("nodes") or []
        conversoes.extend(nodes)

        page_info = pagina.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        scroll_id = page_info.get("scrollId")
        if not scroll_id:
            break
        time.sleep(0.3)  # dá folga pro scrollId (validade curta) não expirar
    return conversoes


def montar_linhas(conversoes):
    linhas = []
    for conv in conversoes:
        status = conv.get("orderStatus")
        if not _status_confirmado(status):
            continue

        purchase_time = conv.get("purchaseTime")
        try:
            data_iso = datetime.utcfromtimestamp(int(purchase_time)).strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            data_iso = ""

        pedidos = conv.get("orders") or []
        itens = [item for pedido in pedidos for item in (pedido.get("items") or [])]

        if itens:
            for item in itens:
                linhas.append({
                    "data": data_iso,
                    "produto": item.get("itemName") or f"Pedido {conv.get('conversionId')}",
                    "comissao_recebida": item.get("itemTotalCommission") or 0,
                    "conversion_id": conv.get("conversionId"),
                    "order_status": status,
                })
        else:
            # Sem detalhamento por item — registra a conversão inteira
            linhas.append({
                "data": data_iso,
                "produto": f"Conversão {conv.get('conversionId')}",
                "comissao_recebida": conv.get("totalCommission") or 0,
                "conversion_id": conv.get("conversionId"),
                "order_status": status,
            })
    return linhas


def salvar_csv(linhas, caminho=CAMINHO_SAIDA):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["data", "produto", "comissao_recebida", "conversion_id", "order_status"]
        )
        writer.writeheader()
        writer.writerows(linhas)


def main():
    if config.USE_MOCK_DATA:
        print(
            "USE_MOCK_DATA está true — configure USE_MOCK_DATA=false no .env "
            "para buscar vendas reais."
        )
        return

    fim = datetime.utcnow()
    inicio = fim - timedelta(days=DIAS_PARA_TRAS)
    inicio_ts, fim_ts = int(inicio.timestamp()), int(fim.timestamp())

    try:
        conversoes = buscar_todas_conversoes(inicio_ts, fim_ts)
    except Exception as e:
        print(f"Erro ao buscar conversões: {e}", file=sys.stderr)
        print(
            "Isso é esperado na primeira tentativa se algum nome de campo "
            "estiver diferente do que a Shopee espera — copia essa "
            "mensagem de erro e me manda que eu ajusto.",
            file=sys.stderr,
        )
        sys.exit(1)

    linhas = montar_linhas(conversoes)
    salvar_csv(linhas)

    print(f"{len(conversoes)} conversões encontradas nos últimos {DIAS_PARA_TRAS} dias.")
    print(f"{len(linhas)} linhas de venda confirmada salvas em {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
