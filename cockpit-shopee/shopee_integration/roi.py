"""
Lógica de cálculo do ROI: lê os arquivos financeiro/investimentos.csv e
financeiro/vendas.csv (preenchidos manualmente) e calcula os indicadores
usados pelo painel de ROI.
"""

import csv
import json
from collections import defaultdict
from datetime import date, datetime

META_MENSAL = 10000.0
ROI_META = 3.0

CAMINHO_INVESTIMENTOS = "financeiro/investimentos.csv"
CAMINHO_VENDAS = "financeiro/vendas.csv"
CAMINHO_VENDAS_SHOPEE = "financeiro/vendas_shopee.csv"
CAMINHO_VENDAS_PENDENTES = "financeiro/vendas_pendentes.csv"
CAMINHO_RESUMO_JSON = "financeiro/resumo.json"


def _ler_csv(caminho):
    try:
        with open(caminho, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def _float_seguro(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def carregar_investimentos(caminho=CAMINHO_INVESTIMENTOS):
    linhas = _ler_csv(caminho)
    return [
        {
            "data": l.get("data", "").strip(),
            "produto": l.get("produto", "").strip(),
            "valor": _float_seguro(l.get("valor_investido")),
            "observacao": l.get("observacao", "").strip(),
        }
        for l in linhas
        if l.get("data")
    ]


def carregar_vendas(caminho=CAMINHO_VENDAS, caminho_shopee=CAMINHO_VENDAS_SHOPEE):
    """Junta as vendas digitadas manualmente (vendas.csv) com as vindas da
    Shopee (vendas_shopee.csv — só linhas confirmadas, escritas tanto
    por `importar_extratos.py` (import manual do relatório exportado)
    quanto por `sincronizar_vendas.py` (automático via API, desde
    12/09, rodando todo dia dentro de `leva-diaria.yml`) — os dois
    escrevem no mesmo arquivo, sem duplicar (dedupe por `conversion_id`
    nos dois lados) — são arquivos separados de `vendas.csv` de
    propósito, pra nunca sobrescrever o que você digitou à mão."""
    linhas_manuais = _ler_csv(caminho)
    linhas_shopee = _ler_csv(caminho_shopee)

    vendas = [
        {
            "data": l.get("data", "").strip(),
            "produto": l.get("produto", "").strip(),
            "valor": _float_seguro(l.get("comissao_recebida")),
            "observacao": l.get("observacao", "").strip(),
        }
        for l in linhas_manuais
        if l.get("data")
    ]
    vendas += [
        {
            "data": l.get("data", "").strip(),
            "produto": l.get("produto", "").strip(),
            "valor": _float_seguro(l.get("comissao_recebida")),
            "observacao": f"Shopee, pedido {l.get('conversion_id', '')}",
        }
        for l in linhas_shopee
        if l.get("data")
    ]
    return vendas


def carregar_vendas_pendentes(caminho=CAMINHO_VENDAS_PENDENTES, caminho_shopee=CAMINHO_VENDAS_SHOPEE):
    """Vendas com status "Pendente" no relatório de comissões da Shopee —
    ainda podem ser canceladas, então NÃO contam no ROI nem na meta
    mensal (`calcular_resumo`/`calcular_roi_por_produto` não leem este
    arquivo). Servem só pra mostrar no Dashboard quanto tem "em
    trânsito", separado do que já é garantido. Um pedido "graduado" de
    pendente pra confirmado (a sincronização via API roda todo dia,
    então isso acontece o tempo todo) é excluído daqui.

    NOTA (12/09): a exclusão casa por (`conversion_id`, `produto`), não
    só `conversion_id` — validado contra a API real que um mesmo
    `conversion_id` pode agrupar mais de um produto/pedido com status
    diferentes entre si (um confirmado, outro ainda pendente). Casando
    só por `conversion_id` faria o produto ainda pendente sumir do
    Dashboard assim que QUALQUER produto daquele mesmo conversion_id
    confirmasse — contando a menos o que ainda está em trânsito."""
    linhas = _ler_csv(caminho)
    ja_confirmados = {
        (l.get("conversion_id"), l.get("produto", "").strip())
        for l in _ler_csv(caminho_shopee)
        if l.get("conversion_id")
    }
    return [
        {
            "data": l.get("data", "").strip(),
            "produto": l.get("produto", "").strip(),
            "valor": _float_seguro(l.get("comissao_prevista")),
            "observacao": f"Shopee, pedido {l.get('conversion_id', '')} (pendente)",
        }
        for l in linhas
        if l.get("data")
        and (l.get("conversion_id"), l.get("produto", "").strip()) not in ja_confirmados
    ]


def status_roi(roi):
    """Classifica o ROI de um produto/campanha em good/warning/critical,
    seguindo a meta do blueprint (3x)."""
    if roi is None:
        return "warning"  # investiu mas ainda não vendeu nada
    if roi >= ROI_META:
        return "good"
    if roi >= 1.0:
        return "warning"
    return "critical"


def calcular_roi_por_produto(investimentos, vendas):
    """Agrupa investimento e comissão por produto/campanha e calcula o ROI
    de cada um."""
    investido_por_produto = defaultdict(float)
    comissao_por_produto = defaultdict(float)

    for i in investimentos:
        investido_por_produto[i["produto"]] += i["valor"]
    for v in vendas:
        comissao_por_produto[v["produto"]] += v["valor"]

    produtos = set(investido_por_produto) | set(comissao_por_produto)

    resultado = []
    for produto in produtos:
        investido = investido_por_produto.get(produto, 0.0)
        comissao = comissao_por_produto.get(produto, 0.0)
        roi = (comissao / investido) if investido > 0 else None
        resultado.append(
            {
                "produto": produto,
                "investido": investido,
                "comissao": comissao,
                "roi": roi,
                "status": status_roi(roi),
            }
        )

    resultado.sort(key=lambda p: (p["roi"] is None, -(p["roi"] or 0)))
    return resultado


def calcular_serie_acumulada(vendas, ano=None, mes=None):
    """Comissão acumulada dia a dia dentro do mês informado (padrão: mês
    atual). Retorna uma lista de {data, acumulado}."""
    hoje = date.today()
    ano = ano or hoje.year
    mes = mes or hoje.month

    por_dia = defaultdict(float)
    for v in vendas:
        try:
            d = datetime.strptime(v["data"], "%Y-%m-%d").date()
        except ValueError:
            continue
        if d.year == ano and d.month == mes:
            por_dia[d.isoformat()] += v["valor"]

    dias_ordenados = sorted(por_dia.keys())
    acumulado = 0.0
    serie = []
    for dia in dias_ordenados:
        acumulado += por_dia[dia]
        serie.append({"data": dia, "acumulado": round(acumulado, 2)})
    return serie


def calcular_resumo(investimentos, vendas, vendas_pendentes=None):
    hoje = date.today()
    vendas_pendentes = vendas_pendentes or []

    total_investido = sum(i["valor"] for i in investimentos)
    total_comissao = sum(v["valor"] for v in vendas)
    roi_medio = (total_comissao / total_investido) if total_investido > 0 else None

    comissao_mes_atual = sum(
        v["valor"]
        for v in vendas
        if v["data"][:7] == hoje.strftime("%Y-%m")
    )
    progresso_meta = min(comissao_mes_atual / META_MENSAL, 1.0) if META_MENSAL else 0

    # Comissão "Pendente" no relatório da Shopee — não é garantida (pode
    # cancelar), então fica só informativa, fora do ROI e da meta mensal.
    comissao_pendente = sum(v["valor"] for v in vendas_pendentes)

    return {
        "total_investido": total_investido,
        "total_comissao": total_comissao,
        "roi_medio": roi_medio,
        "comissao_mes_atual": comissao_mes_atual,
        "progresso_meta": progresso_meta,
        "meta_mensal": META_MENSAL,
        "comissao_pendente": comissao_pendente,
    }


def exportar_resumo_json(caminho=CAMINHO_RESUMO_JSON):
    """Escreve um retrato do estado financeiro em JSON — é o que o chat do
    coach (api/chat.js) lê pra responder com dados reais, sem precisar
    entender o HTML dos painéis."""
    investimentos = carregar_investimentos()
    vendas = carregar_vendas()
    vendas_pendentes = carregar_vendas_pendentes()
    resumo = calcular_resumo(investimentos, vendas, vendas_pendentes)
    por_produto = calcular_roi_por_produto(investimentos, vendas)
    serie = calcular_serie_acumulada(vendas)

    dados = {
        "atualizado_em": datetime.now().isoformat(timespec="seconds"),
        "resumo": resumo,
        "roi_por_produto": por_produto,
        "serie_acumulada_mes": serie,
    }

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return caminho
