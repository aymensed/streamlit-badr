import streamlit as st
import pandas as pd
import time
from datetime import datetime

# =====================================================
# CONFIGURATION PAGE
# =====================================================
st.set_page_config(
    page_title="🚨 Détection de Fraude - Banque Badr",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# STYLE CSS
# =====================================================
st.markdown("""
<style>
.card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.card-header {
    background: linear-gradient(135deg, #2c3e50, #3498db);
    color: white;
    padding: 15px;
    border-radius: 10px 10px 0 0;
    margin: -20px -20px 20px -20px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# INITIALISATION SESSION STATE
# =====================================================
if "transactions" not in st.session_state:
    st.session_state.transactions = []
    st.session_state.counter = 1
    st.session_state.stats = {"total": 0, "fraud": 0, "normal": 0}

DEFAULT_TRANSACTION = {
    "montant": 8500,
    "heure": 14,
    "type": "ACHAT_CARTE",
    "categorie": "SUPERMARCHE",
    "canal": "CARTE_PHYSIQUE",
    "wilaya": "Alger",
    "revenu": 45000,
    "anciennete": 500,
}

# Injecter les valeurs par défaut dans session_state
for k, v in DEFAULT_TRANSACTION.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =====================================================
# PRESETS
# =====================================================
PRESET_TRANSACTIONS = [
    {
        "id": "normal_1",
        "name": "💳 Achat Supermarché",
        "description": "8 500 DZD à 14h",
        **DEFAULT_TRANSACTION
    },
    {
        "id": "fraud_1",
        "name": "🚨 Achat nocturne",
        "description": "125 000 DZD à 03h",
        "montant": 125000,
        "heure": 3,
        "type": "PAIEMENT_EN_LIGNE",
        "categorie": "ELECTRONIQUE",
        "canal": "INTERNET_BANKING",
        "wilaya": "Alger",
        "revenu": 35000,
        "anciennete": 30
    },
]

# =====================================================
# FONCTIONS
# =====================================================
def load_preset(preset_id):
    for p in PRESET_TRANSACTIONS:
        if p["id"] == preset_id:
            for key in DEFAULT_TRANSACTION.keys():
                st.session_state[key] = p[key]
            st.success(f"✅ {p['name']} chargé")
            st.rerun()

def analyze():
    ratio = st.session_state.montant / st.session_state.revenu
    score = 0

    if ratio > 0.5:
        score += 0.4
    if 1 <= st.session_state.heure <= 5:
        score += 0.3
    if st.session_state.categorie in ["ELECTRONIQUE", "VOYAGE", "IMMOBILIER"]:
        score += 0.2
    if st.session_state.anciennete < 90:
        score += 0.1

    score = min(score, 1.0)
    is_fraud = score > 0.5

    return score, is_fraud

def save_result(score, is_fraud):
    st.session_state.transactions.append({
        "id": f"TX-{st.session_state.counter}",
        "time": datetime.now().strftime("%H:%M:%S"),
        "montant": st.session_state.montant,
        "score": score,
        "fraud": is_fraud
    })
    st.session_state.counter += 1
    st.session_state.stats["total"] += 1
    st.session_state.stats["fraud" if is_fraud else "normal"] += 1

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div style="padding:25px;background:linear-gradient(135deg,#2c3e50,#3498db);
border-radius:12px;color:white">
<h1>🏦 Banque Badr</h1>
<h3>Système Intelligent de Détection de Fraude</h3>
</div>
""", unsafe_allow_html=True)

# =====================================================
# LAYOUT
# =====================================================
col1, col2 = st.columns([5,7])

# =====================================================
# COLONNE GAUCHE
# =====================================================
with col1:
    st.markdown('<div class="card"><div class="card-header">📝 Transaction</div>', unsafe_allow_html=True)

    st.number_input("💰 Montant", 1000, 1000000, step=100, key="montant")
    st.selectbox("🕐 Heure", list(range(24)), key="heure")
    st.selectbox("📋 Type", ["ACHAT_CARTE","RETRAIT_DAB","VIREMENT","PAIEMENT_EN_LIGNE"], key="type")
    st.selectbox("🏷️ Catégorie", ["SUPERMARCHE","ELECTRONIQUE","VOYAGE","IMMOBILIER"], key="categorie")
    st.selectbox("📱 Canal", ["CARTE_PHYSIQUE","MOBILE_BANKING","INTERNET_BANKING"], key="canal")
    st.selectbox("📍 Wilaya", ["Alger","Oran","Sétif","Annaba"], key="wilaya")
    st.number_input("💵 Revenu", 10000, 500000, step=1000, key="revenu")
    st.number_input("📅 Ancienneté (jours)", 1, 3650, key="anciennete")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">🧪 Cas de Test</div>', unsafe_allow_html=True)
    for p in PRESET_TRANSACTIONS:
        if st.button(f"📥 {p['name']}", key=p["id"]):
            load_preset(p["id"])
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔬 Analyser", type="primary", use_container_width=True):
        with st.spinner("Analyse en cours..."):
            time.sleep(1)
            score, fraud = analyze()
            save_result(score, fraud)
            st.success("Analyse terminée")
            st.rerun()

# =====================================================
# COLONNE DROITE
# =====================================================
with col2:
    st.markdown('<div class="card"><div class="card-header">📊 Résultats</div>', unsafe_allow_html=True)

    if st.session_state.transactions:
        t = st.session_state.transactions[-1]
        st.metric("Score de risque", f"{t['score']*100:.1f}%")
        st.metric("Statut", "🚨 Fraude" if t["fraud"] else "✅ Normal")
        st.progress(t["score"])
    else:
        st.info("Aucune analyse effectuée")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">📋 Historique</div>', unsafe_allow_html=True)
    if st.session_state.transactions:
        st.dataframe(pd.DataFrame(st.session_state.transactions))
    else:
        st.write("Historique vide")
    st.markdown("</div>", unsafe_allow_html=True)
