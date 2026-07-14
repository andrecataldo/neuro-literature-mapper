from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from neuro_mapper.config import load_config
from neuro_mapper.pipeline import run_api_search
from neuro_mapper.venue_search import generate_venue_searches


st.set_page_config(page_title="Neuro Literature Mapper", layout="wide")

st.title("Neuro Literature Mapper")
st.caption("Mapeamento exploratório de literatura de SI sobre LLMs, IA generativa, vieses, julgamento e decisão.")

load_dotenv()

config_path = st.sidebar.text_input("Arquivo de configuração", "config/queries_neuro.yaml")
config = load_config(config_path)

tab_venues, tab_api = st.tabs(["Buscas por venue", "Busca por APIs"])

with tab_venues:
    st.subheader("Buscas direcionadas nos venues indicados")

    rows = generate_venue_searches(config)
    df = pd.DataFrame(rows)

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Baixar buscas_venues.csv",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="buscas_venues.csv",
        mime="text/csv",
    )

with tab_api:
    st.subheader("Busca automatizada ampla")

    st.warning("Esta busca consulta APIs abertas. Pode demorar e depende da internet local.")

    if st.button("Executar busca"):
        with st.spinner("Executando buscas..."):
            records = run_api_search(config)
            df_api = pd.DataFrame([record.to_dict() for record in records])

        st.success(f"Registros únicos encontrados: {len(df_api)}")
        st.dataframe(df_api, use_container_width=True)

        st.download_button(
            "Baixar resultados_neuro.csv",
            data=df_api.to_csv(index=False).encode("utf-8-sig"),
            file_name="resultados_neuro.csv",
            mime="text/csv",
        )
