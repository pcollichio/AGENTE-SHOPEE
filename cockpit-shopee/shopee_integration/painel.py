"""
Gera o painel visual (HTML autônomo, sem dependências externas) com a leva
de produtos do dia, para ser aberto direto no navegador ou publicado via
GitHub Pages.

O painel permite marcar produtos (da leva automática ou dos adicionados
manualmente via produtos_manuais.txt) e baixar a lista marcada como um
arquivo Markdown — essa lista é o que segue para a esteira de produção de
conteúdo (criativos e texto).
"""

import json
from datetime import date

from . import nav

TIER_LABELS = {
    "baixo": "Baixo",
    "medio": "Médio",
    "alto": "Alto",
}

# Banco de "ganchos" do modelo de narração Papai Resolve: para cada
# categoria de busca, um problema comum de casa (o gancho inicial) e o
# motivo pelo qual o produto resolve. Usado para montar o roteiro
# automaticamente a partir do produto marcado no painel.
GANCHOS_ROTEIRO = {
    "ferramentas": {
        "problema": "Aquele reparo simples que vira perrengue por falta da ferramenta certa?",
        "motivo": "resolve porque entrega o que precisa pro serviço, sem chamar ninguém",
    },
    "organizacao": {
        "problema": "Cansado de procurar as coisas porque nada tem lugar certo?",
        "motivo": "resolve porque dá um lugar fixo pra cada coisa, sem obra",
    },
    "iluminacao": {
        "problema": "Aquele cantinho de casa que fica sempre escuro?",
        "motivo": "resolve porque instala em minutos e muda o ambiente na hora",
    },
    "hidraulica": {
        "problema": "Vazamento ou entupimento que não para de voltar?",
        "motivo": "resolve porque se ajusta sem precisar chamar encanador",
    },
    "decoracao": {
        "problema": "Ambiente parecendo sem graça, meio vazio?",
        "motivo": "resolve porque transforma o visual sem reforma",
    },
    "cozinha": {
        "problema": "Cozinha bagunçada na hora de cozinhar?",
        "motivo": "resolve porque organiza e agiliza o dia a dia",
    },
    "banheiro": {
        "problema": "Banheiro pequeno e sem espaço pra nada?",
        "motivo": "resolve porque aproveita cada cantinho",
    },
    "jardim": {
        "problema": "Plantas morrendo por falta de cuidado?",
        "motivo": "resolve porque facilita a rotina de cuidar delas",
    },
    "eletrica": {
        "problema": "Tomada que não dá conta de tudo que você precisa ligar?",
        "motivo": "resolve porque multiplica os pontos com segurança",
    },
    "pintura": {
        "problema": "Parede desbotada mas dá preguiça de chamar pintor?",
        "motivo": "resolve porque você mesmo aplica numa tarde",
    },
    "limpeza": {
        "problema": "Aquela sujeira que não sai de jeito nenhum?",
        "motivo": "resolve porque foi feito pra esse tipo de sujeira",
    },
    "moveis": {
        "problema": "Espaço apertado que não cabe móvel grande?",
        "motivo": "resolve porque é compacto e multifuncional",
    },
    "_padrao": {
        "problema": "Aquele probleminha de casa que ninguém resolve direito?",
        "motivo": "resolve na prática, sem complicação",
    },
}


def _linha_produto(produto, posicao, id_prefixo):
    p = produto
    nome = (p["name"] or "(sem nome)").replace("<", "&lt;").replace(">", "&gt;")
    loja = (p.get("shop_name") or "").replace("<", "&lt;").replace(">", "&gt;")
    categoria = p.get("termo_busca") or ""
    row_id = f"{id_prefixo}-{p['product_id']}"
    imagem_url = p.get("image_url") or ""
    if imagem_url:
        foto_html = f'<img class="foto-produto" src="{imagem_url}" alt="" loading="lazy" onerror="this.style.display=\'none\'">'
    else:
        foto_html = '<div class="foto-produto foto-vazia" aria-hidden="true"></div>'
    return f"""
        <tr data-tier="{p['tier']}">
          <td class="col-check">
            <input type="checkbox" class="chk-produto" id="{row_id}"
              data-nome="{nome}" data-preco="{p['price']:.2f}"
              data-comissao="{p['commission_rate']*100:.0f}"
              data-link="{p['affiliate_link']}"
              data-categoria="{categoria}">
          </td>
          <td class="col-pos">{posicao:02d}</td>
          <td class="col-foto">
            <a href="{p['affiliate_link']}" target="_blank" rel="noopener">{foto_html}</a>
          </td>
          <td class="col-nome">
            <label for="{row_id}" class="nome">{nome}</label>
            <div class="loja">{loja}</div>
          </td>
          <td class="col-tier"><span class="selo selo-{p['tier']}">{TIER_LABELS[p['tier']]}</span></td>
          <td class="col-num">R$&nbsp;{p['price']:.2f}</td>
          <td class="col-num destaque">{p['commission_rate']*100:.0f}%</td>
          <td class="col-num">{p['rating']:.1f}&#9733;</td>
          <td class="col-num">{p['total_sold']:,}</td>
          <td class="col-link"><a href="{p['affiliate_link']}" target="_blank" rel="noopener">Abrir&nbsp;&#8599;</a></td>
        </tr>"""


def _tabela(produtos, id_prefixo, com_filtro=True):
    linhas_html = "".join(
        _linha_produto(p, i, id_prefixo) for i, p in enumerate(produtos, start=1)
    )
    filtro_html = ""
    if com_filtro:
        filtro_html = """
    <div class="filtros" role="tablist" aria-label="Filtrar por faixa de ticket">
      <button class="filtro ativo" data-filtro="todos" data-alvo="tabela-principal" role="tab" aria-selected="true">Todos</button>
      <button class="filtro" data-filtro="baixo" data-alvo="tabela-principal" role="tab" aria-selected="false">Ticket baixo</button>
      <button class="filtro" data-filtro="medio" data-alvo="tabela-principal" role="tab" aria-selected="false">Ticket médio</button>
      <button class="filtro" data-filtro="alto" data-alvo="tabela-principal" role="tab" aria-selected="false">Ticket alto</button>
    </div>"""
    return f"""{filtro_html}
    <div class="tabela-scroll">
      <table>
        <thead>
          <tr>
            <th></th><th>#</th><th>Foto</th><th>Produto</th><th>Faixa</th><th>Preço</th><th>Comissão</th>
            <th>Avaliação</th><th>Vendidos</th><th>Link</th>
          </tr>
        </thead>
        <tbody id="{id_prefixo}-corpo">{linhas_html}
        </tbody>
      </table>
    </div>"""


def gerar_html(produtos, extras=None, titulo="Painel Shopee — Casa & Construção"):
    """Recebe a leva de produtos (cada um já com a chave 'tier':
    'baixo'/'medio'/'alto') e, opcionalmente, uma lista `extras` de produtos
    buscados manualmente (via produtos_manuais.txt). Devolve uma página
    HTML autônoma, com seleção por checkbox e exportação para a esteira."""

    extras = extras or []

    contagem = {"baixo": 0, "medio": 0, "alto": 0}
    for p in produtos:
        contagem[p["tier"]] = contagem.get(p["tier"], 0) + 1

    comissao_media = (
        sum(p["commission_rate"] for p in produtos) / len(produtos) * 100
        if produtos
        else 0
    )

    tabela_principal_html = _tabela(produtos, "tabela-principal", com_filtro=True)
    ganchos_json = json.dumps(GANCHOS_ROTEIRO, ensure_ascii=False)

    secao_extras_html = ""
    if extras:
        tabela_extras_html = _tabela(extras, "tabela-extras", com_filtro=False)
        secao_extras_html = f"""
    <h2 class="titulo-secao">Adicionados manualmente</h2>
    <p class="descricao-secao">Produtos buscados via <code>produtos_manuais.txt</code>, fora da curadoria automática.</p>
    {tabela_extras_html}"""

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
    --bg: #eef1f0;
    --grid-line: rgba(20, 60, 90, 0.07);
    --card: #ffffff;
    --text: #14202b;
    --muted: #5b6b74;
    --border: #d7dfe0;
    --accent: #d9670c;
    --accent-ink: #a84e08;
    --accent-soft: #fbe7d4;
    --baixo: #1f8a5f;
    --baixo-soft: #dcf1e7;
    --medio: #1d64b0;
    --medio-soft: #dde9f7;
    --alto: #a13c2f;
    --alto-soft: #f6e2df;
    --focus: #1d64b0;
    --barra-bg: #14202b;
    --barra-texto: #eef1f0;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #0f1417;
      --grid-line: rgba(255, 255, 255, 0.05);
      --card: #171e22;
      --text: #e7edf0;
      --muted: #93a2a9;
      --border: #2a3338;
      --accent: #ff9439;
      --accent-ink: #ffb066;
      --accent-soft: #3a2a17;
      --baixo: #3fbf8a;
      --baixo-soft: #16332a;
      --medio: #6badf0;
      --medio-soft: #182a3d;
      --alto: #e0776a;
      --alto-soft: #3a201c;
      --focus: #6badf0;
      --barra-bg: #232c32;
      --barra-texto: #e7edf0;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #0f1417;
    --grid-line: rgba(255, 255, 255, 0.05);
    --card: #171e22;
    --text: #e7edf0;
    --muted: #93a2a9;
    --border: #2a3338;
    --accent: #ff9439;
    --accent-ink: #ffb066;
    --accent-soft: #3a2a17;
    --baixo: #3fbf8a;
    --baixo-soft: #16332a;
    --medio: #6badf0;
    --medio-soft: #182a3d;
    --alto: #e0776a;
    --alto-soft: #3a201c;
    --focus: #6badf0;
    --barra-bg: #232c32;
    --barra-texto: #e7edf0;
  }}
  * {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{
    margin: 0;
    padding: 40px 24px 96px;
    background:
      repeating-linear-gradient(0deg, var(--grid-line) 0 1px, transparent 1px 32px),
      repeating-linear-gradient(90deg, var(--grid-line) 0 1px, transparent 1px 32px),
      var(--bg);
    color: var(--text);
    font-family: "IBM Plex Sans", system-ui, -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 1120px; margin: 0 auto; }}

  .cabecalho {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 28px;
    border-bottom: 2px solid var(--border);
    padding-bottom: 20px;
  }}
  .eyebrow {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-ink);
    margin: 0 0 8px;
    font-weight: 600;
  }}
  h1 {{
    font-family: "Archivo", system-ui, sans-serif;
    font-weight: 800;
    font-size: clamp(1.5rem, 2.4vw, 2rem);
    margin: 0;
    letter-spacing: -0.01em;
    text-wrap: balance;
  }}
  .atualizado {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.8rem;
    color: var(--muted);
    text-align: right;
  }}

  .resumo {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 28px;
  }}
  .stat {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px 18px;
  }}
  .stat .n {{
    font-family: "IBM Plex Mono", monospace;
    font-variant-numeric: tabular-nums;
    font-size: 1.6rem;
    font-weight: 600;
    line-height: 1.1;
  }}
  .stat.stat-baixo .n {{ color: var(--baixo); }}
  .stat.stat-medio .n {{ color: var(--medio); }}
  .stat.stat-alto .n {{ color: var(--alto); }}
  .stat.stat-comissao .n {{ color: var(--accent-ink); }}
  .stat .l {{
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 4px;
  }}

  .titulo-secao {{
    font-family: "Archivo", system-ui, sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    margin: 36px 0 4px;
  }}
  .descricao-secao {{
    font-size: 0.85rem;
    color: var(--muted);
    margin: 0 0 14px;
  }}
  .descricao-secao code {{
    font-family: "IBM Plex Mono", monospace;
    background: var(--accent-soft);
    color: var(--accent-ink);
    padding: 1px 5px;
    border-radius: 3px;
  }}

  .filtros {{
    display: inline-flex;
    gap: 4px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 4px;
    margin-bottom: 18px;
  }}
  .filtro {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.84rem;
    font-weight: 500;
    border: none;
    background: transparent;
    color: var(--muted);
    padding: 7px 16px;
    border-radius: 5px;
    cursor: pointer;
  }}
  .filtro:hover {{ color: var(--text); }}
  .filtro:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 2px; }}
  .filtro.ativo {{ background: var(--accent); color: #fff; }}

  .tabela-scroll {{
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--card);
  }}
  table {{ width: 100%; border-collapse: collapse; min-width: 760px; }}
  th, td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 0.88rem; }}
  th {{
    text-align: left;
    color: var(--muted);
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-family: "IBM Plex Mono", monospace;
  }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover {{ background: var(--accent-soft); }}
  .col-check {{ width: 20px; }}
  .col-check input {{ width: 17px; height: 17px; accent-color: var(--accent); cursor: pointer; }}
  .col-foto {{ width: 56px; padding: 8px 10px; }}
  .foto-produto {{
    width: 48px; height: 48px; border-radius: 6px; object-fit: cover;
    border: 1px solid var(--border); display: block; background: var(--bg);
  }}
  .foto-vazia {{ background: var(--bg); }}
  .col-pos {{
    font-family: "IBM Plex Mono", monospace;
    color: var(--muted);
    font-variant-numeric: tabular-nums;
  }}
  .col-num {{
    text-align: right;
    white-space: nowrap;
    font-family: "IBM Plex Mono", monospace;
    font-variant-numeric: tabular-nums;
  }}
  .destaque {{ font-weight: 600; color: var(--accent-ink); }}
  .nome {{ font-weight: 600; cursor: pointer; }}
  .loja {{ font-size: 0.76rem; color: var(--muted); margin-top: 2px; }}

  .selo {{
    display: inline-block;
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 4px;
    border: 1px solid transparent;
  }}
  .selo-baixo {{ color: var(--baixo); background: var(--baixo-soft); border-color: var(--baixo); }}
  .selo-medio {{ color: var(--medio); background: var(--medio-soft); border-color: var(--medio); }}
  .selo-alto {{ color: var(--alto); background: var(--alto-soft); border-color: var(--alto); }}

  .col-link a {{
    color: var(--accent-ink);
    text-decoration: none;
    font-weight: 600;
    white-space: nowrap;
  }}
  .col-link a:hover {{ text-decoration: underline; }}
  .col-link a:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 2px; }}

  .rodape {{
    margin-top: 20px;
    font-size: 0.78rem;
    color: var(--muted);
    font-family: "IBM Plex Mono", monospace;
  }}

  .barra-selecao {{
    position: fixed;
    left: 0; right: 0; bottom: 0;
    display: flex;
    justify-content: center;
    padding: 16px;
    pointer-events: none;
  }}
  .barra-selecao-conteudo {{
    pointer-events: auto;
    background: var(--barra-bg);
    color: var(--barra-texto);
    border-radius: 10px;
    padding: 12px 14px 12px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  }}
  .barra-contagem {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.85rem;
  }}
  .barra-contagem b {{ font-size: 1rem; }}
  .btn-baixar {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 10px 18px;
    border-radius: 7px;
    cursor: pointer;
  }}
  .btn-baixar:disabled {{ opacity: 0.4; cursor: not-allowed; }}
  .btn-baixar:focus-visible {{ outline: 2px solid #fff; outline-offset: 2px; }}
  .btn-salvar {{
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    background: transparent;
    color: var(--barra-texto);
    border: 1px solid var(--barra-texto);
    padding: 10px 18px;
    border-radius: 7px;
    cursor: pointer;
  }}
  .btn-salvar:disabled {{ opacity: 0.4; cursor: not-allowed; }}
  .btn-salvar:focus-visible {{ outline: 2px solid #fff; outline-offset: 2px; }}

  .busca-caixa {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 20px; margin-bottom: 36px;
  }}
  .busca-form {{ display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }}
  .busca-form input {{
    flex: 1; min-width: 200px; font-family: "IBM Plex Sans", sans-serif; font-size: 0.9rem;
    padding: 10px 14px; border-radius: 7px; border: 1px solid var(--border);
    background: var(--bg); color: var(--text);
  }}
  .busca-form input:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 1px; }}
  .btn-buscar {{
    font-family: "IBM Plex Sans", sans-serif; font-size: 0.85rem; font-weight: 600;
    background: var(--accent); color: #fff; border: none; padding: 0 20px;
    border-radius: 7px; cursor: pointer;
  }}
  .btn-buscar:disabled {{ opacity: 0.5; cursor: not-allowed; }}
  .busca-resultados {{ display: flex; flex-direction: column; gap: 10px; }}
  .resultado-item {{
    display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
    padding: 12px; border: 1px solid var(--border); border-radius: 8px;
  }}
  .resultado-item .foto-produto {{ width: 56px; height: 56px; }}
  .resultado-info {{ flex: 1; min-width: 180px; }}
  .resultado-meta {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
    font-size: 0.85rem; margin-top: 4px; }}
  .resultado-abrir {{ font-size: 0.85rem; font-weight: 600; color: var(--accent-ink); text-decoration: none;
    white-space: nowrap; }}
  .resultado-abrir:hover {{ text-decoration: underline; }}
  .busca-aviso {{ color: var(--muted); font-size: 0.82rem; margin: 10px 0 0; }}

  @media (max-width: 640px) {{
    .resumo {{ grid-template-columns: repeat(2, 1fr); }}
    .barra-selecao-conteudo {{ flex-direction: column; align-items: stretch; text-align: center; }}
  }}
{nav.MENU_CSS}
</style>
</head>
<body>
  <div class="wrap">
    {nav.gerar_menu_html("painel.html")}
    <header class="cabecalho">
      <div>
        <p class="eyebrow">Cockpit de Afiliação &middot; @papairesolve_br</p>
        <h1>{titulo}</h1>
      </div>
      <p class="atualizado">Atualizado&nbsp;{date.today().strftime('%d/%m/%Y')}<br>{len(produtos)} produtos</p>
    </header>

    <section class="resumo" aria-label="Resumo da leva">
      <div class="stat stat-baixo"><div class="n">{contagem.get('baixo', 0):02d}</div><div class="l">Ticket baixo (até R$50)</div></div>
      <div class="stat stat-medio"><div class="n">{contagem.get('medio', 0):02d}</div><div class="l">Ticket médio (R$50&ndash;150)</div></div>
      <div class="stat stat-alto"><div class="n">{contagem.get('alto', 0):02d}</div><div class="l">Ticket alto (acima de R$150)</div></div>
      <div class="stat stat-comissao"><div class="n">{comissao_media:.0f}%</div><div class="l">Comissão média da leva</div></div>
    </section>

    {tabela_principal_html}
    {secao_extras_html}

    <h2 class="titulo-secao">Buscar um produto específico</h2>
    <p class="descricao-secao">Tem um produto em mente que não apareceu na leva de hoje? Busque direto na Shopee pelo nome.</p>
    <div class="busca-caixa">
      <form class="busca-form" id="form-busca">
        <input type="text" id="busca-input" placeholder="Ex: torneira de cozinha" autocomplete="off">
        <button class="btn-buscar" id="btn-buscar" type="submit">Buscar</button>
      </form>
      <div class="busca-resultados" id="busca-resultados"></div>
      <p class="busca-aviso" id="busca-aviso" hidden></p>
    </div>

    <p class="rodape">Gerado a partir da Shopee Affiliate API &middot; Cockpit de Afiliação IA-First</p>
  </div>

  <div class="barra-selecao">
    <div class="barra-selecao-conteudo">
      <span class="barra-contagem"><b id="contagem-selecionados">0</b> selecionado(s)</span>
      <button class="btn-salvar" id="btn-salvar-selecao" disabled>Salvar seleção agora</button>
      <button class="btn-baixar" id="btn-baixar-selecao" disabled>Baixar seleção para a esteira</button>
    </div>
  </div>

  <script>
    document.querySelectorAll('.filtro').forEach(function (botao) {{
      botao.addEventListener('click', function () {{
        var grupo = document.querySelectorAll('.filtro[data-alvo="' + botao.getAttribute('data-alvo') + '"]');
        grupo.forEach(function (b) {{
          b.classList.remove('ativo');
          b.setAttribute('aria-selected', 'false');
        }});
        botao.classList.add('ativo');
        botao.setAttribute('aria-selected', 'true');
        var filtro = botao.getAttribute('data-filtro');
        document.querySelectorAll('#' + botao.getAttribute('data-alvo') + '-corpo tr').forEach(function (linha) {{
          linha.style.display = (filtro === 'todos' || linha.getAttribute('data-tier') === filtro) ? '' : 'none';
        }});
      }});
    }});

    function atualizarBarraSelecao() {{
      var marcados = document.querySelectorAll('.chk-produto:checked');
      document.getElementById('contagem-selecionados').textContent = marcados.length;
      document.getElementById('btn-baixar-selecao').disabled = marcados.length === 0;
      document.getElementById('btn-salvar-selecao').disabled = marcados.length === 0;
    }}
    document.querySelectorAll('.chk-produto').forEach(function (chk) {{
      chk.addEventListener('change', atualizarBarraSelecao);
    }});

    var GANCHOS_ROTEIRO = {ganchos_json};

    function montarRoteiro(chk) {{
      var categoria = chk.getAttribute('data-categoria');
      var gancho = GANCHOS_ROTEIRO[categoria] || GANCHOS_ROTEIRO['_padrao'];
      var nome = chk.getAttribute('data-nome');
      var preco = chk.getAttribute('data-preco');
      var link = chk.getAttribute('data-link');
      return [
        '## ' + nome,
        '',
        '**Link de afiliado:** ' + link + '  ',
        '**Preço:** R$' + preco + '  ',
        '**Comissão:** ' + chk.getAttribute('data-comissao') + '%',
        '',
        '**Roteiro (modelo Papai Resolve, ~20s):**',
        '',
        '1. *(0-3s, Problema)* — "' + gancho['problema'] + '"',
        '2. *(3-6s, Agravar)* — "Já tentei de tudo e nada resolvia direito."',
        '3. *(6-12s, Solução)* — "Até eu achar ' + nome + ' — ' + gancho['motivo'] + '."',
        '4. *(12-18s, Prova)* — [mostra o produto resolvendo o problema na prática, sem falar]',
        '5. *(18-22s, Oferta + CTA)* — "Tá com preço especial agora, R$' + preco + ' — link na bio, comenta \\'QUERO\\' que eu mando."',
        ''
      ].join('\\n');
    }}

    (function () {{
      var form = document.getElementById('form-busca');
      var input = document.getElementById('busca-input');
      var botaoBuscar = document.getElementById('btn-buscar');
      var resultados = document.getElementById('busca-resultados');
      var aviso = document.getElementById('busca-aviso');

      function mostrarAviso(texto) {{
        aviso.textContent = texto;
        aviso.hidden = false;
      }}

      function limparAviso() {{
        aviso.hidden = true;
      }}

      function criarSelo(tier) {{
        var rotulos = {{ baixo: 'Baixo', medio: 'Médio', alto: 'Alto' }};
        var span = document.createElement('span');
        span.className = 'selo selo-' + (tier || '');
        span.textContent = rotulos[tier] || (tier || '?');
        return span;
      }}

      function montarItem(p) {{
        var rowId = 'busca-' + p.product_id;

        var chk = document.createElement('input');
        chk.type = 'checkbox';
        chk.className = 'chk-produto';
        chk.id = rowId;
        chk.setAttribute('data-nome', p.name || '(sem nome)');
        chk.setAttribute('data-preco', Number(p.price || 0).toFixed(2));
        chk.setAttribute('data-comissao', Math.round((p.commission_rate || 0) * 100));
        chk.setAttribute('data-link', p.affiliate_link || '');
        chk.setAttribute('data-categoria', '');
        chk.addEventListener('change', atualizarBarraSelecao);

        var linkFoto = document.createElement('a');
        linkFoto.href = p.affiliate_link || '#';
        linkFoto.target = '_blank';
        linkFoto.rel = 'noopener';
        var foto = document.createElement('img');
        foto.className = 'foto-produto';
        foto.loading = 'lazy';
        foto.alt = '';
        foto.src = p.image_url || '';
        foto.onerror = function () {{ foto.style.display = 'none'; }};
        linkFoto.appendChild(foto);

        var label = document.createElement('label');
        label.setAttribute('for', rowId);
        label.className = 'nome';
        label.textContent = p.name || '(sem nome)';

        var loja = document.createElement('div');
        loja.className = 'loja';
        loja.textContent = p.shop_name || '';

        var meta = document.createElement('div');
        meta.className = 'resultado-meta';
        meta.appendChild(criarSelo(p.tier));
        var preco = document.createElement('span');
        preco.textContent = 'R$ ' + Number(p.price || 0).toFixed(2);
        meta.appendChild(preco);
        var comissao = document.createElement('span');
        comissao.className = 'destaque';
        comissao.textContent = Math.round((p.commission_rate || 0) * 100) + '%';
        meta.appendChild(comissao);
        var avaliacao = document.createElement('span');
        avaliacao.textContent = Number(p.rating || 0).toFixed(1) + '\\u2605';
        meta.appendChild(avaliacao);
        var vendidos = document.createElement('span');
        vendidos.textContent = (p.total_sold || 0).toLocaleString('pt-BR') + ' vendidos';
        meta.appendChild(vendidos);

        var info = document.createElement('div');
        info.className = 'resultado-info';
        info.appendChild(label);
        info.appendChild(loja);
        info.appendChild(meta);

        var abrir = document.createElement('a');
        abrir.className = 'resultado-abrir';
        abrir.href = p.affiliate_link || '#';
        abrir.target = '_blank';
        abrir.rel = 'noopener';
        abrir.textContent = 'Abrir \\u2197';

        var item = document.createElement('div');
        item.className = 'resultado-item';
        item.appendChild(chk);
        item.appendChild(linkFoto);
        item.appendChild(info);
        item.appendChild(abrir);
        return item;
      }}

      form.addEventListener('submit', function (ev) {{
        ev.preventDefault();
        var termo = input.value.trim();
        if (!termo) return;

        limparAviso();
        resultados.innerHTML = '';
        botaoBuscar.disabled = true;
        botaoBuscar.textContent = 'Buscando...';

        fetch('/api/buscar_produto?q=' + encodeURIComponent(termo))
          .then(function (resposta) {{
            return resposta.json().then(function (dados) {{
              return {{ ok: resposta.ok, dados: dados }};
            }});
          }})
          .then(function (r) {{
            if (!r.ok) {{
              mostrarAviso(r.dados.erro || 'Não consegui buscar agora.');
              return;
            }}
            var produtos = r.dados.produtos || [];
            if (produtos.length === 0) {{
              mostrarAviso('Nenhum produto encontrado para "' + termo + '".');
              return;
            }}
            produtos.forEach(function (p) {{
              resultados.appendChild(montarItem(p));
            }});
            atualizarBarraSelecao();
          }})
          .catch(function () {{
            mostrarAviso('Não consegui falar com o servidor de busca. Essa função só funciona depois de publicar o cockpit na Vercel (veja o README).');
          }})
          .finally(function () {{
            botaoBuscar.disabled = false;
            botaoBuscar.textContent = 'Buscar';
          }});
      }});
    }})();

    document.getElementById('btn-salvar-selecao').addEventListener('click', function () {{
      var botao = this;
      var marcados = document.querySelectorAll('.chk-produto:checked');
      var produtos = Array.prototype.map.call(marcados, function (chk) {{
        return {{
          nome: chk.getAttribute('data-nome'),
          preco: chk.getAttribute('data-preco'),
          comissao: chk.getAttribute('data-comissao'),
          link: chk.getAttribute('data-link'),
          categoria: chk.getAttribute('data-categoria'),
        }};
      }});

      botao.disabled = true;
      var textoOriginal = botao.textContent;
      botao.textContent = 'Salvando...';

      fetch('/api/selecionar', {{
        method: 'POST',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{ produtos: produtos }}),
      }})
        .then(function (resposta) {{
          return resposta.json().then(function (dados) {{ return {{ ok: resposta.ok, dados: dados }}; }});
        }})
        .then(function (r) {{
          if (r.ok) {{
            botao.textContent = 'Salvo! \\u2713';
          }} else {{
            botao.textContent = textoOriginal;
            alert(r.dados.erro || 'Não consegui salvar a seleção.');
          }}
        }})
        .catch(function () {{
          botao.textContent = textoOriginal;
          alert('Não consegui falar com o servidor. Essa função só funciona no cockpit publicado na Vercel (veja o README).');
        }})
        .finally(function () {{
          setTimeout(function () {{
            botao.disabled = document.querySelectorAll('.chk-produto:checked').length === 0;
            botao.textContent = textoOriginal;
          }}, 2500);
        }});
    }});

    document.getElementById('btn-baixar-selecao').addEventListener('click', function () {{
      var marcados = document.querySelectorAll('.chk-produto:checked');
      var hoje = new Date().toISOString().slice(0, 10);
      var linhas = [
        '# Esteira de produção — ' + hoje,
        '',
        '## Resumo',
        '',
        '| Produto | Preço | Comissão | Link de afiliado |',
        '|---|---|---|---|'
      ];
      marcados.forEach(function (chk) {{
        linhas.push(
          '| ' + chk.getAttribute('data-nome') +
          ' | R$' + chk.getAttribute('data-preco') +
          ' | ' + chk.getAttribute('data-comissao') + '%' +
          ' | ' + chk.getAttribute('data-link') + ' |'
        );
      }});
      linhas.push('', '---', '', '# Roteiros', '');
      marcados.forEach(function (chk) {{
        linhas.push(montarRoteiro(chk));
      }});
      var conteudo = linhas.join('\\n');
      var blob = new Blob([conteudo], {{ type: 'text/markdown;charset=utf-8' }});
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'esteira-' + hoje + '.md';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }});
  </script>
</body>
</html>
"""


def salvar_painel(produtos, caminho, extras=None, titulo="Painel Shopee — Casa & Construção"):
    html = gerar_html(produtos, extras=extras, titulo=titulo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    return caminho
