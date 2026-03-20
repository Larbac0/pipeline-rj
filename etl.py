from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

def extract():
    df_clima  = pd.read_sql("SELECT * FROM weather_raw ORDER BY coletado_em", engine)
    df_cambio = pd.read_sql("SELECT * FROM exchange_raw ORDER BY coletado_em", engine)
    df_acoes  = pd.read_sql("SELECT * FROM stocks_raw ORDER BY coletado_em", engine)
    print(f"Clima: {len(df_clima)} | Câmbio: {len(df_cambio)} | Ações: {len(df_acoes)}")
    return df_clima, df_cambio, df_acoes


def transform(df_clima, df_cambio, df_acoes):
    for df in [df_clima, df_cambio]:
        df['coletado_em'] = pd.to_datetime(df['coletado_em'])
        df['hora'] = df['coletado_em'].dt.hour

    clima_hora = df_clima.groupby('hora').agg(
        temp_media  = ('temperatura', 'mean'),
        vento_medio = ('vento', 'mean'),
        chuva_total = ('chuva', 'sum')
    ).reset_index()

    cambio_hora = df_cambio.groupby('hora').agg(
        usd_medio = ('usd_brl', 'mean'),
        eur_medio = ('eur_brl', 'mean'),
        btc_medio = ('btc_brl', 'mean')
    ).reset_index()

    df_combined = pd.merge(clima_hora, cambio_hora, on='hora', how='inner')
   
    acoes_atual = df_acoes.sort_values('coletado_em').groupby('ticker').last().reset_index()

    return clima_hora, cambio_hora, df_combined, acoes_atual

def load(clima_hora, cambio_hora, df_combined, acoes_atual):
    clima_hora.to_sql('weather_analytics',  engine, if_exists='replace', index=False)
    cambio_hora.to_sql('exchange_analytics', engine, if_exists='replace', index=False)
    df_combined.to_sql('combined_analytics', engine, if_exists='replace', index=False)
    acoes_atual.to_sql('stocks_analytics',   engine, if_exists='replace', index=False)
    print("ETL finalizado com sucesso.")

if __name__ == '__main__':
    df_clima, df_cambio, df_acoes = extract()
    clima_hora, cambio_hora, combined, acoes_atual = transform(df_clima, df_cambio, df_acoes)
    load(clima_hora, cambio_hora, combined, acoes_atual)
