"""
Gera o painel visual de ROI (HTML autônomo): progresso da meta mensal,
investido x comissão recebida, e ROI por produto/campanha.
"""

import json
from datetime import date

from . import nav
from . import roi as roi_calc

# Paleta de status reservada (fixa, não temática) — usada só pra estado
# (bom/atenção/crítico), nunca para identidade de série.
STATUS = {
    "good": {"cor": "#0ca30c", "rotulo": "Dentro da meta (3x+)"},
    "warning": {"cor": "#fab219", "rotulo": "Abaixo da meta"},
    "critical": {"cor": "#d03b3b", "rotulo": "No prejuízo"},
}

STATUS_ICONE = {
    "good": '<path d="M4 10l4 4 8-8" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "warning": '<path d="M10 6v6M10 15h.01" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M10 2 1 17h18L10 2z" stroke="currentColor" stroke-width="1.6" fill="none" stroke-linejoin="round"/>',
    "critical": '<path d="M6 6l8 8M14 6l-8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
}


def _linha_produto(p):
    status = STATUS[p["status"]]
    roi_texto = f"{p['roi']:.1f}x" if p["roi"] is not None else "—"
    return f"""
        <tr>
          <td class="col-nome">{p['produto']}</td>
          <td class="col-num">R$&nbsp;{p['investido']:.2f}</td>
          <td class="col-num">R$&nbsp;{p['comissao']:.2f}</td>
          <td class="col-num destaque">{roi_texto}</td>
          <td class="col-status">
            <span class="status status-{p['status']}">
              <svg width="14" height="14" viewBox="0 0 20 20" fill="none">{STATUS_ICONE[p['status']]}</svg>
              {status['rotulo']}
            </span>
          </td>
        </tr>"""


def _grafico_svg(serie):
    if not serie:
        return '<div class="grafico-vazio">Ainda não há vendas registradas neste mês. Adicione entradas em <code>financeiro/vendas.csv</code> para ver a evolução aqui.</div>'

    largura, altura = 900, 240
    margem_esq, margem_baixo = 56, 32
    area_w = largura - margem_esq - 16
    area_h = altura - margem_baixo - 16

    valores = [p["acumulado"] for p in serie]
    y_max = max(valores) * 1.15 if max(valores) > 0 else 1

    n = len(serie)
    pontos = []
    for i, p in enumerate(serie):
        x = margem_esq + (area_w * (i / (n - 1)) if n > 1 else area_w / 2)
        y = 16 + area_h - (p["acumulado"] / y_max) * area_h
        pontos.append((round(x, 1), round(y, 1)))

    path_linha = "M " + " L ".join(f"{x},{y}" for x, y in pontos)
    path_area = path_linha + f" L {pontos[-1][0]},{16 + area_h} L {pontos[0][0]},{16 + area_h} Z"

    # Linhas de grade horizontais (recessivas) + rótulos do eixo Y
    grade_html = ""
    for fracao in (0, 0.25, 0.5, 0.75, 1.0):
        y = 16 + area_h - fracao * area_h
        valor = y_max * fracao
        grade_html += (
            f'<line x1="{margem_esq}" y1="{y}" x2="{largura - 16}" y2="{y}" '
            f'stroke="var(--grade)" stroke-width="1"/>'
            f'<text x="{margem_esq - 10}" y="{y + 4}" text-anchor="end" '
            f'class="rotulo-eixo">R${valor:.0f}</text>'
        )

    pontos_dados = [{"x": x, "y": y, "data": p["data"], "valor": p["acumulado"]} for (x, y), p in zip(pontos, serie)]

    return f"""
    <div class="grafico-wrap">
      <svg viewBox="0 0 {largura} {altura}" class="grafico-svg" id="grafico-roi">
        {grade_html}
        <path d="{path_area}" fill="var(--accent-soft)" stroke="none"/>
        <path d="{path_linha}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
        <circle cx="{pontos[-1][0]}" cy="{pontos[-1][1]}" r="4" fill="var(--accent)"/>
        <g id="crosshair" style="display:none;">
          <line x1="0" y1="16" x2="0" y2="{16 + area_h}" stroke="var(--muted)" stroke-width="1" stroke-dasharray="3 3"/>
          <circle r="5" fill="var(--accent)" stroke="var(--card)" stroke-width="2"/>
        </g>
      </svg>
      <div id="tooltip-roi" class="tooltip-roi" style="display:none;"></div>
    </div>
    <script>
      (function() {{
        var dados = {json.dumps(pontos_dados)};
        var svg = document.getElementById('grafico-roi');
        var crosshair = document.getElementById('crosshair');
        var tooltip = document.getElementById('tooltip-roi');
        var linhaV = crosshair.querySelector('line');
        var ponto = crosshair.querySelector('circle');

        function maisProximo(mouseX) {{
          var melhor = dados[0];
          dados.forEach(function (d) {{
            if (Math.abs(d.x - mouseX) < Math.abs(melhor.x - mouseX)) melhor = d;
          }});
          return melhor;
        }}

        svg.addEventListener('mousemove', function (ev) {{
          var rect = svg.getBoundingClientRect();
          var escala = {largura} / rect.width;
          var mouseX = (ev.clientX - rect.left) * escala;
          var d = maisProximo(mouseX);
          crosshair.style.display = '';
          linhaV.setAttribute('x1', d.x); linhaV.setAttribute('x2', d.x);
          ponto.setAttribute('cx', d.x); ponto.setAttribute('cy', d.y);
          tooltip.style.display = '';
          tooltip.style.left = (d.x / {largura} * 100) + '%';
          var dataFmt = d.data.split('-').reverse().slice(0,2).join('/');
          tooltip.innerHTML = '<b>' + dataFmt + '</b><br>R$ ' + d.valor.toFixed(2) + ' acumulado';
        }});
        svg.addEventListener('mouseleave', function () {{
          crosshair.style.display = 'none';
          tooltip.style.display = 'none';
        }});
      }})();
    </script>"""


def gerar_html(investimentos, vendas, titulo="Painel de ROI — Papai Resolve"):
    resumo = roi_calc.calcular_resumo(investimentos, vendas)
    por_produto = roi_calc.calcular_roi_por_produto(investimentos, vendas)
    serie = roi_calc.calcular_serie_acumulada(vendas)

    linhas_produtos = "".join(_linha_produto(p) for p in por_produto) or (
        '<tr><td colspan="5" class="vazio">Nenhum investimento ou venda registrado ainda. '
        'Preencha financeiro/investimentos.csv e financeiro/vendas.csv.</td></tr>'
    )

    grafico_html = _grafico_svg(serie)

    roi_medio_texto = f"{resumo['roi_medio']:.1f}x" if resumo["roi_medio"] is not None else "—"
    progresso_pct = resumo["progresso_meta"] * 100

    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #eef1f0; --grid-line: rgba(20, 60, 90, 0.07); --card: #ffffff;
    --text: #14202b; --muted: #5b6b74; --border: #d7dfe0;
    --accent: #d9670c; --accent-ink: #a84e08; --accent-soft: #fbe7d422;
    --grade: rgba(20, 60, 90, 0.1); --focus: #1d64b0;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #0f1417; --grid-line: rgba(255,255,255,0.05); --card: #171e22;
      --text: #e7edf0; --muted: #93a2a9; --border: #2a3338;
      --accent: #ff9439; --accent-ink: #ffb066; --accent-soft: #ff943922;
      --grade: rgba(255,255,255,0.08); --focus: #6badf0;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #0f1417; --grid-line: rgba(255,255,255,0.05); --card: #171e22;
    --text: #e7edf0; --muted: #93a2a9; --border: #2a3338;
    --accent: #ff9439; --accent-ink: #ffb066; --accent-soft: #ff943922;
    --grade: rgba(255,255,255,0.08); --focus: #6badf0;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 40px 24px 64px;
    background: repeating-linear-gradient(0deg, var(--grid-line) 0 1px, transparent 1px 32px),
      repeating-linear-gradient(90deg, var(--grid-line) 0 1px, transparent 1px 32px), var(--bg);
    color: var(--text); font-family: "IBM Plex Sans", system-ui, sans-serif;
  }}
  .wrap {{ max-width: 1000px; margin: 0 auto; }}
  .cabecalho {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px;
    flex-wrap: wrap; margin-bottom: 28px; border-bottom: 2px solid var(--border); padding-bottom: 20px; }}
  .eyebrow {{ font-family: "IBM Plex Mono", monospace; font-size: 0.72rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--accent-ink); margin: 0 0 8px; font-weight: 600; }}
  h1 {{ font-family: "Archivo", sans-serif; font-weight: 800; font-size: clamp(1.4rem, 2.2vw, 1.9rem); margin: 0; }}
  .atualizado {{ font-family: "IBM Plex Mono", monospace; font-size: 0.8rem; color: var(--muted); }}

  .resumo {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }}
  .stat {{ background: var(--card); border: 1px solid var(--border); border-radius: 6px; padding: 16px 18px; }}
  .stat .n {{ font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums;
    font-size: 1.5rem; font-weight: 600; }}
  .stat .l {{ font-size: 0.75rem; color: var(--muted); margin-top: 4px; }}

  .meta-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 20px 24px; margin-bottom: 24px; }}
  .meta-topo {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }}
  .meta-titulo {{ font-family: "IBM Plex Mono", monospace; font-size: 0.75rem; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }}
  .meta-valor {{ font-family: "IBM Plex Mono", monospace; font-size: 1rem; font-weight: 600; }}
  .barra-bg {{ background: var(--border); border-radius: 999px; height: 12px; overflow: hidden; }}
  .barra-fill {{ background: var(--accent); height: 100%; border-radius: 999px; }}

  .secao-titulo {{ font-family: "Archivo", sans-serif; font-weight: 700; font-size: 1.05rem; margin: 32px 0 12px; }}

  .grafico-wrap {{ position: relative; background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px; }}
  .grafico-svg {{ width: 100%; height: auto; display: block; }}
  .rotulo-eixo {{ font-family: "IBM Plex Mono", monospace; font-size: 10px; fill: var(--muted); }}
  .grafico-vazio {{ background: var(--card); border: 1px dashed var(--border); border-radius: 10px;
    padding: 32px; text-align: center; color: var(--muted); font-size: 0.9rem; }}
  .grafico-vazio code {{ font-family: "IBM Plex Mono", monospace; background: var(--accent-soft);
    padding: 1px 5px; border-radius: 3px; }}
  .tooltip-roi {{ position: absolute; top: 12px; transform: translateX(-50%); background: var(--text);
    color: var(--bg); font-family: "IBM Plex Mono", monospace; font-size: 0.78rem; padding: 6px 10px;
    border-radius: 6px; pointer-events: none; white-space: nowrap; }}

  .tabela-scroll {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; background: var(--card); }}
  table {{ width: 100%; border-collapse: collapse; min-width: 640px; }}
  th, td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 0.88rem; }}
  th {{ text-align: left; color: var(--muted); font-weight: 600; font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 0.06em; font-family: "IBM Plex Mono", monospace; }}
  tbody tr:last-child td {{ border-bottom: none; }}
  .col-num {{ text-align: right; font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; }}
  .destaque {{ font-weight: 600; }}
  .vazio {{ text-align: center; color: var(--muted); padding: 24px; }}

  .status {{ display: inline-flex; align-items: center; gap: 6px; font-size: 0.82rem;
    font-weight: 600; color: var(--text); }}
  .status svg {{ flex-shrink: 0; }}
  .status-good svg {{ color: #0ca30c; }}
  .status-warning svg {{ color: #a5730a; }}
  .status-critical svg {{ color: #d03b3b; }}

  .rodape {{ margin-top: 24px; font-size: 0.78rem; color: var(--muted); font-family: "IBM Plex Mono", monospace; }}

  @media (max-width: 640px) {{ .resumo {{ grid-template-columns: repeat(2, 1fr); }} }}
{nav.MENU_CSS}
</style>
</head>
<body>
  <div class="wrap">
    {nav.gerar_menu_html("painel_roi.html")}
    <header class="cabecalho">
      <div>
        <p class="eyebrow">Cockpit de Afiliação &middot; @papairesolve_br</p>
        <h1>Painel de ROI</h1>
      </div>
      <p class="atualizado">Atualizado {date.today().strftime('%d/%m/%Y')}</p>
    </header>

    <div class="meta-card">
      <div class="meta-topo">
        <span class="meta-titulo">Meta mensal &middot; R$ {resumo['meta_mensal']:.0f}</span>
        <span class="meta-valor">R$ {resumo['comissao_mes_atual']:.2f} ({progresso_pct:.0f}%)</span>
      </div>
      <div class="barra-bg"><div class="barra-fill" style="width:{progresso_pct:.1f}%"></div></div>
    </div>

    <section class="resumo">
      <div class="stat"><div class="n">R$ {resumo['total_investido']:.2f}</div><div class="l">Total investido</div></div>
      <div class="stat"><div class="n">R$ {resumo['total_comissao']:.2f}</div><div class="l">Total em comissão</div></div>
      <div class="stat"><div class="n">{roi_medio_texto}</div><div class="l">ROI médio (meta: 3x)</div></div>
      <div class="stat"><div class="n">{len(por_produto)}</div><div class="l">Produtos/campanhas com dado</div></div>
    </section>

    <div class="secao-titulo">Comissão acumulada no mês</div>
    {grafico_html}

    <div class="secao-titulo">ROI por produto/campanha</div>
    <div class="tabela-scroll">
      <table>
        <thead><tr><th>Produto</th><th>Investido</th><th>Comissão</th><th>ROI</th><th>Status</th></tr></thead>
        <tbody>{linhas_produtos}</tbody>
      </table>
    </div>

    <p class="rodape">Dados de financeiro/investimentos.csv e financeiro/vendas.csv, preenchidos manualmente.</p>
  </div>
</body>
</html>
"""


def salvar_painel(investimentos, vendas, caminho, titulo="Painel de ROI — Papai Resolve"):
    html = gerar_html(investimentos, vendas, titulo=titulo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    return caminho
