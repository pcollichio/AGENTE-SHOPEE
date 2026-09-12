"""
Puxa as vendas/comissões reais direto da Shopee (via a query
conversionReport) e ACRESCENTA em financeiro/vendas_shopee.csv
(confirmada) e financeiro/vendas_pendentes.csv (pendente) — os MESMOS
arquivos e a MESMA regra de dedupe por `conversion_id` que
`importar_extratos.py` usa pro import manual do relatório exportado,
então os dois convivem sem duplicar nada (pedido do usuário em 12/09:
"Liga [a sincronização automática] mas mantenha a opção de import").

Roda sozinho todo dia às 9h, dentro de `leva-diaria.yml` (antes de
`gerar_roi.py`, pra já entrar no cálculo do dia) — mas também pode ser
rodado à mão: python sincronizar_vendas.py

IMPORTANTE: precisa de acesso real à internet e das credenciais reais
(USE_MOCK_DATA=false) — não roda na sessão do Claude (rede bloqueada).

NOTA: validado contra resposta real da Shopee em 11/09 — ver a NOTA em
`client.buscar_conversoes()` sobre o bug do argumento `scrollId` (só
pode ir na query quando há um cursor de verdade) que travava toda
busca antes disso. Testado de ponta a ponta: a mesma venda já
confirmada manualmente (R$1,80, "Escova Elétrica de Limpeza...") veio
certinha pela API.
"""

import sys
import time
from datetime import datetime, timedelta, timezone

from shopee_integration import client, config
from importar_extratos import (
    CAMINHO_VENDAS_SHOPEE,
    CAMINHO_VENDAS_PENDENTES,
    _acrescentar_csv,
    _ids_ja_importados,
)

# Quantos dias pra trás buscar a cada rodada — a Shopee mantém o
# histórico de conversionReport por mais tempo, mas rodando todo dia
# não precisa de uma janela grande; 30 dias dá folga confortável mesmo
# se a sincronização ficar parada por um tempo.
DIAS_PARA_TRAS = 30

# conversionStatus observados contra a API real em 11/09: "COMPLETED"
# (confirmada) e "PENDING" (ainda pode cancelar). Qualquer outro status
# (ex: cancelada/rejeitada) é ignorado — nem confirmada nem pendente.
STATUS_CONFIRMADOS = ["complet"]
STATUS_PENDENTES = ["pending"]


def _status_bate(status, termos):
    status = (status or "").lower()
    return any(termo in status for termo in termos)


def buscar_todas_conversoes(inicio_ts, fim_ts):
    conversoes = []
    scroll_id = None
    while True:
        pagina = client.buscar_conversoes(inicio_ts, fim_ts, limit=100, scroll_id=scroll_id)
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


def _montar_linhas(conversoes):
    """Devolve (linhas_confirmadas, linhas_pendentes), já no formato de
    linha de vendas_shopee.csv / vendas_pendentes.csv — mesmas colunas
    que importar_extratos.py escreve, pra dar pra acrescentar direto."""
    confirmadas = []
    pendentes = []

    for conv in conversoes:
        status = conv.get("conversionStatus")
        conversion_id = str(conv.get("conversionId") or "")
        if not conversion_id:
            continue

        purchase_time = conv.get("purchaseTime")
        try:
            data_iso = datetime.fromtimestamp(int(purchase_time), tz=timezone.utc).strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            data_iso = ""

        pedidos = conv.get("orders") or []
        itens = [item for pedido in pedidos for item in (pedido.get("items") or [])]
        if not itens:
            # Sem detalhamento por item — registra a conversão inteira.
            itens = [{"itemName": None, "itemTotalCommission": None}]

        for item in itens:
            produto = item.get("itemName") or f"Conversão {conversion_id}"
            comissao = item.get("itemTotalCommission")
            if comissao in (None, ""):
                comissao = conv.get("totalCommission") or 0
            linha = [data_iso, produto, comissao, conversion_id, "Sincronizado via API"]

            if _status_bate(status, STATUS_CONFIRMADOS):
                confirmadas.append(linha)
            elif _status_bate(status, STATUS_PENDENTES):
                pendentes.append(linha)
            # outros status (cancelada, rejeitada etc.) ficam de fora dos dois

    return confirmadas, pendentes


def main():
    if config.USE_MOCK_DATA:
        print(
            "USE_MOCK_DATA está true — configure USE_MOCK_DATA=false pra "
            "sincronizar vendas de verdade."
        )
        return

    fim = datetime.now(timezone.utc)
    inicio = fim - timedelta(days=DIAS_PARA_TRAS)

    try:
        conversoes = buscar_todas_conversoes(int(inicio.timestamp()), int(fim.timestamp()))
    except Exception as e:
        # Não derruba o workflow diário por uma falha pontual da API — só
        # avisa. O import manual (importar_extratos.py) continua
        # disponível como alternativa se a sincronização automática
        # ficar fora do ar por um tempo.
        print(f"Aviso: não consegui sincronizar vendas via API agora: {e}", file=sys.stderr)
        return

    confirmadas, pendentes = _montar_linhas(conversoes)

    ja_confirmadas = _ids_ja_importados(CAMINHO_VENDAS_SHOPEE, "conversion_id")
    ja_pendentes = _ids_ja_importados(CAMINHO_VENDAS_PENDENTES, "conversion_id")

    novas_confirmadas = [l for l in confirmadas if l[3] not in ja_confirmadas]
    novas_pendentes = [l for l in pendentes if l[3] not in ja_pendentes]

    if novas_confirmadas:
        _acrescentar_csv(
            CAMINHO_VENDAS_SHOPEE,
            ["data", "produto", "comissao_recebida", "conversion_id", "observacao"],
            novas_confirmadas,
        )
    if novas_pendentes:
        _acrescentar_csv(
            CAMINHO_VENDAS_PENDENTES,
            ["data", "produto", "comissao_prevista", "conversion_id", "observacao"],
            novas_pendentes,
        )

    print(
        f"{len(conversoes)} conversão(ões) via API nos últimos {DIAS_PARA_TRAS} dias — "
        f"{len(novas_confirmadas)} confirmada(s) nova(s), {len(novas_pendentes)} pendente(s) "
        f"nova(s) (o que já estava importado, manual ou automático, não duplica)."
    )


if __name__ == "__main__":
    main()
