"""
A esteira: a lista viva dos produtos que você já selecionou pra virar
conteúdo (salvos pelo botão "Salvar seleção agora" no painel), com um
status calculado automaticamente cruzando com o financeiro —
selecionado / impulsionado (tem investimento registrado) / vendido (tem
comissão registrada) — pra você (e o Claude) acompanhar cada produto do
início ao fim, sem perder o rastro.
"""

import json
import unicodedata
from datetime import date

from . import nav
from . import roi as roi_calc

CAMINHO_ESTEIRA = "esteira.json"

STATUS_ESTEIRA = {
    "selecionado": {"rotulo": "Selecionado", "classe": "neutro"},
    "impulsionado": {"rotulo": "Impulsionado", "classe": "warning"},
    "vendido": {"rotulo": "Vendido", "classe": "good"},
}

STATUS_ICONE = {
    "neutro": '<circle cx="10" cy="10" r="4" fill="currentColor"/>',
    "warning": '<path d="M10 6v6M10 15h.01" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M10 2 1 17h18L10 2z" stroke="currentColor" stroke-width="1.6" fill="none" stroke-linejoin="round"/>',
    "good": '<path d="M4 10l4 4 8-8" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
}


def carregar_esteira(caminho=CAMINHO_ESTEIRA):
    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
        return dados if isinstance(dados, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).lower().strip()


def _bate(nome_produto, nome_financeiro):
    """Compara de forma tolerante: o campo do financeiro costuma ser
    digitado à mão (mais curto que o nome real do produto na Shopee), então
    basta um "conter" o outro."""
    a = _normalizar(nome_produto)
    b = _normalizar(nome_financeiro)
    if not a or not b:
        return False
    return b in a or a in b


def calcular_status(esteira, investimentos, vendas):
    """Deduplica por produto_id (mantém a seleção mais recente) e calcula
    o status de cada item cruzando com o financeiro pelo nome."""
    vistos = {}
    for item in esteira:
        chave = item.get("produto_id") or item.get("nome")
        if not chave:
            continue
        atual = vistos.get(chave)
        if not atual or item.get("selecionado_em", "") > atual.get("selecionado_em", ""):
            vistos[chave] = item

    resultado = []
    for item in vistos.values():
        nome = item.get("nome", "")
        investido = sum(i["valor"] for i in investimentos if _bate(nome, i["produto"]))
        comissao = sum(v["valor"] for v in vendas if _bate(nome, v["produto"]))

        if comissao > 0:
            status = "vendido"
        elif investido > 0:
            status = "impulsionado"
        else:
            status = "selecionado"

        roi_valor = (comissao / investido) if investido > 0 and comissao > 0 else None

        resultado.append({
            **item,
            "status": status,
            "investido": investido,
            "comissao_recebida": comissao,
            "roi": roi_valor,
        })

    resultado.sort(key=lambda p: p.get("selecionado_em", ""), reverse=True)
    return resultado


def _linha(p):
    status = STATUS_ESTEIRA[p["status"]]
    icone = STATUS_ICONE[status["classe"]]
    nome = (p.get("nome") or "(sem nome)").replace("<", "&lt;").replace(">", "&gt;")
    link = p.get("link") or "#"
    data_sel = (p.get("selecionado_em") or "")[:10]
    roi_texto = f"{p['roi']:.1f}x" if p["roi"] is not None else "—"
    return f"""
        <tr>
          <td class="col-status">
            <span class="status status-{status['classe']}">
              <svg width="14" height="14" viewBox="0 0 20 20" fill="none">{icone}</svg>
              {status['rotulo']}
            </span>
          </td>
          <td class="col-nome">
            <a href="{link}" target="_blank" rel="noopener">{nome}</a>
          </td>
          <td class="col-data">{data_sel}</td>
          <td class="col-num">R$&nbsp;{p.get('preco', 0):.2f}</td>
          <td class="col-num">{p.get('comissao', 0):.0f}%</td>
          <td class="col-num">{"R$ " + format(p['investido'], ".2f") if p['investido'] else "—"}</td>
          <td class="col-num">{"R$ " + format(p['comissao_recebida'], ".2f") if p['comissao_recebida'] else "—"}</td>
          <td class="col-num destaque">{roi_texto}</td>
        </tr>"""


def gerar_html(esteira_calculada, titulo="Esteira — Papai Resolve"):
    contagem = {"selecionado": 0, "impulsionado": 0, "vendido": 0}
    for p in esteira_calculada:
        contagem[p["status"]] = contagem.get(p["status"], 0) + 1

    linhas = "".join(_linha(p) for p in esteira_calculada) or (
        '<tr><td colspan="8" class="vazio">Nenhum produto na esteira ainda. '
        'Marque produtos no painel e clique em "Salvar seleção agora".</td></tr>'
    )

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
    --accent: #d9670c; --accent-ink: #a84e08; --accent-soft: #fbe7d4;
    --focus: #1d64b0;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #0f1417; --grid-line: rgba(255,255,255,0.05); --card: #171e22;
      --text: #e7edf0; --muted: #93a2a9; --border: #2a3338;
      --accent: #ff9439; --accent-ink: #ffb066; --accent-soft: #3a2a17;
      --focus: #6badf0;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #0f1417; --grid-line: rgba(255,255,255,0.05); --card: #171e22;
    --text: #e7edf0; --muted: #93a2a9; --border: #2a3338;
    --accent: #ff9439; --accent-ink: #ffb066; --accent-soft: #3a2a17;
    --focus: #6badf0;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 40px 24px 64px;
    background: repeating-linear-gradient(0deg, var(--grid-line) 0 1px, transparent 1px 32px),
      repeating-linear-gradient(90deg, var(--grid-line) 0 1px, transparent 1px 32px), var(--bg);
    color: var(--text); font-family: "IBM Plex Sans", system-ui, sans-serif;
  }}
  .wrap {{ max-width: 1080px; margin: 0 auto; }}
  .cabecalho {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px;
    flex-wrap: wrap; margin-bottom: 28px; border-bottom: 2px solid var(--border); padding-bottom: 20px; }}
  .eyebrow {{ font-family: "IBM Plex Mono", monospace; font-size: 0.72rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--accent-ink); margin: 0 0 8px; font-weight: 600; }}
  h1 {{ font-family: "Archivo", sans-serif; font-weight: 800; font-size: clamp(1.4rem, 2.2vw, 1.9rem); margin: 0; }}
  .atualizado {{ font-family: "IBM Plex Mono", monospace; font-size: 0.8rem; color: var(--muted); }}

  .resumo {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 28px; }}
  .stat {{ background: var(--card); border: 1px solid var(--border); border-radius: 6px; padding: 16px 18px; }}
  .stat .n {{ font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums;
    font-size: 1.5rem; font-weight: 600; }}
  .stat .l {{ font-size: 0.75rem; color: var(--muted); margin-top: 4px; }}
  .stat-selecionado .n {{ color: var(--muted); }}
  .stat-impulsionado .n {{ color: #a5730a; }}
  .stat-vendido .n {{ color: #0ca30c; }}

  .descricao-secao {{ font-size: 0.85rem; color: var(--muted); margin: 0 0 18px; max-width: 68ch; }}

  .tabela-scroll {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; background: var(--card); }}
  table {{ width: 100%; border-collapse: collapse; min-width: 820px; }}
  th, td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 0.88rem; }}
  th {{ text-align: left; color: var(--muted); font-weight: 600; font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 0.06em; font-family: "IBM Plex Mono", monospace; }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover {{ background: var(--accent-soft); }}
  .col-nome a {{ color: var(--text); text-decoration: none; font-weight: 600; }}
  .col-nome a:hover {{ text-decoration: underline; }}
  .col-data {{ font-family: "IBM Plex Mono", monospace; color: var(--muted); white-space: nowrap; }}
  .col-num {{ text-align: right; white-space: nowrap; font-family: "IBM Plex Mono", monospace;
    font-variant-numeric: tabular-nums; }}
  .destaque {{ font-weight: 600; color: var(--accent-ink); }}
  .vazio {{ text-align: center; color: var(--muted); padding: 32px; }}

  .status {{ display: inline-flex; align-items: center; gap: 6px; font-size: 0.82rem;
    font-weight: 600; color: var(--text); white-space: nowrap; }}
  .status svg {{ flex-shrink: 0; }}
  .status-neutro svg {{ color: var(--muted); }}
  .status-warning svg {{ color: #a5730a; }}
  .status-good svg {{ color: #0ca30c; }}

  .rodape {{ margin-top: 24px; font-size: 0.78rem; color: var(--muted); font-family: "IBM Plex Mono", monospace; }}

  @media (max-width: 640px) {{ .resumo {{ grid-template-columns: 1fr; }} }}
{nav.MENU_CSS}
</style>
</head>
<body>
  <div class="wrap">
    {nav.gerar_menu_html("esteira.html")}
    <header class="cabecalho">
      <div>
        <p class="eyebrow">Cockpit de Afiliação &middot; @papairesolve_br</p>
        <h1>Esteira</h1>
      </div>
      <p class="atualizado">Atualizado {date.today().strftime('%d/%m/%Y')}</p>
    </header>

    <p class="descricao-secao">Todo produto que você marca no painel e salva entra aqui. O status é calculado sozinho: vira <b>Impulsionado</b> quando você registra investimento nele em <code>importar.html</code>, e <b>Vendido</b> quando registra a comissão recebida.</p>

    <section class="resumo" aria-label="Resumo da esteira">
      <div class="stat stat-selecionado"><div class="n">{contagem.get('selecionado', 0):02d}</div><div class="l">Selecionado, aguardando</div></div>
      <div class="stat stat-impulsionado"><div class="n">{contagem.get('impulsionado', 0):02d}</div><div class="l">Impulsionado, aguardando venda</div></div>
      <div class="stat stat-vendido"><div class="n">{contagem.get('vendido', 0):02d}</div><div class="l">Já vendeu</div></div>
    </section>

    <div class="tabela-scroll">
      <table>
        <thead>
          <tr>
            <th>Status</th><th>Produto</th><th>Selecionado em</th><th>Preço</th><th>Comissão</th>
            <th>Investido</th><th>Recebido</th><th>ROI</th>
          </tr>
        </thead>
        <tbody>{linhas}
        </tbody>
      </table>
    </div>

    <p class="rodape">Cockpit de Afiliação IA-First &middot; @papairesolve_br</p>
  </div>
</body>
</html>
"""


def salvar_painel(caminho_esteira=CAMINHO_ESTEIRA, caminho_saida="esteira.html"):
    esteira = carregar_esteira(caminho_esteira)
    investimentos = roi_calc.carregar_investimentos()
    vendas = roi_calc.carregar_vendas()
    calculada = calcular_status(esteira, investimentos, vendas)

    html = gerar_html(calculada)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(html)
    return caminho_saida
