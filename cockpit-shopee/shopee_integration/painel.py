"""
Gera o painel visual (HTML autônomo, sem dependências externas) com a leva
de produtos do dia, para ser aberto direto no navegador ou publicado via
GitHub Pages.

O painel permite marcar produtos (da leva automática, da busca ao vivo
por descrição/link, ou dos adicionados manualmente via
produtos_manuais.txt) e salvar a seleção direto na esteira de produção
de conteúdo (criativos e texto), já com roteiro e legenda prontos.
"""

from datetime import date

from . import nav, segmentos

TIER_LABELS = {
    "baixo": "Baixo",
    "medio": "Médio",
    "alto": "Alto",
}

# Modelo de narração/legenda — padrão fixado em 2026-08-31, voz
# ajustada em 2026-09-01, generalizado em 10/09 (a leva deixou de ser
# restrita ao nicho casa & construção — traz os mais vendidos da Shopee
# em qualquer categoria, então o roteiro não pode mais depender de um
# banco de "ganchos" por categoria de casa, tipo hidráulica/cozinha/etc,
# que só fazia sentido pro nicho antigo). Depois, no mesmo dia, tirada
# também a persona "Papai Resolve" da narração em si (o usuário pediu
# pra esquecer essa narrativa) — agora é direto: Dor → Solução → Prova
# (visual) → Call to action, sem personagem nem abertura fixa, frases
# genéricas o bastante pra qualquer produto (roupa, beleza, eletrônico,
# casa etc.), sem citar um problema específico de categoria. Pedido em
# 11/09: removido também o vínculo restante com a marca "Papai
# Resolve" — tirada a hashtag `#papairesolve` das legendas geradas.
# Implementado em montarRoteiro()/montarLegenda() abaixo.


def _linha_produto(produto, posicao, id_prefixo):
    p = produto
    nome = (p["name"] or "(sem nome)").replace("<", "&lt;").replace(">", "&gt;")
    loja = (p.get("shop_name") or "").replace("<", "&lt;").replace(">", "&gt;")
    categoria = p.get("termo_busca") or ""
    segmento = p.get("segmento") or "outros"
    segmento_label = segmentos.SEGMENTO_LABELS.get(segmento, "Outros")
    row_id = f"{id_prefixo}-{p['product_id']}"
    imagem_url = p.get("image_url") or ""
    if imagem_url:
        foto_html = f'<img class="foto-produto" src="{imagem_url}" alt="" loading="lazy" onerror="this.style.display=\'none\'">'
    else:
        foto_html = '<div class="foto-produto foto-vazia" aria-hidden="true"></div>'
    return f"""
        <tr data-tier="{p['tier']}" data-comissao="{p['commission_rate']*100:.0f}" data-avaliacao="{p['rating']:.1f}" data-vendidos="{p['total_sold']}" data-segmento="{segmento}">
          <td class="col-check">
            <input type="checkbox" class="chk-produto" id="{row_id}"
              data-produto-id="{p['product_id']}"
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
          <td class="col-segmento">{segmento_label}</td>
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
        segmentos_presentes = {p.get("segmento") or "outros" for p in produtos}
        opcoes_segmento = "".join(
            f'<option value="{chave}">{segmentos.SEGMENTO_LABELS[chave]}</option>'
            for chave in segmentos.ORDEM_EXIBICAO
            if chave in segmentos_presentes
        )
        filtro_html = f"""
    <div class="filtros-linha">
      <div class="filtros" role="tablist" aria-label="Filtrar por faixa de ticket">
        <button class="filtro ativo" data-filtro="todos" data-alvo="tabela-principal" role="tab" aria-selected="true">Todos</button>
        <button class="filtro" data-filtro="baixo" data-alvo="tabela-principal" role="tab" aria-selected="false">Ticket baixo</button>
        <button class="filtro" data-filtro="medio" data-alvo="tabela-principal" role="tab" aria-selected="false">Ticket médio</button>
        <button class="filtro" data-filtro="alto" data-alvo="tabela-principal" role="tab" aria-selected="false">Ticket alto</button>
      </div>
      <div class="filtros-select">
        <label for="filtro-segmento">Segmento</label>
        <select id="filtro-segmento" data-alvo="tabela-principal">
          <option value="todos">Todos</option>
          {opcoes_segmento}
        </select>
        <label for="filtro-comissao">Comissão mínima</label>
        <select id="filtro-comissao" data-alvo="tabela-principal">
          <option value="0">Todas</option>
          <option value="10">10%+</option>
          <option value="20">20%+</option>
          <option value="30">30%+</option>
          <option value="40">40%+</option>
        </select>
        <label for="filtro-avaliacao">Avaliação mínima</label>
        <select id="filtro-avaliacao" data-alvo="tabela-principal">
          <option value="0">Todas</option>
          <option value="4">4.0+&#9733;</option>
          <option value="4.5">4.5+&#9733;</option>
          <option value="4.8">4.8+&#9733;</option>
        </select>
        <label for="filtro-vendidos">Vendidos mínimo</label>
        <select id="filtro-vendidos" data-alvo="tabela-principal">
          <option value="0">Todos</option>
          <option value="50">50+</option>
          <option value="100">100+</option>
          <option value="300">300+</option>
          <option value="500">500+</option>
          <option value="1000">1000+</option>
        </select>
      </div>
    </div>"""
    return f"""{filtro_html}
    <div class="tabela-scroll">
      <table>
        <thead>
          <tr>
            <th></th><th>#</th><th>Foto</th><th>Produto</th><th>Faixa</th><th>Segmento</th><th>Preço</th><th>Comissão</th>
            <th>Avaliação</th><th>Vendidos</th><th>Link</th>
          </tr>
        </thead>
        <tbody id="{id_prefixo}-corpo">{linhas_html}
        </tbody>
      </table>
    </div>"""


def gerar_html(produtos, extras=None, titulo="Painel Shopee — Mais Vendidos"):
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
  :root, :root:not([data-theme="light"]), :root[data-theme="dark"] {{
    /* Identidade visual fixa laranja & branco (igual Shopee) — pedido
       do usuário em 10/09, não muda com o tema do sistema. */
    --bg: #ee4d2d;
    --on-bg: #ffffff;
    --on-bg-muted: #ffd9cc;
    --grid-line: rgba(255, 255, 255, 0.12);
    --card: #ffffff;
    --text: #2a1a12;
    --muted: #8a6a5c;
    --border: #f3d0c2;
    --accent: #ee4d2d;
    --accent-ink: #c73e1f;
    --accent-soft: #fde8e0;
    --baixo: #1f8a5f;
    --baixo-soft: #dcf1e7;
    --medio: #1d64b0;
    --medio-soft: #dde9f7;
    --alto: #a13c2f;
    --alto-soft: #f6e2df;
    --focus: #a8341a;
    --barra-bg: #2a1a12;
    --barra-texto: #ffffff;
  }}
  * {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{
    margin: 0;
    padding: 40px 24px 96px;
    background: var(--bg);
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
    border-bottom: 2px solid rgba(255,255,255,0.3);
    padding-bottom: 20px;
  }}
  .eyebrow {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--on-bg);
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
    color: var(--on-bg);
  }}
  .atualizado {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.8rem;
    color: var(--on-bg-muted);
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
    color: var(--on-bg);
  }}
  .descricao-secao {{
    font-size: 0.85rem;
    color: var(--on-bg-muted);
    margin: 0 0 14px;
  }}
  .descricao-secao code {{
    font-family: "IBM Plex Mono", monospace;
    background: var(--accent-soft);
    color: var(--accent-ink);
    padding: 1px 5px;
    border-radius: 3px;
  }}

  .filtros-linha {{
    display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin-bottom: 18px;
  }}
  .filtros {{
    display: inline-flex;
    gap: 4px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 4px;
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
  .filtros-select {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .filtros-select label {{
    font-family: "IBM Plex Sans", sans-serif; font-size: 0.82rem; font-weight: 600; color: var(--on-bg-muted);
  }}
  .filtros-select select {{
    font-family: "IBM Plex Sans", sans-serif; font-size: 0.84rem; color: var(--text);
    background: var(--card); border: 1px solid var(--border); border-radius: 6px;
    padding: 6px 10px; cursor: pointer;
  }}
  .filtros-select select:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 1px; }}

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
    border: 1px solid var(--border); display: block; background: var(--accent-soft);
  }}
  .foto-vazia {{ background: var(--accent-soft); }}
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
  .col-segmento {{ font-size: 0.78rem; color: var(--muted); white-space: nowrap; }}

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
    color: var(--on-bg-muted);
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

  .busca-caixa {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 20px; margin-bottom: 36px;
  }}
  .busca-form {{ display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }}
  .busca-form input {{
    flex: 1; min-width: 200px; font-family: "IBM Plex Sans", sans-serif; font-size: 0.9rem;
    padding: 10px 14px; border-radius: 7px; border: 1px solid var(--border);
    background: #ffffff; color: var(--text);
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
        <p class="eyebrow">Agente Shopee</p>
        <h1>{titulo}</h1>
      </div>
      <p class="atualizado">Atualizado&nbsp;{date.today().strftime('%d/%m/%Y')}<br>{len(produtos)} produtos</p>
    </header>

    <h2 class="titulo-secao">Buscar um produto específico</h2>
    <p class="descricao-secao">Achou um produto no app da Shopee? Cole o link aqui (ou digite uma descrição) — é o jeito mais rápido de trazer ele pro agente sem esperar a leva do dia.</p>
    <div class="busca-caixa">
      <form class="busca-form" id="form-busca">
        <input type="text" id="busca-input" placeholder="Cole o link da Shopee ou digite, ex: torneira de cozinha" autocomplete="off">
        <button class="btn-buscar" id="btn-buscar" type="submit">Buscar</button>
      </form>
      <div class="busca-resultados" id="busca-resultados"></div>
      <p class="busca-aviso" id="busca-aviso" hidden></p>
    </div>

    <h2 class="titulo-secao">Leva do dia &mdash; {len(produtos)} produtos mais vendidos</h2>
    <section class="resumo" aria-label="Resumo da leva">
      <div class="stat stat-baixo"><div class="n">{contagem.get('baixo', 0):02d}</div><div class="l">Ticket baixo (até R$50)</div></div>
      <div class="stat stat-medio"><div class="n">{contagem.get('medio', 0):02d}</div><div class="l">Ticket médio (R$50&ndash;150)</div></div>
      <div class="stat stat-alto"><div class="n">{contagem.get('alto', 0):02d}</div><div class="l">Ticket alto (acima de R$150)</div></div>
      <div class="stat stat-comissao"><div class="n">{comissao_media:.0f}%</div><div class="l">Comissão média da leva</div></div>
    </section>

    {tabela_principal_html}
    {secao_extras_html}

    <p class="rodape">Gerado a partir da Shopee Affiliate API &middot; Agente Shopee</p>
  </div>

  <div class="barra-selecao">
    <div class="barra-selecao-conteudo">
      <span class="barra-contagem"><b id="contagem-selecionados">0</b> selecionado(s)</span>
      <button class="btn-baixar" id="btn-baixar-selecao" disabled>Salvar seleção na esteira</button>
    </div>
  </div>

  <script>
    function aplicarFiltros(alvo) {{
      var grupoTier = document.querySelectorAll('.filtro[data-alvo="' + alvo + '"]');
      var botaoAtivo = document.querySelector('.filtro.ativo[data-alvo="' + alvo + '"]');
      var tier = botaoAtivo ? botaoAtivo.getAttribute('data-filtro') : 'todos';
      var segmento = (document.getElementById('filtro-segmento') || {{}}).value || 'todos';
      var comissaoMin = parseFloat((document.getElementById('filtro-comissao') || {{}}).value || '0');
      var avaliacaoMin = parseFloat((document.getElementById('filtro-avaliacao') || {{}}).value || '0');
      var vendidosMin = parseFloat((document.getElementById('filtro-vendidos') || {{}}).value || '0');

      document.querySelectorAll('#' + alvo + '-corpo tr').forEach(function (linha) {{
        var bateTier = tier === 'todos' || linha.getAttribute('data-tier') === tier;
        var bateSegmento = segmento === 'todos' || linha.getAttribute('data-segmento') === segmento;
        var bateComissao = parseFloat(linha.getAttribute('data-comissao') || '0') >= comissaoMin;
        var bateAvaliacao = parseFloat(linha.getAttribute('data-avaliacao') || '0') >= avaliacaoMin;
        var bateVendidos = parseFloat(linha.getAttribute('data-vendidos') || '0') >= vendidosMin;
        linha.style.display = (bateTier && bateSegmento && bateComissao && bateAvaliacao && bateVendidos) ? '' : 'none';
      }});
    }}

    document.querySelectorAll('.filtro').forEach(function (botao) {{
      botao.addEventListener('click', function () {{
        var alvo = botao.getAttribute('data-alvo');
        document.querySelectorAll('.filtro[data-alvo="' + alvo + '"]').forEach(function (b) {{
          b.classList.remove('ativo');
          b.setAttribute('aria-selected', 'false');
        }});
        botao.classList.add('ativo');
        botao.setAttribute('aria-selected', 'true');
        aplicarFiltros(alvo);
      }});
    }});

    ['filtro-segmento', 'filtro-comissao', 'filtro-avaliacao', 'filtro-vendidos'].forEach(function (id) {{
      var campo = document.getElementById(id);
      if (campo) campo.addEventListener('change', function () {{ aplicarFiltros(campo.getAttribute('data-alvo')); }});
    }});

    function atualizarBarraSelecao() {{
      var marcados = document.querySelectorAll('.chk-produto:checked');
      document.getElementById('contagem-selecionados').textContent = marcados.length;
      document.getElementById('btn-baixar-selecao').disabled = marcados.length === 0;
    }}
    document.querySelectorAll('.chk-produto').forEach(function (chk) {{
      chk.addEventListener('change', atualizarBarraSelecao);
    }});

    function montarRoteiro(chk) {{
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
        '**Roteiro (~20s, direto ao ponto):**',
        '',
        '1. *(0-5s, Dor)* — "Eu tinha um probleminha desse tipo e nada resolvia direito!"',
        '2. *(5-13s, Solução)* — "Aí eu achei ' + nome + ' — resolveu na hora!"',
        '3. *(13-17s, Prova)* — [mostra o produto resolvendo o problema na prática, sem falar]',
        '4. *(17-20s, Call to action)* — "Corre que tá com desconto, R$' + preco + ' — link na bio, comenta \\'QUERO\\' que a gente manda!"',
        ''
      ].join('\\n');
    }}

    function montarLegenda(chk) {{
      var nome = chk.getAttribute('data-nome');
      return [
        '\\u{{1F62B}} Tinha um probleminha desse tipo e nada resolvia direito!',
        '',
        '\\u2705 Resolvi com ' + nome + ' \\u2014 resolveu na hora!',
        '',
        '\\u{{1F6D2}} Link na bio ou comenta "QUERO" que a gente manda o link!',
        '',
        '#achadosdashopee #shopeebrasil #promoshopee #achadinhos'
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

      // Rótulos de segmento — espelha shopee_integration/segmentos.py
      // (SEGMENTO_LABELS), só pra exibir aqui no resultado da busca ao vivo.
      var ROTULOS_SEGMENTO = {{
        beleza: 'Beleza', casa_construcao: 'Casa & Construção', moda: 'Moda',
        eletronicos: 'Eletrônicos', pet: 'Pet', infantil: 'Infantil',
        esporte_lazer: 'Esporte & Lazer', saude: 'Saúde',
        papelaria_escritorio: 'Papelaria & Escritório', automotivo: 'Automotivo',
        outros: 'Outros',
      }};

      function montarItem(p) {{
        var rowId = 'busca-' + p.product_id;

        var chk = document.createElement('input');
        chk.type = 'checkbox';
        chk.className = 'chk-produto';
        chk.id = rowId;
        chk.setAttribute('data-produto-id', p.product_id || '');
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
        var segmento = document.createElement('span');
        segmento.textContent = ROTULOS_SEGMENTO[p.segmento] || 'Outros';
        meta.appendChild(segmento);
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
            if (produtos.length === 0 && !r.dados.link_rastreavel_sem_correspondencia) {{
              mostrarAviso('Nenhum produto encontrado para "' + termo + '".');
              return;
            }}
            if (r.dados.correspondencia_exata) {{
              mostrarAviso('Encontrado direto pelo link \\u2713');
            }} else if (r.dados.link_rastreavel_sem_correspondencia) {{
              mostrarAviso(
                'N\\u00e3o achei os detalhes desse produto (nome/pre\\u00e7o/foto) na busca, mas gerei ' +
                'o link rastre\\u00e1vel certo dele \\u2014 copie e use direto: ' +
                r.dados.link_rastreavel_sem_correspondencia +
                ' (ainda n\\u00e3o d\\u00e1 pra adicionar na esteira sem os detalhes, só pelo link).'
              );
            }} else if (r.dados.termo_usado) {{
              mostrarAviso('Busquei por "' + r.dados.termo_usado + '" (extraído do link) \\u2014 confira se é o produto certo antes de marcar.');
            }}
            produtos.forEach(function (p) {{
              resultados.appendChild(montarItem(p));
            }});
            atualizarBarraSelecao();
          }})
          .catch(function () {{
            mostrarAviso('Não consegui falar com o servidor de busca. Essa função só funciona depois de publicado na Vercel (veja o README).');
          }})
          .finally(function () {{
            botaoBuscar.disabled = false;
            botaoBuscar.textContent = 'Buscar';
          }});
      }});
    }})();

    function salvarNaEsteira(marcados) {{
      var produtos = Array.prototype.map.call(marcados, function (chk) {{
        return {{
          produto_id: chk.getAttribute('data-produto-id'),
          nome: chk.getAttribute('data-nome'),
          preco: chk.getAttribute('data-preco'),
          comissao: chk.getAttribute('data-comissao'),
          link: chk.getAttribute('data-link'),
          categoria: chk.getAttribute('data-categoria'),
          narracao: montarRoteiro(chk),
          legenda: montarLegenda(chk),
        }};
      }});
      return fetch('/api/selecionar', {{
        method: 'POST',
        headers: {{ 'content-type': 'application/json' }},
        body: JSON.stringify({{ produtos: produtos }}),
      }}).then(function (resposta) {{
        return resposta.json().then(function (dados) {{ return {{ ok: resposta.ok, dados: dados }}; }});
      }});
    }}

    document.getElementById('btn-baixar-selecao').addEventListener('click', function () {{
      var botao = this;
      var marcados = document.querySelectorAll('.chk-produto:checked');
      var textoOriginal = botao.textContent;

      botao.disabled = true;
      botao.textContent = 'Salvando na esteira...';
      salvarNaEsteira(marcados)
        .then(function (r) {{
          if (r.ok) {{
            botao.textContent = 'Salvo na esteira! \\u2713';
          }} else {{
            botao.textContent = textoOriginal;
            alert(r.dados.erro || 'Não consegui salvar na esteira.');
          }}
        }})
        .catch(function () {{
          botao.textContent = textoOriginal;
          alert('Não consegui salvar na esteira (essa parte só funciona depois de publicado na Vercel — veja o README).');
        }})
        .finally(function () {{
          setTimeout(function () {{
            botao.disabled = document.querySelectorAll('.chk-produto:checked').length === 0;
            botao.textContent = textoOriginal;
          }}, 3000);
        }});
    }});
  </script>
</body>
</html>
"""


def salvar_painel(produtos, caminho, extras=None, titulo="Painel Shopee — Mais Vendidos"):
    html = gerar_html(produtos, extras=extras, titulo=titulo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    return caminho
