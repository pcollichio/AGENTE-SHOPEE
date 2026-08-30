"""
Gera o index.html — o "cockpit central". Não é só um mapa estático: o
topo da página ("O que fazer hoje") é montado a partir dos dados reais
de financeiro/ROI, funcionando como o agente coach do blueprint.
"""

from datetime import date

from . import coach, nav

PRIORIDADE_LABEL = {"alta": "Prioridade", "normal": "Rotina"}


def _cartao_recomendacao(r, indice):
    destaque = "alta" if r["prioridade"] == "alta" else "normal"
    tarefa_id = f"tarefa-{indice}"
    return f"""
        <div class="recomendacao recomendacao-{destaque}" data-tarefa-id="{tarefa_id}">
          <label class="recomendacao-check">
            <input type="checkbox" class="chk-tarefa" data-tarefa-id="{tarefa_id}">
            <div class="recomendacao-corpo">
              <div class="recomendacao-topo">
                <span class="tag tag-{destaque}">{PRIORIDADE_LABEL[r['prioridade']]}</span>
                <span class="recomendacao-titulo">{r['titulo']}</span>
              </div>
              <p class="recomendacao-desc">{r['descricao']}</p>
            </div>
          </label>
          <a class="recomendacao-link" href="{r['link']}">{r['rotulo_link']} &rarr;</a>
        </div>"""


ETAPAS = [
    {
        "titulo": "Buscar produtos na Shopee", "status": "bom", "status_label": "Automático",
        "desc": "Todo dia às 9h, busca produtos reais do nicho, filtra fora do que não é casa &amp; construção, e monta a leva de 20 (baixo/médio/alto ticket).",
        "links": [("painel.html", "Ver painel de produtos", False), ("historico/", "Ver histórico", False)],
    },
    {
        "titulo": "Selecionar o que vai pra esteira", "status": "manual", "status_label": "Manual",
        "desc": "Você marca os produtos no painel (ou adiciona um específico via <code>produtos_manuais.txt</code>) e baixa a seleção.",
        "links": [("painel.html", "Marcar produtos", False)],
    },
    {
        "titulo": "Texto e roteiro", "status": "bom", "status_label": "Automático",
        "desc": "Ao baixar a seleção, cada produto já sai com o roteiro pronto (Problema &rarr; Agrava &rarr; Solução &rarr; Prova &rarr; Oferta), no modelo Papai Resolve.",
        "links": [("painel.html", "Fica dentro do painel de produtos", False)],
    },
    {
        "titulo": "Identidade visual", "status": "bom", "status_label": "Pronta",
        "desc": "Logo, paleta e uma capa de exemplo pra Reels — pra usar como marca d'água e referência visual dos vídeos.",
        "links": [(nav.IDENTIDADE_URL, "Ver identidade visual", True)],
    },
    {
        "titulo": "Gravar/editar o vídeo", "status": "manual", "status_label": "Manual",
        "desc": "CapCut, usando o roteiro da etapa 3 e a mídia oficial do produto — narração por IA, sem precisar aparecer.",
        "links": [],
    },
    {
        "titulo": "Publicar (Instagram / WhatsApp)", "status": "proximo", "status_label": "Não construído",
        "desc": "Instagram: publicação + impulsionamento manual por enquanto. WhatsApp (fila de mensagens com imagem + texto pro grupo): ainda não começamos.",
        "links": [],
    },
    {
        "titulo": "Registrar investimento e vendas", "status": "manual", "status_label": "Manual",
        "desc": "Depois de impulsionar ou confirmar uma venda, registra aqui — vira uma linha pronta pra colar nos arquivos do financeiro.",
        "links": [("importar.html", "Importar dados", False)],
    },
    {
        "titulo": "Acompanhar ROI e meta mensal", "status": "bom", "status_label": "Automático",
        "desc": "Cruza investimento x comissão recebida, mostra o progresso da meta de R$10.000/mês e o ROI por produto (meta: 3x).",
        "links": [("painel_roi.html", "Ver painel de ROI", False)],
    },
]


def _link_etapa_html(href, rotulo, externo):
    atributos_extra = ' class="externo" target="_blank" rel="noopener"' if externo else ""
    return f'<a{atributos_extra} href="{href}">{rotulo}</a>'


def _etapa_html(numero, etapa):
    links_html = "".join(
        _link_etapa_html(href, rotulo, externo) for href, rotulo, externo in etapa["links"]
    )
    links_bloco = f'<div class="etapa-links">{links_html}</div>' if links_html else ""
    return f"""
      <div class="etapa">
        <div class="etapa-marca">{numero}</div>
        <div class="etapa-corpo">
          <div class="etapa-topo">
            <span class="etapa-titulo">{etapa['titulo']}</span>
            <span class="status status-{etapa['status']}">{etapa['status_label']}</span>
          </div>
          <p class="etapa-desc">{etapa['desc']}</p>
          {links_bloco}
        </div>
      </div>"""


def gerar_html():
    recomendacoes = coach.gerar_recomendacoes()
    recomendacoes_html = "".join(
        _cartao_recomendacao(r, i) for i, r in enumerate(recomendacoes)
    )
    etapas_html = "".join(_etapa_html(i, e) for i, e in enumerate(ETAPAS, start=1))

    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cockpit Papai Resolve</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #eef1f0; --grid-line: rgba(20, 60, 90, 0.07); --card: #ffffff;
    --text: #14202b; --muted: #5b6b74; --border: #d7dfe0;
    --accent: #d9670c; --accent-ink: #a84e08; --accent-soft: #fbe7d4;
    --focus: #1d64b0;
    --bom: #0ca30c; --bom-soft: #e3f6e0;
    --manual: #a5730a; --manual-soft: #fdf1d9;
    --proximo: #5b6b74; --proximo-soft: #e4e8e7;
    --alta: #d03b3b; --alta-soft: #f8e2e2;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #0f1417; --grid-line: rgba(255,255,255,0.05); --card: #171e22;
      --text: #e7edf0; --muted: #93a2a9; --border: #2a3338;
      --accent: #ff9439; --accent-ink: #ffb066; --accent-soft: #3a2a17;
      --focus: #6badf0;
      --bom: #3fbf8a; --bom-soft: #16332a;
      --manual: #e0b64b; --manual-soft: #3a2f13;
      --proximo: #93a2a9; --proximo-soft: #232c30;
      --alta: #e0776a; --alta-soft: #3a201c;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #0f1417; --grid-line: rgba(255,255,255,0.05); --card: #171e22;
    --text: #e7edf0; --muted: #93a2a9; --border: #2a3338;
    --accent: #ff9439; --accent-ink: #ffb066; --accent-soft: #3a2a17;
    --focus: #6badf0;
    --bom: #3fbf8a; --bom-soft: #16332a;
    --manual: #e0b64b; --manual-soft: #3a2f13;
    --proximo: #93a2a9; --proximo-soft: #232c30;
    --alta: #e0776a; --alta-soft: #3a201c;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 40px 24px 64px;
    background: repeating-linear-gradient(0deg, var(--grid-line) 0 1px, transparent 1px 32px),
      repeating-linear-gradient(90deg, var(--grid-line) 0 1px, transparent 1px 32px), var(--bg);
    color: var(--text); font-family: "IBM Plex Sans", system-ui, sans-serif;
  }}
  .wrap {{ max-width: 900px; margin: 0 auto; }}
{nav.MENU_CSS}
  .cabecalho {{ display: flex; align-items: center; gap: 16px; border-bottom: 2px solid var(--border);
    padding-bottom: 24px; margin-bottom: 28px; }}
  svg.logo {{ flex-shrink: 0; }}
  .cabecalho-texto .eyebrow {{ font-family: "IBM Plex Mono", monospace; font-size: 0.72rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--accent-ink); margin: 0 0 6px; font-weight: 600; }}
  h1 {{ font-family: "Archivo", sans-serif; font-weight: 800; font-size: 1.7rem; margin: 0; }}

  .secao-titulo {{ font-family: "Archivo", sans-serif; font-weight: 700; font-size: 1.1rem; margin: 0 0 4px; }}
  .secao-sub {{ color: var(--muted); font-size: 0.85rem; margin: 0 0 16px; }}
  .secao-topo-flex {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; }}
  .progresso-dia {{ font-family: "IBM Plex Mono", monospace; font-size: 0.78rem; font-weight: 600;
    color: var(--accent-ink); background: var(--accent-soft); padding: 6px 12px; border-radius: 999px;
    white-space: nowrap; }}

  .recomendacoes {{ display: flex; flex-direction: column; gap: 10px; margin-bottom: 36px; }}
  .recomendacao {{ background: var(--card); border: 1px solid var(--border); border-left: 3px solid var(--border);
    border-radius: 8px; padding: 14px 18px; display: flex; align-items: flex-start; justify-content: space-between;
    gap: 12px; flex-wrap: wrap; }}
  .recomendacao-alta {{ border-left-color: var(--alta); }}
  .recomendacao-check {{ display: flex; align-items: flex-start; gap: 12px; cursor: pointer; flex: 1; min-width: 220px; }}
  .chk-tarefa {{ margin-top: 3px; width: 17px; height: 17px; accent-color: var(--accent); cursor: pointer; flex-shrink: 0; }}
  .recomendacao.concluida {{ opacity: 0.55; }}
  .recomendacao.concluida .recomendacao-titulo {{ text-decoration: line-through; }}
  .recomendacao-topo {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 4px; }}
  .tag {{ font-family: "IBM Plex Mono", monospace; font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em; padding: 2px 8px; border-radius: 999px; }}
  .tag-alta {{ color: var(--alta); background: var(--alta-soft); }}
  .tag-normal {{ color: var(--muted); background: var(--proximo-soft); }}
  .recomendacao-titulo {{ font-weight: 600; font-size: 0.95rem; }}
  .recomendacao-desc {{ color: var(--muted); font-size: 0.85rem; margin: 0 0 8px; }}
  .recomendacao-link {{ font-size: 0.82rem; font-weight: 600; color: var(--accent-ink); text-decoration: none; }}
  .recomendacao-link:hover {{ text-decoration: underline; }}

  .legenda {{ display: flex; gap: 18px; flex-wrap: wrap; margin: 4px 0 20px; font-size: 0.8rem; color: var(--muted); }}
  .legenda span {{ display: inline-flex; align-items: center; gap: 6px; }}
  .ponto {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; }}
  .ponto-bom {{ background: var(--bom); }}
  .ponto-manual {{ background: var(--manual); }}
  .ponto-proximo {{ background: var(--proximo); }}

  .fluxo {{ display: flex; flex-direction: column; }}
  .etapa {{ display: flex; gap: 18px; position: relative; }}
  .etapa:not(:last-child)::before {{
    content: ''; position: absolute; left: 15px; top: 38px; bottom: -18px; width: 2px;
    background: var(--border);
  }}
  .etapa-marca {{ flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; background: var(--card);
    border: 2px solid var(--border); display: flex; align-items: center; justify-content: center;
    font-family: "IBM Plex Mono", monospace; font-size: 0.78rem; font-weight: 600; color: var(--muted);
    z-index: 1; }}
  .etapa-corpo {{ flex: 1; padding-bottom: 26px; }}
  .etapa-topo {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 4px; }}
  .etapa-titulo {{ font-family: "Archivo", sans-serif; font-weight: 700; font-size: 1.05rem; }}
  .status {{ font-family: "IBM Plex Mono", monospace; font-size: 0.68rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.04em; padding: 3px 9px; border-radius: 999px; }}
  .status-bom {{ color: var(--bom); background: var(--bom-soft); }}
  .status-manual {{ color: var(--manual); background: var(--manual-soft); }}
  .status-proximo {{ color: var(--proximo); background: var(--proximo-soft); }}
  .etapa-desc {{ color: var(--muted); font-size: 0.88rem; margin: 4px 0 10px; max-width: 62ch; }}
  .etapa-desc code {{ font-family: "IBM Plex Mono", monospace; background: var(--accent-soft); color: var(--accent-ink);
    padding: 1px 5px; border-radius: 3px; }}
  .etapa-links {{ display: flex; gap: 10px; flex-wrap: wrap; }}
  .etapa-links a {{ font-family: "IBM Plex Sans", sans-serif; font-size: 0.82rem; font-weight: 600;
    color: var(--accent-ink); text-decoration: none; border: 1px solid var(--accent-ink);
    padding: 6px 14px; border-radius: 6px; }}
  .etapa-links a:hover {{ background: var(--accent-soft); }}
  .etapa-links a.externo::after {{ content: ' \\2197'; }}

  .rodape {{ margin-top: 32px; padding-top: 20px; border-top: 1px solid var(--border);
    font-size: 0.78rem; color: var(--muted); font-family: "IBM Plex Mono", monospace; }}
</style>
</head>
<body>
  <div class="wrap">
    {nav.gerar_menu_html("index.html")}

    <header class="cabecalho">
      <svg class="logo" width="44" height="44" viewBox="0 0 120 120" fill="none">
        <circle cx="60" cy="60" r="52" stroke="#a84e08" stroke-width="5"/>
        <circle cx="60" cy="60" r="42" stroke="#5b6b74" stroke-width="1.5" stroke-dasharray="2 6"/>
        <path d="M38 62 L54 78 L86 40" stroke="#d9670c" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div class="cabecalho-texto">
        <p class="eyebrow">Papai Resolve &middot; Casa &amp; Construção</p>
        <h1>Cockpit de Afiliação</h1>
      </div>
    </header>

    <div class="secao-topo-flex">
      <div>
        <div class="secao-titulo">O que fazer hoje</div>
        <p class="secao-sub">Atualizado {date.today().strftime('%d/%m/%Y')} &middot; calculado a partir dos seus dados reais</p>
      </div>
      <div class="progresso-dia" id="progresso-dia">0 de {len(recomendacoes)} feitas hoje</div>
    </div>
    <div class="recomendacoes" id="lista-recomendacoes" data-total="{len(recomendacoes)}">{recomendacoes_html}
    </div>

    <div class="secao-titulo">Como a esteira funciona, ponta a ponta</div>
    <div class="legenda">
      <span><span class="ponto ponto-bom"></span> Automático</span>
      <span><span class="ponto ponto-manual"></span> Manual (com apoio do cockpit)</span>
      <span><span class="ponto ponto-proximo"></span> Ainda não construído</span>
    </div>

    <div class="fluxo">{etapas_html}
    </div>

    <p class="rodape">Cockpit de Afiliação IA-First &middot; @papairesolve_br &middot; Fase 1</p>
  </div>

  <script>
    (function () {{
      var hoje = new Date().toISOString().slice(0, 10);
      var chave = 'coach-' + hoje;
      var feitas = [];
      try {{ feitas = JSON.parse(localStorage.getItem(chave) || '[]'); }} catch (e) {{ feitas = []; }}

      var lista = document.getElementById('lista-recomendacoes');
      var total = lista ? (parseInt(lista.getAttribute('data-total'), 10) || 0) : 0;
      var contador = document.getElementById('progresso-dia');

      function salvar() {{
        try {{ localStorage.setItem(chave, JSON.stringify(feitas)); }} catch (e) {{}}
      }}

      function atualizarProgresso() {{
        if (contador) contador.textContent = feitas.length + ' de ' + total + ' feitas hoje';
      }}

      document.querySelectorAll('.chk-tarefa').forEach(function (chk) {{
        var id = chk.getAttribute('data-tarefa-id');
        var cartao = chk.closest('.recomendacao');
        if (feitas.indexOf(id) !== -1) {{
          chk.checked = true;
          if (cartao) cartao.classList.add('concluida');
        }}
        chk.addEventListener('change', function () {{
          var idx = feitas.indexOf(id);
          if (chk.checked) {{
            if (idx === -1) feitas.push(id);
            if (cartao) cartao.classList.add('concluida');
          }} else {{
            if (idx !== -1) feitas.splice(idx, 1);
            if (cartao) cartao.classList.remove('concluida');
          }}
          salvar();
          atualizarProgresso();
        }});
      }});

      atualizarProgresso();
    }})();
  </script>
</body>
</html>
"""


def salvar_painel(caminho="index.html"):
    html = gerar_html()
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    return caminho
