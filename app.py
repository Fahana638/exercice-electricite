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

total = filtre["kwh"].sum()
par_abonne = filtre["kwh_par_abonne"].mean()
heures = filtre["heures_courant"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Consommation totale", f"{total / 1e6:.2f} millions de kWh")
col2.metric("kWh par abonné", f"{par_abonne:.1f}")
col3.metric("Heures de courant par jour", f"{heures:.1f}")

import matplotlib.pyplot as plt

onglets = st.tabs([
    "Quartiers",
    "Évolution",
    "Chaleur ou courant ?",
    "Coupures",
    "Relevés hors du lot",
])

# 1. Quartiers : consommation par abonné
with onglets[0]:
    classement = (filtre.groupby("quartier")["kwh_par_abonne"].mean() .sort_values())
    fig, ax = plt.subplots(figsize=(8, 5))
    classement.plot(kind="barh", ax=ax)
    ax.set_title("Consommation moyenne par abonné et par quartier")
    ax.set_xlabel("kWh par abonné")
    ax.set_ylabel("Quartier")
    st.pyplot(fig)
    tete = classement.index[-1]
    st.write(f"{tete} consomme le plus : {classement.iloc[-1]:.1f} kWh par abonné.")

# 2. Évolution : courbe par commune
with onglets[1]:
    g = filtre.groupby(["mois", "commune"])[["kwh", "abonnes"]].sum()
    courbe = (g["kwh"] / g["abonnes"]).unstack()
    fig, ax = plt.subplots(figsize=(8, 4))
    courbe.plot(ax=ax)
    ax.set_title("Consommation par abonné et par commune")
    ax.set_xlabel("Mois")
    ax.set_ylabel("kWh par abonné")
    st.pyplot(fig)
    st.write(f"{len(choix_communes)} commune(s) affichée(s) pour {choix_annee}.")

# 3. Chaleur ou courant ? (résidentiel, toutes années)
with onglets[2]:
    res = df[df["type"] == "Résidentiel"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(res["heures_courant"], res["kwh_par_abonne"])
    ax.set_title("Quartiers résidentiels : courant et consommation")
    ax.set_xlabel("Heures de courant par jour")
    ax.set_ylabel("kWh par abonné")
    st.pyplot(fig)
    c1 = res["kwh_par_abonne"].corr(res["heures_courant"])
    c2 = res["kwh_par_abonne"].corr(res["temperature_c"])
    st.write(f"Corrélation avec les heures de courant : {c1:.2f} ; "
             f"avec la température : {c2:.2f}.")

# 4. Coupures : heures de courant par commune
with onglets[3]:
    med = filtre.groupby("commune")["heures_courant"].median().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4))
    med.plot(kind="barh", ax=ax)
    ax.set_title("Médiane des heures de courant par jour")
    ax.set_xlabel("Heures de courant par jour")
    ax.set_ylabel("Commune")
    st.pyplot(fig)
    st.write(f"{med.index[0]} a les coupures les plus longues "
             f"(médiane de {med.iloc[0]:.1f} h de courant par jour).")

# 5. Relevés hors du lot
with onglets[4]:
    top = df.nlargest(3, "kwh")[["mois", "quartier", "type", "kwh"]]
    st.dataframe(top, hide_index=True)
    st.write(f"Le plus gros relevé : {top.iloc[0]['quartier']} en "
             f"{top.iloc[0]['mois']} ({top.iloc[0]['kwh']:,} kWh).")