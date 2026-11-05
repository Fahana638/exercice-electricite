from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")

@st.cache_data
def charger():
    return pd.read_csv(DOSSIER / "consommation_propre.csv")


df = charger()

st.write(
    "Ce tableau de bord présente la consommation d'électricité de 12 quartiers "
    "de Port-au-Prince, Delmas, Pétion-Ville et Cap-Haïtien."
)
st.write(
    "Question du directeur : la consommation suit-elle la chaleur, "
    "ou les heures de courant ?"
)
communes = sorted(df["commune"].unique())
annees = sorted(df["annee"].unique())

choix_communes = st.sidebar.multiselect("Communes", communes, default=communes)
choix_annee = st.sidebar.selectbox(
    "Année", annees, index=len(annees) - 1
)

if not choix_communes:
    st.warning("Choisissez au moins une commune dans la barre latérale.")
    st.stop()

filtre = df[(df["commune"].isin(choix_communes)) & (df["annee"] == choix_annee)]

st.white(len(filtre))