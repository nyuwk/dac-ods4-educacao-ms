import plotly.express as px
import streamlit as st

from src.repository import RepositorioEscolar

st.set_page_config(page_title="Educação em MS — ODS 4", layout="wide")
st.title("Evolução da educação na rede estadual de Mato Grosso do Sul")
st.caption(
    "Fonte: Portal de Dados Abertos de MS / SED (licença CC-BY). "
    "2025 não está disponível no portal. 2024 e 2026 são retratos do meio do ano letivo: "
    "mostram matrículas, mas não têm taxas de rendimento."
)


@st.cache_resource
def repositorio() -> RepositorioEscolar:
    return RepositorioEscolar()


repo = repositorio()
anos = repo.anos()

with st.sidebar:
    st.header("Filtros")
    sel_mun = st.multiselect("Municípios (vazio = estado todo)", repo.municipios())
    ano_ini, ano_fim = st.select_slider("Período", options=anos, value=(anos[0], anos[-1]))

df = repo.indicadores(sel_mun, ano_ini, ano_fim)
if df.empty:
    st.warning("Nenhum dado para os filtros escolhidos.")
    st.stop()

# Agregado por ano (estado todo ou municípios escolhidos)
soma = ["matriculas", "aprovados", "reprovados", "abandono", "cancelados", "cursando"]
agg = df.groupby("ano", as_index=False)[soma].sum()
base = agg["aprovados"] + agg["reprovados"] + agg["abandono"]
agg["completo"] = agg["cursando"] < 0.05 * agg["matriculas"]
agg["Aprovação"] = (agg["aprovados"] / base * 100).where(agg["completo"])
agg["Reprovação"] = (agg["reprovados"] / base * 100).where(agg["completo"])
agg["Abandono"] = (agg["abandono"] / base * 100).where(agg["completo"])
agg["Cancelamento"] = (agg["cancelados"] / (base + agg["cancelados"]) * 100).where(agg["completo"])
completos = agg[agg["completo"]]

def pct(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")


def pp(v: float) -> str:
    return f"{v:+.1f}".replace(".", ",") + " p.p."


# Cartões: primeiro e último ano completos do período
if len(completos) >= 2:
    a, b = completos.iloc[0], completos.iloc[-1]
    ini, fim = int(a.ano), int(b.ano)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Aprovação {fim}", pct(b["Aprovação"]), f"{pp(b['Aprovação'] - a['Aprovação'])} desde {ini}")
    c2.metric(f"Reprovação {fim}", pct(b["Reprovação"]),
              f"{pp(b['Reprovação'] - a['Reprovação'])} desde {ini}", delta_color="inverse")
    c3.metric(f"Cancelamento {fim}", pct(b["Cancelamento"]),
              f"{pp(b['Cancelamento'] - a['Cancelamento'])} desde {ini}", delta_color="inverse")
    ult = agg.iloc[-1]
    c4.metric(f"Matrículas {int(ult.ano)}", f"{int(ult.matriculas):,}".replace(",", "."))
else:
    st.info("Escolha um período com pelo menos dois anos completos (2018 a 2023) para ver a variação.")

if not completos.empty:
    st.subheader("Taxas de rendimento por ano (anos completos)")
    longo = completos.melt(id_vars="ano", value_vars=["Aprovação", "Reprovação", "Abandono", "Cancelamento"],
                           var_name="Indicador", value_name="Taxa (%)")
    fig = px.line(longo, x="ano", y="Taxa (%)", color="Indicador", markers=True, labels={"ano": "Ano"})
    fig.update_xaxes(dtick=1)
    fig.update_layout(separators=",.")
    st.plotly_chart(fig, width="stretch")
    st.caption("O portal registra abandono igual a zero em todas as escolas a partir de 2020. "
               "Cancelamento (matrículas canceladas) é exibido como indicador complementar.")

st.subheader("Matrículas por ano")
barras = agg.assign(ano=agg["ano"].astype(str))  # eixo por categoria: 2025 não aparece como coluna vazia
fig = px.bar(barras, x="ano", y="matriculas", text="matriculas", labels={"matriculas": "Matrículas", "ano": "Ano"})
fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
fig.update_xaxes(type="category")
fig.update_layout(separators=",.")
st.plotly_chart(fig, width="stretch")
st.caption("Não há arquivo de 2025 no portal. 2024 e 2026 são retratos do meio do ano letivo.")

anos_completos = sorted(df.loc[df["ano_completo"] == 1, "ano"].unique())
if anos_completos and len(sel_mun) != 1:
    ano_rank = int(anos_completos[-1])
    rank = df[df["ano"] == ano_rank].dropna(subset=["taxa_aprovacao"]).sort_values("taxa_aprovacao").head(15)
    st.subheader(f"Municípios com menor aprovação em {ano_rank}")
    fig = px.bar(rank, x="taxa_aprovacao", y="municipio", orientation="h", text="taxa_aprovacao",
                 labels={"taxa_aprovacao": "Aprovação (%)", "municipio": ""})
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_yaxes(autorange="reversed")  # o pior fica em cima
    fig.update_xaxes(range=[0, 100])
    fig.update_layout(separators=",.", height=120 + 32 * len(rank))
    st.plotly_chart(fig, width="stretch")

if len(sel_mun) == 1:
    st.subheader(f"Escolas de {sel_mun[0]}")
    st.dataframe(repo.escolas(sel_mun[0], ano_ini, ano_fim), width="stretch")

st.subheader("Dados filtrados")
st.dataframe(df, width="stretch")
st.download_button("Baixar CSV", df.to_csv(index=False).encode("utf-8-sig"), "indicadores_ms.csv")
