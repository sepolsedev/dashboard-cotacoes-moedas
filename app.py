"""Dashboard acadêmico: dólar, euro e libra em reais."""
import pandas as pd
import streamlit as st
from api_moedas import MOEDAS
from banco import criar_tabela, ler_cotacoes
from coleta import executar_coleta

st.set_page_config(page_title="Cotações de Moedas", page_icon="💱", layout="wide")
st.title("Dashboard de Cotações de Moedas")
st.subheader("Dólar, euro e libra em relação ao real brasileiro")
st.write("Projeto acadêmico de ETL com API pública, SQLite, Pandas e Streamlit.")

# A coleta acontece por ação do usuário, sem consultas repetidas a cada filtro.
if st.sidebar.button("Coletar / atualizar dados"):
    with st.spinner("Consultando a AwesomeAPI..."):
        for sucesso, mensagem in executar_coleta():
            if sucesso:
                st.sidebar.success(mensagem)
            else:
                st.sidebar.error(mensagem)

criar_tabela()
df = ler_cotacoes()
if df.empty:
    st.info("Clique em 'Coletar / atualizar dados' para buscar o histórico das três moedas.")
    st.stop()

df["data"] = pd.to_datetime(df["data"])
moedas_disponiveis = [m for m in MOEDAS if m in df["moeda"].unique()]
moeda = st.sidebar.selectbox(
    "Moeda para análise", moedas_disponiveis, format_func=lambda m: MOEDAS[m]
)
campo = st.sidebar.selectbox("Tipo de cotação", ["compra", "venda"])
base = df[df["moeda"] == moeda]
periodo = st.sidebar.date_input(
    "Período", value=(base["data"].min().date(), base["data"].max().date()),
    min_value=base["data"].min().date(), max_value=base["data"].max().date(),
)
if len(periodo) != 2:
    st.info("Selecione as duas datas do período.")
    st.stop()

# Os indicadores e gráficos usam o mesmo recorte de datas.
inicio, fim = map(pd.Timestamp, periodo)
recorte = df[df["data"].between(inicio, fim)]
dados = recorte[recorte["moeda"] == moeda].sort_values("data")
if dados.empty:
    st.warning("Não há registros dessa moeda no período selecionado.")
    st.stop()


def reais(valor):
    return "R$ " + f"{valor:,.4f}".replace(",", "_").replace(".", ",").replace("_", ".")


serie = dados[campo]
st.caption(f"Cotação de {campo}: reais por 1 unidade de {MOEDAS[moeda]}.")
colunas = st.columns(5)
for coluna, rotulo, valor in zip(
    colunas,
    ["Mais recente no período", "Maior cotação", "Menor cotação", "Média", "Mediana"],
    [serie.iloc[-1], serie.max(), serie.min(), serie.mean(), serie.median()],
):
    coluna.metric(rotulo, reais(valor))

st.subheader(f"Evolução da cotação — {MOEDAS[moeda]}")
st.line_chart(dados.set_index("data")[[campo]], height=430)
st.caption("Cada ponto representa uma cotação diária disponível, e não a máxima ou mínima intradiária.")
st.subheader("Comparação das três moedas em reais")
comparacao = recorte.pivot(index="data", columns="moeda", values=campo)
st.line_chart(comparacao.rename(columns=MOEDAS), height=350)

st.subheader("Dados usados na análise")
st.dataframe(dados[["data", "moeda", "compra", "venda"]], hide_index=True)
st.download_button(
    "Baixar tabela em CSV",
    dados.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
    file_name="cotacoes_filtradas.csv", mime="text/csv",
)
st.caption(
    "Fonte: AwesomeAPI. A cotação mais recente pode ser parcial. Datas sem registro "
    "não são preenchidas; média e mediana consideram apenas os registros disponíveis. "
    "O histórico permanece salvo no SQLite após novas coletas."
)
st.markdown("[Documentação da fonte](https://docs.awesomeapi.com.br/api-de-moedas)")
