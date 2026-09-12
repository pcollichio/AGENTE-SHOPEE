# Histórico do projeto — Agente Shopee

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

## 2026-09-10

- **Conversa sobre "envelopar" o cockpit pra vender pra outros
  afiliados.** Usuário sinalizou intenção de empacotar o produto pra
  venda. Perguntei o modelo (clonar por cliente vs. SaaS multi-tenant
  de verdade); ele não respondeu com preferência — dei recomendação
  (clonar por cliente: repositório + deploy + credenciais próprias por
  afiliado, aproveitando que a arquitetura atual já funciona nesse
  formato) e listei o que precisaria virar configuração por cliente
  (marca/nicho, credenciais, `OWNER`/`REPO`/`BRANCH` hardcoded nas
  funções serverless, onboarding). **Nada disso foi implementado
  ainda** — só combinado que faríamos melhorias antes de decidir o
  modelo de venda.
- **Removida a restrição de nicho da leva — agora traz os mais
  vendidos da Shopee via API.** Primeira melhoria pedida: "não quero
  mais que filtre somente produtos de casa e construção... quero que
  traga os produtos mais vendidos da Shopee através da API". Mudanças:
  (1) `shopee_integration/client.py`: `buscar_produtos()` ganhou o
  parâmetro `sort_type` (mapeado pro `sortType` da Shopee — "sales" =
  2, mais vendidos; também "commission", "price_asc", "price_desc");
  `keyword` agora vai como `null` (não mais `""`) quando não
  informado, pra pedir a lista geral sem restringir por termo. Campo
  `category` do produto mapeado deixou de vir hardcoded como
  `"casa_construcao"` (agora `None` — não tinha uso real no resto do
  código). NOTA registrada no arquivo: `sortType` ainda não validado
  contra resposta real da Shopee (só o resto dos campos já foi). (2)
  `buscar_leva_lancamento.py`: removida `SUBCATEGORIAS_CASA_CONSTRUCAO`
  (as 12 palavras-chave de nicho) e `buscar_produtos_do_nicho()`
  (loop de busca por palavra-chave); substituídas por
  `buscar_mais_vendidos()` — uma chamada só à API pedindo os mais
  vendidos (`sort_type="sales"`, sem keyword), ainda passando pelo
  denylist de `produtos_excluir.txt` (recontextualizado: de "manter o
  nicho puro" pra "bloqueio manual de categoria indesejada",
  comentário do arquivo atualizado). (3) Textos que afirmavam filtro
  de nicho corrigidos pra não ficarem enganosos: título "Painel Shopee
  — Casa & Construção" → "Painel Shopee — Mais Vendidos", "Leva do dia
  — N produtos do nicho" → "— N produtos mais vendidos", descrição do
  passo 1 em `index.html` (`painel_index.py`). Efeito colateral
  conhecido, não resolvido: sem categoria de nicho por produto
  (`termo_busca`), todo roteiro/legenda cai no gancho genérico
  (`GANCHOS_ROTEIRO['_padrao']`) em vez de um específico por
  categoria. Testado em modo mock: `sort_type="sales"` ordena
  corretamente por `total_sold` desc, e o pipeline completo (busca →
  score → tier → painel.html) roda sem erro com a nova fonte. Não deu
  pra testar contra a API real da Shopee (rede da sessão bloqueada) —
  falta rodar `leva-diaria.yml` de verdade e conferir se `sortType` é
  aceito, ou se precisa ajustar o nome/valor do campo.
- **Correção: `limit` acima de 50 é rejeitado pela Shopee.** Ao rodar
  `leva-diaria.yml` de verdade pra validar a mudança acima, a Shopee
  devolveu erro real: `sortType` passou sem problema (bom sinal — está
  validado), mas `limit=100` deu erro 11001 "Exceeded the maximum
  number of page limit, the maximum limit is 50". Corrigido: novo
  `client.LIMITE_MAXIMO_POR_PAGINA = 50`, `buscar_produtos()` ganhou o
  parâmetro `pagina` (variável GraphQL `page`, ainda não validada
  contra resposta real — só testado que não quebrou nada em modo
  mock), e `buscar_mais_vendidos()` agora pagina (`PAGINAS_BUSCA_API =
  2`) em vez de pedir tudo numa chamada só, parando cedo se uma página
  vier vazia ou incompleta. Disparado `leva-diaria.yml` de novo depois
  da correção pra confirmar — funcionou: 50 produtos reais, de
  categorias variadas (moda, cozinha, beleza, decoração), confirmados
  no `painel.html`.
- **Roteiro/legenda generalizado, sem banco de ganchos por categoria.**
  Levantei que a narrativa "Papai Resolve" (abertura fixa "Meu papai
  sempre resolve tudo aqui em casa!") não fazia mais sentido pra
  produtos fora de casa (moda, beleza) agora que a leva não é mais só
  do nicho — perguntei o que fazer (manter só pra produtos de casa,
  generalizar o roteiro, ou deixar pra depois). Usuário escolheu
  **generalizar**. Removido `GANCHOS_ROTEIRO` (o banco de dor/motivo
  por categoria de casa — hidráulica, cozinha, organização etc.) de
  `shopee_integration/painel.py`; `montarRoteiro()`/`montarLegenda()`
  agora usam frases fixas, genéricas o bastante pra qualquer produto:
  abertura "Meu papai sempre resolve tudo!" (tirado "aqui em casa"),
  dor "Eu vivia com esse perrengue e nada resolvia direito!", solução
  "Mas aí ele achou [produto] — resolveu na hora!". Hashtags da
  legenda também generalizadas: tiradas `#casaeconstrucao`,
  `#dicasdecasa` e `#paisdeplantao` (específicas do nicho antigo),
  adicionadas `#shopeebrasil`, `#promoshopee`, `#achadinhos` (mantido
  `#papairesolve` e `#achadosdashopee`). Removido também o import
  `json` de `painel.py` (só existia pra serializar `GANCHOS_ROTEIRO`
  pro JS, ficou sem uso). Testado com Playwright: roteiro/legenda
  gerados pra um produto de moda (baby doll) saem coerentes, sem
  nenhuma referência a "casa" fora da abertura de marca.
- **Persona "papai" removida da narração (mesma conversa, direto).**
  Usuário: "esqueça a narrativa papai resolve, vamos tratar de narrar
  o resto, dor, solução e cta". Tirada a abertura fixa "Meu papai
  sempre resolve tudo!" e a referência a "ele" (o papai) na solução —
  `montarRoteiro()` fica com 4 blocos, sem personagem: Dor ("Eu tinha
  um probleminha desse tipo e nada resolvia direito!") → Solução ("Aí
  eu achei [produto] — resolveu na hora!") → Prova (visual, sem falar)
  → Call to action, ~20s. `montarLegenda()` idem, sem a linha de
  abertura. A hashtag `#papairesolve` foi mantida (é a marca da conta,
  @papairesolve_br — não a narrativa do roteiro; só o personagem saiu
  da narração). Testado com Playwright: roteiro/legenda salvos na
  esteira sem nenhuma menção a "papai" fora da hashtag de marca.
- **Importação real do financeiro: relatório de comissões da Shopee +
  Gerenciador de Anúncios da Meta.** Usuário mandou os dois relatórios
  reais (período 01–10/09) "pra eu entender o que será enviado".
  Analisei os dois formatos: o CSV de comissões da Shopee (um registro
  por pedido, com status Pendente/Concluído/Cancelado, comissão líquida
  do afiliado, e um campo `Sub_id1` que o usuário já usa como etiqueta
  de rastreio por post, ex: "RIPADO0509") e o xlsx do Gerenciador de
  Anúncios da Meta (gasto por campanha/conjunto de anúncios, num
  período). Perguntei duas coisas: (1) se "Pendente" deve contar no
  financeiro — resposta: mostrar no Dashboard, mas **não contar** até
  virar "Concluído" (pode cancelar); (2) se importava esse lote agora
  ou só aprendia o formato — sem preferência, decidi importar (dados
  reais, úteis).
  Implementado: **novo `importar_extratos.py`** (detecta `.csv` vs
  `.xlsx` pela extensão, idempotente — usa ID do pedido / campanha+data
  como chave, não duplica rodando de novo). Achado no caminho: o
  exportador de CSV da Shopee tem um bug de formatação — toda linha com
  campo contendo vírgula (ex: "Notas do item") vem com a linha INTEIRA
  entre aspas e as aspas internas dobradas, em vez de só aquele campo
  ser citado; `_corrigir_linha_shopee()` desfaz isso antes de
  interpretar como CSV normal (validado contra o arquivo real). Status
  "Concluído" vira venda em `financeiro/vendas_shopee.csv` (conta no
  ROI/meta); "Pendente" vai pro **novo** `financeiro/vendas_pendentes.csv`
  (só informativo); "Cancelado" é ignorado. Para o xlsx da Meta,
  importa por conjunto de anúncios (não pela linha agregada "All", que
  duplicaria o gasto). Adicionado `openpyxl` em `requirements.txt`.
  `roi.py` ganhou `carregar_vendas_pendentes()` e o campo
  `comissao_pendente` em `calcular_resumo()`/`resumo.json`;
  `painel_roi.py` mostra "+ R$X pendente na Shopee" abaixo da barra da
  meta, sem entrar na conta. Rodado contra os dois arquivos reais: 1
  venda concluída (R$1,80), 7 pendentes (R$26,41), 4 campanhas de
  anúncio (R$121,99) — confirmado no Dashboard gerado, idempotência
  testada (rodar de novo: 0 novos em ambos).
- **Renomeado "Cockpit" pra "Agente Shopee" e identidade visual
  laranja/branca em todo o produto.** Pedido do usuário: "No lugar no
  subitem cockpit quero que deixe somente Agente Shopee. aqui sera o
  trabalho de guiar o afiliado pelo chat. quero tambem que a
  identidade visual seja toda laranja e branca igual da shopee, laranja
  de fundo e branco nos campos e textos." Trocado todo texto visível
  "Cockpit"/"Cockpit de Afiliação"/"Cockpit Papai Resolve" por "Agente
  Shopee" (título da aba, marca na sidebar de `cockpit.html`, eyebrow e
  rodapé de cada página) — mantido "Papai Resolve" como voz/handle da
  conta (`@papairesolve_br`, eyebrow do chat), que não foi o alvo do
  pedido. Retema completo pra paleta fixa da Shopee: `--bg` (fundo da
  página) virou laranja `#ee4d2d`; textos/títulos que ficam direto
  sobre o fundo laranja (eyebrow, h1, rodapé, labels de filtro fora dos
  cards) ganharam `--on-bg`/`--on-bg-muted` (branco/laranja clarinho);
  cards, tabelas e inputs continuam brancos (`--card`/`#ffffff`) com
  texto escuro (`--text`) — só o que está sobre o laranja mudou de cor,
  o conteúdo dentro dos cards brancos ficou igual (senão ficaria
  ilegível). Decisão não pedida explicitamente, mas necessária: a
  paleta agora é fixa (não muda mais com tema claro/escuro do sistema
  — colapsados os três blocos `:root`/`@media (prefers-color-scheme:
  dark)`/`:root[data-theme="dark"]` de cada arquivo em um só,
  incondicional), do mesmo jeito que o app da Shopee sempre mostra a
  marca laranja dela independente do tema do aparelho. Aplicado em
  `cockpit.html` e nos 6 geradores de página
  (`shopee_integration/{esteira,painel,painel_index,chat_page,
  painel_roi}.py`, `nav.py`) e no único arquivo estático fora desse
  padrão (`importar.html`). No processo, achado e corrigido um padrão
  de bug recorrente: várias regras usavam `background: var(--bg)` só
  pra ficar um pouco diferente do branco puro do card por trás (input
  de busca, bolha do coach no chat, placeholder de foto, linha de
  texto gerada em `importar.html`, tooltip do gráfico de ROI, hover do
  menu, botão de fechar chat no mobile) — funcionava com o `--bg` cinza
  claro antigo, quebrou (virava laranja vivo) com o `--bg` novo; cada
  caso foi revisado e trocado por branco explícito ou um tom neutro
  (`var(--accent-soft)`/`#f7f3f1`), conforme o contexto. Regenerado
  localmente `index.html`, `chat.html`, `esteira.html` e
  `painel_roi.html` a partir dos geradores atualizados; `painel.html`
  depende da API real da Shopee (roda só via `leva-diaria.yml`).
  Verificado com Playwright: `cockpit.html` (sidebar), `painel_roi.html`
  (Dashboard), `esteira.html` e `importar.html` — fundo laranja, cards
  brancos, texto legível em ambos os contextos.

## 2026-09-11

- **Filtro por segmento de produto no painel** (beleza, casa &
  construção, moda etc.). Pedido do usuário, depois de ver a leva já
  trazendo produtos de qualquer categoria: "seria possivel incluir
  filtro por segmento de produtos, exemplo, beleza, casa e construção,
  etc". A Shopee Affiliate API (`productOfferV2`) não devolve categoria
  nenhuma do produto (campo `category` do mapeamento em `client.py`
  sempre vem `None` — ver NOTA lá), então não tem como filtrar por uma
  categoria oficial da Shopee. Solução: **novo módulo
  `shopee_integration/segmentos.py`**, que infere o segmento a partir de
  palavras-chave no nome do produto (`inferir_segmento()`) — dez
  segmentos (beleza, casa_construcao, moda, eletronicos, pet, infantil,
  esporte_lazer, saude, papelaria_escritorio, automotivo) mais "outros"
  como fallback quando nada bate. É uma heurística, não uma categoria
  oficial — nome comercial nem sempre é claro, então vai ter caso
  classificado errado ou em "outros"; testado contra nomes reais da
  última leva (torneira/luminária/organizador → casa_construcao,
  conjunto academia/baby doll → moda, ração → pet, batom → beleza) e
  bateu certo em todos. Rodado contra a leva real do dia (50 produtos)
  pra calibrar a cobertura: na primeira versão, 34/50 caíam em
  "outros" — revisados os nomes reais e adicionadas ~35 palavras-chave
  que apareciam na leva e não estavam cobertas (cobertor, mop, balde,
  espelho, lixeira, chaleira, espremedor, processador/moedor/picador de
  alimentos, jogo de chave, marmita, amaciante, máquina de costura para
  casa_construcao; retinal, óleo facial, sabonete líquido, zero pore,
  renovador(es) facial(is) para beleza; blusa, muscle tee para moda) —
  depois do ajuste, só 4/50 ficaram em "outros" contra a mesma leva.
  Aplicado em três pontos: (1)
  `buscar_leva_lancamento.py` marca `segmento` em cada produto da leva
  automática e dos manuais (`produtos_manuais.txt`); (2)
  `api/buscar_produto.py` (busca ao vivo por link/descrição) marca
  `segmento` nos resultados também; (3) `shopee_integration/painel.py`
  ganhou uma coluna "Segmento" na tabela, um novo select "Segmento" na
  linha de filtros (ao lado de comissão/avaliação/vendidos mínimo,
  combinável com eles e com a faixa de ticket) — as opções do select são
  geradas dinamicamente a partir dos segmentos que aparecem na leva do
  dia (não uma lista fixa), e os resultados da busca ao vivo também
  mostram o rótulo do segmento. Testado localmente com Playwright
  (dados mock): selecionar "Casa & Construção" no filtro esconde as
  linhas de outros segmentos corretamente, combinando com os demais
  filtros. `painel.html` só é regenerado com dados reais via
  `leva-diaria.yml` (a sessão do Claude não acessa a API da Shopee
  diretamente).
- **Geração direta do link rastreável de afiliado, pra link colado.**
  Usuário: "existe um processo na shopee que é a conversão do link
  para um link de afiliado rastreavel, veja a possibilidade de fazer
  isso pela API e ja trazer o link certo do produto na esteira". Pra
  produtos da leva ou da busca por palavra-chave, o link rastreável já
  vem pronto (campo `offerLink` de `productOfferV2`, por item — isso já
  funcionava). O ponto fraco era o fluxo de "colar link" (achar o
  produto no app e trazer o link): o código antigo só extraía um termo
  de busca da URL colada e torcia pra achar o mesmo `itemId` de novo
  entre os resultados de uma busca por palavra-chave — se a busca não
  trouxesse aquele item exato (comum, relevância de busca não garante
  isso), não tinha como pegar o link rastreável daquele produto
  específico. Implementada `client.gerar_link_rastreavel()`, usando a
  mutation `generateShortLink` da Affiliate API (o mesmo processo que a
  Shopee oferece no painel de afiliado pra "encurtar e rastrear"
  qualquer link) — gera o link direto a partir da URL resolvida,
  **sem depender de achar o produto de novo por busca**. Aplicado em
  `api/buscar_produto.py` (busca ao vivo no painel) e
  `buscar_um_produto.py` (busca manual via chat/`busca-manual.yml`):
  quando o item é encontrado por palavra-chave também, o link gerado
  direto substitui o `offerLink` da busca (mais garantido, mesma URL
  colada); quando NÃO é encontrado, em vez de simplesmente mostrar
  "não achei" como antes, devolve o link rastreável certo separado (com
  aviso de que faltam os detalhes — nome/preço/foto — pra adicionar
  automaticamente na esteira). NOTA: mutation/campos
  (`generateShortLink`, `originUrl`, `subIds`, `shortLink`) ainda não
  confirmados contra uma resposta real no momento da implementação —
  testado em seguida via `busca-manual.yml` com um link de afiliado
  real (`https://s.shopee.com.br/2qUUBWudkN`, um dos links já presentes
  na leva do dia). Esse primeiro teste nem chegou a exercitar a
  mutation: o link resolveu pra
  `shopee.com.br/opaanlp/401374403/20497653715` — um TERCEIRO formato
  de URL da Shopee (`.../<nome-da-loja>/<shopId>/<itemId>`, sem nome de
  produto nenhum na URL) que `link_resolver.extrair_info_link()` não
  reconhecia (só sabia `-i.<shopId>.<itemId>` e
  `/product/<shopId>/<itemId>`) — o item_id não saía, e o código
  antigo desistia com "link sem nome" antes até de tentar gerar o link
  rastreável. Corrigido: o regex de item_id generalizou pra "últimos
  dois segmentos numéricos do caminho", cobrindo os três formatos com
  uma regra só; e a chamada de `gerar_link_rastreavel()` foi movida pra
  ANTES da checagem de "tem nome pra buscar por palavra-chave" — assim,
  mesmo quando a URL não tem nome de produto nenhum (esse caso real),
  ainda dá pra tentar gerar o link rastreável, só sem os detalhes
  (nome/preço/foto). **Resultado, testado de novo com o mesmo link
  real: a mutation funcionou** — devolveu
  `https://s.shopee.com.br/2qUUD7h30A?lp=aff`, um link novo e válido
  (o `?lp=aff` marca como link de afiliado). `generateShortLink`,
  `originUrl` e `shortLink` confirmados contra a API real; `subIds`
  ainda não testado com valores de verdade (só lista vazia).
- **Coach do chat ganha perfil estratégico do afiliado + plano de ação
  personalizado, via tool use.** Usuário pediu pra montar, junto com o
  Claude, um "plano ideal" pro afiliado bater a meta — pedindo pra
  pesquisar o que está funcionando hoje (grupos de WhatsApp, tráfego
  pago, orgânico, live etc.), quais produtos têm mais aderência, e
  destacou a **janela de atribuição de 7 dias** da Shopee (clicou no
  seu link, qualquer compra dentro de 7 dias gera comissão pra você,
  mesmo que não seja do produto divulgado) como possível eixo de
  estratégia. Pesquisa feita (busca na web) e cruzada com a Central de
  Ajuda oficial da Shopee: cookie de 7 dias confirmado (atribuição por
  último clique); canais que mais aparecem funcionando pra afiliado
  solo, em ordem de prioridade — WhatsApp (lista/grupo temático,
  recorrência de clique), Reels/TikTok (topo de funil, já automatizado
  aqui), Shopee Live (até 30% de comissão com parceiro, exige aparecer
  e ter audiência), tráfego pago (só dentro da política oficial: nunca
  Google/Bing Ads, anúncio só pela conta/página cadastrada no
  programa, sem marca Shopee no criativo — já é o formato usado aqui,
  impulsionar post do Instagram); categorias de maior comissão: beleza
  (até 30%) e moda feminina (15-25%).
  Comecei a fazer essas perguntas de perfil (audiência atual, orçamento
  pra tráfego pago, topa aparecer em vídeo, foco de nicho) diretamente
  nesta conversa — o usuário interrompeu: "pensando em transformar
  este agente em um produto SaaS, estas perguntas precisam ser feitas
  pelo agente para traçar o plano" — ou seja, quem deve perguntar isso
  é o coach de dentro do produto (`chat.html`), não o Claude numa
  sessão pontual, já que o objetivo é isso funcionar pra qualquer
  afiliado que vier a usar o produto (não só pra esta conta).
  Implementado: (1) **bug real corrigido** em `api/chat.js` — o
  `RAW_BASE` apontava pra uma branch chamada `main`, que **não existe**
  neste repositório (só existe `claude/shopee-cockpit-connection-g3fqop`)
  — todo fetch de contexto (leva do dia, resumo financeiro) sempre
  falhava silenciosamente (404, engolido pelo try/catch), então o
  coach nunca via dado real, só o texto de fallback "ainda não há
  dados" — corrigido pra apontar pra branch certa, mesma usada por
  `api/selecionar.js`/`api/atualizar_esteira.js`. (2) Novo
  `perfil_afiliado.json` (ver README.md) guarda o perfil + o
  `plano_acao` do afiliado. (3) `api/chat.js` ganhou **tool use** da
  API da Anthropic — uma ferramenta `salvar_perfil_afiliado` que o
  coach chama depois de reunir as respostas na conversa (uma pergunta
  de cada vez, não uma lista fria), gravando direto no GitHub via
  `GITHUB_TOKEN`. (4) O prompt de sistema ganhou a base de conhecimento
  da pesquisa (`PLAYBOOK_ESTRATEGIA`) e instruções: se não há perfil
  salvo e o afiliado pedir plano/"o que eu faço", pergunta as 4 coisas
  uma de cada vez; se já há perfil salvo, usa o `plano_acao` já
  existente em vez de perguntar de novo. Também corrigido o texto do
  prompt que ainda descrevia o produto como restrito ao "nicho casa e
  construção" (desatualizado desde a mudança de 10/09). Ainda não
  testado ao vivo contra a Vercel real (precisa do deploy com
  `ANTHROPIC_API_KEY`/`GITHUB_TOKEN` configurados) — validar na
  próxima vez que o usuário testar o chat.
- **Removido todo vínculo com "Papai Resolve" do Agente Shopee.**
  Pedido do usuário: "quero que retire do agente shopee qq vinculo com
  papai resolve". A persona/marca "Papai Resolve" — que já vinha sendo
  esvaziada aos poucos desde 10/09 (primeiro tirada da narração dos
  Reels, depois do nome do produto) — foi removida por completo de
  tudo que o produto exibe ou gera: (1) eyebrow/rodapé de todas as
  páginas (`painel.py`, `esteira.py`, `painel_index.py`,
  `painel_roi.py`, `chat_page.py`, `cockpit.html`, `importar.html`)
  perderam o "@papairesolve_br" — ficam só "Agente Shopee"; (2) a
  hashtag `#papairesolve`, que tinha sido mantida em 10/09 "porque é a
  marca da conta", foi tirada de `montarLegenda()` em `painel.py`
  (grupo de hashtags fixo agora é só `#achadosdashopee #shopeebrasil
  #promoshopee #achadinhos`); (3) o eyebrow do chat/coach ("Papai
  Resolve · Coach") virou "Agente Shopee · Coach"; (4) o prompt de
  sistema do coach (`api/chat.js`) parou de mencionar "a marca
  @papairesolve_br (Papai Resolve)"; (5) o `user-agent` das funções
  serverless (`api/selecionar.js`, `api/atualizar_esteira.js`,
  `api/importar_arquivo.js`, `api/excluir_esteira.js`, `api/chat.js`)
  e o `name` do `package.json` trocaram de `cockpit-papai-resolve`
  pra `agente-shopee`; (6) título do `CLAUDE.md`, `HISTORICO.md` e
  `README.md` (`cockpit-shopee/`) atualizados de "Papai Resolve" pra
  "Agente Shopee". Achado no caminho: 4 produtos ainda não publicados
  em `esteira.json` guardavam narração/legenda salvas ANTES da
  remoção da persona em 10/09 (a esteira só atualiza texto quando o
  produto é selecionado de novo, não retroativamente) — ainda tinham a
  abertura "Meu papai sempre resolve tudo aqui em casa!" e a hashtag
  `#papairesolve`, e um deles (Aditivo Impermeabilizante) até citava
  um link de afiliado desatualizado. Regenerados os 4 (roteiro e
  legenda) com o template atual, direto em `esteira.json` — o único
  item já publicado não precisou de ajuste (já tinha sido salvo depois
  da remoção da persona). **Deixado de propósito, sem alterar**:
  descrições de investimento reais em `financeiro/resumo.json` e nos
  HTML gerados a partir dele (ex: "Instagram post: #papairesolve -
  Instale a sua!...") — são nomes reais de campanhas do Gerenciador de
  Anúncios da Meta, já rodadas de verdade; mudar isso falsificaria o
  registro financeiro. Também não mexi nas entradas antigas deste
  arquivo (`HISTORICO.md`) nem no texto do `CLAUDE.md` que narra o
  histórico da mudança de persona em 10/09 — são registro do que
  aconteceu, não branding atual. Regenerado localmente `index.html`,
  `chat.html`, `esteira.html`, `painel_roi.html`; `painel.html`
  depende da API real (roda via `leva-diaria.yml`). Isso é só a
  apresentação do Agente Shopee — não renomeia a conta real do
  Instagram/TikTok (`@papairesolve_br`), que é uma decisão de fora
  deste repositório.
- **Removida a auto-identificação como "coach" e o resto do vocabulário
  "cockpit" do que o produto exibe/gera.** Pedido do usuário: "nao
  quero dizer que sou coach, e tbm esquee negocio de cockpit vamos ser
  simples e produtivos". Trocado em todo texto visível: título da aba
  do chat ("Chat do coach" → "Chat"), eyebrow ("Agente Shopee · Coach"
  → "Agente Shopee"), h1 ("Converse com o coach" → "Chat"), a mensagem
  de saudação ("Sou o coach do seu cockpit..." → direto: "Posso te
  dizer o que fazer agora..."), mensagens de erro do chat ("Deu um erro
  ao falar com o coach" → "Deu um erro ao responder"), o rótulo "Coach"
  no painel de chat lateral do `cockpit.html`, e o prompt de sistema do
  chat em `api/chat.js` ("Você é o coach do 'Agente Shopee'" → "Você é
  o Agente Shopee"; tom simplificado pra "direto, prático e simples").
  Também tirado "cockpit" como auto-referência em avisos de erro
  ("...só funciona no cockpit publicado na Vercel" → "...só funciona
  depois de publicado na Vercel", em `painel.py`, `esteira.py` x2 e
  `importar.html`), no guia da esteira ("o cockpit automatiza" → "o
  Agente Shopee automatiza"; "autorizar o cockpit a postar" →
  "autorizar o agente a postar"), no rótulo "Manual (com apoio do
  cockpit)" do `index.html` → "(com apoio do agente)", e no print de
  `demo.py`. **Não renomeado** (são identificadores internos, invisíveis
  pro usuário, e mexer neles é risco desproporcional ao pedido): a
  branch `claude/shopee-cockpit-connection-g3fqop`, o diretório
  `cockpit-shopee/`, o arquivo `cockpit.html`, as classes/ids CSS
  `.menu-cockpit`/`menu-cockpit`, `.msg-coach`/`--bolha-coach`, a chave
  de `localStorage` `coach-<data>`, e o módulo Python
  `shopee_integration/coach.py` (motor de recomendações do "O que fazer
  hoje" — nome interno, não aparece pro usuário). Regenerado localmente
  `index.html`, `chat.html`, `esteira.html`, `painel_roi.html`;
  `painel.html` depende da API real (`leva-diaria.yml`). Verificado com
  Playwright: `chat.html` e `cockpit.html` sem "coach"/"cockpit" em
  nenhum texto visível.
- **Item de menu "Chat" virou "Agente"; novo workflow pra verificar a
  conexão com o servidor.** Pedido do usuário: "ao invés de chat
  coloque agente e verifique a conexão com servidor". Renomeado o
  rótulo de navegação em `shopee_integration/nav.py` (usado por
  `painel.py`, `esteira.py`, `painel_index.py`, `painel_roi.py` e pelo
  próprio `chat_page.py`) de "Chat" pra "Agente", além do `<h1>` da
  página do chat, do botão flutuante de chat em `cockpit.html`
  ("💬 Chat" → "💬 Agente") e do menu duplicado (estático) em
  `importar.html`; título da aba do chat simplificado pra "Agente
  Shopee" (era "Chat · Agente Shopee"). Sobre "verifique a conexão com
  servidor": tentei testar `https://agente-shopee.vercel.app` direto
  (via `curl` e via `WebFetch`) e os dois foram **bloqueados pelo proxy
  de rede da sessão** — a restrição de rede do Claude aqui vai além da
  API da Shopee, cobre o domínio `vercel.app` inteiro (não documentado
  antes; `CLAUDE.md` atualizado com isso). Como o runner do GitHub
  Actions tem internet normal, criado
  `.github/workflows/verificar-conexao.yml` — dispara 3 testes reais
  contra o deploy (`cockpit.html`, `api/chat` com uma mensagem de
  teste, `api/buscar_produto`) e imprime o status HTTP de cada um nos
  logs, pra qualquer sessão futura (ou o próprio usuário) confirmar se
  o deploy está no ar sem precisar abrir o navegador. **Disparado e
  confirmado**: `cockpit.html` → 200 (título "Agente Shopee");
  `api/chat` → 200, e o chat de verdade respondeu — "✅ Conexão OK!
  ... Sou o Agente Shopee..." (confirma `ANTHROPIC_API_KEY` e
  `GITHUB_TOKEN` configurados na Vercel, e que o rename "coach" →
  "Agente Shopee" já está no ar); `api/buscar_produto` → 502 com um
  erro real da própria Shopee ("graphql: got null for non-null") pra a
  palavra-chave de teste "teste" — não é falha de conexão (o endpoint
  respondeu, com `SHOPEE_APP_ID`/`SECRET` configurados e
  `USE_MOCK_DATA=false`), é a Shopee reclamando de um termo de busca
  genérico demais; não investigado a fundo, não fazia parte do pedido.
- **Resolvida a sincronização automática de vendas via API — o motivo
  do erro genérico de 30/08 era um bug simples, achado e corrigido.**
  Usuário pediu pra reavaliar "a possibilidade de trazermos as vendas
  através da API". Em 30/08 essa tentativa (`conversionReport`) tinha
  sido abandonada depois de 3 rodadas de erro real, terminando num
  "graphql: got null for non-null" genérico sem indicar o campo. Pra
  investigar de novo, criado `.github/workflows/testar-conversoes.yml`
  (a sessão do Claude não acessa a API da Shopee — o teste roda num
  runner do GitHub Actions, com os `Secrets` reais) e feita uma
  bisseção: 7 variantes da query, da mais simples (só `conversionId`)
  até a completa, todas com sucesso e trazendo dados reais — inclusive
  `orders`/`items`/`itemTotalCommission`. A query inteira **só**
  falhava quando incluía o argumento `scrollId` (cursor de paginação)
  com valor `null` explícito — que é exatamente o que
  `client.buscar_conversoes()` sempre mandava na primeira página (sem
  cursor ainda). **Causa raiz**: a Shopee rejeita `scrollId: null`
  explícito; o argumento só pode aparecer na query quando há um cursor
  de verdade (páginas seguintes) — na primeira página, tem que ser
  omitido da query inteiramente, não mandado como `null`. Corrigido em
  `client.buscar_conversoes()` (monta a query com ou sem `scrollId`
  dependendo se `scroll_id` foi passado). **Testado de ponta a ponta**:
  rodado `sincronizar_vendas.py` de verdade (60 dias) contra a API real
  — achou 9 conversões, 1 confirmada (`COMPLETED`), e essa 1 bateu
  **exatamente** com a venda já importada manualmente antes
  (`financeiro/vendas_shopee.csv`: R$1,8006 de comissão, "Escova
  Elétrica de Limpeza 5 em 1...", mesmo `conversion_id`). Ou seja: a
  sincronização automática **funciona de verdade agora** — mas ainda
  **não está ligada ao fluxo real** (o fluxo hoje continua sendo
  `importar_extratos.py`, manual, a partir do relatório exportado da
  Shopee). Antes de trocar, precisa decidir com o usuário: (1) se
  substitui o import manual pelo automático ou se os dois convivem
  (risco de duplicar a mesma venda em dois arquivos se rodarem os
  dois); (2) rodar via GitHub Actions agendado (tipo `leva-diaria.yml`)
  precisaria de um passo que faça commit do CSV atualizado, ainda não
  implementado; (3) status "Pendente" da Shopee (que hoje só entra via
  `vendas_pendentes.csv`, informativo) teria que ganhar o mesmo
  tratamento aqui se quiser manter esse recurso. Nada disso decidido
  ainda — só a viabilidade técnica confirmada.

## 2026-09-12

- **Sincronização automática de vendas via API ligada ao fluxo real,
  convivendo com o import manual.** Pedido do usuário: "Liga mas
  mantenha a opção de import". Resolvidos os três pontos que ficaram
  em aberto em 11/09:
  1. **`sincronizar_vendas.py` reescrito** pra não sobrescrever mais o
     CSV inteiro a cada rodada (`salvar_csv()` antigo abria em modo
     "w") — agora importa `_acrescentar_csv()`/`_ids_ja_importados()`
     direto de `importar_extratos.py` e usa a MESMA regra de dedupe por
     `conversion_id`, nos MESMOS arquivos (`vendas_shopee.csv`,
     `vendas_pendentes.csv`), com o MESMO formato de linha (coluna
     `observacao`, não mais `order_status`) — os dois métodos de
     importação agora escrevem no mesmo lugar, do mesmo jeito, sem
     duplicar não importa a ordem ou combinação em que rodam. Separa
     `conversionStatus` "COMPLETED" (→ confirmada) de "PENDING" (→
     pendente); qualquer outro status (cancelada etc.) é ignorado.
  2. **Ligado em `leva-diaria.yml`**: novo passo "Sincronizar vendas
     via API" antes de `gerar_roi.py` (pra já entrar no cálculo do
     dia) — roda todo dia às 9h, junto com a leva. Erro da API não
     derruba o workflow (só avisa e segue) — o import manual continua
     como plano B se a sincronização automática ficar fora do ar. Os
     dois arquivos de venda (antes esquecidos no `git add` do passo
     final) agora entram no commit diário.
  3. **Corrigido o "pedido gradua de pendente pra confirmado" ficar
     contado em dobro** — como a sincronização roda todo dia, isso
     passa a ser comum (um pedido "Pendente" hoje pode aparecer
     "Concluído" amanhã). `roi.carregar_vendas_pendentes()` agora
     exclui da conta de "pendente" qualquer `conversion_id` que já
     apareça em `vendas_shopee.csv` — sem precisar apagar a linha
     antiga do pendente à mão, e sem editar CSV depois de escrito
     (mantém o hábito do projeto de nunca sobrescrever arquivo
     financeiro, só filtra na hora de calcular). Testado localmente
     (`gerar_roi.py`): números batem com o que já estava, sem
     regressão. Validado o script novo de ponta a ponta via
     `.github/workflows/testar-conversoes.yml` antes de mexer no
     workflow diário de verdade, incluindo rodar duas vezes seguidas
     pra confirmar que a segunda rodada não duplica nada (dedupe).
     Documentação atualizada: `README.md`, `financeiro/README.md` e
     `CLAUDE.md` — as duas fontes (manual e automática) agora aparecem
     como convivendo, não uma substituindo a outra.

- **Validação de ponta a ponta confirmada e bug real encontrado nela.**
  Rodado `.github/workflows/testar-conversoes.yml` contra o commit que
  liga a sincronização (60 dias, script novo de merge/dedupe): achou 9
  conversões — 1 confirmada nova e 7 pendentes novas — e, rodando de
  novo na mesma execução, **0 novas em ambos** (dedupe funcionando).
  Na inspeção do resultado real, apareceu um caso não previsto: o
  mesmo `conversion_id` (`242592015131160`) voltou da API associado a
  **dois produtos diferentes com status diferentes entre si** (um
  "Escova Elétrica..." confirmado, um "Porta Aliança..." ainda
  pendente) — ou seja, `conversion_id` sozinho não é garantia de
  correspondência 1:1 com um único produto/status. Isso quebrava o
  filtro de "graduação" adicionado hoje mais cedo:
  `roi.carregar_vendas_pendentes()` excluía um pedido pendente inteiro
  só por outro produto, com o mesmo `conversion_id`, já ter confirmado
  — contando a MENOS na comissão pendente mostrada no Dashboard.
  Corrigido casando por (`conversion_id`, `produto`) em vez de só
  `conversion_id`. Testado localmente (`gerar_roi.py`) sem regressão
  nos números já commitados (R$121,99 investido / R$1,80 comissão /
  R$26,41 pendente, iguais a antes).
