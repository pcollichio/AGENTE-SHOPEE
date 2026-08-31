// Função serverless (Vercel) que recebe um arquivo (relatório de vendas
// da Shopee, extrato/print do Meta Ads, etc.) enviado pelo importar.html
// e grava direto no GitHub, em cockpit-shopee/financeiro/importados/ —
// não processa o conteúdo (formatos variam demais pra confiar num
// parser automático); o Claude lê e converte pros CSVs de
// investimentos/vendas quando avisado.
//
// Precisa de GITHUB_TOKEN configurado como variável de ambiente na
// Vercel (mesma usada por api/selecionar.js).

const OWNER = "pcollichio";
const REPO = "AGENTE-SHOPEE";
const BRANCH = "claude/shopee-cockpit-connection-g3fqop";
const PASTA = "cockpit-shopee/financeiro/importados";

// Limite prático: a Vercel (plano gratuito) recusa requisições com corpo
// acima de ~4.5MB, então mantemos uma margem de segurança.
const LIMITE_BASE64 = 4 * 1024 * 1024;

function sanitizarNomeArquivo(nome) {
  return String(nome || "arquivo").replace(/[^a-zA-Z0-9._-]/g, "_").slice(0, 120);
}

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
  const tipo = String(corpo.tipo || "arquivo").replace(/[^a-z_]/g, "").slice(0, 40) || "arquivo";
  const nomeArquivo = sanitizarNomeArquivo(corpo.nome_arquivo);
  const conteudoBase64 = corpo.conteudo_base64;

  if (!conteudoBase64) {
    res.status(400).json({ erro: "Nenhum arquivo recebido." });
    return;
  }

  if (conteudoBase64.length > LIMITE_BASE64) {
    res.status(400).json({
      erro: "Arquivo grande demais pra esse envio (limite ~3MB). Tente exportar em CSV, "
        + "que costuma ser bem menor que XLSX/PDF/print.",
    });
    return;
  }

  const agora = new Date().toISOString().replace(/[:.]/g, "-");
  const caminho = `${PASTA}/${agora}-${tipo}-${nomeArquivo}`;
  const apiBase = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${caminho}`;

  try {
    const respostaPut = await fetch(apiBase, {
      method: "PUT",
      headers: {
        authorization: `Bearer ${token}`,
        accept: "application/vnd.github+json",
        "content-type": "application/json",
        "user-agent": "cockpit-papai-resolve",
      },
      body: JSON.stringify({
        message: `Importa arquivo (${tipo}): ${nomeArquivo}`,
        content: conteudoBase64,
        branch: BRANCH,
      }),
    });

    if (!respostaPut.ok) {
      const detalhe = await respostaPut.text();
      res.status(502).json({ erro: "Falha ao salvar o arquivo no GitHub.", detalhe });
      return;
    }

    res.status(200).json({ ok: true, caminho });
  } catch (erro) {
    res.status(500).json({ erro: "Erro interno.", detalhe: String(erro) });
  }
};

module.exports.config = {
  api: { bodyParser: { sizeLimit: "4mb" } },
};
