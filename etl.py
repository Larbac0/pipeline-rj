from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

def extract():
    df_clima  = pd.read_sql("SELECT * FROM weather_raw ORDER BY coletado_em", engine)
    df_cambio = pd.read_sql("SELECT * FROM exchange_raw ORDER BY coletado_em", engine)
    print(f"Clima: {len(df_clima)} registros | Câmbio: {len(df_cambio)} registros")
    return df_clima, df_cambio

def transform(df_clima, df_cambio):
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

    return clima_hora, cambio_hora, df_combined

def load(clima_hora, cambio_hora, df_combined):
    clima_hora.to_sql('weather_analytics',  engine, if_exists='replace', index=False)
    cambio_hora.to_sql('exchange_analytics', engine, if_exists='replace', index=False)
    df_combined.to_sql('combined_analytics', engine, if_exists='replace', index=False)
    print("ETL finalizado com sucesso.")

if __name__ == '__main__':
    df_clima, df_cambio = extract()
    clima_hora, cambio_hora, combined = transform(df_clima, df_cambio)
    load(clima_hora, cambio_hora, combined)
