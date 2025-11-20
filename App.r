import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------
# Carregar dados (já limpos)
# -----------------------------------------
df = tabelao_2024_limpeza_final.copy()

st.set_page_config(page_title="Dashboard TJs 2024", layout="wide")

st.title("📊 Dashboard Tribunais de Justiça – 2024")
st.write("Média salarial por estado e quantidade de magistrados")

# -----------------------------------------
# Pré-processamento
# -----------------------------------------

# Considerar salário como soma de todas as categorias (ou apenas 'valor')
if "valor" in df.columns:
    df["salario"] = df["valor"]
else:
    st.error("Coluna 'valor' não encontrada no dataframe.")

# Normalizar nome do cargo para detectar magistrados
df["cargo_lower"] = df["cargo"].str.lower()

is_magistrado = df["cargo_lower"].str.contains("juiz") | df["cargo_lower"].str.contains("desembargador")

# -----------------------------------------
# Cálculo: média salarial por estado
# -----------------------------------------
media_estado = (
    df.groupby("tribunal")["salario"]
    .mean()
    .reset_index()
    .rename(columns={"salario": "media_salarial"})
)

# -----------------------------------------
# Cálculo: quantidade de magistrados
# -----------------------------------------
qtd_magistrados = (
    df[is_magistrado]
    .groupby("tribunal")["nome"]
    .nunique()
    .reset_index()
    .rename(columns={"nome": "magistrados"})
)

# -----------------------------------------
# Mesclar indicadores
# -----------------------------------------
indicadores = media_estado.merge(qtd_magistrados, on="tribunal", how="left")
indicadores["magistrados"] = indicadores["magistrados"].fillna(0).astype(int)

# -----------------------------------------
# Layout do Dashboard
# -----------------------------------------
col1, col2 = st.columns(2)

# KPI 1 – Média global
col1.metric(
    "💰 Média salarial geral",
    f"R$ {df['salario'].mean():,.2f}"
)

# KPI 2 – Total de magistrados
col2.metric(
    "⚖️ Total de magistrados",
    int(qtd_magistrados["magistrados"].sum())
)

st.markdown("---")

# -----------------------------------------
# Gráfico: média por estado
# -----------------------------------------
st.subheader("🏛️ Média salarial por Tribunal")

fig1 = px.bar(
    indicadores,
    x="tribunal",
    y="media_salarial",
    text="media_salarial",
    title="Média Salarial por Tribunal",
)
fig1.update_traces(texttemplate="R$ %{text:.2f}", textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------------------
# Gráfico: quantidade de magistrados
# -----------------------------------------
st.subheader("⚖️ Quantidade de Magistrados por Tribunal")

fig2 = px.bar(
    indicadores,
    x="tribunal",
    y="magistrados",
    text="magistrados",
    title="Magistrados por Tribunal",
)
fig2.update_traces(textposition="outside")
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------
# Tabela final
# -----------------------------------------
st.subheader("📄 Tabela de Indicadores Consolidada")
st.dataframe(indicadores)