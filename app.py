import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página para layout amplo (Responsivo para Desktop e Mobile)
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada (CSS) para Cards e Identidade Visual Adaptativa
st.markdown("""
    <style>
    .main {
        background-color: var(--background-color);
    }
    .main-title {
        background-color: #0d6efd;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .card-container {
        background-color: var(--background-color);
        border: 1px solid var(--secondary-background-color);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .card-title {
        color: var(--text-color);
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 8px;
        opacity: 0.8;
    }
    .card-value {
        color: #0d6efd;
        font-size: 22px;
        font-weight: bold;
    }
    .mobile-card {
        background-color: var(--background-color);
        color: var(--text-color);
        border: 1px solid var(--secondary-background-color);
        padding: 15px;
        border-left: 5px solid #0d6efd;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        font-size: 14px;
        line-height: 1.6;
    }
    .mobile-card strong {
        color: #0d6efd;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">DASHBOARD DE VENDAS</div>', unsafe_allow_html=True)

# --- PAINEL LATERAL: UPLOAD E FILTROS ---
st.sidebar.header("📁 Carga de Dados")
uploaded_file = st.sidebar.file_uploader("Faça upload da base de dados Excel (.xlsx)", type=["xlsx"])

# Cache do Streamlit para evitar que a base reinicie a cada clique no filtro
@st.cache_data
def obter_dados_demonstrativos():
    picos = [
        ('2026-01-15', 'Filial Belo Horizonte', 23000.000),
        ('2026-02-15', 'Filial Cuiaba', 84000.000),
        ('2026-03-15', 'Filial Recife', 4000.000),
        ('2026-04-15', 'Filial Curitiba', 46000.000),
        ('2026-05-15', 'Filial Cuiaba', 11000.000),
        ('2026-06-15', 'Filial Belo Horizonte', 13000.000),
        ('2026-07-15', 'Filial Cuiaba', 35000.000),
        ('2026-08-15', 'Filial Belo Horizonte', 81000.000),
        ('2026-09-15', 'Filial Fortaleza', 17000.000),
        ('2026-10-15', 'Filial Curitiba', 22000.000),
        ('2026-11-15', 'Filial Belo Horizonte', 59000.000),
        ('2026-12-15', 'Filial Florianópolis', 81000.000),
        ('2026-04-10', 'Filial Rio Branco', 98000.000),
        ('2026-08-20', 'Filial Manaus', 90000.000),
        ('2026-03-05', 'Filial Natal', 24000.000),
        ('2026-06-22', 'Filial Vitória', 17000.000),
        ('2026-07-11', 'Matriz', 17000.000),
        ('2026-09-18', 'Filial Rio de Janeiro', 10000.000),
        ('2026-01-25', 'Filial Salvador', 10000.000),
        ('2026-11-05', 'Filial Rio Grande do Sul', 7000.000),
        ('2026-12-02', 'Filial São Paulo', 5110.000)
    ]
    
    data = []
    for dt, loja, valor in picos:
        data.append({
            'Loja': loja, 'Produto': 'Produto Padrão', 'QTD': 0, 'Data Venda': pd.to_datetime(dt),
            'Forma Pagto': 'Cartão de Crédito', 'Nº Parcelas': 2, 'Desconto %': 11.69,
            'Valor': valor, 'Status': 'Concluído', 'Se cancelado moti': ''
        })
        
    df = pd.DataFrame(data)
    df['QTD'] = [5, 20, 2, 12, 4, 3, 10, 18, 5, 6, 14, 18, 22, 20, 5, 3, 3, 2, 1, 1, 0]
    df.loc[df['QTD'] == 0, 'QTD'] = 1
    return df

# Tratamento do upload com cache dinâmico para estabilizar a sessão
@st.cache_data
def carregar_dados_upload(arquivo):
    try:
        df = pd.read_excel(arquivo)
        df.columns = df.columns.str.strip()
        mapeamento = {
            'loja': 'Loja', 'produto': 'Produto', 'qtd': 'QTD', 'data venda': 'Data Venda',
            'forma pagto': 'Forma Pagto', 'nº parcelas': 'Nº Parcelas', 'desconto %': 'Desconto %',
            'valor': 'Valor', 'status': 'Status'
        }
        df.rename(columns=lambda x: mapeamento.get(x.lower(), x), inplace=True)
        if 'Data Venda' in df.columns:
            df['Data Venda'] = pd.to_datetime(df['Data Venda'])
        return df, True
    except Exception as e:
        return None, f"Erro ao ler o arquivo: {e}"

if uploaded_file is not None:
    df, status = carregar_dados_upload(uploaded_file)
    if df is None:
        st.sidebar.error(status)
        df = obter_dados_demonstrativos()
    else:
        st.sidebar.success("✅ Base carregada com sucesso!")
else:
    df = obter_dados_demonstrativos()

# Criar coluna Ano_Mes de forma fixa na tabela base
if 'Data Venda' in df.columns and 'Ano_Mes' not in df.columns:
    df['Ano_Mes'] = df['Data Venda'].dt.strftime('%Y-%m')
elif 'Ano_Mes' not in df.columns:
    df['Ano_Mes'] = 'N/A'

# --- 2. FILTROS DE SEGMENTAÇÃO ---
st.sidebar.header("🔍 Filtros de Segmentação")

lista_lojas = sorted(df['Loja'].dropna().unique().tolist()) if 'Loja' in df.columns else []
lojas_selecionadas = st.sidebar.multiselect("Selecione as Filiais/Lojas", options=lista_lojas, default=lista_lojas)

lista_meses = sorted(df['Ano_Mes'].dropna().unique().tolist()) if 'Ano_Mes' in df.columns else []
meses_selecionados = st.sidebar.multiselect("Selecione o Período (Ano-Mês)", options=lista_meses, default=lista_meses)

# Filtragem Cruzada Reativa Aplicada
df_filtrado = df[(df['Loja'].isin(lojas_selecionadas)) & (df['Ano_Mes'].isin(meses_selecionados))]

if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
else:
    # --- 3. INDICADORES PRINCIPAIS (KPIs) ---
    val_total = df_filtrado['Valor'].sum() if 'Valor' in df_filtrado.columns else 0.0
    med_desconto = df_filtrado['Desconto %'].mean() if 'Desconto %' in df_filtrado.columns else 0.0
    qtd_total = df_filtrado['QTD'].sum() if 'QTD' in df_filtrado.columns else 0
    med_parcelas = df_filtrado['Nº Parcelas'].mean() if 'Nº Parcelas' in df_filtrado.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="card-container"><div class="card-title">Valor Total de Vendas</div><div class="card-value">{val_total:,.3f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card-container"><div class="card-title">Média de Desconto</div><div class="card-value">{med_desconto:.2f}%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card-container"><div class="card-title">Quantidade Total de Vendas</div><div class="card-value">{qtd_total}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="card-container"><div class="card-title">Média de Parcelas</div><div class="card-value">{int(round(med_parcelas))}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- 4. GRÁFICO: SOMA DE VALOR POR MÊS ---
    st.subheader("📊 Soma de Valor por Mês")
    
    if 'Data Venda' in df_filtrado.columns and 'Valor' in df_filtrado.columns:
        df_mes = df_filtrado.copy()
        meses_pt = {
            'January': 'janeiro', 'February': 'fevereiro', 'March': 'março', 'April': 'abril',
            'May': 'maio', 'June': 'junho', 'July': 'julho', 'August': 'agosto',
            'September': 'setembro', 'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
        }
        df_mes['Mes_PT'] = df_mes['Data Venda'].dt.strftime('%B').map(meses_pt)
        df_mes['Num_Mes'] = df_mes['Data Venda'].dt.month
        
        df_linha = df_mes.groupby(['Num_Mes', 'Mes_PT']).agg({'Valor': 'sum'}).reset_index().sort_values('Num_Mes')
        
        label_textos = []
        for _, row in df_linha.iterrows():
            dados_mes = df_mes[df_mes['Mes_PT'] == row['Mes_PT']]
            if not dados_mes.empty and 'Loja' in df_mes.columns:
                top_loja_mes = dados_mes.groupby('Loja')['Valor'].sum().idxmax()
                val_loja_mes = dados_mes.groupby('Loja')['Valor'].sum().max()
                label_textos.append(f"{val_loja_mes:,.3f} {top_loja_mes}")
            else:
                label_textos.append("")

        fig_linha = px.area(df_linha, x='Mes_PT', y='Valor', markers=True)
        fig_linha.update_traces(
            line_color='#0d6efd',
            fillcolor='rgba(13, 110, 253, 0.2)',
            text=label_textos,
            textposition='top center',
            mode='lines+markers+text'
        )
        fig_linha.update_layout(
            yaxis=dict(tickformat=",.3f", automargin=True),
            xaxis_title=None,
            autosize=True,
            height=340,
            margin=dict(l=20, r=20, t=40, b=20),
            template="plotly_white"
        )
        st.plotly_chart(fig_linha, use_container_width=True, config={'responsive': True})

    st.markdown("---")

    # --- 5. GRÁFICOS INFERIORES: TOP FILIAIS E REGIÃO ---
    col_inf1, col_inf2 = st.columns([1, 1])

    with col_inf1:
        st.subheader("🏆 TOP 10 FILIAL")
        if 'Loja' in df_filtrado.columns and 'Valor' in df_filtrado.columns:
            df_top10 = df_filtrado.groupby('Loja').agg({'Valor': 'sum'}).reset_index()
            df_top10 = df_top10.sort_values(by='Valor', ascending=True).tail(10)
            
            labels_top10 = [f"{val:,.3f} {loja}" for val, loja in zip(df_top10['Valor'], df_top10['Loja'])]
            
            fig_bar = go.Figure(go.Bar(
                x=df_top10['Valor'],
                y=df_top10['Loja'],
                orientation='h',
                text=labels_top10,
                textposition='inside',
                marker_color='#0d6efd'
            ))
            fig_bar.update_layout(
                xaxis=dict(tickformat=",.3f"),
                yaxis=dict(showticklabels=False),
                autosize=True,
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
                template="plotly_white"
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'responsive': True})

    with col_inf2:
        st.subheader("🗺️ TOTAL POR REGIÃO")
        if 'Loja' in df_filtrado.columns and 'Valor' in df_filtrado.columns:
            coords = {
                'Filial Cuiaba': [-15.601, -56.097], 'Filial Belo Horizonte': [-19.917, -43.934],
                'Filial Florianópolis': [-27.595, -48.548], 'Filial Curitiba': [-25.428, -49.273],
                'Filial Recife': [-8.054, -34.881], 'Filial Fortaleza': [-3.731, -38.526],
                'Filial Rio Branco': [-9.974, -67.807], 'Filial Manaus': [-3.119, -60.021],
                'Filial Natal': [-5.794, -35.211], 'Filial Vitória': [-20.315, -40.312],
                'Matriz': [-23.550, -46.633], 'Filial Rio de Janeiro': [-22.906, -43.172],
                'Filial Salvador': [-12.971, -38.510], 'Filial Rio Grande do Sul': [-30.034, -51.217],
                'Filial São Paulo': [-23.550, -46.633]
            }
            df_regiao = df_filtrado.groupby('Loja').agg({'Valor': 'sum'}).reset_index()
            df_regiao['lat'] = df_regiao['Loja'].map(lambda x: coords.get(x, [-23.55, -46.63])[0])
            df_regiao['lon'] = df_regiao['Loja'].map(lambda x: coords.get(x, [-23.55, -46.63])[1])
            
            fig_map = px.scatter_mapbox(
                df_regiao, lat="lat", lon="lon", size="Valor", color="Loja",
                size_max=30, zoom=3, mapbox_style="carto-positron"
            )
            fig_map.update_layout(
                autosize=True,
                height=380, 
                margin=dict(l=0, r=0, t=0, b=0), 
                showlegend=False
            )
            st.plotly_chart(fig_map, use_container_width=True, config={'responsive': True})

    # --- 6. EXIBIÇÃO EM CARDS (MOBILE RESPONSIVE ADAPTATIVO) ---
    st.markdown("---")
    st.subheader("📋 Visualização dos Registros em Cards")
    
    for idx, row in df_filtrado.iterrows():
        loja_card = row.get('Loja', 'Não Informado')
        prod_card = row.get('Produto', 'Não Informado')
        qtd_card = row.get('QTD', 0)
        data_card = row['Data Venda'].strftime('%d/%m/%Y') if 'Data Venda' in row and pd.notna(row['Data Venda']) else 'N/A'
        pagto_card = row.get('Forma Pagto', 'N/A')
        parc_card = row.get('Nº Parcelas', 0)
        desc_card = row.get('Desconto %', 0.00)
        val_card = row.get('Valor', 0.000)
        status_card = row.get('Status', 'N/A')
        
        motivo = row.get('Se cancelado moti') if 'Se cancelado moti' in row else row.get('Se cancelado motivo', '')

        with st.container():
            st.markdown(f'''
                <div class="mobile-card">
                    <strong>📍 Loja:</strong> {loja_card}<br>
                    <strong>📦 Produto:</strong> {prod_card} | <strong>Qtd:</strong> {qtd_card}<br>
                    <strong>📅 Data:</strong> {data_card} | <strong>💰 Valor:</strong> R$ {val_card:,.3f}<br>
                    <strong>💳 Pagto:</strong> {pagto_card} ({parc_card}x) | <strong>🏷️ Desc:</strong> {desc_card:.2f}%<br>
                    <strong>📊 Status:</strong> {status_card}
                    {f"<br><strong>⚠️ Motivo:</strong> {motivo}" if pd.notna(motivo) and motivo != "" else ""}
                </div>
            ''', unsafe_allow_html=True)
