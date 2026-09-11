# Cockpit de Afiliação IA-First — Papai Resolve

Contexto que toda sessão do Claude neste repositório deve carregar
primeiro. Leia isto e `HISTORICO.md` antes de responder qualquer coisa
sobre o projeto — evita reexplicar do zero a cada conversa nova.

## O que é

Cockpit de afiliação pra @papairesolve_br (Shopee). Meta: R$10.000/mês
de comissão, ROI mínimo 3x. O usuário (dono do projeto) não é técnico,
usa celular/navegador, prefere resolver tudo puxando o Claude em vez de
mexer em código ou infraestrutura.

Desde 10/09 a leva **não é mais restrita ao nicho casa & construção**
— traz os produtos mais vendidos da Shopee em geral, direto da API
(ver "Pedido do usuário em 10/09" abaixo). O usuário sinalizou em 10/09
que a intenção é eventualmente "envelopar" o cockpit pra vender pra
outros afiliados (fora do nicho casa & construção) — isso ainda não
foi implementado (autenticação, multi-tenant, config por cliente), só
combinado; ver a conversa daquele dia em `HISTORICO.md` antes de
sugerir arquitetura pra isso.

**Desde 10/09 o produto se chama "Agente Shopee"** (não mais
"Cockpit") em todo texto visível — título de aba, marca na sidebar,
eyebrow e rodapé de cada página. "Papai Resolve" continua sendo a voz
da conta (`@papairesolve_br`), não foi afetado. **Identidade visual
fixa: fundo laranja (`#ee4d2d`, cor da Shopee) e branco** — cards,
tabelas e inputs brancos com texto escuro; textos que ficam direto
sobre o fundo laranja (títulos, eyebrow, rodapé) em branco/laranja
claro. Essa paleta é fixa, não muda com tema claro/escuro do sistema —
ver detalhes e o histórico completo do retema em `HISTORICO.md`
(10/09).

## Como trabalhamos (modelo operacional — confirmado pelo usuário em 30/08)

- **Conversa, decisão e "o que fazer agora"**: aqui, com o Claude, numa
  sessão de chat. O Claude é a cabeça pensante — mantém o histórico e
  guia o passo a passo de forma objetiva.
- **Tudo visual/interativo** (fotos de produto, marcar seleção, gráfico
  de ROI): fica no `painel.html` e nas outras páginas do
  `cockpit-shopee/`, publicadas no GitHub Pages, tudo versionado no
  GitHub. O Claude não tenta recriar isso em texto — aponta pro link.
- **Regra explícita (usuário, 31/08): a relação/lista de produtos
  NUNCA é exibida em texto/tabela no chat.** Quando o usuário pedir pra
  ver os produtos (da leva, de uma busca, etc.), a resposta é sempre o
  link do `painel.html` (ou da página relevante) — nunca listar item a
  item aqui. Pode comentar destaques pontuais (ex: "o #7 tem prova
  social forte") sem recriar a lista inteira.
- **Toda decisão e marco importante entra em `HISTORICO.md`**, com
  data. Ao começar uma sessão nova, releia esse arquivo antes de agir.
- A sessão do Claude tem uma restrição de rede: não acessa a API da
  Shopee nem carrega imagens externas diretamente. Pra buscar um
  produto específico sob demanda, dispare o workflow
  `.github/workflows/busca-manual.yml` (via `actions_run_trigger`,
  input `termo`) e leia o resultado nos logs do job.
- **Decisão de 31/08: o cockpit roda na Vercel.** O usuário pediu uma
  conexão de verdade entre o painel (onde ele seleciona produtos) e o
  Claude — decidiu usar a Vercel em vez do fluxo manual por GitHub
  Issues. O botão "Salvar seleção agora" no `painel.html` acrescenta
  (não sobrescreve) a seleção em `cockpit-shopee/esteira.json` (via
  `api/selecionar.js`, que escreve no GitHub usando um `GITHUB_TOKEN`).
  `esteira.html` mostra o status de cada produto (selecionado /
  impulsionado / vendido), calculado cruzando com o financeiro.
- Chat (`chat.html` + `api/chat.js`) e busca ao vivo no site
  (`api/buscar_produto.py`) também rodam na Vercel — todos os três
  (chat, busca, seleção) dependem do deploy estar ativo.
- **Desde 11/09, o coach do chat monta um plano de ação personalizado
  pro afiliado**, via tool use da API da Anthropic — pergunta (uma de
  cada vez, se ainda não souber) audiência atual, orçamento pra
  tráfego pago, disposição pra aparecer em vídeo/live, e foco de
  nicho, e salva tudo + o `plano_acao` em `perfil_afiliado.json`
  (`salvar_perfil_afiliado`, escreve direto no GitHub). Isso foi
  pedido pra rodar **dentro do produto** (não como pergunta pontual do
  Claude aqui na sessão), pensando na meta de "envelopar" o cockpit
  como SaaS pra outros afiliados — qualquer um que usar o chat passa
  pelo mesmo fluxo de descoberta. O prompt de sistema carrega uma base
  de conhecimento fixa sobre o que funciona pra afiliado Shopee (janela
  de atribuição de 7 dias, canais, categorias de maior comissão — ver
  `PLAYBOOK_ESTRATEGIA` em `api/chat.js` e o histórico da pesquisa em
  `HISTORICO.md`). De quebra, corrigido um bug real: `api/chat.js`
  buscava contexto (leva/resumo) na branch `main`, que não existe
  neste repo — o coach nunca via dado real antes disso.
- `importar.html` tem um campo de **upload de arquivo** (relatório de
  vendas Shopee, extrato/print do Meta Ads) — envia pro GitHub em
  `financeiro/importados/` via `api/importar_arquivo.js`. Desde 10/09,
  os dois formatos reais já são conhecidos e têm parser:
  `importar_extratos.py caminho/do/arquivo` (`.csv` = comissões da
  Shopee, `.xlsx` = Gerenciador de Anúncios da Meta) — rode com esse
  arquivo quando o usuário avisar que subiu um. Se vier um formato
  diferente desses dois (ou o layout mudar), leia manualmente e
  converta pros CSVs de `financeiro/` você mesmo, do jeito que sempre
  fez.

## Onde as coisas estão

- `cockpit-shopee/README.md` — visão geral técnica de cada arquivo e
  workflow.
- `cockpit-shopee/leva_do_dia.md` — leva de produtos do dia (atualizada
  às 9h por `leva-diaria.yml`).
- `cockpit-shopee/financeiro/` — investimento e vendas. `investimentos.csv`
  e `vendas.csv` são manuais; desde 10/09, `vendas_shopee.csv` (venda
  confirmada) e `vendas_pendentes.csv` (não confirmada, só informativa,
  fora do ROI/meta) vêm de `importar_extratos.py`, a partir do
  relatório de comissões exportado do painel de afiliado da Shopee —
  ver `financeiro/README.md`.
- `cockpit-shopee/financeiro/resumo.json` — resumo do ROI em JSON
  (inclui `comissao_pendente`, desde 10/09).
- `cockpit-shopee/esteira.json` — lista viva (acumulada, não
  sobrescrita) de todos os produtos já selecionados no painel; leia
  antes de gerar roteiro ou responder sobre o que já foi selecionado.
  Cada item tem dois eixos de status independentes: financeiro
  (selecionado/impulsionado/vendido, calculado sozinho cruzando com o
  financeiro) e `etapa_conteudo` (roteiro_pronto/em_producao/publicado,
  atualizado manualmente pelo usuário no seletor de `esteira.html`, via
  `api/atualizar_esteira.js`). Desde 01/09 cada item também guarda
  `narracao` e `legenda` (o texto pronto pra gravação e pra legenda do
  post, gerados no momento da seleção — ver "Padrão de narração e
  legenda dos Reels" abaixo).
- `cockpit-shopee/esteira.html` — visão da esteira. Desde 03/09, busca o
  estado mais recente ao abrir (`GET /api/esteira.py`, que reaproveita
  `calcular_status()`) e re-renderiza a tabela em JS — antes a página
  só era atualizada pelo workflow diário, então um produto selecionado
  no painel só aparecia aqui no dia seguinte ("a esteira não está
  atualizando", reportado pelo usuário). Se a busca falhar (ex: página
  estática do GitHub Pages, sem Vercel), mantém o último snapshot
  gerado e avisa no lugar de "Atualizado". Mostra status financeiro
  calculado automaticamente (selecionado / impulsionado / vendido),
  cruzando `esteira.json` com o financeiro, um seletor manual de etapa
  de conteúdo por produto, o link de afiliado com botão de copiar
  (direto na linha do produto, ao lado do nome), os textos de
  narração/legenda prontos pra copiar ("Ver textos"), um botão pra
  excluir produto ainda não publicado (`api/excluir_esteira.js`,
  bloqueado no servidor pra produto já publicado) e um guia embutido do
  processo roteiro→gravação→edição→publicação→avaliação (deixa claro
  que gravar, editar e publicar são passos manuais do usuário — o
  Claude não grava vídeo nem publica sozinho, não há integração com
  API do Meta/TikTok configurada).
- Pedido do usuário em 01/09: o filtro de qualidade (comissão mínima,
  avaliação mínima) não corta mais produto do nicho antes da leva — a
  leva traz todos os produtos do nicho casa & construção, e o filtro
  acontece interativamente no painel, no momento da seleção (selects de
  comissão mínima / avaliação mínima em `painel.html`, combináveis com o
  filtro de faixa de preço). Pedido em 02/09: revertido o "todos" por
  volume — a leva agora traz só os **50 melhores** do nicho, por score
  de curadoria (`LIMITE_LEVA` em `buscar_leva_lancamento.py`); o filtro
  de qualidade continua interativo, no painel. Pedido em 03/09: o
  filtro ganhou um terceiro select, **vendidos mínimo**
  (`data-vendidos` no `<tr>`, select `#filtro-vendidos`), combinável
  com comissão/avaliação/faixa de preço. Pedido em 11/09: mais um
  filtro, **segmento** (beleza, casa & construção, moda etc.) — como a
  API não devolve categoria oficial do produto, o segmento é inferido
  por palavras-chave no nome (`shopee_integration/segmentos.py`,
  `inferir_segmento()`), aplicado na leva, nos produtos manuais e na
  busca ao vivo; select `#filtro-segmento`, com opções geradas a partir
  dos segmentos presentes na leva do dia. É heurística, não categoria
  oficial — pode classificar errado ou cair em "Outros".
- Pedido do usuário em 02/09: "o fluxo mais fácil vai ser achar o
  produto no app Shopee e trazer pro agente" — a busca por descrição
  **ou link colado** do produto (usa `shopee_integration/link_resolver.py`,
  compartilhado com `buscar_um_produto.py`) subiu pro topo do
  `painel.html`, acima da leva do dia, em vez de ficar embaixo da
  tabela. Todo produto marcado — venha da leva, da busca por link ou
  por descrição, ou de `produtos_manuais.txt` — usa os mesmos
  `montarRoteiro()`/`montarLegenda()` no momento de salvar, então
  sempre sai com narração e legenda prontas na esteira, sem exceção.
  Pedido em 11/09: quando o produto vem de um **link colado**, o link
  de afiliado agora é gerado direto da URL colada
  (`client.gerar_link_rastreavel()`, mutation `generateShortLink`,
  validada contra a API real em 11/09), em vez de depender de achar o
  mesmo item de novo numa busca por palavra-chave — funciona até
  quando a URL não tem nome de produto nenhum (link de loja, sem
  slug); ver HISTORICO.md pro caso real que motivou o ajuste.
- Pedido do usuário em 03/09: o botão do painel não baixa mais um
  arquivo `.md` — o usuário reportou problema em incluir produto na
  esteira e apontou o download como causa provável (falha comum em
  navegador mobile). O botão "Salvar seleção na esteira" agora só
  salva (POST em `api/selecionar`, sem `Blob`/download); o roteiro e a
  legenda continuam saindo prontos, só que visíveis exclusivamente em
  `esteira.html` ("Ver textos"), nunca mais como arquivo baixado.
- **Pedido do usuário em 10/09: removida a restrição de nicho.** A leva
  não busca mais por palavra-chave de casa & construção — pede direto
  à API os produtos **mais vendidos da Shopee em geral**
  (`client.buscar_produtos(sort_type="sales")`, sem `keyword`).
  `sortType` validado contra resposta real (não deu erro); `limit`
  acima de 50 deu erro 11001 da Shopee (corrigido com paginação — ver
  `client.LIMITE_MAXIMO_POR_PAGINA` e `PAGINAS_BUSCA_API`); `page`
  (paginação) ainda não validado. Removidas
  `SUBCATEGORIAS_CASA_CONSTRUCAO` e `buscar_produtos_do_nicho()` de
  `buscar_leva_lancamento.py`, substituídas por `buscar_mais_vendidos()`.
  `produtos_excluir.txt` continua funcionando, só que agora como
  bloqueio manual de categorias indesejadas (não mais "manter o
  nicho puro"). Testado contra a API real: 50 produtos de categorias
  variadas (moda, beleza, cozinha, decoração) confirmados no painel.
  Efeito colateral resolvido no mesmo dia: ver "Padrão de narração e
  legenda dos Reels" abaixo — `GANCHOS_ROTEIRO` (por categoria de
  nicho) foi removido e substituído por um roteiro genérico, que serve
  pra qualquer produto.
- Links publicados: GitHub Pages em
  `https://pcollichio.github.io/AGENTE-SHOPEE/cockpit-shopee/cockpit.html`
  (e `/painel.html`, `/painel_roi.html`, etc.)

## Padrão de narração e legenda dos Reels (fixado em 31/08, generalizado e sem persona em 10/09)

**Histórico da mudança de 10/09** (dois passos, mesmo dia): primeiro,
com a leva deixando de ser restrita ao nicho casa & construção, removi
o banco `GANCHOS_ROTEIRO` (ganchos de dor por categoria de casa —
hidráulica, cozinha, organização) e troquei a abertura fixa de "Meu
papai sempre resolve tudo aqui em casa!" pra "Meu papai sempre resolve
tudo!" (mesma persona, sem a especificidade de casa). Na sequência, o
usuário pediu pra **esquecer de vez a narrativa "papai resolve"** e
narrar só dor, solução e CTA — removida a abertura/persona por
completo.

**Formato atual**: sem personagem, direto ao ponto (~20s, 4 blocos):
Dor → Solução (cita o produto) → Prova (visual, sem falar) → Call to
action. Frases fixas, genéricas o bastante pra qualquer produto (roupa,
beleza, eletrônico, casa etc.), sem citar problema específico de
categoria: "Eu tinha um probleminha desse tipo e nada resolvia
direito!" → "Aí eu achei [produto] — resolveu na hora!" → [prova
visual] → "Corre que tá com desconto, R$[preço] — link na bio, comenta
'QUERO' que a gente manda!". Implementado em `montarRoteiro()` em
`shopee_integration/painel.py` — se o usuário pedir um roteiro pontual
no chat, siga esse mesmo modelo (sem reintroduzir "papai" como
personagem da narração).

A **legenda do post** segue a mesma estrutura, sem a abertura: (1) dor,
em uma linha, com emoji 😩; (2) solução citando o produto pelo nome, com
emoji ✅; (3) call to action pedindo pra comentar "QUERO" ou ir no link
da bio, com emoji 🛒; (4) hashtags fixas — `#papairesolve
#achadosdashopee #shopeebrasil #promoshopee #achadinhos`. A hashtag
`#papairesolve` continua porque é a marca da conta (@papairesolve_br),
não a narrativa do roteiro — só o personagem "papai" saiu da narração
em si. Implementado em `montarLegenda()`, ao lado de `montarRoteiro()`,
no mesmo arquivo.

Desde 01/09, tanto a narração quanto a legenda são salvas por produto em
`esteira.json` (campos `narracao`/`legenda`) no momento da seleção no
painel, e ficam visíveis (com botão de copiar) em `esteira.html`, em "Ver
textos" na linha do produto — fecha o ciclo criar → publicar → avaliar
sem precisar digitar o texto de novo. Um produto que ainda não foi
publicado (`etapa_conteudo` != `publicado`) pode ser removido da esteira
por lá; a checagem que impede excluir produto já publicado é feita no
servidor (`api/excluir_esteira.js`), não só na tela.

## Segurança

Nunca commitar `.env` nem qualquer credencial (Shopee, Anthropic) em
nenhum arquivo do repositório — só como Secret do GitHub ou variável de
ambiente na Vercel.
