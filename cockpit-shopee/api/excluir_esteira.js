// Função serverless (Vercel) que remove um produto da esteira — usada
// pelo botão "Excluir" em esteira.html. Só permite excluir produto que
// ainda não foi publicado (etapa_conteudo !== 'publicado'); a checagem é
// feita aqui, no servidor, não só na tela, pra não perder o histórico de
// um produto que já virou conteúdo publicado.
//
// Precisa de GITHUB_TOKEN configurado como variável de ambiente na
// Vercel (mesma usada por api/selecionar.js).

const OWNER = "pcollichio";
const REPO = "AGENTE-SHOPEE";
const BRANCH = "claude/shopee-cockpit-connection-g3fqop";
const CAMINHO = "cockpit-shopee/esteira.json";

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
  const produtoId = String(corpo.produto_id || "");

  if (!produtoId) {
    res.status(400).json({ erro: "Informe produto_id." });
    return;
  }

  const apiBase = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${CAMINHO}`;
  const headers = {
    authorization: `Bearer ${token}`,
    accept: "application/vnd.github+json",
    "content-type": "application/json",
    "user-agent": "cockpit-papai-resolve",
  };

  try {
    const respostaAtual = await fetch(`${apiBase}?ref=${BRANCH}`, { headers });
    if (!respostaAtual.ok) {
      const detalhe = await respostaAtual.text();
      res.status(502).json({ erro: "Falha ao ler a esteira atual no GitHub.", detalhe });
      return;
    }
    const atual = await respostaAtual.json();
    let esteira = [];
    try {
      esteira = JSON.parse(Buffer.from(atual.content, "base64").toString("utf-8"));
      if (!Array.isArray(esteira)) esteira = [];
    } catch {
      esteira = [];
    }

    const item = esteira.find((e) => e.produto_id === produtoId);
    if (!item) {
      res.status(404).json({ erro: "Produto não encontrado na esteira." });
      return;
    }
    if (item.etapa_conteudo === "publicado") {
      res.status(403).json({ erro: "Esse produto já foi publicado — não dá pra excluir da esteira." });
      return;
    }

    const esteiraNova = esteira.filter((e) => e.produto_id !== produtoId);

    const conteudoBase64 = Buffer.from(JSON.stringify(esteiraNova, null, 2), "utf-8").toString("base64");
    const respostaPut = await fetch(apiBase, {
      method: "PUT",
      headers,
      body: JSON.stringify({
        message: `Remove produto da esteira (${produtoId})`,
        content: conteudoBase64,
        branch: BRANCH,
        sha: atual.sha,
      }),
    });

    if (!respostaPut.ok) {
      const detalhe = await respostaPut.text();
      res.status(502).json({ erro: "Falha ao salvar no GitHub.", detalhe });
      return;
    }

    res.status(200).json({ ok: true });
  } catch (erro) {
    res.status(500).json({ erro: "Erro interno.", detalhe: String(erro) });
  }
};
