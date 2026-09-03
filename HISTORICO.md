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
  criar o token.
- **Vercel ativada e testada em produção** (`agente-shopee.vercel.app`).
  Troubleshooting real: primeiro deploy deu 404 (Root Directory não
  configurado como `cockpit-shopee` — corrigido em Settings → General
  → Redeploy); GITHUB_TOKEN criado via fine-grained personal access
  token (usuário confundiu com "Deploy keys" na primeira tentativa —
  o caminho certo é github.com/settings/personal-access-tokens/new,
  configurações da conta, não do repositório).
- **5 melhorias pedidas pelo usuário** (lote de 31/08): (1) a leva não
  estava batendo a quantidade combinada; (2) processo alternativo de
  colar link de produto olhado no app; (3) precisa de um ambiente pra
  gerenciar a esteira (produtos selecionados → impulsionados →
  vendidos), com o chat dando apoio a toda decisão; (4) agenda de
  atividades mais simples; (5) layout pouco funcional, ideia de menu
  lateral + chat central (modelo Claude). Prioridade combinada: 3 → 5
  → 1 → 4 → 2.
- **Resolvido o item 1 (quantidade)**: usuário decidiu não fixar mais
  um número — `montar_leva_variada()` agora devolve TODOS os produtos
  que passam no filtro de comissão + avaliação (sem piso de vendas,
  sem cap de quantidade nem distribuição forçada por tier). A seleção
  de quantos/quais usar fica inteiramente com o usuário, no painel
  (que já tem filtro por faixa de preço). `VENDIDOS_MINIMO` e
  `QUANTIDADE_TOTAL` removidos do código.
- **Resolvido o item 3 (ambiente de gestão da esteira)**: `esteira.json`
  deixou de ser sobrescrito a cada seleção — `api/selecionar.js` agora
  acrescenta (dedup por `produto_id`). Novo módulo
  `shopee_integration/esteira.py` gera `esteira.html`: lista todo
  produto já selecionado, com status calculado sozinho cruzando o nome
  do produto com `financeiro/investimentos.csv` e `vendas.csv`
  (comparação tolerante — um nome "contém" o outro, já que o campo do
  financeiro é digitado à mão) — selecionado → impulsionado (tem
  investimento) → vendido (tem comissão), com ROI por produto quando
  aplicável. Nova página no menu, novo script `gerar_esteira.py`
  integrado à automação diária.
- **Resolvido o item 5 (layout)**: `cockpit.html` redesenhado —
  antes era um menu horizontal em cima + iframe embaixo; agora é
  **menu lateral fixo à esquerda + área de conteúdo + painel de chat
  fixo à direita** (modelo Claude), com o chat sempre visível
  "apoiando em tudo", falando direto com `api/chat.js` sem precisar
  trocar de aba. Responsivo: no celular, o menu lateral vira uma barra
  horizontal no topo e o chat vira um botão flutuante que abre em tela
  cheia. Cada página (`painel.html`, `esteira.html` etc.) ainda tem seu
  próprio menu horizontal pra quando é aberta sozinha (fora do
  cockpit.html) — `nav.py` agora detecta se está dentro de um iframe
  (`window.self !== window.top`) e esconde esse menu duplicado nesse
  caso. Testado em desktop e mobile com Playwright.
- **Ajustes finos pedidos pelo usuário**: fundo quadriculado (grid de
  linhas) removido de todas as páginas — usuário achou ruim; agora é
  fundo liso (`var(--bg)`). Label "ROI" virou "Dashboard" no menu e no
  título/H1 de `painel_roi.html` (conteúdo interno continua chamando
  os números de ROI, só a marca da página mudou).
- **Resolvido o item 2 (colar link do produto)**: `buscar_um_produto.py`
  agora aceita link da Shopee além de nome — segue o link (inclusive
  link curto `s.shopee.com.br/...`), extrai o nome do produto do slug
  da URL e o itemId (quando o padrão `-i.<shopId>.<itemId>` aparece),
  busca por esse nome e prioriza o resultado com itemId exatamente
  igual, se achar.
- **Resolvido o item 4 (agenda simples)**: a seção "Como a esteira
  funciona, ponta a ponta" (8 passos com descrição longa) virou um
  `<details>` recolhido por padrão, com cada passo compactado numa
  linha (era um card grande com parágrafo). "O que fazer hoje" (a
  agenda de verdade) passa a ser o conteúdo dominante da página —
  o resto fica escondido atrás de um clique, disponível se precisar.

Com isso, os 5 itens pedidos em 31/08 estão todos resolvidos.

## 2026-08-31 (continuação) — bug real de uso + mais 3 pedidos

- **Bug real reportado pelo usuário**: produtos selecionados e
  baixados no painel não apareciam na esteira. Causa: existiam dois
  botões parecidos — "Salvar seleção agora" (chamava `/api/selecionar`)
  e "Baixar seleção para a esteira" (só baixava o arquivo .md, sem
  chamar a API) — o usuário usava o segundo, que nunca salvava de
  verdade. **Corrigido fundindo os dois num só**: "Baixar roteiro e
  salvar na esteira" agora baixa o arquivo E chama `/api/selecionar`
  ao mesmo tempo. Testado com Playwright confirmando as duas ações.
- **Upload de arquivo em `importar.html`**: novo campo (tipo + arquivo)
  que envia relatório de vendas da Shopee ou extrato/print do Meta Ads
  pro GitHub, em `financeiro/importados/`, via nova função serverless
  `api/importar_arquivo.js`. Não tenta parsear automaticamente (os
  formatos desses relatórios ainda não foram vistos de verdade) — o
  Claude lê e converte manualmente quando avisado. Limite prático de
  ~3MB por arquivo (limite de payload da Vercel no plano gratuito).
- **Dashboard ganhou mais indicadores**: além de investido/comissão/ROI
  médio, agora tem "Comissão média por venda" e uma seção nova, **Funil
  da esteira** (Selecionados / Impulsionados / Venderam / Taxa de
  conversão), lendo `esteira.json` cruzado com o financeiro — mesma
  lógica de `esteira.py`, reaproveitada. Testado com dados simulados
  (3 selecionados, 2 impulsionados, 1 vendeu → 50% conversão, valores
  batendo certinho no screenshot).
- **Novo padrão fixo de narração dos Reels**: usuário pediu — a partir
  de agora, todo roteiro é narrado em **voz de criança**, trazendo a
  dor de um problema de casa até o Papai resolver com o produto,
  fechando com call to action. Reescrito `GANCHOS_ROTEIRO` (as 13
  categorias, cada "problema" agora em 1ª pessoa/voz de criança) e a
  estrutura fixa de 5 blocos em `montarRoteiro()`
  (`shopee_integration/painel.py`): Dor → Agrava → Solução (o Papai
  acha o produto) → Prova (visual) → Call to action. Testado gerando
  um roteiro real (Torneira De Banheiro) e conferindo o texto baixado.
  Registrado como padrão em `CLAUDE.md`, pra valer também quando o
  usuário pedir um roteiro pontual no chat.

## 2026-09-01

- **Filtro de qualidade movido pro momento da seleção**: usuário pediu
  que todos os produtos do nicho casa & construção venham pro painel,
  sem cortar por comissão/avaliação antes — o filtro deve acontecer na
  hora de escolher. Removido o filtro de `montar_leva_variada()` e do
  `min_comissao` passado à API (só resta o filtro de nicho, via
  `produtos_excluir.txt`). Painel ganha dois seletores (Comissão
  mínima / Avaliação mínima) que combinam com o filtro de faixa de
  preço já existente, tudo em tempo real via JS. Testado com
  Playwright confirmando a combinação dos três filtros.
- **Pedido: processo de criação e publicação dos Reels.** Resposta
  honesta dada ao usuário: gerar o vídeo de verdade (voz sintética,
  edição) e publicar automaticamente no Instagram/TikTok não são coisas
  que o Claude consegue fazer aqui — faltam ferramenta de vídeo/voz e
  uma integração com a API da Meta/TikTok (que exige aprovação e conta
  comercial verificada, fora do escopo atual). O que foi construído em
  vez disso: a esteira ganhou uma **etapa de conteúdo** paralela ao
  status financeiro — Roteiro pronto (padrão) → Em produção →
  Publicado — atualizada manualmente por um seletor em cada linha
  (`api/atualizar_esteira.js`, novo, salva no GitHub). `esteira.html`
  também ganhou um guia claro dos 5 passos do processo (roteiro →
  narração IA → edição no CapCut → publicar → marcar como publicado),
  deixando explícito quais passos são manuais. Testado com Playwright
  (mudança de etapa envia a chamada certa e atualiza a cor na hora).
- **Pipeline criar → publicar → avaliar: textos prontos + exclusão na
  esteira.** Complemento do item acima, a pedido do usuário: (1) fixado
  o **padrão de legenda** (novo `montarLegenda()` em `painel.py`, ao
  lado de `montarRoteiro()`) — dor com emoji 😩, solução citando o
  produto com emoji ✅, call to action com emoji 🛒, hashtags fixas
  (`#papairesolve #casaeconstrucao #achadosdashopee #dicasdecasa
  #paisdeplantao`); documentado em `CLAUDE.md` junto do padrão de
  narração. (2) O botão de salvar no painel agora manda `narracao` e
  `legenda` prontas junto com cada produto, e `api/selecionar.js`
  grava esses dois campos em `esteira.json`. (3) `esteira.html` mostra
  os textos por produto num "Ver textos" com botão de copiar
  (`navigator.clipboard`), e ganhou um botão **Excluir** por produto —
  só funciona se o produto ainda não estiver com etapa "Publicado"; a
  checagem é feita no servidor (`api/excluir_esteira.js`, novo), não só
  na tela, pra não perder histórico de conteúdo já publicado. (4) O
  guia do processo ganhou um 6º passo, "Avaliar o resultado", fechando
  o ciclo com o Dashboard/ROI. Testado com Playwright: copiar pra
  clipboard funciona, botão excluir vem desabilitado num produto
  "publicado" e habilitado num "roteiro_pronto", e excluir remove a
  linha da tabela na hora.
- **Voz do roteiro ajustada: de criança pra jovem, com abertura fixa.**
  Usuário pediu — a narração deixa de ser em voz de criança e passa a
  ser em **voz de jovem** (nem criança, nem adolescente), sempre abrindo
  com a frase fixa "Meu papai sempre resolve tudo aqui em casa!", depois
  a dor do problema, a solução com o produto e o call to action.
  Reescrito `montarRoteiro()` (5 blocos: Abertura → Dor → Solução →
  Prova → CTA, removido o antigo bloco "Agrava") e `montarLegenda()`
  (mesma abertura fixa antes da dor) em `painel.py`; removida diminutivos
  e dição infantil de `GANCHOS_ROTEIRO` (ex: "brinquedos" → "minhas
  coisas", "chinelo" → "chão todo", "probleminha" → "problema").
  Atualizado texto do guia em `esteira.html` e do passo "Texto e
  roteiro" em `painel_index.py` (Problema→Agrava→Solução→Prova→Oferta
  virou Abertura→Dor→Solução→Prova→CTA). Registrado o novo padrão em
  `CLAUDE.md`.

## 2026-09-02

- **Leva limitada a 50 produtos + busca por link no topo do painel.**
  Dois pedidos juntos: (1) a leva diária volta a ter teto — só os 50
  melhores do nicho por score de curadoria (`LIMITE_LEVA` em
  `buscar_leva_lancamento.py`), revertendo o "traz todos" de 01/09 só
  no quesito volume (o filtro de qualidade continua interativo, no
  painel). (2) A busca de produto específico subiu pro **topo** do
  `painel.html` (antes ficava embaixo da tabela) e passou a aceitar
  tanto descrição quanto **link colado do app da Shopee** — o usuário
  apontou que na prática é assim que vai usar: "achar produto no app
  Shopee e trazer pro agente". Extraída a lógica de resolver link
  (segue redirecionamento, extrai nome/itemId da URL) de
  `buscar_um_produto.py` pra um módulo compartilhado,
  `shopee_integration/link_resolver.py`, e reaproveitada em
  `api/buscar_produto.py` (que antes só buscava por palavra-chave) —
  evita duas implementações da mesma regex divergindo com o tempo.
  Revisado que todo produto marcado pra esteira — venha da leva, da
  busca (por nome ou link) ou de `produtos_manuais.txt` — sempre gera
  narração e legenda ao salvar: `montarRoteiro()`/`montarLegenda()` só
  dependem dos atributos `data-*` do checkbox, preenchidos igual nos
  três casos (categoria cai no gancho `_padrao` quando o produto não
  tem `termo_busca`, ex: vindo de busca ao vivo). Testado com
  Playwright: busca por link simulando a resposta com `termo_usado`
  mostra aviso "Busquei por... confira se é o produto certo", e o
  roteiro baixado sai completo tanto pro produto da leva quanto pro
  achado por link.
## 2026-09-03

- **Bug reportado: produto não entrava na esteira + filtro por
  vendidos.** Usuário relatou problema ao incluir produtos na esteira e
  apontou a causa provável: o botão baixava um arquivo `.md` (via
  `Blob`/`URL.createObjectURL`) *junto* com o salvamento — comum de
  falhar silenciosamente em navegador mobile (diálogo de download pode
  suspender o JS antes do `fetch` de salvar terminar). Removida a
  função `baixarRoteiro()` inteira e a chamada de download no clique do
  botão em `painel.py` — agora "Salvar seleção na esteira" só faz o
  `POST` em `/api/selecionar`; roteiro e legenda continuam saindo
  prontos, só que só ficam visíveis em `esteira.html` ("Ver textos"),
  nunca mais como arquivo baixado. Também adicionado o filtro
  **Vendidos mínimo** (terceiro select, ao lado de comissão e
  avaliação, mesma lógica combinável) — `data-vendidos` no `<tr>` de
  `_linha_produto`, opções 50+/100+/300+/500+/1000+. Testado com
  Playwright: filtro por vendidos≥100 esconde o produto com poucas
  vendas corretamente, e o clique em salvar não dispara mais nenhum
  evento de download.
- **Link de afiliado visível e copiável na esteira.** Usuário pediu pra
  trazer o link de afiliado do produto na linha da esteira. O link já
  era salvo (`esteira.json`, campo `link`, usado no `href` do nome do
  produto), mas não tinha texto visível nem jeito de copiar. Adicionado
  um botão "Copiar link" logo abaixo do nome, em cada linha
  (`shopee_integration/esteira.py`, reaproveitando o mesmo mecanismo de
  copiar já usado em narração/legenda — `navigator.clipboard`, sem JS
  novo). Produto sem link salvo mostra "Sem link salvo" no lugar do
  botão. Testado com Playwright: copiar link bate certinho com o valor
  salvo, e o aviso aparece quando o campo está vazio.
- **Bug reportado: "a esteira não está atualizando".** Causa raiz: a
  `esteira.html` era um retrato HTML totalmente estático, regravado
  *só* quando o workflow `leva-diaria.yml` roda (uma vez por dia, 9h)
  — então um produto selecionado no painel, uma etapa mudada ou uma
  venda registrada às 23h, por exemplo, só apareciam na página no dia
  seguinte, mesmo `esteira.json` já tendo sido atualizado na hora (via
  `api/selecionar.js`/`atualizar_esteira.js`/`excluir_esteira.js`).
  Corrigido com uma função serverless nova, `api/esteira.py` (GET),
  que reaproveita `calcular_status()` de `shopee_integration/esteira.py`
  sem duplicar lógica e devolve o estado atual como JSON — os arquivos
  (`esteira.json`, `financeiro/*.csv`) fazem parte do deploy da Vercel,
  então já vêm atualizados a cada redeploy (que acontece sozinho a
  cada commit, incluindo os que as próprias funções serverless fazem).
  `esteira.html` agora busca esse endpoint ao abrir e re-renderiza a
  tabela e os cards de resumo em JS (`renderizarEsteira()`,
  `montarLinhaEsteira()` — porta fiel de `_linha()`/`_bloco_texto()`
  pro lado do cliente, sem duplicar a lógica de *cálculo*, só a de
  *desenho*), religando os mesmos listeners de seletor/copiar/excluir
  nas linhas novas (`ativarAcoesLinha()`, chamada tanto no load quanto
  depois do re-render). Se a busca falhar (ex: aberto como página
  estática do GitHub Pages, sem `/api/*`), a página mantém o último
  snapshot gerado pelo workflow e troca o texto de "Atualizado" por um
  aviso, em vez de quebrar. Testado com Playwright: simulando uma
  resposta de `/api/esteira` diferente da gravada no HTML, a página
  troca os produtos exibidos, atualiza os cards e mantém os botões
  funcionando nas linhas recém-renderizadas; simulando a ausência do
  endpoint, mantém o snapshot estático e mostra o aviso.
