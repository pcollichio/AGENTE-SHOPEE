"""
Importa os relatórios que você exporta manualmente (comissões de
afiliado da Shopee, gasto do gerenciador de anúncios da Meta) pros
CSVs de financeiro/ que o Dashboard lê — pra não precisar digitar cada
venda/investimento à mão.

Rode com:
    python importar_extratos.py caminho/do/relatorio.csv
    python importar_extratos.py caminho/do/relatorio.xlsx
    python importar_extratos.py relatorio_shopee.csv relatorio_meta.xlsx

O tipo é detectado pela extensão do arquivo. Rodar de novo com o mesmo
arquivo (ou um relatório mais recente que repete pedidos antigos) não
duplica nada — usa o ID do pedido/campanha+data como chave.

NOTA sobre o CSV da Shopee: o exportador do painel de afiliado tem um
bug de formatação — toda linha que tem algum campo com vírgula dentro
(ex: "Notas do item") vem com a linha INTEIRA envolta em aspas, com as
aspas do campo interno dobradas (""), em vez de só aquele campo ser
citado. `_corrigir_linha_shopee()` desfaz isso antes de interpretar
como CSV de verdade — validado em 10/09 contra um export real.
"""

import csv
import sys

CAMINHO_VENDAS_SHOPEE = "financeiro/vendas_shopee.csv"
CAMINHO_VENDAS_PENDENTES = "financeiro/vendas_pendentes.csv"
CAMINHO_INVESTIMENTOS = "financeiro/investimentos.csv"


def _corrigir_linha_shopee(linha):
    """Desfaz o bug de quoting do exportador da Shopee (ver NOTA no topo
    do arquivo): se a linha inteira estiver entre aspas, tira essa
    aspa de fora e desfaz o escape duplicado (\"\" -> \") do campo que
    causou o problema — o resultado é uma linha CSV normal."""
    linha = linha.rstrip("\r\n")
    if linha.startswith('"') and linha.endswith('"'):
        linha = linha[1:-1].replace('""', '"')
    return linha


def _ler_relatorio_shopee(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        linhas = f.readlines()
    if not linhas:
        return []

    header = next(csv.reader([linhas[0]]))
    registros = []
    for linha in linhas[1:]:
        corrigida = _corrigir_linha_shopee(linha)
        if not corrigida.strip():
            continue
        campos = next(csv.reader([corrigida]))
        if len(campos) != len(header):
            print(f"Aviso: linha ignorada (esperava {len(header)} campos, achou {len(campos)}): {linha[:80]!r}")
            continue
        registros.append(dict(zip(header, campos)))
    return registros


def _ids_ja_importados(caminho, campo_id):
    """IDs já presentes num CSV de financeiro/, pra não duplicar ao
    importar o mesmo relatório (ou um que repete pedidos antigos)."""
    try:
        with open(caminho, encoding="utf-8", newline="") as f:
            return {l[campo_id] for l in csv.DictReader(f) if l.get(campo_id)}
    except FileNotFoundError:
        return set()


def _acrescentar_csv(caminho, header, linhas_novas):
    """Acrescenta linhas a um CSV de financeiro/, criando com cabeçalho
    se o arquivo ainda não existir (nunca sobrescreve o que já tem)."""
    try:
        existe_conteudo = bool(open(caminho, encoding="utf-8").readline())
    except FileNotFoundError:
        existe_conteudo = False

    with open(caminho, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not existe_conteudo:
            writer.writerow(header)
        writer.writerows(linhas_novas)


def importar_comissoes_shopee(caminho_csv):
    """Lê o relatório de comissões de afiliado exportado do painel da
    Shopee. Só "Concluído" vira venda de verdade (vendas_shopee.csv,
    conta no ROI e na meta); "Pendente" vai pra vendas_pendentes.csv
    (só informativo, ainda pode cancelar); "Cancelado" é ignorado."""
    registros = _ler_relatorio_shopee(caminho_csv)

    ja_concluidas = _ids_ja_importados(CAMINHO_VENDAS_SHOPEE, "conversion_id")
    ja_pendentes = _ids_ja_importados(CAMINHO_VENDAS_PENDENTES, "conversion_id")

    novas_concluidas = []
    novas_pendentes = []
    canceladas = 0

    for r in registros:
        pedido_id = r.get("ID do pedido", "")
        status = r.get("Status do Pedido", "")
        produto = r.get("Nome do Item", "")
        sub_id = r.get("Sub_id1", "")
        observacao = f"Sub_id: {sub_id}" if sub_id else ""

        if status == "Concluído":
            if pedido_id in ja_concluidas:
                continue
            data = (r.get("Tempo de Conclusão") or r.get("Horário do pedido") or "")[:10]
            comissao = r.get("Comissão líquida do afiliado(R$)", "0")
            novas_concluidas.append([data, produto, comissao, pedido_id, observacao])
            ja_concluidas.add(pedido_id)
        elif status == "Pendente":
            if pedido_id in ja_pendentes:
                continue
            data = (r.get("Horário do pedido") or "")[:10]
            comissao = r.get("Comissão líquida do afiliado(R$)", "0")
            novas_pendentes.append([data, produto, comissao, pedido_id, observacao])
            ja_pendentes.add(pedido_id)
        elif status == "Cancelado":
            canceladas += 1

    if novas_concluidas:
        _acrescentar_csv(
            CAMINHO_VENDAS_SHOPEE,
            ["data", "produto", "comissao_recebida", "conversion_id", "observacao"],
            novas_concluidas,
        )
    if novas_pendentes:
        _acrescentar_csv(
            CAMINHO_VENDAS_PENDENTES,
            ["data", "produto", "comissao_prevista", "conversion_id", "observacao"],
            novas_pendentes,
        )

    print(
        f"Shopee ({caminho_csv}): {len(novas_concluidas)} venda(s) concluída(s) nova(s), "
        f"{len(novas_pendentes)} pendente(s) nova(s), {canceladas} cancelada(s) ignorada(s)."
    )


def _linhas_planilha(caminho_xlsx, aba="Raw Data Report"):
    import openpyxl

    wb = openpyxl.load_workbook(caminho_xlsx, data_only=True)
    ws = wb[aba] if aba in wb.sheetnames else wb[wb.sheetnames[0]]
    return list(ws.iter_rows(values_only=True))


def importar_gasto_meta(caminho_xlsx):
    """Lê o relatório do gerenciador de anúncios da Meta (.xlsx) e
    acrescenta uma linha em investimentos.csv por conjunto de anúncios
    real (ignora as linhas "All", que são só o total agregado da
    campanha e duplicariam o gasto já contado no nível do conjunto)."""
    linhas = _linhas_planilha(caminho_xlsx)

    idx_header = next(
        (i for i, l in enumerate(linhas) if l and "Nome da campanha" in l), None
    )
    if idx_header is None:
        print(f"Aviso: não achei a linha de cabeçalho em {caminho_xlsx} — formato inesperado.")
        return

    header = linhas[idx_header]
    dados = [
        dict(zip(header, linha))
        for linha in linhas[idx_header + 1:]
        if linha and any(v not in (None, "") for v in linha)
    ]

    ja_importadas = set()
    try:
        with open(CAMINHO_INVESTIMENTOS, encoding="utf-8", newline="") as f:
            ja_importadas = {(l["produto"], l["data"]) for l in csv.DictReader(f)}
    except FileNotFoundError:
        pass

    novas = []
    for d in dados:
        conjunto = d.get("Nome do conjunto de anúncios")
        if conjunto in (None, "", "All"):
            continue
        campanha = d.get("Nome da campanha") or conjunto
        gasto = d.get("Valor gasto (BRL)")
        if gasto in (None, ""):
            continue
        data = str(d.get("Início") or d.get("Início dos relatórios") or "")[:10]
        chave = (campanha, data)
        if chave in ja_importadas:
            continue
        alcance = d.get("Alcance")
        cliques = d.get("Cliques (todos)")
        observacao = f"Meta Ads — alcance {alcance}, {cliques} cliques"
        novas.append([data, campanha, f"{float(gasto):.2f}", observacao])
        ja_importadas.add(chave)

    if novas:
        _acrescentar_csv(
            CAMINHO_INVESTIMENTOS,
            ["data", "produto", "valor_investido", "observacao"],
            novas,
        )
    print(f"Meta Ads ({caminho_xlsx}): {len(novas)} campanha(s)/conjunto(s) novo(s) importado(s).")


def main():
    if len(sys.argv) < 2:
        print("Uso: python importar_extratos.py arquivo1 [arquivo2 ...]")
        return
    for caminho in sys.argv[1:]:
        if caminho.lower().endswith(".csv"):
            importar_comissoes_shopee(caminho)
        elif caminho.lower().endswith(".xlsx"):
            importar_gasto_meta(caminho)
        else:
            print(f"Aviso: não sei importar {caminho} (esperava .csv ou .xlsx).")


if __name__ == "__main__":
    main()
