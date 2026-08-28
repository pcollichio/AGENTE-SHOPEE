"""
Lógica de cálculo do ROI: lê os arquivos financeiro/investimentos.csv e
financeiro/vendas.csv (preenchidos manualmente) e calcula os indicadores
usados pelo painel de ROI.
"""

import csv
from collections import defaultdict
from datetime import date, datetime

META_MENSAL = 10000.0
ROI_META = 3.0

CAMINHO_INVESTIMENTOS = "financeiro/investimentos.csv"
CAMINHO_VENDAS = "financeiro/vendas.csv"


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


def carregar_vendas(caminho=CAMINHO_VENDAS):
    linhas = _ler_csv(caminho)
    return [
        {
            "data": l.get("data", "").strip(),
            "produto": l.get("produto", "").strip(),
            "valor": _float_seguro(l.get("comissao_recebida")),
            "observacao": l.get("observacao", "").strip(),
        }
        for l in linhas
        if l.get("data")
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


def calcular_resumo(investimentos, vendas):
    hoje = date.today()

    total_investido = sum(i["valor"] for i in investimentos)
    total_comissao = sum(v["valor"] for v in vendas)
    roi_medio = (total_comissao / total_investido) if total_investido > 0 else None

    comissao_mes_atual = sum(
        v["valor"]
        for v in vendas
        if v["data"][:7] == hoje.strftime("%Y-%m")
    )
    progresso_meta = min(comissao_mes_atual / META_MENSAL, 1.0) if META_MENSAL else 0

    return {
        "total_investido": total_investido,
        "total_comissao": total_comissao,
        "roi_medio": roi_medio,
        "comissao_mes_atual": comissao_mes_atual,
        "progresso_meta": progresso_meta,
        "meta_mensal": META_MENSAL,
    }
