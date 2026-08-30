// Função serverless (Vercel) que dá vida ao chat do coach no index.html.
// Recebe o histórico de mensagens do navegador, busca os dados reais do
// cockpit (leva do dia + resumo financeiro, direto do GitHub) e repassa
// tudo pra API da Anthropic com um prompt de sistema fixo em português.
//
// A chave da Anthropic vem só de process.env.ANTHROPIC_API_KEY — configure
// como variável de ambiente no Vercel, nunca deixe o valor neste arquivo.

const RAW_BASE = "https://raw.githubusercontent.com/pcollichio/AGENTE-SHOPEE/main/cockpit-shopee";

async function buscarTexto(caminho) {
  try {
    const resposta = await fetch(`${RAW_BASE}/${caminho}`);
    if (!resposta.ok) return null;
    return await resposta.text();
  } catch {
    return null;
  }
}

async function montarContexto() {
  const [leva, resumoTexto] = await Promise.all([
    buscarTexto("leva_do_dia.md"),
    buscarTexto("financeiro/resumo.json"),
  ]);

  let resumo = null;
  if (resumoTexto) {
    try {
      resumo = JSON.parse(resumoTexto);
    } catch {
      resumo = null;
    }
  }

  const partes = [];
  partes.push(
    "Você é o coach do 'Cockpit de Afiliação IA-First', ajudando a pessoa " +
    "por trás da marca @papairesolve_br (Papai Resolve) a divulgar produtos " +
    "de afiliado da Shopee no nicho casa e construção, via Reels no " +
    "Instagram/TikTok.\n\n" +
    "Meta do North Star: R$10.000 de comissão por mês, com ROI mínimo de 3x " +
    "(cada R$1 investido em impulsionamento deve voltar pelo menos R$3 em " +
    "comissão).\n\n" +
    "Seu papel é guiar, passo a passo, num tom direto, prático e encorajador " +
    "em português do Brasil — a pessoa não é técnica, então evite jargão. " +
    "Responda sempre com base nos dados reais abaixo, nunca invente números. " +
    "Quando fizer sentido, aponte pra aba certa do cockpit (Produtos, " +
    "Importar ou ROI) pra próxima ação."
  );

  if (leva) {
    partes.push("### Produtos selecionados para hoje\n\n" + leva);
  } else {
    partes.push("### Produtos selecionados para hoje\n\n(ainda não há leva gerada hoje)");
  }

  if (resumo) {
    partes.push("### Resumo financeiro atual (JSON)\n\n" + JSON.stringify(resumo, null, 2));
  } else {
    partes.push("### Resumo financeiro atual\n\n(ainda não há dados financeiros registrados)");
  }

  return partes.join("\n\n");
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.status(405).json({ erro: "Use POST." });
    return;
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    res.status(500).json({ erro: "ANTHROPIC_API_KEY não configurada no servidor." });
    return;
  }

  const corpo = req.body || {};
  const mensagens = Array.isArray(corpo.mensagens) ? corpo.mensagens : [];

  if (mensagens.length === 0) {
    res.status(400).json({ erro: "Envie ao menos uma mensagem." });
    return;
  }

  const mensagensValidas = mensagens
    .filter((m) => m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string")
    .slice(-20);

  try {
    const systemPrompt = await montarContexto();

    const respostaAnthropic = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5",
        max_tokens: 1024,
        system: systemPrompt,
        messages: mensagensValidas,
      }),
    });

    if (!respostaAnthropic.ok) {
      const detalhe = await respostaAnthropic.text();
      res.status(502).json({ erro: "Falha ao falar com a API da Anthropic.", detalhe });
      return;
    }

    const dados = await respostaAnthropic.json();
    const texto = (dados.content || [])
      .filter((bloco) => bloco.type === "text")
      .map((bloco) => bloco.text)
      .join("\n");

    res.status(200).json({ resposta: texto });
  } catch (erro) {
    res.status(500).json({ erro: "Erro interno.", detalhe: String(erro) });
  }
};
