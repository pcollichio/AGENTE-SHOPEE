# Histórico do projeto — Cockpit Papai Resolve

Log cronológico de decisões e marcos, mantido pelo Claude. Toda sessão
nova deve ler isto (junto com `CLAUDE.md`) antes de agir.

## 2026-08-25 a 2026-08-28 — Fundação

- Integração real com a Shopee Affiliate API (GraphQL) validada —
  `productOfferV2` funciona, traz produtos reais com foto, preço,
  comissão, avaliação e link de afiliado.
- Curadoria diária automática: busca por palavra-chave (sem categoria
  oficial "casa & construção" na API), filtro de comissão mínima +
  avaliação mínima, distribuição em 20 produtos entre ticket
  baixo/médio/alto. Refinada com `produtos_excluir.txt` (tira produtos
  fora do nicho) e `produtos_manuais.txt` (garante produtos específicos).
- Automação diária via GitHub Actions (`leva-diaria.yml`), 9h de
  Brasília, credenciais em Secrets do repositório.
- Painel visual (`painel.html`) com seleção por checkbox e exportação
  da esteira (roteiro pronto, estilo Papai Resolve) em Markdown.
- Identidade visual (logo, paleta, exemplo de Reels) publicada como
  Claude Design.

## 2026-08-29 — ROI e sincronização de vendas

- Painel de ROI (`painel_roi.html`) com progresso da meta mensal
  (R$10.000) e ROI por produto (meta 3x), a partir de
  `financeiro/investimentos.csv` e `financeiro/vendas.csv`.
- **Tentativa de sincronizar vendas automaticamente via API
  (`conversionReport`) — abandonada.** Depois de 3 rodadas de debug
  real contra a API (tipo `Int64` precisa ser string, campo é
  `conversionStatus` não `orderStatus`, erro genérico "wrong type"
  sem mais detalhe), o usuário decidiu parar e manter o financeiro
  100% manual/importado. `sincronizar_vendas.py` fica só como
  histórico/experimento, não faz parte do fluxo.
- `index.html` virou o "cockpit central" com um agente coach real
  (`coach.py`): calcula recomendações do dia a partir dos dados reais
  (financeiro desatualizado, ritmo da meta, ROI crítico), com checklist
  que persiste no localStorage.
- Menu de navegação compartilhado (`nav.py`) em todas as páginas.

## 2026-08-30 — Consolidação, chat, e pivô pro "agente dentro do Claude"

- `cockpit.html`: entrada única com abas (iframe). Descoberto e
  documentado um bug real do Chrome — iframe de `file://` bloqueia
  navegação entre abas; resolvido publicando via GitHub Pages (HTTPS).
- GitHub Pages ativado com sucesso:
  `https://pcollichio.github.io/AGENTE-SHOPEE/cockpit-shopee/cockpit.html`
  — confirmado funcionando pelo usuário.
- Fotos de produto adicionadas ao `painel.html` (usuário pediu — "não
  dá pra pegar só com o título").
- **Construído e depois pausado**: chat de verdade (`chat.html` +
  `api/chat.js`, função serverless na Vercel chamando a API da
  Anthropic) e busca de produto específico no site (`api/buscar_produto.py`,
  Python na Vercel, reaproveitando `client.py`). Ambos continuam no
  repositório, prontos, mas **não são o modo de operação atual** — ver
  decisão abaixo.
- Testado um "banco de produtos aleatórios" pré-gerado
  (`produtos_pool.json`) — **removido a pedido do usuário**: a ideia
  certa era buscar ao vivo na API, não sortear de um banco estático.
  Virou a busca ao vivo acima.
- **Decisão final do dia**: o usuário perguntou "pra que a Vercel se eu
  já tenho o Claude?" — decisão foi usar **o Claude como o agente do
  MVP**, não o chat do site. Testado e confirmado: esta sessão do
  Claude não acessa a API da Shopee diretamente (proxy de rede
  bloqueia), então foi criado `buscar_um_produto.py` +
  `.github/workflows/busca-manual.yml` — um workflow disparável sob
  demanda (`workflow_dispatch` com input `termo`) que roda com acesso
  real à internet do GitHub Actions. O Claude dispara esse workflow e
  lê o resultado nos logs quando o usuário pede pra buscar algo.
  Testado ao vivo com sucesso ("torneira de cozinha" trouxe resultados
  reais).
- README reorganizado: a seção "Como usar agora" (o agente dentro do
  Claude) vira a principal; a Vercel vira seção opcional.
- Confirmado o modelo operacional definitivo (ver `CLAUDE.md`): chat
  aqui com o Claude, visual/interativo no `painel.html` arquivado no
  GitHub, Claude mantém o histórico neste arquivo.
- Testando o fluxo de seleção de produtos: usuário pediu pra ver fotos
  no meio da conversa — confirmado que a sessão do Claude não carrega
  imagens externas (mesma restrição de rede), então a seleção visual
  fica no `painel.html` mesmo; o Claude aponta o link e resume os
  dados em texto/tabela.
- **Critério de curadoria endurecido**: usuário pediu produtos
  "validados" — comissão boa, nota boa e volume de vendas alto, não
  mais aposta sem histórico. Adicionado `VENDIDOS_MINIMO` como filtro
  em `montar_leva_variada()` (`buscar_leva_lancamento.py`), e a leva
  do dia caiu de 20 pra **10 produtos** (`QUANTIDADE_TOTAL = 10`),
  ainda distribuídos entre ticket baixo/médio/alto.
  **Calibração com dados reais**: 150 vendas deixava só 1 produto no
  catálogo do dia (de 347 encontrados, só 111 tinham nota ≥4.5, e só 1
  cruzava 150 vendas). Diagnóstico temporário confirmou com o usuário:
  **`VENDIDOS_MINIMO = 50`** é o valor final — ainda validado, mas com
  candidato suficiente pra preencher as 3 faixas de preço. Também
  aumentado `limite` da busca por palavra-chave de 20 pra 50, pra ter
  mais candidatos antes do filtro. Teste real com esse valor trouxe 9
  de 10 produtos, bem distribuídos — um item (porta aliança de
  casamento) escapou do nicho, sinal de que `produtos_excluir.txt`
  precisa de um ajuste fino nesse tipo de item.
- **Regra explícita: nunca listar a relação de produtos em texto/tabela
  no chat.** O usuário pediu — sempre que quiser ver os produtos (leva,
  busca, etc.), a resposta do Claude é o link do `painel.html`, nunca
  uma lista item a item aqui. Comentários pontuais sobre destaques
  específicos continuam ok. Registrado em `CLAUDE.md`.
- Usuário pediu roteiro + vídeo sem marca d'água de um produto: roteiro
  eu gero, vídeo eu recusei (não tenho como baixar mídia externa, e
  tirar marca d'água de conteúdo do vendedor não é algo que devo
  fazer) — expliquei o fluxo real (CapCut com mídia oficial + roteiro).
- Usuário pediu "um agente que saiba o que selecionei e me guie" —
  ficou claro que não existia conexão nenhuma entre o clique no painel
  e o Claude. Propus duas opções (GitHub Issues sem Vercel, ou Vercel
  com sync instantâneo) — **usuário escolheu Vercel**.
- **Vercel confirmada como parte do stack.** Construído
  `api/selecionar.js`: o botão "Salvar seleção agora" no painel
  (novo, ao lado do botão de baixar) grava a seleção instantaneamente
  em `selecao_atual.json` via GitHub Contents API (usa um
  `GITHUB_TOKEN` — Personal Access Token fine-grained, só deste
  repositório, permissão Contents: Read and write — configurado como
  variável de ambiente na Vercel, nunca no código). O Claude passa a
  ler esse arquivo pra saber o que foi selecionado, sem precisar que o
  usuário digite de novo. README atualizado com o passo a passo de
  criar o token. Pendente: usuário ainda precisa fazer o deploy na
  Vercel e configurar as variáveis de ambiente (ANTHROPIC_API_KEY,
  SHOPEE_APP_ID, SHOPEE_APP_SECRET, USE_MOCK_DATA=false, GITHUB_TOKEN).
