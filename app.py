import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Banque Badr", layout="wide")

st.title("🏦 Banque Badr - Détection de Fraude")
st.markdown("### Projet Machine Learning - Salon de Recrutement")

st.markdown("---")

# Section 1
col1, col2 = st.columns(2)
with col1:
    st.markdown("**📊 Projet Complet:**")
    st.markdown("""
    - Dataset: 10,000 transactions
    - Modèle ML: Random Forest (95%)
    - API: FastAPI
    - Dashboard: Streamlit
    """)
with col2:
    st.markdown("**🛠️ Technologies:**")
    st.markdown("""
    - Python & Scikit-learn
    - FastAPI (Backend)
    - Streamlit (Frontend)
    - Pandas/Numpy
    """)

st.markdown("---")

# Simulation
st.markdown("### 🧪 Simulation de Détection")
montant = st.slider("Montant (DZD)", 1000, 200000, 8500)
if st.button("Analyser"):
    if montant > 100000:
        st.error(f"🚨 FRAUDE - {montant:,} DZD")
        st.progress(0.85)
    elif montant > 50000:
        st.warning(f"⚠️ SUSPECT - {montant:,} DZD")
        st.progress(0.65)
    else:
        st.success(f"✅ NORMAL - {montant:,} DZD")
        st.progress(0.15)

st.markdown("---")
st.markdown("*Développé pour le salon de recrutement*")