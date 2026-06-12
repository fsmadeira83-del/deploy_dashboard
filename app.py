import streamlit as st
import pandas as pd

# --------------------------------------------------
# Configuração da página
# --------------------------------------------------
st.set_page_config(
    page_title="Dados Económico-Financeiros Economia Portuguesa 2006-2024", # O título que mostra na tab do browser
    layout="wide" # A opção "centered" coloca a página numa coluna central
)

st.title("📊 Dados Económico-Financeiros Economia Portuguesa 2006-2024")
st.markdown("Dashboard de Volume de Negócios Médio")

# --------------------------------------------------
# Carregamento dos dados
# --------------------------------------------------
# Esta linha é extremamente importante. 
# Ao ler o ficheiro a primeira vez, a app guarda os dados em memória (cache)
# Assim, sempre que houver interações com o dashboard (ex: mudar um filtro), não é necessário ler o ficheiro csv novamente
@st.cache_data 
def load_data():
    file_name = "BaseDadosFinal.xlxs"
    df = pd.read_csv(file_name, parse_dates=["Order Date"])
    return df

df = load_data()

# --------------------------------------------------
# Definir um Sidebar com filtros
# --------------------------------------------------
st.sidebar.header("Filtros")

# Filtro de Sector de Atividade
sorted_SectorAtividade = sorted(df["SectorAtividade"].unique())
SectorAtividade = st.sidebar.multiselect(
    "Sector de Atividade",
    options=sorted_SectorAtividade,
    default=sorted_SectorAtividade
)

# Filtro de Tamanho de Empresa
sorted_TamanhoEmpresa = sorted(df["TamanhoEmpresa"].unique())
TamanhoEmpresa = st.sidebar.multiselect(
    "Tamanho de Empresa",
    options=sorted_TamanhoEmpresa,
    default=sorted_TamanhoEmpresa
)

# Filtro de Ano
years = sorted(df["Ano"].dt.year.unique())
year_range = st.sidebar.slider(
    "Ano",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

# Aplicar filtros
filtered_df = df[
    (df["SectorAtividade"].isin(SectorAtividade)) &
    (df["TamanhoEmpresa"].isin(TamanhoEmpresa)) &
    (df["Ano"].dt.year.between(year_range[0], year_range[1]))
]

# --------------------------------------------------
# Parte superior com KPIs
# --------------------------------------------------
media_VendasServicos = filtered_df["VendasServicos"].mean()
media_ResultadoLiquido = filtered_df["RL"].mean()
num_empresas = filtered_df["NºEmpresas"].sum()

# Vamos dividir a área em 3 colunas para mostrar os KPIs lado a lado
col1, col2, col3 = st.columns(3)
col1.metric("💰 Vendas Médias", f"${media_VendasServicos:,.0f}")
col2.metric("📈 Lucro Médio", f"${media_ResultadoLiquido:,.0f}")
col3.metric("🧾 Nº de Empresas", num_empresas)

st.divider()

# ------------------------------------------------------------------
# Gráfico 1 - Vendas ao longo do tempo (cada categoria é uma série)
# ------------------------------------------------------------------
st.subheader("📅 Vendas ao longo do tempo por categoria")

# Agrupar a soma de Sales em cada mês por Category
sales_over_time = (
    filtered_df
    .groupby(
        [pd.Grouper(key="Order Date", freq="ME"), "Category"]
    )["Sales"]
    .sum()
    .reset_index()
)

# Criar uma pivot table
sales_pivot = sales_over_time.pivot(
    index="Order Date",
    columns="Category",
    values="Sales"
)

st.line_chart(sales_pivot)

# --------------------------------------------------
# Gráfico 2 - Vendas por Região
# --------------------------------------------------
st.subheader("🌍 Vendas por Região")

# Agrupar a soma de Sales por Region
sales_by_region = (
    filtered_df
    .groupby("Region")["Sales"]
    .sum()
)

st.bar_chart(sales_by_region)

st.divider()

# --------------------------------------------------
# Table - Top produtos
# --------------------------------------------------
st.subheader("🏆 Top 10 produtos por vendas")

# Agrupar a soma de Sales por Product Name, ordenar e mostrar os top 10
top_products = (
    filtered_df
    .groupby("Product Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.dataframe(top_products)

# --------------------------------------------------
# Rodapé
# --------------------------------------------------
st.caption("Dados: Sample Superstore")
