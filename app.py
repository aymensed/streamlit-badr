import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ======================================================
# CONFIG PAGE
# ======================================================
st.set_page_config(
    page_title="🚨 Anti-Fraude - Banque Badr",
    page_icon="🏦",
    layout="wide"
)

# ======================================================
# CSS
# ======================================================
st.markdown("""
<style>
.card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.card-header {
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    color: white;
    padding: 15px;
    border-radius: 10px 10px 0 0;
    margin: -25px -25px 20px -25px;
    font-weight: bold;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# INITIALISATION SESSION STATE
# ======================================================
DEFAULTS = {
    "montant": 8500,
    "heure": 14,
    "type": "ACHAT_CARTE",
    "categorie": "SUPERMARCHE",
    "canal": "CARTE_PHYSIQUE",
    "wilaya": "Alger",
    "revenu": 45000,
    "anciennete": 500
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "transactions" not in st.session_state:
    st.session_state.transactions = []

# ======================================================
# PRESETS
# ======================================================
PRESETS = [
    {
        "id": "normal",
        "name": "💳 Achat Supermarché",
        "montant": 8500, "heure": 14, "type": "ACHAT_CARTE",
        "categorie": "SUPERMARCHE", "canal": "CARTE_PHYSIQUE",
        "wilaya": "Alger", "revenu": 45000, "anciennete": 500
    },
    {
        "id": "fraud1",
        "name": "🚨 Achat Nocturne",
        "montant": 125000, "heure": 3, "type": "PAIEMENT_EN_LIGNE",
        "categorie": "ELECTRONIQUE", "canal": "INTERNET_BANKING",
        "wilaya": "Alger", "revenu": 35000, "anciennete": 30
    }
]

def load_preset(preset):
    for k in DEFAULTS.keys():
        st.session_state[k] = preset[k]
    st.rerun()

# ======================================================
# LOGIQUE FRAUDE
# ======================================================
def analyze():
    score = 0
    ratio = st.session_state.montant / st.session_state.revenu

    if ratio > 0.6:
        score += 0.5
    if 1 <= st.session_state.heure <= 5:
        score += 0.3
    if st.session_state.anciennete < 60:
        score += 0.2

    score = min(score, 1.0)
    return score, score >= 0.5

# ======================================================
# UI
# ======================================================
st.markdown("""
<div style="background:linear-gradient(135deg,#1e3c72,#2a5298);
padding:25px;border-radius:15px;color:white;text-align:center">
<h1>🏦 Banque Badr – IA Anti-Fraude</h1>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5, 7])

# ======================================================
# FORMULAIRE
# ======================================================
with col1:
    st.markdown('<div class="card"><div class="card-header">📝 Transaction</div>', unsafe_allow_html=True)

    st.number_input("💰 Montant", min_value=0, key="montant")
    st.selectbox("🕐 Heure", list(range(24)), key="heure")
    st.selectbox("📋 Type", ["ACHAT_CARTE","VIREMENT","PAIEMENT_EN_LIGNE"], key="type")
    st.selectbox("🏷️ Catégorie", ["SUPERMARCHE","ELECTRONIQUE","VOYAGE"], key="categorie")
    st.selectbox("📱 Canal", ["CARTE_PHYSIQUE","INTERNET_BANKING"], key="canal")
    st.selectbox("📍 Wilaya", ["Alger","Oran","Sétif"], key="wilaya")
    st.number_input("💵 Revenu", min_value=1, key="revenu")
    st.number_input("📅 Ancienneté (jours)", min_value=0, key="anciennete")

    if st.button("🔬 ANALYSER", type="primary"):
        score, fraud = analyze()
        st.session_state.transactions.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "score": score,
            "fraud": fraud
        })
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">🧪 Presets</div>', unsafe_allow_html=True)
    for p in PRESETS:
        st.button(f"📥 {p['name']}", on_click=load_preset, args=(p,))
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# RÉSULTATS
# ======================================================
with col2:
    st.markdown('<div class="card"><div class="card-header">📊 Résultat</div>', unsafe_allow_html=True)

    if st.session_state.transactions:
        last = st.session_state.transactions[-1]
        st.metric("Score", f"{last['score']*100:.1f}%")
        st.progress(last['score'])
        st.success("🚨 FRAUDE" if last["fraud"] else "✅ TRANSACTION OK")
    else:
        st.info("Aucune analyse")

    st.markdown("</div>", unsafe_allow_html=True)
