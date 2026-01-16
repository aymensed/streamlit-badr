import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="🚨 Détection de Fraude - Banque Badr",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== CSS PERSONNALISÉ ==========
st.markdown("""
<style>
    .main { background: #f8f9fa; }
    .card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .card-header {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 12px 20px;
        border-radius: 10px 10px 0 0;
        margin: -20px -20px 20px -20px;
        font-weight: bold;
    }
    .stButton>button { width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ========== INITIALISATION DES ÉTATS (SESSION STATE) ==========
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
    st.session_state.transaction_counter = 1
    st.session_state.stats = {'total': 0, 'fraud': 0, 'normal': 0, 'total_amount': 0}

# Initialisation des clés du formulaire pour le lien bidirectionnel
default_values = {
    'montant_input': 8500,
    'heure_input': 14,
    'type_input': "ACHAT_CARTE",
    'categorie_input': "SUPERMARCHE",
    'canal_input': "CARTE_PHYSIQUE",
    'wilaya_input': "Alger",
    'revenu_input': 45000,
    'anciennete_input': 500
}

for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ========== DONNÉES DE TEST (PRESETS) ==========
PRESET_TRANSACTIONS = [
    {
        'id': 'normale_1',
        'name': '💳 Achat Supermarché',
        'description': 'Achat quotidien normal - 8,500 DZD à 14h',
        'montant': 8500, 'heure': 14, 'type': 'ACHAT_CARTE',
        'categorie': 'SUPERMARCHE', 'canal': 'CARTE_PHYSIQUE',
        'wilaya': 'Alger', 'revenu': 45000, 'anciennete': 500
    },
    {
        'id': 'fraud_1',
        'name': '🚨 Fraude Electronique',
        'description': 'Achat à 3h du matin - 125,000 DZD (Risque élevé)',
        'montant': 125000, 'heure': 3, 'type': 'PAIEMENT_EN_LIGNE',
        'categorie': 'ELECTRONIQUE', 'canal': 'INTERNET_BANKING',
        'wilaya': 'Alger', 'revenu': 35000, 'anciennete': 30
    },
    {
        'id': 'fraud_2',
        'name': '🚨 Virement Suspect',
        'description': 'Gros virement international à 23h',
        'montant': 250000, 'heure': 23, 'type': 'VIREMENT',
        'categorie': 'VOYAGE', 'canal': 'INTERNET_BANKING',
        'wilaya': 'Oran', 'revenu': 42000, 'anciennete': 45
    }
]

# ========== FONCTIONS LOGIQUES ==========
def load_preset_transaction(preset):
    """Met à jour directement le session_state lié aux widgets"""
    st.session_state.montant_input = preset['montant']
    st.session_state.heure_input = preset['heure']
    st.session_state.type_input = preset['type']
    st.session_state.categorie_input = preset['categorie']
    st.session_state.canal_input = preset['canal']
    st.session_state.wilaya_input = preset['wilaya']
    st.session_state.revenu_input = preset['revenu']
    st.session_state.anciennete_input = preset['anciennete']
    st.toast(f"✅ {preset['name']} chargé !")

def analyze_transaction(data):
    """Logique algorithmique de détection"""
    score = 0.0
    reasons = []
    
    # 1. Montant / Revenu
    ratio = data['montant'] / data['revenu']
    if ratio > 0.5:
        score += 0.5
        reasons.append(f"Montant très élevé ({ratio*100:.0f}% du revenu)")
    
    # 2. Heure critique
    if 1 <= data['heure'] <= 5:
        score += 0.3
        reasons.append(f"Transaction nocturne ({data['heure']}h)")
    
    # 3. Ancienneté
    if data['anciennete'] < 90:
        score += 0.2
        reasons.append("Compte trop récent")

    score = min(score, 1.0)
    is_fraud = score >= 0.5
    
    return {
        'is_fraud': is_fraud,
        'score': score,
        'risk_level': "HIGH" if score >= 0.7 else ("MEDIUM" if score >= 0.4 else "LOW"),
        'reasons': reasons,
        'recommendation': "🚨 BLOQUER" if score >= 0.7 else ("⚠️ VÉRIFIER" if score >= 0.4 else "✅ APPROUVER"),
        'confidence': 0.92
    }

# ========== INTERFACE UTILISATEUR ==========

# Header
st.markdown("""
<div style="background: #1e3a8a; padding: 20px; border-radius: 10px; color: white; margin-bottom: 25px;">
    <h1 style='margin:0;'>🏦 Banque Badr - IA Fraud Shield</h1>
    <p style='margin:0; opacity: 0.8;'>Système de surveillance des transactions en temps réel</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5, 7], gap="large")

with col1:
    # 1. FORMULAIRE (Directement lié au session_state)
    st.markdown('<div class="card"><div class="card-header">📝 Paramètres de Transaction</div>', unsafe_allow_html=True)
    
    st.number_input("💰 Montant (DZD)", min_value=1000, step=1000, key="montant_input")
    st.selectbox("🕐 Heure", options=list(range(24)), key="heure_input")
    st.selectbox("📋 Type", ["ACHAT_CARTE", "RETRAIT_DAB", "VIREMENT", "PAIEMENT_EN_LIGNE"], key="type_input")
    st.selectbox("🏷️ Catégorie", ["SUPERMARCHE", "ELECTRONIQUE", "VOYAGE", "RESTAURANT", "ESSENCE"], key="categorie_input")
    st.selectbox("📱 Canal", ["CARTE_PHYSIQUE", "MOBILE_BANKING", "INTERNET_BANKING", "AGENCE"], key="canal_input")
    st.selectbox("📍 Wilaya", ["Alger", "Oran", "Constantine", "Annaba", "Sétif"], key="wilaya_input")
    st.number_input("💵 Revenu mensuel (DZD)", min_value=10000, step=1000, key="revenu_input")
    st.number_input("📅 Ancienneté (jours)", min_value=1, key="anciennete_input")
    
    if st.button("🔬 Analyser maintenant", type="primary"):
        current_data = {
            'montant': st.session_state.montant_input,
            'heure': st.session_state.heure_input,
            'type': st.session_state.type_input,
            'categorie': st.session_state.categorie_input,
            'canal': st.session_state.canal_input,
            'wilaya': st.session_state.wilaya_input,
            'revenu': st.session_state.revenu_input,
            'anciennete': st.session_state.anciennete_input
        }
        res = analyze_transaction(current_data)
        
        # Enregistrement
        record = {**current_data, **res, 'id': f"TX-{st.session_state.transaction_counter}", 'time': datetime.now().strftime("%H:%M:%S")}
        st.session_state.transactions.append(record)
        st.session_state.transaction_counter += 1
        st.session_state.stats['total'] += 1
        if res['is_fraud']: st.session_state.stats['fraud'] += 1
        else: st.session_state.stats['normal'] += 1
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. PRESETS
    st.markdown('<div class="card"><div class="card-header">🧪 Scénarios de Test</div>', unsafe_allow_html=True)
    for p in PRESET_TRANSACTIONS:
        if st.button(f"📥 Charger : {p['name']}", key=f"btn_{p['id']}"):
            load_preset_transaction(p)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # 3. RÉSULTAT DE L'ANALYSE
    st.markdown('<div class="card"><div class="card-header">📊 Diagnostic IA</div>', unsafe_allow_html=True)
    if st.session_state.transactions:
        last = st.session_state.transactions[-1]
        
        # Alerte visuelle
        color = "#ef4444" if last['is_fraud'] else "#10b981"
        st.markdown(f"""
        <div style="padding:15px; border-radius:10px; background:{color}22; border:2px solid {color}; text-align:center;">
            <h2 style="color:{color}; margin:0;">{last['risk_level']} RISK</h2>
            <h1 style="color:{color}; margin:0;">{last['recommendation']}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(f"**Probabilité de fraude :** {last['score']*100:.1f}%")
        st.progress(last['score'])
        
        if last['reasons']:
            st.warning("**Indicateurs détectés :**\n" + "\n".join([f"- {r}" for r in last['reasons']]))
    else:
        st.info("En attente d'une transaction à analyser...")
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. HISTORIQUE
    st.markdown('<div class="card"><div class="card-header">📋 Dernières Analyses</div>', unsafe_allow_html=True)
    if st.session_state.transactions:
        df = pd.DataFrame(st.session_state.transactions).tail(5)
        st.dataframe(df[['id', 'time', 'montant', 'risk_level', 'recommendation']], use_container_width=True)
        if st.button("🗑️ Effacer tout"):
            st.session_state.transactions = []
            st.session_state.stats = {'total': 0, 'fraud': 0, 'normal': 0, 'total_amount': 0}
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.caption("Version Démo - Salon de recrutement 2026 - Banque Badr")
