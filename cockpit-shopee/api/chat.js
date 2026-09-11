// Função serverless (Vercel) que dá vida ao chat no index.html.
// Recebe o histórico de mensagens do navegador, busca os dados reais
// (leva do dia + resumo financeiro, direto do GitHub) e repassa
// tudo pra API da Anthropic com um prompt de sistema fixo em português.
//
// A chave da Anthropic vem só de process.env.ANTHROPIC_API_KEY — configure
// como variável de ambiente no Vercel, nunca deixe o valor neste arquivo.

// BUG real corrigido em 11/09: apontava pra "main", branch que não existe
// neste repositório (só existe claude/shopee-cockpit-connection-g3fqop) —
// todo fetch aqui sempre falhava (404, silenciado pelo try/catch em
// buscarTexto), então o chat nunca via a leva/resumo/perfil de verdade,
// só o texto de fallback "ainda não há dados". Mesma branch usada por
// api/selecionar.js e api/atualizar_esteira.js pra escrever.
const OWNER = "pcollichio";
const REPO = "AGENTE-SHOPEE";
const BRANCH = "claude/shopee-cockpit-connection-g3fqop";
const RAW_BASE = `https://raw.githubusercontent.com/${OWNER}/${REPO}/${BRANCH}/cockpit-shopee`;

async function buscarTexto(caminho) {
  try {
    const resposta = await fetch(`${RAW_BASE}/${caminho}`);
    if (!resposta.ok) return null;
    return await resposta.text();
  } catch {
    return null;
  }
}

const CAMINHO_PERFIL = "cockpit-shopee/perfil_afiliado.json";

// Base de conhecimento fixa sobre o que funciona pra afiliado Shopee em
// 2026 (pesquisa feita em 11/09, cruzada com a política oficial da
// Shopee) — usada pra montar o plano de ação, depois de
// reunir o perfil. Não é lista de produto (seria só orientação de
// canal/estratégia), então não fere a regra de nunca listar produto em
// texto no chat.
const PLAYBOOK_ESTRATEGIA = `
### Base de conhecimento: o que funciona pra afiliado Shopee (pesquisa 11/09)

**Janela de atribuição de 7 dias (pilar central da estratégia):** quando
alguém clica no link do afiliado, TODA compra que essa pessoa fizer na
Shopee nos 7 dias seguintes gera comissão pra esse afiliado — mesmo que
compre um produto diferente do que foi divulgado (atribuição por último
clique, confirmado na Central de Ajuda oficial da Shopee). Isso muda a
lógica de conteúdo: o produto divulgado é só a porta de entrada, o que
importa é maximizar CLIQUES recorrentes da mesma pessoa. Por isso vale
ter dois tipos de produto na curadoria: os de comissão alta (quando a
venda for exatamente aquele item) e "iscas" baratas/curiosas de clique
fácil (só pra reabrir a janela de 7 dias com o máximo de gente).

**Canais, por ordem de prioridade pra quem está construindo do zero:**
1. WhatsApp (lista de transmissão ou grupo temático de 200-500
   contatos engajados) — o canal mais citado como eficiente pra
   explorar a janela de 7 dias: envio diário/frequente de achadinhos
   pros mesmos contatos, alta recorrência de clique.
2. Reels/TikTok (topo de funil) — vídeo curto de 15-60s mostrando o
   produto na prática, constância de pelo menos 1 post/dia; público
   de 18-35 anos majoritariamente feminino, bom encaixe com
   beleza/moda. Já é o formato que o Agente Shopee automatiza (roteiro +
   legenda prontos por produto).
3. Shopee Live (amplificador, exige aparecer e ter alguma audiência
   prévia) — comissão de 3% nas vendas da live, podendo chegar a 30%
   em produtos de parceiros selecionados; usa uma "Sacola Laranja" de
   15-30 produtos por transmissão.
4. Tráfego pago (só com orçamento e seguindo a política da Shopee à
   risca) — PROIBIDO anúncio pago em busca (Google/Bing Ads); anúncio
   em Meta/TikTok/Pinterest só pode sair da conta/página comercial
   cadastrada no programa de afiliados (nunca perfil pessoal), sem
   logo/marca da Shopee no criativo, e nunca linkando direto pra
   Shopee num anúncio de busca paga — o formato seguro já em uso aqui
   é impulsionar o post do Instagram (sem link direto da Shopee no
   anúncio).

**Categorias com maior comissão média:** beleza/skincare (até 30%),
moda feminina (15-25%) — bom encaixe com o público majoritário do
WhatsApp/TikTok pra afiliado (mulheres, 18-35 anos). Produtos com menos
de 100 avaliações convertem mal por falta de prova social; frete
grátis converte melhor (comissão é só sobre o valor do produto, sem
frete).

Use esse conhecimento pra montar o plano de ação SÓ depois de ter o
perfil do afiliado (ver seção de perfil abaixo) — o plano tem que ser
calibrado pra realidade da pessoa, não genérico.
`;

const FERRAMENTA_SALVAR_PERFIL = {
  name: "salvar_perfil_afiliado",
  description:
    "Salva ou atualiza o perfil estratégico do afiliado (audiência atual, " +
    "orçamento pra tráfego pago, disposição pra aparecer em vídeo/live, " +
    "foco de nicho preferido) e o plano de ação personalizado. Chame só " +
    "depois de já ter reunido as respostas na conversa — pode chamar de " +
    "novo, mais tarde, só com os campos que mudaram (atualização parcial).",
  input_schema: {
    type: "object",
    properties: {
      audiencia_atual: {
        type: "string",
        enum: ["zero", "pequena", "estabelecida"],
        description: "Tamanho da audiência/contatos que o afiliado já tem hoje pra começar a distribuir conteúdo.",
      },
      orcamento_trafego_pago: {
        type: "string",
        enum: ["zero", "ate_150", "300_mais"],
        description: "Orçamento mensal disponível pra tráfego pago (impulsionar posts/anúncios).",
      },
      topa_aparecer_em_video: {
        type: "boolean",
        description: "Se o afiliado topa aparecer em vídeo/câmera, inclusive Shopee Live.",
      },
      foco_nicho: {
        type: "string",
        enum: ["beleza_moda", "amplo_com_peso", "amplo_sem_vies"],
        description: "Preferência de foco de segmento de produto na curadoria.",
      },
      plano_acao: {
        type: "string",
        description:
          "O plano de ação personalizado e resumido (canais priorizados, cadência de postagem, " +
          "próximos passos concretos) que você montou a partir das respostas — texto em markdown " +
          "simples, curto o bastante pra reler rápido numa próxima conversa.",
      },
    },
  },
};

async function montarContexto() {
  const [leva, resumoTexto, perfilTexto] = await Promise.all([
    buscarTexto("leva_do_dia.md"),
    buscarTexto("financeiro/resumo.json"),
    buscarTexto("perfil_afiliado.json"),
  ]);

  let resumo = null;
  if (resumoTexto) {
    try {
      resumo = JSON.parse(resumoTexto);
    } catch {
      resumo = null;
    }
  }

  let perfil = null;
  if (perfilTexto) {
    try {
      perfil = JSON.parse(perfilTexto);
    } catch {
      perfil = null;
    }
  }

  const partes = [];
  partes.push(
    "Você é o Agente Shopee, ajudando a pessoa a divulgar produtos de " +
    "afiliado da Shopee — a leva traz os mais vendidos da Shopee em " +
    "geral (não é mais restrita a um nicho), via Reels no " +
    "Instagram/TikTok, com roteiro e legenda gerados automaticamente.\n\n" +
    "Meta do North Star: R$10.000 de comissão por mês, com ROI mínimo de 3x " +
    "(cada R$1 investido em impulsionamento deve voltar pelo menos R$3 em " +
    "comissão).\n\n" +
    "Seja direto, prático e simples — a pessoa não é técnica, então evite " +
    "jargão e não enrole. Responda sempre com base nos dados reais abaixo, " +
    "nunca invente números. Quando fizer sentido, aponte pra aba certa " +
    "(Produtos, Importar ou ROI) pra próxima ação."
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

  partes.push(PLAYBOOK_ESTRATEGIA);

  if (perfil && (perfil.audiencia_atual || perfil.orcamento_trafego_pago || perfil.plano_acao)) {
    partes.push(
      "### Perfil estratégico do afiliado (já coletado)\n\n" +
      JSON.stringify(perfil, null, 2) +
      "\n\nJá temos esse perfil — não peça essas informações de novo. Se o " +
      "afiliado perguntar 'o que eu faço agora' ou pedir o plano, use o " +
      "`plano_acao` já salvo (ou refine ele, se fizer sentido pela conversa) " +
      "em vez de recomeçar do zero."
    );
  } else {
    partes.push(
      "### Perfil estratégico do afiliado (ainda não coletado)\n\n" +
      "Ainda não sabemos: (1) audiência/contatos atuais (zero, pequena ou " +
      "estabelecida), (2) orçamento mensal pra tráfego pago (zero, até " +
      "R$150, ou R$300+), (3) se topa aparecer em vídeo/câmera/Shopee Live, " +
      "(4) preferência de foco de nicho (beleza/moda, amplo com peso nesses, " +
      "ou 100% amplo). Se o afiliado pedir um 'plano', 'o que eu faço', ou " +
      "algo parecido com estratégia de crescimento, faça essas 4 perguntas " +
      "UMA DE CADA VEZ, num tom de conversa natural (não uma lista fria) — " +
      "espere a resposta antes de passar pra próxima. Depois de ter as 4 " +
      "respostas, monte um plano de ação curto e concreto usando a base de " +
      "conhecimento acima, calibrado pra essa pessoa específica, e chame a " +
      "ferramenta `salvar_perfil_afiliado` pra guardar tudo (perfil + plano) " +
      "antes de apresentar o plano na resposta."
    );
  }

  return partes.join("\n\n");
}

async function salvarPerfil(campos) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    return { ok: false, erro: "GITHUB_TOKEN não configurado no servidor." };
  }

  const apiBase = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${CAMINHO_PERFIL}`;
  const headers = {
    authorization: `Bearer ${token}`,
    accept: "application/vnd.github+json",
    "content-type": "application/json",
    "user-agent": "agente-shopee",
  };

  try {
    let sha;
    let perfil = {};
    const respostaAtual = await fetch(`${apiBase}?ref=${BRANCH}`, { headers });
    if (respostaAtual.ok) {
      const atual = await respostaAtual.json();
      sha = atual.sha;
      try {
        perfil = JSON.parse(Buffer.from(atual.content, "base64").toString("utf-8"));
        if (!perfil || typeof perfil !== "object" || Array.isArray(perfil)) perfil = {};
      } catch {
        perfil = {};
      }
    } else if (respostaAtual.status !== 404) {
      const detalhe = await respostaAtual.text();
      return { ok: false, erro: `Falha ao ler o perfil atual no GitHub: ${detalhe}` };
    }

    const CAMPOS_VALIDOS = [
      "audiencia_atual",
      "orcamento_trafego_pago",
      "topa_aparecer_em_video",
      "foco_nicho",
      "plano_acao",
    ];
    CAMPOS_VALIDOS.forEach((campo) => {
      if (campos[campo] !== undefined) perfil[campo] = campos[campo];
    });
    perfil.atualizado_em = new Date().toISOString();

    const conteudoBase64 = Buffer.from(JSON.stringify(perfil, null, 2), "utf-8").toString("base64");
    const respostaPut = await fetch(apiBase, {
      method: "PUT",
      headers,
      body: JSON.stringify({
        message: "Atualiza o perfil estratégico do afiliado",
        content: conteudoBase64,
        branch: BRANCH,
        sha,
      }),
    });

    if (!respostaPut.ok) {
      const detalhe = await respostaPut.text();
      return { ok: false, erro: `Falha ao salvar o perfil no GitHub: ${detalhe}` };
    }

    return { ok: true, perfil };
  } catch (erro) {
    return { ok: false, erro: String(erro) };
  }
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
    const historico = mensagensValidas.slice();

    // Loop de tool use: o modelo pode chamar salvar_perfil_afiliado depois
    // de reunir as respostas na conversa. No máximo algumas idas e voltas —
    // o comportamento esperado é chamar a ferramenta uma ou duas vezes por
    // turno (perfil + eventual ajuste do plano).
    let texto = "";
    for (let volta = 0; volta < 4; volta++) {
      const respostaAnthropic = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": apiKey,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model: "claude-haiku-4-5",
          max_tokens: 1536,
          system: systemPrompt,
          messages: historico,
          tools: [FERRAMENTA_SALVAR_PERFIL],
        }),
      });

      if (!respostaAnthropic.ok) {
        const detalhe = await respostaAnthropic.text();
        res.status(502).json({ erro: "Falha ao falar com a API da Anthropic.", detalhe });
        return;
      }

      const dados = await respostaAnthropic.json();
      const blocos = dados.content || [];
      texto = blocos
        .filter((bloco) => bloco.type === "text")
        .map((bloco) => bloco.text)
        .join("\n");

      const chamadasDeFerramenta = blocos.filter((bloco) => bloco.type === "tool_use");
      if (dados.stop_reason !== "tool_use" || chamadasDeFerramenta.length === 0) {
        break;
      }

      historico.push({ role: "assistant", content: blocos });

      const resultados = [];
      for (const chamada of chamadasDeFerramenta) {
        if (chamada.name === "salvar_perfil_afiliado") {
          const resultado = await salvarPerfil(chamada.input || {});
          resultados.push({
            type: "tool_result",
            tool_use_id: chamada.id,
            content: resultado.ok
              ? "Perfil salvo com sucesso."
              : `Não consegui salvar o perfil: ${resultado.erro}`,
            is_error: !resultado.ok,
          });
        } else {
          resultados.push({
            type: "tool_result",
            tool_use_id: chamada.id,
            content: "Ferramenta desconhecida.",
            is_error: true,
          });
        }
      }
      historico.push({ role: "user", content: resultados });
    }

    res.status(200).json({ resposta: texto });
  } catch (erro) {
    res.status(500).json({ erro: "Erro interno.", detalhe: String(erro) });
  }
};
