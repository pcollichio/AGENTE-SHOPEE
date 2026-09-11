"""
Gera o chat.html — o chat de verdade com o Agente Shopee. A página é
estática (só HTML/CSS/JS), mas o JS conversa com api/chat.js (função
serverless na Vercel), que por sua vez chama a API da Anthropic com o
contexto real (leva do dia + resumo financeiro).
"""

from . import nav


def gerar_html():
    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agente Shopee</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
  :root, :root:not([data-theme="light"]), :root[data-theme="dark"] {{
    /* Identidade visual fixa laranja & branco (igual Shopee) — pedido
       do usuário em 10/09, não muda com o tema do sistema. */
    --bg: #ee4d2d; --on-bg: #ffffff; --on-bg-muted: #ffd9cc;
    --grid-line: rgba(255,255,255,0.12); --card: #ffffff;
    --text: #2a1a12; --muted: #8a6a5c; --border: #f3d0c2;
    --accent: #ee4d2d; --accent-ink: #c73e1f; --accent-soft: #fde8e0;
    --focus: #a8341a; --bolha-usuario: #ee4d2d; --bolha-coach: #fde8e0;
    --erro: #d03b3b; --erro-soft: #f8e2e2;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ height: 100%; }}
  body {{
    margin: 0; padding: 24px; height: 100%;
    background: var(--bg);
    color: var(--text); font-family: "IBM Plex Sans", system-ui, sans-serif;
    display: flex; flex-direction: column;
  }}
  .wrap {{ max-width: 760px; margin: 0 auto; width: 100%; display: flex; flex-direction: column;
    flex: 1; min-height: 0; }}
{nav.MENU_CSS}
  .cabecalho {{ display: flex; align-items: center; gap: 14px; margin-bottom: 18px; }}
  svg.logo {{ flex-shrink: 0; }}
  .cabecalho-texto .eyebrow {{ font-family: "IBM Plex Mono", monospace; font-size: 0.72rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--on-bg); margin: 0 0 4px; font-weight: 600; }}
  h1 {{ font-family: "Archivo", sans-serif; font-weight: 800; font-size: 1.4rem; margin: 0; color: var(--on-bg); }}

  .caixa-chat {{ flex: 1; min-height: 0; display: flex; flex-direction: column; background: var(--card);
    border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
  .mensagens {{ flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 14px; }}
  .msg {{ display: flex; }}
  .msg-coach {{ justify-content: flex-start; }}
  .msg-usuario {{ justify-content: flex-end; }}
  .bolha {{ max-width: 82%; padding: 10px 14px; border-radius: 12px; font-size: 0.92rem; line-height: 1.5;
    white-space: pre-wrap; }}
  .msg-coach .bolha {{ background: var(--bolha-coach); border: 1px solid var(--border); border-bottom-left-radius: 3px; }}
  .msg-usuario .bolha {{ background: var(--bolha-usuario); color: #fff; border-bottom-right-radius: 3px; }}
  .msg-erro .bolha {{ background: var(--erro-soft); color: var(--erro); border: 1px solid var(--erro); }}
  .msg-carregando .bolha {{ color: var(--muted); font-style: italic; }}

  .sugestoes {{ display: flex; gap: 8px; flex-wrap: wrap; padding: 0 20px 14px; }}
  .sugestao {{ font-family: "IBM Plex Sans", sans-serif; font-size: 0.8rem; font-weight: 600;
    color: var(--accent-ink); background: var(--accent-soft); border: none; border-radius: 999px;
    padding: 7px 14px; cursor: pointer; }}
  .sugestao:hover {{ opacity: 0.85; }}

  .form-msg {{ display: flex; gap: 10px; padding: 14px; border-top: 1px solid var(--border); }}
  .form-msg input {{ flex: 1; font-family: "IBM Plex Sans", sans-serif; font-size: 0.92rem; padding: 11px 14px;
    border-radius: 8px; border: 1px solid var(--border); background: #ffffff; color: var(--text); }}
  .form-msg input:focus {{ outline: 2px solid var(--focus); outline-offset: 1px; }}
  .form-msg button {{ font-family: "IBM Plex Sans", sans-serif; font-size: 0.9rem; font-weight: 700;
    color: #fff; background: var(--accent); border: none; border-radius: 8px; padding: 0 20px; cursor: pointer; }}
  .form-msg button:disabled {{ opacity: 0.5; cursor: not-allowed; }}

  .aviso-config {{ font-size: 0.8rem; color: var(--on-bg-muted); margin-top: 10px; font-family: "IBM Plex Mono", monospace; }}
</style>
</head>
<body>
  <div class="wrap">
    {nav.gerar_menu_html("chat.html")}

    <header class="cabecalho">
      <svg class="logo" width="36" height="36" viewBox="0 0 120 120" fill="none">
        <circle cx="60" cy="60" r="52" stroke="#ffffff" stroke-width="5"/>
        <path d="M38 62 L54 78 L86 40" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div class="cabecalho-texto">
        <p class="eyebrow">Agente Shopee</p>
        <h1>Agente</h1>
      </div>
    </header>

    <div class="caixa-chat">
      <div class="mensagens" id="mensagens">
        <div class="msg msg-coach">
          <div class="bolha">Oi! Posso te dizer o que fazer agora, explicar os números do ROI ou ajudar a decidir o próximo produto. O que você precisa?</div>
        </div>
      </div>
      <div class="sugestoes">
        <button class="sugestao" type="button" data-msg="O que eu faço agora?">O que eu faço agora?</button>
        <button class="sugestao" type="button" data-msg="Como está o ROI do mês?">Como está o ROI do mês?</button>
        <button class="sugestao" type="button" data-msg="Qual produto da leva de hoje eu escolho?">Qual produto escolher hoje?</button>
      </div>
      <form class="form-msg" id="form-msg">
        <input type="text" id="campo-msg" placeholder="Escreva sua pergunta..." autocomplete="off">
        <button type="submit" id="botao-enviar">Enviar</button>
      </form>
    </div>
    <p class="aviso-config" id="aviso-config" hidden>
      O chat ainda não está configurado neste servidor (falta a chave da Anthropic). Peça pra configurar
      a variável ANTHROPIC_API_KEY no Vercel.
    </p>
  </div>

  <script>
    (function () {{
      var historico = [];
      var lista = document.getElementById('mensagens');
      var form = document.getElementById('form-msg');
      var campo = document.getElementById('campo-msg');
      var botao = document.getElementById('botao-enviar');
      var avisoConfig = document.getElementById('aviso-config');

      function rolarParaFinal() {{
        lista.scrollTop = lista.scrollHeight;
      }}

      function adicionarBolha(texto, tipo) {{
        var div = document.createElement('div');
        div.className = 'msg msg-' + tipo;
        var bolha = document.createElement('div');
        bolha.className = 'bolha';
        bolha.textContent = texto;
        div.appendChild(bolha);
        lista.appendChild(div);
        rolarParaFinal();
        return div;
      }}

      async function enviar(texto) {{
        if (!texto.trim()) return;
        adicionarBolha(texto, 'usuario');
        historico.push({{ role: 'user', content: texto }});
        campo.value = '';
        botao.disabled = true;
        var carregando = adicionarBolha('Pensando...', 'carregando');

        try {{
          var resposta = await fetch('/api/chat', {{
            method: 'POST',
            headers: {{ 'content-type': 'application/json' }},
            body: JSON.stringify({{ mensagens: historico }}),
          }});
          var dados = await resposta.json();
          carregando.remove();

          if (!resposta.ok) {{
            if (resposta.status === 500 && dados.erro && dados.erro.indexOf('ANTHROPIC_API_KEY') !== -1) {{
              avisoConfig.hidden = false;
            }}
            adicionarBolha(dados.erro || 'Deu um erro ao responder.', 'erro');
            return;
          }}

          adicionarBolha(dados.resposta, 'coach');
          historico.push({{ role: 'assistant', content: dados.resposta }});
        }} catch (e) {{
          carregando.remove();
          adicionarBolha('Não consegui falar com o servidor do chat. Verifique sua conexão.', 'erro');
        }} finally {{
          botao.disabled = false;
          campo.focus();
        }}
      }}

      form.addEventListener('submit', function (ev) {{
        ev.preventDefault();
        enviar(campo.value);
      }});

      document.querySelectorAll('.sugestao').forEach(function (b) {{
        b.addEventListener('click', function () {{
          enviar(b.getAttribute('data-msg'));
        }});
      }});
    }})();
  </script>
</body>
</html>
"""


def salvar_painel(caminho="chat.html"):
    html = gerar_html()
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    return caminho
