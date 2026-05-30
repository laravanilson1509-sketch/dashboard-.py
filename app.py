import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64, gzip, io
from datetime import date, timedelta

st.set_page_config(
    page_title="Análise de Produção 2026",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }
.main { background-color: #0f1117; }
.block-container { padding: 1.2rem 2rem; }
.kpi-card {
    background: linear-gradient(135deg,#1a1d27 0%,#22263a 100%);
    border: 1px solid #2e3350; border-radius: 12px;
    padding: 1rem 1.2rem; text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4); height: 110px;
    display: flex; flex-direction: column; justify-content: center;
}
.kpi-label { color:#8b93b5; font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:0.25rem; }
.kpi-value { font-family:'Barlow Condensed',sans-serif; font-size:2rem; font-weight:700; line-height:1; color:#e8ecff; }
.kpi-sub   { color:#5c6380; font-size:0.68rem; margin-top:0.2rem; }
.kpi-green  .kpi-value { color:#4ade80; }
.kpi-blue   .kpi-value { color:#60a5fa; }
.kpi-amber  .kpi-value { color:#fbbf24; }
.kpi-red    .kpi-value { color:#f87171; }
.kpi-purple .kpi-value { color:#c084fc; }
.section-title {
    font-family:'Barlow Condensed',sans-serif; font-size:1rem; font-weight:600;
    color:#8b93b5; text-transform:uppercase; letter-spacing:2px;
    border-left:3px solid #3b5bdb; padding-left:0.7rem; margin:1.2rem 0 0.6rem;
}
div[data-testid="stDateInput"] input { background:#1a1d27; color:#e8ecff; border:1px solid #3b5bdb; border-radius:8px; }
</style>
""", unsafe_allow_html=True)

# ── DADOS EMBUTIDOS ──────────────────────────────────────────────────────────
DATA_B64 = """H4sIAKa6/GkC/+S9S5McR5ImeN9fkUeUSNDb3o9jNJisyW0AyUmCqNq5ZRdR3ZAhgRoQrO6Z6x72d6zsYX5I/7Gxl0eYefgjTFV9EJQtYYFCIUPdTFVNTU0fn77+j//3v/324ePz4fFv7z8//8f//I//79Ph7acvzz/fvf7w8bcvn349vH7/5fOnX+9effj4/vnz+/DP4vDt85fnu6f3zz9/+B/lJ+nXP336/H8wpr55ffzP3726//Od0Ozu4cCYv/vm7vun+++PT8f/+H/+4/9+PCh2OBwEE+Ybxr9h5nB89frxz8enh++O3z7evXj++ZdP//78+cNfA8E/zBHkLBA8vrx/evt44Owg2cAOYuAIilIHig+vwyJ/+OH4ePf2x6c3j3f8wIU+GB3JKz1oBP1LFkg9YcH3j2/eHl/fv3kb6f3t08cvz7+8//hlmwGeHdIK9SA0mKA4E7z79v7u7UP46T8cv396fFeWKwKbdfiKHIxFfCay4fXxzY9v798kuncvAlPehR8/vDv+4SAwPJFxC0/3hSuBvZZFtlg5wNcrzVkt4mqLYoigDgdvInkePuLA9K84GVC1CAITLp0Lr4h46gMjk6oJg9G1RaZyq4IqJ6lpEZXt9AWLZatQNVs7yfG44Fdhxff/5TjRUfTCJJuQQ1jCIHLrk04OxmgE1Rm1xOy6WWRcV9IhPhFw3xK3DZaeM4v9DLYXFuvl49PTfTZYCie9hVvH6QM3iUncOBSXOE/n97v7BxJtu9QLo8nUV6Rdx02LQTkMV+Om73/4/v7pGFXj5eOrx6eHH94eJ1cuvcoF3VYs3ZFc7PmdsI/4GfB5XDTAwYDo5EwpPkhFaOU4w5gPGfnxxx+PT98e3wQOvj6+vX96OL661GbUXZmMhRvcLmzNNk8JxKV24d8Q0BSRtVFM3x7v3sQ1By3749PxdfjngyC954yjukDCKePZONpBw3e+eX+Y4FnHr+jBIj4Tr4/7p6fHYomOf7x/feAqX00OQ7lVB8HISerA5zlvj+pUBA3micNSYujPqBqj8vVQlGZ8veYMOMxlqSY3QD8xFYidFFKiFnapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapNzapP3NzdH5wF2K7Dff9NvfX3bXpNefD69ePzreNn2N/fn9/mIefOshP/9Gf337+vP316bdfb//u9fHPX/+fX5//e/vz09Ofnr+8fv39y5/eff7+6ePX998en59P7w93z7vDpxeU5vH+P/7f4ef/+enrN6+PH3v+fnv/8Oefv/39/Z+vXn893L1f7t98vX/y539/+PH1T0+ff/jw/PDN/fOPh7un+2/fPz7c3b/ff/M/D+/f7+8eP717un/Yvn/896O7+y/fvP/7/Wv79v7z/W6z+D9u/O7u6f756ceP7/afXw++9b79+9X910/fH19+ff/N6z/vf++b+7tn/rX99+3pzeuv7z///M3Lh/uXP77/vHv9dP9m+ffu6fHLy6eb9qH5K/YI3tY+evXl/uX++N2b57vHn55fnf9ffXv37u7u5fn1b+8efzzcf/vm8cfHhy9f7v+N99N+m/4vD5/609u3r7+df/3fX389YPnN9vX/3f/t/f393/dPD/vXbY/fHn98/MvXb9/+2f7zH6+3wP97/fXDp4P/+efDn38GvH3+dKz/T0/fPLy7/3H7/PrD8evnz89f7/df+n9++fD66afXf3x6evjmPz98vTv+d/unD89fHn4++Pbh5enT08OnfT3/fHrePz98erO//7tPv/3z8K8Pn3/f98N/fHi+f/761eufD8+vv9/+M8u/Pjx//unT/X/4Zp/vv/fXf398fv9XzD7e7Z++fP32fvePj/f/879e/9M+/enw6fvnr9++ff767vNvhw9vf3j59mZ7fN3v7x6+Pf7H15f79/u9+fb7p/dvHn66P7w5fP/+7Zft9X159fXw2pffnh7u3u33b/78f9yZ//FmC/p9M80ffnj8/vjp6zdf776bYnz9/R3D8fH+/fPXf3v/+PTu4dfD49s3W/Kvf3o9+OefXz8ePv0wZfrfD+/2X/rfv765X/mH7eHDZgP/0L58fnjZfv76p69fH998e3j/5v7P75/+9PTq9b6uN9uj/Xf6n68e99/Z7b/z7f7f3n3zff/V99ffP79f+MvX92/2+/PD90/Pz6/X0eYFfrj76eEfq//pXw6Pv029/G9vD69+fPr9D3eb7v6b/b++fvP19Wv8m+ev9p/+m8P9T+9/fPfx9fHh9YevNvv+26fHw5uX++u3f3t3/9WXD+ePfvz++eb7r//60+H94+vnh7cPD/uXb9u9+Pbtm//v26vtv3uD/vH5w6fHp6ePr//yZvvm8PnL94cf7r/+8uXpx6evD+df8Of9b88PH/eP0q+//rD/3YdfX23/dfz809vX++f626uP7w///vnT/Q///vD85esP+5P6X9/cf//p9erG//ru6YfDby59u/13/vTj05v9v3zz9uO/v3rY/8m/ffPh4fvX+9/6z6ePD9+93v/P/U8f3226tP8A0y/eXgXG948v++O199/Wd5uKft98O9W4f307/p2Z7K/65p38U2O+v/+2XfO7w//bf9W6gqNfe3/D9O6b58O/v9o/66ubV1uMffZ+2e9qD7y7S/r09X6Z/fWfXp7v3t09frPbfXv96Zdfv33zYTPF+wGmv26B8I/Pvxx+fvPh+X9f3X8D2b//8O6b7fB/e3r65unN9mX649vHl48fvtl/+nSTfP/b8evXb/dfff98eN6H03YpUfP7LcfvXt9sX7++v9//+H8NlD+/H9/fPexv2G9vD/v/9vXN16vW7P84b395evN689df9pS6f7b1/2n7y9eb189ff70X6v/67unh/vNfr39798OPD8f/fP8KCP+K1wG+gffh+w9fH1/+ZfD1D9/c3+8R5f67g9G62S3m89PrwUu9P9x/fbfdI98fD/fffdtu/unT8fVdZODp+wHw3fHNh6vIe/D/Bq3X6/j+w8fH+/unf3kGgX86fvfx9fH+CAb7jN9scZpYp9vP009XlG+g+gR+Zit7C93/9I+vD1e3BfN7B/yO+w7jO9vD9h0W+e/9/fO/fby7/679mH477M6tB03GvN/Z3t/vGzW3Y6D18/2b+y9fPjw+7wXnI83e3z8ebxKqO074bT8G+/r1w/Pdz/e/8unh7unD3ePPw+/3p/79v98Nisv3Xz7dvzvc/+u7v282O5N9v/v80bYFw9P+gXf8L7vE8A+HNx/uDvc/7m5vHn/+6fj8fNhv4f/+9OH5/v7h15fHz4f/8/A+38bB1e23gOfePqY2g90GzU8f9zft3X3mZ9Zf+m8v200Yf9jC0H97d/jX7X9bWv40vYw8wXh3v/t6m/Bf7Zftv97cfXg16B3vvv3m+6f7N89/e3g+vO+E/+6bzWz7t3f789vew3X/Xb9+et6f28+Hw+NfN53e74b7F5v/88fD/Y+Hz8+ffX46fr7bvunH59f//OnhX998/Pnhh99O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+8V9ev7r/9eb7x79sd8O/3r1e/8fPz7fbI7v/04en11fvDw9X2L56eNi78cO3u/uPf70at1vX97e7D1+C7u/P99e//bAd9sOfD5vM+Pn+X+/evXk/7ZvsR23e7fXNfvYfX3+7v97st83X/M/zffb0w0+HBdK7z59/+rX//p05uTf264fDbn+Zbt9vd1mS7IevvtxvXG0H2+t906Efr//2Fz1p/7N1C//n28/w2/f/XgL78OfdZv/fvv98983994e775++73D556vO//7t/evP94ct+v3+3d92m9/fH98f/nC8X+v3f9nvj7tL+v02X/H6fPh//3D90b69/u/b41X5fXf/ZdfPq/uPP+2/u6/vNoO6Xf7b/U+vPr6779//6fPj/ftd/93b7atf+PXDZg78z7t/Z06bBfF9D29/X79e6/Xf92m/d98M7gC7XN+f757/88fD97u+uN9f9/fPv715vtvvff/y8/X//M/7zZ96efr88W8Pux7/d+u++L9f7/p9s7v+YQstN//x7uGf7l7tL9vXP/222dZffv/T59uY/O//Zfvt02/+Sfv001ffXt3vj+Hrt89f7/df8vP+5fvDn3/afM1Pr9dvf/v8Ydf9/27f8uW/u9uC48P998fX6/3v7P/mbyf69eunw7et8X/zEwDffT1++f/f3w/vHz+t/z6O0p//eT+G281Zvd4f982E25wP2+H9t//Zf/F++PrD88PnN/f3w//vX99efb27P+z/+K8f7q+n8999evP2fv++f9300H98+u7u/uPhYbe//88/vr16+PrD4Yf/8+3N198ef371tF9v++f7r8/bN37996fPz7d/M2+g9pU//fbw8Prh/vvDvx9fHj8ePv35p7ub3dY/Pr/f/7Y3G/GfXj9+urv/7bePr+/+/fD9YfePZg2+wZ8fPuwB99ubgfbD4bCHwHcP++P323v/fPj6YdNoN/vP6O0C9E//Z8f8D/ffH6+V0c++fN3/bTNo3T/u5/3t+O9/evjx4d1v7z/eb97yV2E/3G+68M/Hhx+fv3v1dv8O//ru3Xaf6O6wXfFPD98fftt0b/e3u9fHux/fvnr/+v7pYXe9bBvYx333bB72Z+fXD0fXp+PrNxvof9u/sZ/vDvvC/Nf7D5vdvfvp/vjm//vNh3efv9rshb9+M+be7r/b7m/X9wTf/M9Hh3/9YbeZ/+e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"""

# Decodifica e carrega os dados
compressed_data = base64.b64decode(DATA_B64)
with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as f:
    df = pd.read_csv(f)

df['data'] = pd.to_datetime(df['data']).dt.date

# ── SIDEBAR (FILTROS) ────────────────────────────────────────────────────────
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4091/4091453.png", width=80)
st.sidebar.title("Filtros de Produção")

# Correção 1: Segmentação por Listas Suspensas (Dropdowns) conforme orientações
df_anos = sorted(list(set(d.year for d in df['data'])))
ano_sel = st.sidebar.selectbox("Selecione o Ano", df_anos, index=df_anos.index(2026) if 2026 in df_anos else 0)

df_filtrado_ano = df[pd.to_datetime(df['data']).dt.year == ano_sel]
df_meses = sorted(list(set(d.month for d in df_filtrado_ano['data'])))
mes_sel = st.sidebar.selectbox("Selecione o Mês", df_meses, index=0)

df_filtrado = df_filtrado_ano[pd.to_datetime(df_filtrado_ano['data']).dt.month == mes_sel]

maquinas_disponiveis = sorted(df_filtrado['maquina'].dropna().unique())
maquina_sel = st.sidebar.selectbox("Selecione a Máquina", ["Todas"] + maquinas_disponiveis)

if maquina_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['maquina'] == maquina_sel]

# ── PROCESSAMENTO DOS DADOS ──────────────────────────────────────────────────
total_metros = df_filtrado['metros_lineares'].sum()
total_horas_disp = df_filtrado['tempo_disponivel_h'].sum()
total_horas_prod = df_filtrado['tempo_produtivo_h'].sum()
total_paradas = df_filtrado['tempo_parada_h'].sum()

eficiencia = (total_horas_prod / total_horas_disp * 100) if total_horas_disp > 0 else 0.0
velocidade_media = (total_metros / (total_horas_prod * 60)) if total_horas_prod > 0 else 0.0

# ── layout dashboard ─────────────────────────────────────────────────────────
st.title("INOVAFLEX — Gestão Total")
st.subheader(f"Dashboard de Produtividade — {mes_sel:02d}/{ano_sel}")

# KPIs
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f'<div class="kpi-card kpi-blue"><div class="kpi-label">Metros Lineares</div><div class="kpi-value">{total_metros:,.3f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + ' m</div><div class="kpi-sub">Volume total produzido</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="kpi-card kpi-green"><div class="kpi-label">Horas Produtivas</div><div class="kpi-value">{total_horas_prod:,.3f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + ' h</div><div class="kpi-sub">Tempo em operação</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="kpi-card kpi-red"><div class="kpi-label">Horas Paradas</div><div class="kpi-value">{total_paradas:,.3f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + ' h</div><div class="kpi-sub">Tempo de inatividade</div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="kpi-card kpi-amber"><div class="kpi-label">Eficiência Geral</div><div class="kpi-value">{eficiencia:.3f}%</div><div class="kpi-sub">Produtivo / Disponível</div></div>', unsafe_allow_html=True)
with kpi5:
    st.markdown(f'<div class="kpi-card kpi-purple"><div class="kpi-label">Velocidade Média</div><div class="kpi-value">{velocidade_media:,.3f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + ' m/min</div><div class="kpi-sub">Metros por minuto ativo</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── GRÁFICOS PRINCIPAIS ──────────────────────────────────────────────────────
g1, g2 = st.columns(2)

with g1:
    st.markdown('<div class="section-title">Produção por Máquina (Metros Lineares)</div>', unsafe_allow_html=True)
    df_maq = df_filtrado.groupby('maquina', as_index=False)['metros_lineares'].sum().sort_values(by='metros_lineares', ascending=True)
    
    # Correção 2: Formatação personalizada com 3 casas decimais e sem o "k"
    df_maq['texto_label'] = df_maq['metros_lineares'].apply(lambda x: f"{x:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    fig_maq = px.bar(
        df_maq, 
        x='metros_lineares', 
        y='maquina', 
        orientation='h',
        text='texto_label', # injeta a string formatada estritamente
        template='plotly_dark'
    )
    fig_maq.update_traces(
        marker_color='#3b5bdb',
        # Correção 3: Rótulos automáticos posicionados subscritos em cima das barras (internamente)
        textposition='inside', 
        insidetextanchor='end'
    )
    fig_maq.update_layout(
        xaxis_title="Metros Lineares",
        yaxis_title=None,
        margin=dict(l=20, r=20, t=20, b=20),
        height=350,
        xaxis=dict(showgrid=False, showticklabels=False) # Remove linhas e números do eixo para limpar o visual interno
    )
    st.plotly_chart(fig_maq, use_container_width=True)

with g2:
    st.markdown('<div class="section-title">Produção por Operador (Metros Lineares)</div>', unsafe_allow_html=True)
    df_op = df_filtrado.groupby('operador', as_index=False)['metros_lineares'].sum().sort_values(by='metros_lineares', ascending=True)
    
    # Correção 2: Formatação com 3 casas decimais e sem o "k"
    df_op['texto_label'] = df_op['metros_lineares'].apply(lambda x: f"{x:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    fig_op = px.bar(
        df_op, 
        x='metros_lineares', 
        y='operador', 
        orientation='h',
        text='texto_label',
        template='plotly_dark'
    )
    fig_op.update_traces(
        marker_color='#22b8cf',
        # Correção 3: Rótulos automáticos posicionados subscritos em cima das barras (internamente)
        textposition='inside',
        insidetextanchor='end'
    )
    fig_op.update_layout(
        xaxis_title="Metros Lineares",
        yaxis_title=None,
        margin=dict(l=20, r=20, t=20, b=20),
        height=350,
        xaxis=dict(showgrid=False, showticklabels=False)
    )
    st.plotly_chart(fig_op, use_container_width=True)

# ── EVOLUÇÃO DIÁRIA DA PRODUTIVIDADE ─────────────────────────────────────────
st.markdown('<div class="section-title">Evolução Diária da Produção e Paradas</div>', unsafe_allow_html=True)

df_diario = df_filtrado.groupby('data', as_index=False).agg({
    'metros_lineares': 'sum',
    'tempo_parada_h': 'sum'
}).sort_values('data')

fig_diario = make_subplots(specs=[[{"secondary_y": True}]])

# Formatação das dicas flutuantes (hovers) com 3 casas decimais
df_diario['metros_formatado'] = df_diario['metros_lineares'].apply(lambda x: f"{x:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
df_diario['paradas_formatado'] = df_diario['tempo_parada_h'].apply(lambda x: f"{x:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

fig_diario.add_trace(
    go.Bar(
        x=df_diario['data'], 
        y=df_diario['metros_lineares'], 
        name="Metros Lineares",
        marker_color='#3b5bdb',
        text=df_diario['metros_formatado'],
        textposition='none', # Omitido no diário para não poluir devido ao espaço temporal
        hovertemplate="Data: %{x}<br>Metros: %{text}<extra></extra>"
    ),
    secondary_y=False,
)

fig_diario.add_trace(
    go.Scatter(
        x=df_diario['data'], 
        y=df_diario['tempo_parada_h'], 
        name="Horas Paradas",
        marker_color='#f87171',
        line=dict(width=3),
        text=df_diario['paradas_formatado'],
        hovertemplate="Data: %{x}<br>Horas Paradas: %{text} h<extra></extra>"
    ),
    secondary_y=True,
)

fig_diario.update_layout(
    template='plotly_dark',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=20, b=20),
    height=300
)

fig_diario.update_yaxes(title_text="Metros Lineares", secondary_y=False, showgrid=False)
fig_diario.update_yaxes(title_text="Horas Paradas (h)", secondary_y=True, showgrid=False)

st.plotly_chart(fig_diario, use_container_width=True)

# ── EXPORTAÇÃO E VISUALIZAÇÃO DA TABELA ──────────────────────────────────────
st.markdown('<div class="section-title">Dados Detalhados da Produção</div>', unsafe_allow_html=True)

# Deixando a tabela amigável antes de exibir e baixar
df_export = df_filtrado.copy()
df_export['data'] = df_export['data'].astype(str)

# Formata colunas numéricas do dataframe de exibição
for col in ['metros_lineares', 'tempo_disponivel_h', 'tempo_produtivo_h', 'tempo_parada_h']:
    if col in df_export.columns:
        df_export[col] = df_export[col].apply(lambda x: f"{x:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

st.dataframe(df_export, use_container_width=True)

# Botão para baixar relatório Excel
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, sheet_name='Produção', index=False)
    
st.download_button(
    label="📥 Baixar Relatório Completo (Excel)",
    data=buffer.getvalue(),
    file_name=f"relatorio_producao_{mes_sel:02d}_{ano_sel}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
