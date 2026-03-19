import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

st.set_page_config(page_title='Pipeline RJ — Clima & Câmbio', layout='wide')
st.title('Rio de Janeiro — Clima & Câmbio')
st.caption('Pipeline: Open-Meteo + AwesomeAPI → PostgreSQL → ETL Python → Streamlit')

clima  = pd.read_sql("SELECT * FROM weather_analytics ORDER BY hora", engine)
cambio = pd.read_sql("SELECT * FROM exchange_analytics ORDER BY hora", engine)

# Métricas no topo
c1, c2, c3, c4 = st.columns(4)
c1.metric("Temp. média", f"{clima['temp_media'].mean():.1f} °C")
c2.metric("Vento médio", f"{clima['vento_medio'].mean():.1f} km/h")
c3.metric("USD/BRL médio", f"R$ {cambio['usd_medio'].mean():.2f}")
c4.metric("EUR/BRL médio", f"R$ {cambio['eur_medio'].mean():.2f}")

st.divider()

# Gráficos clima
st.subheader("Clima por hora do dia")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Temperatura média (°C)**")
    st.line_chart(clima.set_index('hora')['temp_media'])
with col2:
    st.markdown("**Vento médio (km/h)**")
    st.bar_chart(clima.set_index('hora')['vento_medio'])

st.divider()

# Gráficos câmbio
st.subheader("Câmbio por hora do dia")
col3, col4 = st.columns(2)
with col3:
    st.markdown("**USD/BRL e EUR/BRL**")
    st.line_chart(cambio.set_index('hora')[['usd_medio', 'eur_medio']])
with col4:
    st.markdown("**BTC/BRL**")
    st.line_chart(cambio.set_index('hora')['btc_medio'])

st.divider()

# Tabela combinada
st.subheader("Visão combinada — Clima + Câmbio por hora")
combined = pd.read_sql("SELECT * FROM combined_analytics ORDER BY hora", engine)
st.dataframe(combined, use_container_width=True)
