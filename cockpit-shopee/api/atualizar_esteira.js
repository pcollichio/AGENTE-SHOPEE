// Função serverless (Vercel) que atualiza a etapa de conteúdo
// (roteiro pronto / em produção / publicado) de um produto na esteira,
// direto no GitHub — usada pelo seletor em esteira.html.
//
// Precisa de GITHUB_TOKEN configurado como variável de ambiente na
// Vercel (mesma usada por api/selecionar.js).

const OWNER = "pcollichio";
const REPO = "AGENTE-SHOPEE";
const BRANCH = "claude/shopee-cockpit-connection-g3fqop";
const CAMINHO = "cockpit-shopee/esteira.json";

const ETAPAS_VALIDAS = ["roteiro_pronto", "em_producao", "publicado"];

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
  const etapa = String(corpo.etapa_conteudo || "");

  if (!produtoId || !ETAPAS_VALIDAS.includes(etapa)) {
    res.status(400).json({ erro: "Informe produto_id e uma etapa_conteudo válida." });
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

    var encontrado = false;
    esteira.forEach((item) => {
      if (item.produto_id === produtoId) {
        item.etapa_conteudo = etapa;
        encontrado = true;
      }
    });

    if (!encontrado) {
      res.status(404).json({ erro: "Produto não encontrado na esteira." });
      return;
    }

    const conteudoBase64 = Buffer.from(JSON.stringify(esteira, null, 2), "utf-8").toString("base64");
    const respostaPut = await fetch(apiBase, {
      method: "PUT",
      headers,
      body: JSON.stringify({
        message: `Atualiza etapa de conteúdo (${produtoId} -> ${etapa})`,
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
