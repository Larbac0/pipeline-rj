import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

st.set_page_config(page_title='Pipeline RJ — Clima & Câmbio', layout='wide')
st.title('Rio de Janeiro — Clima, Câmbio & Ações')
st.caption('Pipeline: Open-Meteo + AwesomeAPI + B3 → PostgreSQL → ETL Python → Streamlit')

# Dados atuais
atual = pd.read_sql("""
    SELECT temperatura, vento, chuva, coletado_em
    FROM weather_raw
    ORDER BY coletado_em DESC
    LIMIT 1
""", engine).iloc[0]

# ── Sidebar com filtros ───────────────────────────────────────────────────
st.sidebar.header("Filtros")

periodo = st.sidebar.selectbox(
    "Período",
    ["Últimas 24h", "Últimos 7 dias", "Últimos 30 dias"],
    index=1
)

periodo_map = {"Últimas 24h": 1, "Últimos 7 dias": 7, "Últimos 30 dias": 30}
dias = periodo_map[periodo]

moeda = st.sidebar.selectbox("Moeda", ["USD/BRL", "EUR/BRL", "BTC/BRL"])
moeda_col = {"USD/BRL": "usd_brl", "EUR/BRL": "eur_brl", "BTC/BRL": "btc_brl"}[moeda]

acoes_disponiveis = pd.read_sql("SELECT DISTINCT ticker FROM stocks_raw", engine)['ticker'].tolist()
acoes_selecionadas = st.sidebar.multiselect("Ações", acoes_disponiveis, default=acoes_disponiveis)

# ── Métricas no topo ─────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperatura atual", f"{atual['temperatura']:.1f} °C")
c2.metric("Vento atual", f"{atual['vento']:.1f} km/h")

cambio_atual = pd.read_sql(f"""
    SELECT {moeda_col} as valor, coletado_em
    FROM exchange_raw
    ORDER BY coletado_em DESC LIMIT 2
""", engine)
valor_atual  = cambio_atual.iloc[0]['valor']
valor_antes  = cambio_atual.iloc[1]['valor'] if len(cambio_atual) > 1 else valor_atual
variacao     = round(valor_atual - valor_antes, 4)
c3.metric(moeda, f"R$ {valor_atual:.4f}", delta=f"{variacao:+.4f}")
c4.metric("Chuva atual", f"{atual['chuva']:.1f} mm")

st.divider()

# ── Câmbio com média móvel ────────────────────────────────────────────────
st.subheader(f"Evolução do {moeda} — últimos {dias} dias")

df_cambio = pd.read_sql(f"""
    SELECT coletado_em, {moeda_col} as valor
    FROM exchange_raw
    WHERE coletado_em >= NOW() - INTERVAL '{dias} days'
    ORDER BY coletado_em
""", engine)

if not df_cambio.empty:
    df_cambio['media_movel'] = df_cambio['valor'].rolling(window=24).mean()

    fig_cambio = go.Figure()
    fig_cambio.add_trace(go.Scatter(
        x=df_cambio['coletado_em'], y=df_cambio['valor'],
        name=moeda, line=dict(color='#4f9fff', width=1.5), opacity=0.7
    ))
    fig_cambio.add_trace(go.Scatter(
        x=df_cambio['coletado_em'], y=df_cambio['media_movel'],
        name='Média móvel 24h', line=dict(color='#4fffb0', width=2, dash='dot')
    ))
    fig_cambio.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h'),
        margin=dict(l=0, r=0, t=10, b=0),
        height=300
    )
    st.plotly_chart(fig_cambio, use_container_width=True)

st.divider()

# ── Candlestick das ações ─────────────────────────────────────────────────
st.subheader(f"Ações B3 — Candlestick ({periodo})")

if acoes_selecionadas:
    tickers_str = "','".join(acoes_selecionadas)
    df_hist = pd.read_sql(f"""
        SELECT * FROM stocks_historico
        WHERE ticker IN ('{tickers_str}')
        AND data >= NOW() - INTERVAL '{dias} days'
        ORDER BY data
    """, engine)

    if not df_hist.empty:
        for ticker in acoes_selecionadas:
            df_t = df_hist[df_hist['ticker'] == ticker]
            if df_t.empty:
                continue

            fig = go.Figure(go.Candlestick(
                x=df_t['data'],
                open=df_t['abertura'],
                high=df_t['maxima'],
                low=df_t['minima'],
                close=df_t['fechamento'],
                name=ticker,
                increasing_line_color='#4fffb0',
                decreasing_line_color='#ff6b6b'
            ))
            fig.update_layout(
                title=ticker,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_rangeslider_visible=False,
                margin=dict(l=0, r=0, t=40, b=0),
                height=280
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aguardando mais dias de coleta para exibir o candlestick.")

st.divider()

# ── Métricas das ações ────────────────────────────────────────────────────
st.subheader("Ações B3 — Valores atuais")
acoes = pd.read_sql("SELECT * FROM stocks_analytics", engine)
acoes = acoes[acoes['ticker'].isin(acoes_selecionadas)] if acoes_selecionadas else acoes

cols = st.columns(len(acoes))
for i, (_, row) in enumerate(acoes.iterrows()):
    variacao = round(row['fechamento'] - row['abertura'], 2)
    cols[i].metric(
        label=row['ticker'],
        value=f"R$ {row['fechamento']:.2f}",
        delta=f"{variacao:+.2f}"
    )

st.dataframe(
    acoes[['ticker', 'abertura', 'fechamento', 'maxima', 'minima', 'volume']],
    use_container_width=True
)

st.divider()

# ── Clima ─────────────────────────────────────────────────────────────────
st.subheader("Clima por hora do dia")
clima = pd.read_sql("SELECT * FROM weather_analytics ORDER BY hora", engine)
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Temperatura média (°C)**")
    st.line_chart(clima.set_index('hora')['temp_media'])
with col2:
    st.markdown("**Vento médio (km/h)**")
    st.bar_chart(clima.set_index('hora')['vento_medio'])
