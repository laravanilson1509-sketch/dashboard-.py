import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Configuração de Estilo e Layout
st.set_page_config(page_title="INOVAFLEX - Gestão Total", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    [data-testid="stHeader"] { background-color: #000000; }
    .metric-card {
        background-color: #1a1a1a;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 4px;
        text-align: center;
    }
    .metric-label { font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { font-size: 20px; font-weight: bold; }
    .head-ops { background-color: #00c853; color: black; }
    .head-parado { background-color: #d50000; color: white; }
    .head-prod { background-color: #304ffe; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: Upload e Filtros
st.sidebar.title("FILTROS DE VISÃO")
uploaded_file = st.sidebar.file_uploader("📁 Upload Tabela INOVAFLEX", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    def buscar(lista, colunas):
        for p in lista:
            for c in colunas:
                if p.lower() == c.lower().strip(): return c
        return colunas[0]

    c_maq = buscar(["Máquina", "Maquina"], df.columns)
    c_op = buscar(["Operação", "Operacao"], df.columns)
    c_temp = buscar(["Total Minutos", "Tempo Total"], df.columns)
    c_met = buscar(["Metros Lineares", "Metros"], df.columns)
    c_operador = buscar(["Operador"], df.columns)
    c_apara = buscar(["M2", "Apara", "Metros Apara"], df.columns)
    c_data = buscar(["Data Realização", "Data", "Op Data de Início"], df.columns)

    if c_data:
        df[c_data] = pd.to_datetime(df[c_data], errors='coerce')
        df = df.dropna(subset=[c_data])
        min_d, max_d = df[c_data].min().date(), df[c_data].max().date()
        date_sel = st.sidebar.date_input("🗓️ Selecionar Período", [min_d, max_d])
        if len(date_sel) == 2:
            df = df[(df[c_data].dt.date >= date_sel[0]) & (df[c_data].dt.date <= date_sel[1])]

    maqs_disp = sorted(df[c_maq].unique().tolist())
    sel_maqs = st.sidebar.multiselect("🏗️ Máquinas", options=maqs_disp, default=maqs_disp)
    ops_disp = sorted(df[c_operador].unique().tolist())
    sel_ops = st.sidebar.multiselect("👤 Operadores", options=ops_disp, default=ops_disp)

    df_filtered = df[(df[c_maq].isin(sel_maqs)) & (df[c_operador].isin(sel_ops))]

    def criar_gauge_clean(titulo, valor, cor="#00ff00"):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = valor,
            number = {'suffix': "%", 'font': {'size': 30, 'color': "#e1ad01"}, 'valueformat': ',.3f'},
            title = {'text': titulo, 'font': {'size': 14, 'color': "white"}},
            gauge = {
                'axis': {'range': [0, 100], 'tickformat': ',.3f', 'tickcolor': "white"},
                'bar': {'color': cor},
                'bgcolor': "#e0e0e0",
            }
        ))
        fig.update_layout(height=200, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor="#262626")
        return fig

    tab_horas, tab_operadores, tab_metas = st.tabs(["PRODUÇÃO HORAS", "PRODUÇÃO OPERADORES", "META"])

    with tab_horas:
        st.markdown("<h3 style='text-align: center;'>Dashboard de Produção <span style='color:blue'>INOVA</span> <span style='color:red'>FLEX</span> <span style='color:blue'>PRODUÇÃO HORAS</span></h3>", unsafe_allow_html=True)
        
        k1, k2, k3, k4, k5 = st.columns([1.2, 1.2, 1, 1, 1])
        with k1: st.plotly_chart(criar_gauge_clean("DISPONIBILIDADE", 53.610), use_container_width=True)
        with k2: st.plotly_chart(criar_gauge_clean("TEMPO PARADO %", 46.390, "#d50000"), use_container_width=True)
        with k3: st.markdown(f'<div class="metric-card head-ops"><div class="metric-label">QTD DE OPS</div><div class="metric-value">{len(df_filtered):,.0f}</div></div>', unsafe_allow_html=True)
        with k4: st.markdown(f'<div class="metric-card head-parado"><div class="metric-label">TEMPO PARADO</div><div class="metric-value">39,000 h</div></div>', unsafe_allow_html=True)
        with k5: st.markdown(f'<div class="metric-card head-prod"><div class="metric-label">TEMPO PRODUÇÃO</div><div class="metric-value">{(df_filtered[c_temp].sum()/60):,.3f} h</div></div>', unsafe_allow_html=True)

        c_h1, c_h2 = st.columns(2)

        # ===== NOVO: cálculo único de altura =====
        data_maq = df_filtered.groupby(c_maq)[c_temp].sum().reset_index().sort_values(c_temp, ascending=True)
        data_op = df_filtered.groupby(c_op)[c_temp].sum().reset_index().sort_values(c_temp, ascending=True)

        max_linhas = max(len(data_maq), len(data_op))
        altura_padrao = max(350, max_linhas * 35)
        # ========================================

        with c_h1:
            st.markdown("<p style='text-align:center; background:#333; margin:0;'>HORAS PRODUTIVAS POR MÁQUINA</p>", unsafe_allow_html=True)
            fig1 = px.bar(data_maq, x=c_temp, y=c_maq, orientation='h', color_discrete_sequence=['#00c853'], text_auto=',.3f')
            fig1.update_traces(textposition='auto', cliponaxis=False, textfont_size=12)

            fig1.update_layout(
                paper_bgcolor="black",
                plot_bgcolor="black",
                font_color="white",
                height=altura_padrao,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis={'tickformat': ',.3f'}
            )

            st.plotly_chart(fig1, use_container_width=True)

        with c_h2:
            st.markdown("<p style='text-align:center; background:#333; margin:0;'>TEMPO POR OPERAÇÃO</p>", unsafe_allow_html=True)
            fig2 = px.bar(data_op, x=c_temp, y=c_op, orientation='h', color_discrete_sequence=['#ffea00'], text_auto=',.3f')
            fig2.update_traces(textposition='auto', cliponaxis=False, textfont_size=12)

            fig2.update_layout(
                paper_bgcolor="black",
                plot_bgcolor="black",
                font_color="white",
                height=altura_padrao,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis={'tickformat': ',.3f'}
            )

            st.plotly_chart(fig2, use_container_width=True)

    with tab_operadores:
        st.markdown("<h3 style='text-align: center;'>Dashboard de Produção <span style='color:blue'>INOVA</span> <span style='color:red'>FLEX</span> <span style='color:blue'>PRODUÇÃO OPERADORES</span></h3>", unsafe_allow_html=True)
        
        o1, o2, o3, o4 = st.columns(4)
        o1.markdown(f'<div class="metric-card head-prod"><div class="metric-label">TOTAL PRODUZIDO</div><div class="metric-value">{df_filtered[c_met].sum():,.3f}</div></div>', unsafe_allow_html=True)
        o2.markdown(f'<div class="metric-card head-ops"><div class="metric-label">QTD DE OPS</div><div class="metric-value">{len(df_filtered):,.0f}</div></div>', unsafe_allow_html=True)
        o3.markdown(f'<div class="metric-card head-parado"><div class="metric-label">PERDA REBOBINADEIRA</div><div class="metric-value">35.877,000</div></div>', unsafe_allow_html=True)
        o4.markdown(f'<div class="metric-card head-parado"><div class="metric-label">PERDA GERAL</div><div class="metric-value">{df_filtered[c_apara].sum():,.3f}</div></div>', unsafe_allow_html=True)

        col_o1, col_o2 = st.columns(2)
        with col_o1:
            st.markdown("<p style='text-align:center; background:#333; margin:0;'>METROS PRODUÇÃO POR OPERADOR</p>", unsafe_allow_html=True)
            data_prod = df_filtered.groupby(c_operador)[c_met].sum().reset_index().sort_values(c_met, ascending=True)
            fig3 = px.bar(data_prod, x=c_met, y=c_operador, orientation='h', color_discrete_sequence=['#2979ff'], text_auto=',.3f')
            fig3.update_traces(textposition='auto', cliponaxis=False)
            fig3.update_layout(paper_bgcolor="black", plot_bgcolor="black", font_color="white", height=450, xaxis={'tickformat': ',.3f'})
            st.plotly_chart(fig3, use_container_width=True)

        with col_o2:
            st.markdown("<p style='text-align:center; background:#333; margin:0;'>METROS APARA POR OPERADOR</p>", unsafe_allow_html=True)
            data_apa = df_filtered.groupby(c_operador)[c_apara].sum().reset_index().sort_values(c_apara, ascending=True)
            fig4 = px.bar(data_apa, x=c_apara, y=c_operador, orientation='h', color_discrete_sequence=['#d50000'], text_auto=',.3f')
            fig4.update_traces(textposition='auto', cliponaxis=False)
            fig4.update_layout(paper_bgcolor="black", plot_bgcolor="black", font_color="white", height=450, xaxis={'tickformat': ',.3f'})
            st.plotly_chart(fig4, use_container_width=True)

    with tab_metas:
        st.markdown("<h3 style='text-align: center;'>Dashboard de Produção <span style='color:blue'>INOVA</span> <span style='color:red'>FLEX</span> <span style='color:blue'>META</span></h3>", unsafe_allow_html=True)
        m1, m2 = st.columns([1, 2])
        with m1:
            st.markdown("""
                <div style='background:#111; padding:20px; border: 1px solid #333; border-radius:5px;'>
                    <h4 style='color:#304ffe; margin-top:0;'>ATUAL VS METAS DE EVOLUÇÃO</h4>
                    <p style='color:red; font-size:18px;'>Disponibilidade Atual: 52,600%</p>
                    <hr style='border-color:#333'>
                    <p style='color:#ff4b4b'>Meta Curto Prazo: 60,000%</p>
                    <p style='color:#ffea00'>Meta Médio Prazo: 70,000%</p>
                    <p style='color:#00ff00'>Meta Longo Prazo: 75,000%+</p>
                </div>
            """, unsafe_allow_html=True)
        with m2:
            fig_meta = go.Figure(go.Indicator(
                mode = "gauge+number", value = 52.600,
                number = {'valueformat': ',.3f', 'suffix': '%'},
                gauge = {
                    'axis': {'range': [0, 100], 'tickformat': ',.3f', 'tickcolor': "black"},
                    'bar': {'color': "black", 'thickness': 0.2},
                    'steps': [
                        {'range': [0, 60], 'color': "#d50000"},
                        {'range': [60, 75], 'color': "#ffea00"},
                        {'range': [75, 100], 'color': "#00c853"}
                    ],
                }
            ))
            fig_meta.update_layout(paper_bgcolor="white", font_color="black", height=450)
            st.plotly_chart(fig_meta, use_container_width=True)

else:
    st.info("Aguardando upload para carregar o sistema INOVAFLEX.")
