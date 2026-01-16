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
# CSS PERSONNALISÉ
# ======================================================
st.markdown("""
<style>
.main { background-color: #f5f7f9; }
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
.stButton>button { width: 100%; }
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
# NOUVEAUX CAS PRÉPARÉS (PRESETS)
# ======================================================
PRESETS = [
    {
        "name": "✅ Achat Routine (Normal)",
        "montant": 4200, "heure": 11, "type": "ACHAT_CARTE",
        "categorie": "SUPERMARCHE", "canal": "CARTE_PHYSIQUE",
        "wilaya": "Alger", "revenu": 55000, "anciennete": 1200
    },
    {
        "name": "🚨 Vol de Carte (Nocturne)",
        "montant": 185000, "heure": 3, "type": "PAIEMENT_EN_LIGNE",
        "categorie": "ELECTRONIQUE", "canal": "INTERNET_BANKING",
        "wilaya": "Alger", "revenu": 40000, "anciennete": 450
    },
    {
        "name": "⚠️ Compte Récent (Risque)",
        "montant": 55000, "heure": 15, "type": "VIREMENT",
        "categorie": "VOYAGE", "canal": "INTERNET_BANKING",
        "wilaya": "Oran", "revenu": 35000, "anciennete": 12
    },
    {
        "name": "🚨 Blanchiment (Gros Montant)",
        "montant": 950000, "heure": 10, "type": "VIREMENT",
        "categorie": "IMMOBILIER", "canal": "AGENCE",
        "wilaya": "Sétif", "revenu": 60000, "anciennete": 2000
    },
    {
        "name": "✅ Plein Essence (Normal)",
        "montant": 2500, "heure": 18, "type": "ACHAT_CARTE",
        "categorie": "ESSENCE", "canal": "CARTE_PHYSIQUE",
        "wilaya": "Sétif", "revenu": 48000, "anciennete": 800
    },
    {
        "name": "⚠️ Voyage Inhabituel",
        "montant": 120000, "heure": 22, "type": "PAIEMENT_EN_LIGNE",
        "categorie": "VOYAGE", "canal": "INTERNET_BANKING",
        "wilaya": "Constantine", "revenu": 50000, "anciennete": 150
    }
]

def load_preset(preset):
    for k in DEFAULTS.keys():
        st.session_state[k] = preset[k]

# ======================================================
# LOGIQUE D'ANALYSE
# ======================================================
def analyze():
    score = 0.0
    reasons = []
    
    ratio = st.session_state.montant / st.session_state.revenu

    # 1. Ratio Montant/Revenu
    if ratio > 5: # Plus de 5 mois de salaire en une fois
        score += 0.7
        reasons.append("Montant démesuré par rapport au revenu")
    elif ratio > 1:
        score += 0.4
        reasons.append("Montant supérieur au revenu mensuel")

    # 2. Heure Suspecte
    if 1 <= st.session_state.heure <= 5:
        score += 0.3
        reasons.append("Transaction effectuée au milieu de la nuit")

    # 3. Ancienneté
    if st.session_state.anciennete < 30:
        score += 0.2
        reasons.append("Compte très récent (moins de 30 jours)")

    score = min(score, 1.0)
    return score, score >= 0.5, reasons

# ======================================================
# INTERFACE UTILISATEUR
# ======================================================
st.markdown("""
<div style="background:linear-gradient(135deg,#1e3c72,#2a5298);
padding:25px;border-radius:15px;color:white;text-align:center;margin-bottom:20px">
<h1 style='margin:0'>🏦 Banque Badr – IA Anti-Fraude</h1>
<p style='margin:0; opacity:0.8'>Détection en temps réel des transactions suspectes</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5, 7], gap="large")

# --- COLONNE GAUCHE : FORMULAIRE & PRESETS ---
with col1:
    st.markdown('<div class="card"><div class="card-header">📝 Paramètres de Transaction</div>', unsafe_allow_html=True)
    
    st.number_input("💰 Montant (DZD)", min_value=0, key="montant")
    st.selectbox("🕐 Heure de transaction", list(range(24)), key="heure")
    st.selectbox("📋 Type", ["ACHAT_CARTE","VIREMENT","PAIEMENT_EN_LIGNE","RETRAIT_DAB"], key="type")
    st.selectbox("🏷️ Catégorie", ["SUPERMARCHE","ELECTRONIQUE","VOYAGE","IMMOBILIER","ESSENCE","RESTAURANT"], key="categorie")
    st.selectbox("📱 Canal", ["CARTE_PHYSIQUE","INTERNET_BANKING","MOBILE_BANKING","AGENCE"], key="canal")
    st.selectbox("📍 Wilaya", ["Alger","Oran","Sétif","Constantine","Annaba","Blida"], key="wilaya")
    st.number_input("💵 Revenu Mensuel", min_value=1, key="revenu")
    st.number_input("📅 Ancienneté du compte (jours)", min_value=0, key="anciennete")

    if st.button("🔬 ANALYSER LA TRANSACTION", type="primary"):
        with st.spinner('Analyse IA en cours...'):
            time.sleep(0.5)
            score, is_fraud, reasons = analyze()
            st.session_state.transactions.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "montant": st.session_state.montant,
                "score": score,
                "fraud": is_fraud,
                "reasons": reasons
            })
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">🧪 Cas de Test Préparés</div>', unsafe_allow_html=True)
    cols_preset = st.columns(2)
    for i, p in enumerate(PRESETS):
        with cols_preset[i % 2]:
            st.button(p['name'], on_click=load_preset, args=(p,), key=f"p_{i}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- COLONNE DROITE : RÉSULTATS ---
with col2:
    st.markdown('<div class="card"><div class="card-header">📊 Rapport de Risque</div>', unsafe_allow_html=True)

    if st.session_state.transactions:
        last = st.session_state.transactions[-1]
        
        # Jauge de score
        st.write(f"**Niveau de suspicion : {last['score']*100:.0f}%**")
        st.progress(last['score'])
        
        # Statut avec Alerte
        if last["fraud"]:
            st.markdown(f"""
                <div style="background-color:#ff4b4b; padding:20px; border-radius:10px; color:white; text-align:center; margin-top:20px">
                    <h2 style='margin:0'>🚨 ALERTE FRAUDE</h2>
                    <p style='margin:0'>Transaction bloquée par le système</p>
                </div>
            """, unsafe_allow_html=True)
            if last['reasons']:
                st.info("**Motifs de détection :**\n\n" + "\n".join([f"- {r}" for r in last['reasons']]))
        else:
            st.markdown(f"""
                <div style="background-color:#09ab3b; padding:20px; border-radius:10px; color:white; text-align:center; margin-top:20px">
                    <h2 style='margin:0'>✅ TRANSACTION VALIDE</h2>
                    <p style='margin:0'>Aucune anomalie critique détectée</p>
                </div>
            """, unsafe_allow_html=True)
            
        # Historique rapide
        st.markdown("### 📋 Historique récent")
        df_history = pd.DataFrame(st.session_state.transactions).tail(5)
        st.dataframe(df_history[['time', 'montant', 'score', 'fraud']], use_container_width=True)
        
    else:
        st.info("Veuillez charger un cas de test ou remplir le formulaire pour lancer l'analyse.")

    st.markdown("</div>", unsafe_allow_html=True)
