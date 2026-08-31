// Função serverless (Vercel) que dá vida ao botão "Salvar seleção agora"
// do painel.html: recebe os produtos marcados e grava na hora em
// cockpit-shopee/selecao_atual.json, direto no repositório do GitHub —
// mantém o modelo "tudo arquivado no GitHub" (nada de banco de dados
// separado) e dá ao Claude uma forma real de saber, na próxima
// conversa, o que foi selecionado.
//
// Precisa de GITHUB_TOKEN configurado como variável de ambiente na
// Vercel — um Personal Access Token com permissão de escrita de
// conteúdo (Contents: Read and write) só neste repositório.

const OWNER = "pcollichio";
const REPO = "AGENTE-SHOPEE";
const BRANCH = "claude/shopee-cockpit-connection-g3fqop";
const CAMINHO = "cockpit-shopee/selecao_atual.json";

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.status(405).json({ erro: "Use POST." });
    return;
  }

  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    res.status(500).json({ erro: "GITHUB_TOKEN não configurado no servidor." });
    return;
  }

  const corpo = req.body || {};
  const produtosRecebidos = Array.isArray(corpo.produtos) ? corpo.produtos : [];

  if (produtosRecebidos.length === 0) {
    res.status(400).json({ erro: "Nenhum produto selecionado." });
    return;
  }

  const dados = {
    salvo_em: new Date().toISOString(),
    produtos: produtosRecebidos.slice(0, 50).map((p) => ({
      nome: String(p.nome || "").slice(0, 300),
      preco: Number(p.preco) || 0,
      comissao: Number(p.comissao) || 0,
      link: String(p.link || "").slice(0, 500),
      categoria: String(p.categoria || "").slice(0, 60),
    })),
  };

  const apiBase = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${CAMINHO}`;
  const headers = {
    authorization: `Bearer ${token}`,
    accept: "application/vnd.github+json",
    "content-type": "application/json",
    "user-agent": "cockpit-papai-resolve",
  };

  try {
    let sha;
    const respostaAtual = await fetch(`${apiBase}?ref=${BRANCH}`, { headers });
    if (respostaAtual.ok) {
      const atual = await respostaAtual.json();
      sha = atual.sha;
    } else if (respostaAtual.status !== 404) {
      const detalhe = await respostaAtual.text();
      res.status(502).json({ erro: "Falha ao ler o arquivo atual no GitHub.", detalhe });
      return;
    }

    const conteudoBase64 = Buffer.from(JSON.stringify(dados, null, 2), "utf-8").toString("base64");

    const respostaPut = await fetch(apiBase, {
      method: "PUT",
      headers,
      body: JSON.stringify({
        message: `Seleção de produtos salva pelo painel (${dados.salvo_em})`,
        content: conteudoBase64,
        branch: BRANCH,
        sha,
      }),
    });

    if (!respostaPut.ok) {
      const detalhe = await respostaPut.text();
      res.status(502).json({ erro: "Falha ao salvar no GitHub.", detalhe });
      return;
    }

    res.status(200).json({ ok: true, quantidade: dados.produtos.length });
  } catch (erro) {
    res.status(500).json({ erro: "Erro interno.", detalhe: String(erro) });
  }
};
