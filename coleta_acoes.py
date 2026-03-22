import yfinance as yf
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv('/home/larbac0/pipeline-rj/.env')

tickers = ['PETR3.SA', 'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'MGLU3.SA', 'WEGE3.SA']

conn = psycopg2.connect(os.getenv('DB_URL'))
cur = conn.cursor()

for ticker in tickers:
    dados = yf.Ticker(ticker).fast_info
    cur.execute("""
        INSERT INTO stocks_raw (ticker, abertura, fechamento, maxima, minima, volume)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        ticker.replace('.SA', ''),
        round(dados.open, 2),
        round(dados.last_price, 2),
        round(dados.day_high, 2),
        round(dados.day_low, 2),
        dados.three_month_average_volume
    ))

conn.commit()
cur.close()
conn.close()
print(f"Ações coletadas: {', '.join([t.replace('.SA','') for t in tickers])}")
