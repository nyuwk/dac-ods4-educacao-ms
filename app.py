"""Dashboard: evolução da educação na rede estadual de Mato Grosso do Sul (ODS 4)."""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.repository import RepositorioEscolar

AZUL = "#0B5CAD"
CINZA = "#B8C2CF"
CORES = {"Aprovação": "#0B5CAD", "Reprovação": "#E67E22", "Abandono": "#C0392B", "Cancelamento": "#8E44AD"}
FONTE = "Source Sans Pro, sans-serif"

st.set_page_config(page_title="Educação em MS — ODS 4", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
      .block-container { padding-top: 4.5rem; }
      .cabecalho { display: flex; gap: 1rem; align-items: center; margin-bottom: .25rem; }
      .ods { background: #C5192D; color: #fff; border-radius: 8px; padding: .55rem .8rem; text-align: center;
             font-weight: 700; line-height: 1.05; min-width: 74px; }
      .ods span { display: block; font-size: .62rem; font-weight: 600; letter-spacing: .04em; }
      .ods b { font-size: 1.7rem; }
      .cabecalho h1 { font-size: 1.85rem; margin: 0; padding: 0; color: #12233B; }
      .cabecalho p { margin: .15rem 0 0; color: #5B6472; font-size: .95rem; }
      div[data-testid="stMetric"] { background: #F7F9FC; }
      .nota { color: #5B6472; font-size: .85rem; }
      .equipe-titulo { font-weight: 600; font-size: .9rem; color: #12233B; margin-bottom: .55rem; }
      .membro { display: flex; align-items: center; gap: .6rem; margin-bottom: .5rem; }
      .membro span { font-size: .92rem; color: #1D2430; }
      .avatar { width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 3px #D9DEE6; }
      .equipe-curso { color: #5B6472; font-size: .78rem; margin-top: .35rem; }
    </style>
    <div class="cabecalho">
      <div class="ods"><span>ODS</span><b>4</b><span>EDUCAÇÃO</span></div>
      <div>
        <h1>Evolução da educação na rede estadual de Mato Grosso do Sul</h1>
        <p>Aprovação, reprovação, abandono e matrículas por município e ano · dados oficiais da SED/MS</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def pct(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")


def pp(v: float) -> str:
    return f"{v:+.1f}".replace(".", ",") + " p.p."


def nome(m: str) -> str:
    """CAMPO GRANDE -> Campo Grande; preposições em minúsculas."""
    t = m.title()
    for prep in ("Do", "Da", "De", "Dos", "Das"):
        t = t.replace(f" {prep} ", f" {prep.lower()} ")
    return t


def milhar(v: float) -> str:
    return f"{int(v):,}".replace(",", ".")


def estilo(fig: go.Figure, altura: int = 360) -> go.Figure:
    fig.update_layout(template="plotly_white", height=altura, separators=",.",
                      font=dict(family=FONTE, size=13, color="#1D2430"),
                      margin=dict(l=10, r=10, t=10, b=10), hoverlabel=dict(font_family=FONTE),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E9EDF3")
    return fig


@st.cache_resource
def repositorio() -> RepositorioEscolar:
    return RepositorioEscolar()


repo = repositorio()
anos = repo.anos()

with st.sidebar:
    st.header("Filtros")
    sel_mun = st.multiselect("Municípios", repo.municipios(), placeholder="Estado todo")
    ano_ini, ano_fim = st.select_slider("Período", options=anos, value=(anos[0], anos[-1]))
    st.divider()
    avatar = ("<svg class='avatar' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'>"
              "<rect width='40' height='40' fill='#CDD3DB'/>"
              "<circle cx='20' cy='15.5' r='7.5' fill='#FFFFFF'/>"
              "<ellipse cx='20' cy='38' rx='14' ry='11' fill='#FFFFFF'/></svg>")
    integrantes = ["Breno Salazar", "Maria Eduarda", "Manuela de Araujo", "Giovana Tiemi"]
    lista = "".join(f"<div class='membro'>{avatar}<span>{n}</span></div>" for n in integrantes)
    st.markdown(
        "<div class='equipe'><div class='equipe-titulo'>Desenvolvido pelo grupo</div>"
        f"{lista}<div class='equipe-curso'>UCDB · TADS · 4º semestre</div></div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        "<div class='nota'><b>Sobre os dados</b><br>Fonte: Portal de Dados Abertos de MS (SED/MS, CC-BY).<br>"
        "• 2025 não está disponível no portal.<br>"
        "• 2024 e 2026 são retratos do meio do ano letivo: têm matrículas, mas não taxas.<br>"
        "• O abandono é registrado como zero a partir de 2020; por isso também mostramos o cancelamento.</div>",
        unsafe_allow_html=True,
    )

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
recorte = "Estado todo" if not sel_mun else ", ".join(nome(m) for m in sel_mun[:3]) + ("…" if len(sel_mun) > 3 else "")

st.caption(f"Recorte: **{recorte}** · {ano_ini}–{ano_fim}")

aba_geral, aba_mun, aba_dados = st.tabs(["Visão geral", "Municípios", "Dados"])

# ---------------------------------------------------------------- Visão geral
with aba_geral:
    if len(completos) >= 2:
        a, b = completos.iloc[0], completos.iloc[-1]
        ini, fim = int(a.ano), int(b.ano)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Aprovação {fim}", pct(b["Aprovação"]), f"{pp(b['Aprovação'] - a['Aprovação'])} desde {ini}",
                  border=True)
        c2.metric(f"Reprovação {fim}", pct(b["Reprovação"]), f"{pp(b['Reprovação'] - a['Reprovação'])} desde {ini}",
                  delta_color="inverse", border=True)
        c3.metric(f"Cancelamento {fim}", pct(b["Cancelamento"]),
                  f"{pp(b['Cancelamento'] - a['Cancelamento'])} desde {ini}", delta_color="inverse", border=True)
        ult, pri = agg.iloc[-1], agg.iloc[0]
        var_mat = (ult.matriculas / pri.matriculas - 1) * 100
        c4.metric(f"Matrículas {int(ult.ano)}", milhar(ult.matriculas),
                  f"{var_mat:+.0f}% desde {int(pri.ano)}", delta_color="off", border=True)
    else:
        st.info("Escolha um período com pelo menos dois anos completos (2018 a 2023) para ver a variação.")

    if not completos.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Taxa de aprovação")
            fig = px.line(completos, x="ano", y="Aprovação", markers=True, text="Aprovação",
                          color_discrete_sequence=[AZUL], labels={"ano": "", "Aprovação": ""})
            posicoes = ["bottom center"] + ["top center"] * (len(completos) - 1)
            fig.update_traces(texttemplate="%{text:.1f}%", textposition=posicoes, line_width=3,
                              marker_size=9, hovertemplate="%{x}: %{y:.1f}%<extra></extra>")
            lo, hi = completos["Aprovação"].min(), completos["Aprovação"].max()
            fig.update_yaxes(range=[max(0, lo - 7), min(100, hi + 4)], ticksuffix="%")
            fig.update_xaxes(dtick=1)
            st.plotly_chart(estilo(fig), width="stretch")
        with col2:
            st.markdown("##### Reprovação, abandono e cancelamento")
            longo = completos.melt(id_vars="ano", value_vars=["Reprovação", "Abandono", "Cancelamento"],
                                   var_name="Indicador", value_name="Taxa")
            fig = px.line(longo, x="ano", y="Taxa", color="Indicador", markers=True,
                          color_discrete_map=CORES, labels={"ano": "", "Taxa": ""})
            fig.update_traces(line_width=3, marker_size=8, hovertemplate="%{x}: %{y:.1f}%<extra></extra>")
            fig.update_yaxes(rangemode="tozero", ticksuffix="%")
            fig.update_xaxes(dtick=1)
            st.plotly_chart(estilo(fig), width="stretch")
        st.markdown("<div class='nota'>Taxas calculadas só para anos completos (2018–2023), no padrão INEP: "
                    "Aprovados ÷ (Aprovados + Reprovados + Abandono).</div>", unsafe_allow_html=True)

    st.markdown("##### Matrículas por ano")
    barras = agg.assign(ano=agg["ano"].astype(str),
                        situacao=agg["completo"].map({True: "Ano completo", False: "Retrato parcial do ano"}))
    fig = px.bar(barras, x="ano", y="matriculas", text="matriculas", color="situacao",
                 color_discrete_map={"Ano completo": AZUL, "Retrato parcial do ano": CINZA},
                 labels={"matriculas": "", "ano": ""})
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False,
                      hovertemplate="%{x}: %{y:,.0f} matrículas<extra></extra>")
    fig.update_xaxes(type="category")
    st.plotly_chart(estilo(fig, 380), width="stretch")

# ---------------------------------------------------------------- Municípios
with aba_mun:
    anos_completos = sorted(df.loc[df["ano_completo"] == 1, "ano"].unique())
    if not anos_completos:
        st.info("O período escolhido não tem anos completos (2018 a 2023).")
    elif len(sel_mun) == 1:
        st.info("Com um único município selecionado, veja a tabela de escolas abaixo. "
                "Para comparar municípios, deixe o filtro vazio ou escolha vários.")
    else:
        ano_rank, ano_base = int(anos_completos[-1]), int(anos_completos[0])
        media = completos.loc[completos["ano"] == ano_rank, "Aprovação"].iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"##### Menor aprovação em {ano_rank}")
            rank = (df[df["ano"] == ano_rank].dropna(subset=["taxa_aprovacao"])
                    .sort_values("taxa_aprovacao").head(15))
            fig = go.Figure(go.Bar(x=rank["taxa_aprovacao"], y=rank["municipio"].map(nome), orientation="h",
                                   marker_color=AZUL, text=rank["taxa_aprovacao"], texttemplate="%{text:.1f}%",
                                   textposition="inside", insidetextanchor="end",
                                   textfont=dict(color="#FFFFFF"),
                                   hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
            fig.add_vline(x=media, line_dash="dash", line_color="#C0392B", line_width=2)
            fig.add_annotation(x=media, y=1, yref="paper", yanchor="bottom", showarrow=False,
                               text=f"média {pct(media)}", font=dict(color="#C0392B"))
            fig.update_yaxes(autorange="reversed")
            fig.update_xaxes(range=[0, 100], ticksuffix="%")
            fig = estilo(fig, 160 + 30 * len(rank))
            fig.update_layout(margin=dict(t=34))
            st.plotly_chart(fig, width="stretch")
        with col2:
            st.markdown(f"##### Maiores avanços na aprovação ({ano_base}→{ano_rank})")
            ini = df[df["ano"] == ano_base].set_index("municipio")["taxa_aprovacao"]
            fim = df[df["ano"] == ano_rank].set_index("municipio")["taxa_aprovacao"]
            dif = (fim - ini).dropna()
            var = dif.sort_values(ascending=False).head(15)
            if ano_base == ano_rank or var.empty:
                st.info("Escolha um período com pelo menos dois anos completos.")
            else:
                cores = ["#1E8449" if v >= 0 else "#C0392B" for v in var]
                fig = go.Figure(go.Bar(x=var.values, y=[nome(m) for m in var.index], orientation="h",
                                       marker_color=cores, text=var.values, texttemplate="%{text:+.1f} p.p.",
                                       textposition="outside", cliponaxis=False,
                                       hovertemplate="%{y}: %{x:+.1f} p.p.<extra></extra>"))
                fig.update_yaxes(autorange="reversed")
                fig.update_xaxes(ticksuffix=" p.p.", range=[min(0, var.min()) - 2, max(var.max(), 1) * 1.3])
                fig = estilo(fig, 160 + 30 * len(var))
                fig.update_layout(margin=dict(t=34))
                st.plotly_chart(fig, width="stretch")
                st.markdown(f"<div class='nota'>{int(dif.gt(0).sum())} de {dif.size} municípios aumentaram a "
                            f"aprovação entre {ano_base} e {ano_rank}.</div>", unsafe_allow_html=True)

    if len(sel_mun) == 1:
        st.markdown(f"##### Escolas de {nome(sel_mun[0])}")
        escolas = repo.escolas(sel_mun[0], ano_ini, ano_fim).rename(columns={
            "escola": "Escola", "ano": "Ano", "matriculas": "Matrículas", "aprovados": "Aprovados",
            "reprovados": "Reprovados", "abandono": "Abandono", "cancelados": "Cancelados",
            "transferidos": "Transferidos", "cursando": "Cursando"})
        st.dataframe(escolas, width="stretch", hide_index=True,
                     column_config={"Ano": st.column_config.NumberColumn(format="%d")})

# ---------------------------------------------------------------- Dados
with aba_dados:
    tabela = df.drop(columns=["cursando"]).rename(columns={
        "municipio": "Município", "ano": "Ano", "escolas": "Escolas", "matriculas": "Matrículas",
        "aprovados": "Aprovados", "reprovados": "Reprovados", "abandono": "Abandono", "cancelados": "Cancelados",
        "transferidos": "Transferidos", "ano_completo": "Ano completo", "taxa_aprovacao": "Aprovação (%)",
        "taxa_reprovacao": "Reprovação (%)", "taxa_abandono": "Abandono (%)", "taxa_cancelamento": "Cancelamento (%)"})
    tabela["Município"] = tabela["Município"].map(nome)
    tabela["Ano completo"] = tabela["Ano completo"].map({1: "Sim", 0: "Não"})
    for c in ["Aprovação (%)", "Reprovação (%)", "Abandono (%)", "Cancelamento (%)"]:
        tabela[c] = tabela[c].map(lambda v: "—" if v != v or v is None else f"{v:.1f}".replace(".", ","))
    inteiros = ["Escolas", "Matrículas", "Aprovados", "Reprovados", "Abandono", "Cancelados", "Transferidos"]
    st.dataframe(tabela, width="stretch", hide_index=True, height=480,
                 column_config={"Ano": st.column_config.NumberColumn(format="%d"),
                                **{c: st.column_config.NumberColumn(format="localized") for c in inteiros}})
    st.markdown("<div class='nota'>— = ano incompleto (2024 e 2026), sem taxas de rendimento.</div>",
                unsafe_allow_html=True)
    st.download_button("Baixar CSV", df.to_csv(index=False).encode("utf-8-sig"), "indicadores_ms.csv",
                       type="primary")
