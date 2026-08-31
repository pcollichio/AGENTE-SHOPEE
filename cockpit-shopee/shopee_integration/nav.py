"""
Menu de navegação compartilhado entre as páginas do cockpit — permite ir
direto a qualquer parte, de qualquer lugar, sem precisar voltar pro
index.html toda vez.
"""

PAGINAS = [
    ("index.html", "Início"),
    ("chat.html", "Chat"),
    ("painel.html", "Produtos"),
    ("esteira.html", "Esteira"),
    ("importar.html", "Importar"),
    ("painel_roi.html", "ROI"),
]

IDENTIDADE_URL = "https://claude.ai/code/artifact/a5421828-0ecd-4bd1-8c5f-d3a2799c26bf"

MENU_CSS = """
  .menu-cockpit { display: flex; gap: 4px; background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 4px; margin-bottom: 24px; flex-wrap: wrap; }
  .menu-item { font-family: "IBM Plex Sans", sans-serif; font-size: 0.84rem; font-weight: 600;
    color: var(--muted); text-decoration: none; padding: 8px 14px; border-radius: 6px; }
  .menu-item:hover { color: var(--text); background: var(--bg); }
  .menu-item.ativo { background: var(--accent); color: #fff; }
"""


def gerar_menu_html(pagina_atual):
    itens = []
    for arquivo, rotulo in PAGINAS:
        classe = "menu-item ativo" if arquivo == pagina_atual else "menu-item"
        itens.append(f'<a class="{classe}" href="{arquivo}">{rotulo}</a>')
    itens.append(
        f'<a class="menu-item" href="{IDENTIDADE_URL}" target="_blank" rel="noopener">Identidade&nbsp;&#8599;</a>'
    )
    menu = '<nav class="menu-cockpit" id="menu-cockpit">' + "".join(itens) + "</nav>"
    # Quando a página abre dentro do cockpit.html (iframe com o menu
    # lateral), esconde esse menu horizontal pra não duplicar a navegação.
    script_embutido = (
        "<script>if (window.self !== window.top) { "
        "document.getElementById('menu-cockpit').style.display = 'none'; }</script>"
    )
    return menu + script_embutido
