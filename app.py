import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="Análise de Produção 2025",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }
h1,h2,h3 { font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.5px; }

.main { background-color: #0f1117; }
.block-container { padding: 1.5rem 2rem; }

.kpi-card {
    background: linear-gradient(135deg, #1a1d27 0%, #22263a 100%);
    border: 1px solid #2e3350;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.kpi-label { color: #8b93b5; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.3rem; }
.kpi-value { color: #e8ecff; font-family: 'Barlow Condensed', sans-serif; font-size: 2.4rem; font-weight: 700; line-height: 1; }
.kpi-sub   { color: #5c6380; font-size: 0.72rem; margin-top: 0.25rem; }

.kpi-green  .kpi-value { color: #4ade80; }
.kpi-blue   .kpi-value { color: #60a5fa; }
.kpi-amber  .kpi-value { color: #fbbf24; }
.kpi-red    .kpi-value { color: #f87171; }
.kpi-purple .kpi-value { color: #c084fc; }

.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.1rem; font-weight: 600; color: #8b93b5;
    text-transform: uppercase; letter-spacing: 2px;
    border-left: 3px solid #3b5bdb; padding-left: 0.7rem;
    margin: 1.5rem 0 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
import io as _io

def _parse(df: pd.DataFrame) -> pd.DataFrame:
    df["Op_Codigo"] = df["Operação"].str.extract(r"^(\d+)")[0].astype(str).str.strip()
    df["Data Realização"] = pd.to_datetime(df["Data Realização"], errors="coerce")
    df["Mes"] = df["Data Realização"].dt.to_period("M").astype(str)
    df["Semana"] = df["Data Realização"].dt.isocalendar().week.astype(str)
    df["Total Minutos"] = pd.to_numeric(df["Total Minutos"], errors="coerce").fillna(0)
    df["Metros Lineares"] = pd.to_numeric(df["Metros Lineares"], errors="coerce").fillna(0)
    df["M2"] = pd.to_numeric(df["M2"], errors="coerce").fillna(0)
    return df

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return _parse(pd.read_excel(path))

@st.cache_data
def load_uploaded(data: bytes) -> pd.DataFrame:
    return _parse(pd.read_excel(_io.BytesIO(data)))

# ── POWER BI FORMULAS ────────────────────────────────────────────────────────
# Códigos produtivos: 035, 036  (impressão turno 1 e 2)
PROD_CODES = {"035", "036"}

# Códigos excluídos do cálculo de Tempo Parado (Image 4)
# NOT IN {002,007,008,025,035,036,037,040,001,021,028}
PARADO_EXCL = {"002","007","008","025","035","036","037","040","001","021","028"}

def calc_total_horas_produtivas(df: pd.DataFrame) -> float:
    """Image 3/5/6 – CALCULATE SUM tempo where Op in 35 OR 36, /60"""
    mask = df["Op_Codigo"].isin(PROD_CODES)
    return df.loc[mask, "Total Minutos"].sum() / 60

def calc_tempo_parado(df: pd.DataFrame) -> float:
    """Image 4 – CALCULATE SUM tempo, REMOVEFILTERS Op, NOT IN exclusion list, /60"""
    mask = ~df["Op_Codigo"].isin(PARADO_EXCL)
    return df.loc[mask, "Total Minutos"].sum() / 60

def calc_eficiencia(df: pd.DataFrame) -> float:
    """Image 1 – DIVIDE(Total Horas Produtivas, Total Horas Produtivas + Tempo Parado, 0)"""
    prod = calc_total_horas_produtivas(df)
    parado = calc_tempo_parado(df)
    denom = prod + parado
    return prod / denom if denom > 0 else 0

def calc_percentual_parado(df: pd.DataFrame) -> float:
    """Image 2 – DIVIDE(Tempo Parado, Total Horas Produtivas + Tempo Parado, 0)"""
    prod = calc_total_horas_produtivas(df)
    parado = calc_tempo_parado(df)
    denom = prod + parado
    return parado / denom if denom > 0 else 0

def kpi_card(label: str, value: str, sub: str = "", color: str = "") -> str:
    cls = f"kpi-{color}" if color else ""
    return f"""
    <div class="kpi-card {cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""

def fmt_horas(h: float) -> str:
    hh = int(h)
    mm = int((h - hh) * 60)
    return f"{hh:,}h {mm:02d}m"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 Produção")
    uploaded = st.file_uploader("📂 Carregar planilha", type=["xlsx"])
    st.markdown("---")

if uploaded:
    df_raw = load_uploaded(uploaded.read())
else:
    try:
        df_raw = load_data("TABELA_DE_APONTAMENTOS.xlsx")
    except Exception:
        st.warning("⚠️ Envie a planilha TABELA_DE_APONTAMENTOS.xlsx pelo painel lateral.")
        st.stop()

with st.sidebar:
    maquinas = sorted(df_raw["Máquina"].dropna().unique())
    sel_maquinas = st.multiselect("🔧 Máquina", maquinas, default=maquinas)

    meses = sorted(df_raw["Mes"].dropna().unique())
    sel_meses = st.multiselect("📅 Mês", meses, default=meses)

    operadores = sorted(df_raw["Operador"].dropna().unique())
    sel_operadores = st.multiselect("👷 Operador", operadores, default=operadores)

df = df_raw[
    df_raw["Máquina"].isin(sel_maquinas) &
    df_raw["Mes"].isin(sel_meses) &
    df_raw["Operador"].isin(sel_operadores)
].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='color:#e8ecff;margin-bottom:0'>📊 Análise de Produção 2025</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#5c6380;margin-top:0'>{len(df):,} registros | {df['Data Realização'].min().date()} → {df['Data Realização'].max().date()}</p>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
prod_h   = calc_total_horas_produtivas(df)
parado_h = calc_tempo_parado(df)
efic     = calc_eficiencia(df)
pct_par  = calc_percentual_parado(df)
total_ml = df.loc[df["Op_Codigo"].isin(PROD_CODES), "Metros Lineares"].sum()
total_m2 = df.loc[df["Op_Codigo"].isin(PROD_CODES), "M2"].sum()

st.markdown('<div class="section-title">KPIs Principais</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.markdown(kpi_card("Eficiência", f"{efic:.1%}", "Horas Prod / Total", "green"), unsafe_allow_html=True)
c2.markdown(kpi_card("% Parado",   f"{pct_par:.1%}", "Tempo Parado / Total", "amber"), unsafe_allow_html=True)
c3.markdown(kpi_card("Hrs Produtivas", fmt_horas(prod_h), "Op 35 + 36", "blue"), unsafe_allow_html=True)
c4.markdown(kpi_card("Hrs Parado",     fmt_horas(parado_h), "Demais operações", "red"), unsafe_allow_html=True)
c5.markdown(kpi_card("Metros Lineares", f"{total_ml:,.0f}", "produção impressão", "purple"), unsafe_allow_html=True)
c6.markdown(kpi_card("M²", f"{total_m2:,.0f}", "produção impressão", "blue"), unsafe_allow_html=True)

# ── EVOLUÇÃO MENSAL ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Evolução Mensal</div>', unsafe_allow_html=True)

monthly = []
for mes, grp in df.groupby("Mes"):
    monthly.append({
        "Mes": mes,
        "Horas Produtivas": calc_total_horas_produtivas(grp),
        "Tempo Parado":     calc_tempo_parado(grp),
        "Eficiência (%)":   calc_eficiencia(grp) * 100,
    })
df_monthly = pd.DataFrame(monthly).sort_values("Mes")

fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])
fig_monthly.add_trace(go.Bar(x=df_monthly["Mes"], y=df_monthly["Horas Produtivas"],
    name="Horas Produtivas", marker_color="#3b82f6"), secondary_y=False)
fig_monthly.add_trace(go.Bar(x=df_monthly["Mes"], y=df_monthly["Tempo Parado"],
    name="Tempo Parado", marker_color="#f87171"), secondary_y=False)
fig_monthly.add_trace(go.Scatter(x=df_monthly["Mes"], y=df_monthly["Eficiência (%)"],
    name="Eficiência %", mode="lines+markers", line=dict(color="#4ade80", width=2.5),
    marker=dict(size=7)), secondary_y=True)
fig_monthly.update_layout(barmode="group", template="plotly_dark",
    paper_bgcolor="#1a1d27", plot_bgcolor="#1a1d27", height=320,
    legend=dict(orientation="h", y=1.1), margin=dict(t=10,b=40,l=0,r=0))
fig_monthly.update_yaxes(title_text="Horas", secondary_y=False)
fig_monthly.update_yaxes(title_text="Eficiência (%)", range=[0,110], secondary_y=True)
st.plotly_chart(fig_monthly, use_container_width=True)

# ── EFICIÊNCIA POR MÁQUINA  +  TOP OPERAÇÕES PARADO ──────────────────────────
st.markdown('<div class="section-title">Detalhamento</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Eficiência por Máquina")
    maq_data = []
    for maq, grp in df.groupby("Máquina"):
        maq_data.append({
            "Máquina": maq,
            "Eficiência": calc_eficiencia(grp) * 100,
            "H Prod": calc_total_horas_produtivas(grp),
            "H Parado": calc_tempo_parado(grp),
        })
    df_maq = pd.DataFrame(maq_data).sort_values("Eficiência", ascending=True)
    colors = ["#f87171" if e < 50 else "#fbbf24" if e < 70 else "#4ade80" for e in df_maq["Eficiência"]]
    fig_maq = go.Figure(go.Bar(
        x=df_maq["Eficiência"], y=df_maq["Máquina"],
        orientation="h", marker_color=colors,
        text=df_maq["Eficiência"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside"
    ))
    fig_maq.update_layout(template="plotly_dark", paper_bgcolor="#1a1d27",
        plot_bgcolor="#1a1d27", height=400, margin=dict(t=10,b=20,l=0,r=60),
        xaxis=dict(range=[0,110], title="Eficiência (%)"))
    st.plotly_chart(fig_maq, use_container_width=True)

with col_b:
    st.markdown("#### Composição do Tempo Parado por Operação")
    df_parado = df[~df["Op_Codigo"].isin(PARADO_EXCL)].copy()
    op_agg = df_parado.groupby("Operação")["Total Minutos"].sum().reset_index()
    op_agg["Horas"] = op_agg["Total Minutos"] / 60
    op_agg = op_agg.sort_values("Horas", ascending=False).head(12)
    fig_op = px.bar(op_agg, x="Horas", y="Operação", orientation="h",
        color="Horas", color_continuous_scale=["#fbbf24","#f87171","#dc2626"],
        text=op_agg["Horas"].apply(lambda x: f"{x:.1f}h"))
    fig_op.update_traces(textposition="outside")
    fig_op.update_layout(template="plotly_dark", paper_bgcolor="#1a1d27",
        plot_bgcolor="#1a1d27", height=400, margin=dict(t=10,b=20,l=0,r=60),
        coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_op, use_container_width=True)

# ── PRODUÇÃO IMPRESSÃO ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Produção — Impressão (Op 35 + 36)</div>', unsafe_allow_html=True)
col_c, col_d = st.columns(2)

df_imp = df[df["Op_Codigo"].isin(PROD_CODES)].copy()

with col_c:
    ml_mes = df_imp.groupby("Mes")["Metros Lineares"].sum().reset_index()
    fig_ml = px.area(ml_mes, x="Mes", y="Metros Lineares",
        title="Metros Lineares por Mês",
        color_discrete_sequence=["#3b82f6"])
    fig_ml.update_layout(template="plotly_dark", paper_bgcolor="#1a1d27",
        plot_bgcolor="#1a1d27", height=280, margin=dict(t=30,b=20))
    st.plotly_chart(fig_ml, use_container_width=True)

with col_d:
    ml_maq = df_imp.groupby("Máquina")["Metros Lineares"].sum().reset_index().sort_values("Metros Lineares", ascending=False)
    fig_ml2 = px.bar(ml_maq, x="Máquina", y="Metros Lineares",
        title="Metros Lineares por Máquina",
        color="Metros Lineares", color_continuous_scale=["#1d4ed8","#60a5fa"])
    fig_ml2.update_layout(template="plotly_dark", paper_bgcolor="#1a1d27",
        plot_bgcolor="#1a1d27", height=280, margin=dict(t=30,b=20),
        coloraxis_showscale=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_ml2, use_container_width=True)

# ── TABELA DETALHE ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Resumo por Máquina × Mês</div>', unsafe_allow_html=True)

pivot_rows = []
for (maq, mes), grp in df.groupby(["Máquina","Mes"]):
    pivot_rows.append({
        "Máquina": maq, "Mês": mes,
        "H Produtivas": round(calc_total_horas_produtivas(grp), 2),
        "H Parado":     round(calc_tempo_parado(grp), 2),
        "Eficiência":   f"{calc_eficiencia(grp)*100:.1f}%",
        "Metros Lin.":  round(df.loc[(df["Máquina"]==maq)&(df["Mes"]==mes)&(df["Op_Codigo"].isin(PROD_CODES)),"Metros Lineares"].sum(), 0),
        "M²":           round(df.loc[(df["Máquina"]==maq)&(df["Mes"]==mes)&(df["Op_Codigo"].isin(PROD_CODES)),"M2"].sum(), 0),
    })

df_pivot = pd.DataFrame(pivot_rows).sort_values(["Máquina","Mês"])
st.dataframe(df_pivot, use_container_width=True, height=300,
             column_config={"Eficiência": st.column_config.TextColumn("Eficiência"),
                            "Metros Lin.": st.column_config.NumberColumn(format="%.0f"),
                            "M²": st.column_config.NumberColumn(format="%.0f")})

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><p style='color:#2e3350;text-align:center;font-size:0.75rem'>Análise de Produção 2025 · Fórmulas baseadas em Power BI DAX</p>", unsafe_allow_html=True)
