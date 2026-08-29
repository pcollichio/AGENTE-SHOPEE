"""
Lógica do "agente coach": olha o estado atual (financeiro, ROI, ritmo da
meta) e monta a lista de ações prioritárias do dia — o "o que fazer hoje"
que aparece no topo do index.html.
"""

import calendar
from datetime import date, datetime

from . import roi as roi_calc


def _ultima_data(linhas):
    datas = []
    for l in linhas:
        try:
            datas.append(datetime.strptime(l["data"], "%Y-%m-%d").date())
        except (KeyError, ValueError):
            continue
    return max(datas) if datas else None


def gerar_recomendacoes():
    hoje = date.today()
    investimentos = roi_calc.carregar_investimentos()
    vendas = roi_calc.carregar_vendas()
    resumo = roi_calc.calcular_resumo(investimentos, vendas)
    por_produto = roi_calc.calcular_roi_por_produto(investimentos, vendas)

    recomendacoes = []

    # 1. Sempre presente: revisar a leva do dia e montar a esteira
    recomendacoes.append({
        "titulo": "Revisar os produtos do dia e marcar a esteira",
        "descricao": "Confira a leva de hoje no painel e marque o que vai virar conteúdo — o roteiro já sai pronto.",
        "link": "painel.html",
        "rotulo_link": "Abrir painel de produtos",
        "prioridade": "normal",
    })

    # 2. Financeiro desatualizado
    ultima_venda = _ultima_data(vendas)
    ultimo_investimento = _ultima_data(investimentos)

    if ultima_venda is None and ultimo_investimento is None:
        recomendacoes.append({
            "titulo": "Registrar seu primeiro investimento e venda",
            "descricao": "Ainda não há nenhum dado financeiro registrado — sem isso o painel de ROI fica vazio.",
            "link": "importar.html",
            "rotulo_link": "Importar dados",
            "prioridade": "alta",
        })
    else:
        if ultimo_investimento is not None:
            dias = (hoje - ultimo_investimento).days
            if dias >= 3:
                recomendacoes.append({
                    "titulo": f"Atualizar investimento (última entrada há {dias} dias)",
                    "descricao": "Registre o que foi gasto impulsionando desde a última atualização.",
                    "link": "importar.html",
                    "rotulo_link": "Importar dados",
                    "prioridade": "alta",
                })
        if ultima_venda is not None:
            dias = (hoje - ultima_venda).days
            if dias >= 3:
                recomendacoes.append({
                    "titulo": f"Conferir vendas no painel da Shopee (última entrada há {dias} dias)",
                    "descricao": "Confirme comissões recebidas desde a última atualização.",
                    "link": "importar.html",
                    "rotulo_link": "Importar dados",
                    "prioridade": "alta",
                })

    # 3. Ritmo vs. meta mensal
    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    ritmo_esperado = hoje.day / dias_no_mes
    if ultima_venda is not None:
        progresso_real = resumo["progresso_meta"]
        if progresso_real + 0.05 < ritmo_esperado:
            recomendacoes.append({
                "titulo": "Ritmo abaixo do necessário pra bater a meta do mês",
                "descricao": (
                    f"Você está em {progresso_real*100:.0f}% da meta, mas já se passaram "
                    f"{ritmo_esperado*100:.0f}% do mês. Considere aumentar a frequência de "
                    "posts ou testar produtos de outra categoria."
                ),
                "link": "painel_roi.html",
                "rotulo_link": "Ver painel de ROI",
                "prioridade": "alta",
            })

    # 4. ROI crítico (produto/campanha no prejuízo)
    criticos = [p for p in por_produto if p["status"] == "critical"]
    if criticos:
        nomes = ", ".join(p["produto"] for p in criticos[:3])
        recomendacoes.append({
            "titulo": f"{len(criticos)} produto(s)/campanha(s) no prejuízo",
            "descricao": f"Revise ou pause: {nomes}.",
            "link": "painel_roi.html",
            "rotulo_link": "Ver painel de ROI",
            "prioridade": "alta",
        })

    recomendacoes.sort(key=lambda r: r["prioridade"] != "alta")
    return recomendacoes
