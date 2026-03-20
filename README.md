🌡️ Pipeline RJ — Clima & Câmbio em tempo real

🔗 **Dashboard ao vivo:** https://pipeline.softwavesolutions.com.br

![Dashboard](./docs/dashboard.png)

Pipeline de dados end-to-end que coleta informações de clima e câmbio de hora em hora, armazena em banco relacional, processa com Python e entrega um dashboard interativo.

📌 Visão geral
CamadaTecnologiaFunçãoColetan8n + Open-Meteo + AwesomeAPIWorkflows agendados buscam dados a cada horaArmazenamentoPostgreSQLDados brutos armazenados em tabelas separadasProcessamentoPython + PandasETL: limpeza, tipagem, agregações e joinVisualizaçãoStreamlitDashboard interativo com métricas e gráficos

🏗️ Arquitetura
[Open-Meteo API]      [AwesomeAPI]
       |                    |
  [n8n Workflow 1]    [n8n Workflow 2]
       |                    |
       └──────┬─────────────┘
              ▼
        [PostgreSQL]
        ┌─────────────────┐
        │ weather_raw     │  ← dados brutos de clima
        │ exchange_raw    │  ← dados brutos de câmbio
        │ weather_analytics│ ← agregado por hora
        │ exchange_analytics│← agregado por hora
        │ combined_analytics│← join clima + câmbio
        └─────────────────┘
              ▼
         [etl.py]
              ▼
        [Streamlit app]

📊 Fontes de dados

Open-Meteo — API de clima gratuita, sem autenticação, coordenadas do Rio de Janeiro
AwesomeAPI — API brasileira de câmbio, sem autenticação, pares USD/BRL, EUR/BRL, BTC/BRL

📁 Estrutura do projeto
pipeline-rj/
├── n8n/
│   ├── workflow_clima.json
│   └── workflow_cambio.json
├── db/
│   └── setup.sql
├── etl.py
├── app.py
├── requirements.txt
├── .env.example
└── README.md

📦 Dependências
pandas
sqlalchemy
psycopg2-binary
streamlit
python-dotenv

💡 Possíveis evoluções

Alertas automáticos via n8n (Telegram/Email) quando o dólar ultrapassar um valor
Análise de correlação entre temperatura e variação cambial
Deploy do dashboard no Streamlit Cloud
Substituição do ETL manual por Apache Airflow


👤 Autor
Igor — SoftWave Solutions
Projeto desenvolvido como parte do portfólio de Engenharia de Dados.
