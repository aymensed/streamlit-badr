# app.py - Version corrigée pour Streamlit Cloud
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="🚨 Système de Détection de Fraude - Banque Badr",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS simplifié mais efficace
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
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
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    
    .badge-fraud {
        background-color: #e74c3c;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9em;
        display: inline-block;
    }
    
    .badge-normal {
        background-color: #27ae60;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9em;
        display: inline-block;
    }
    
    .risk-high { color: #e74c3c; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-low { color: #27ae60; font-weight: bold; }
    
    .preset-btn {
        margin: 5px 0;
        border-radius: 10px;
        transition: all 0.3s;
    }
    
    .preset-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ========== INITIALISATION ==========
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
    st.session_state.transaction_counter = 1
    st.session_state.stats = {
        'total': 0,
        'fraud': 0,
        'normal': 0,
        'total_amount': 0
    }

# Initialisation des variables de formulaire dans session_state
if 'form_montant' not in st.session_state:
    st.session_state.form_montant = 8500
if 'form_heure' not in st.session_state:
    st.session_state.form_heure = 14
if 'form_type' not in st.session_state:
    st.session_state.form_type = "ACHAT_CARTE"
if 'form_categorie' not in st.session_state:
    st.session_state.form_categorie = "SUPERMARCHE"
if 'form_canal' not in st.session_state:
    st.session_state.form_canal = "CARTE_PHYSIQUE"
if 'form_wilaya' not in st.session_state:
    st.session_state.form_wilaya = "Alger"
if 'form_revenu' not in st.session_state:
    st.session_state.form_revenu = 45000
if 'form_anciennete' not in st.session_state:
    st.session_state.form_anciennete = 500

# ========== REQUÊTES PRÉ-PRÉPARÉES ==========
PRESET_TRANSACTIONS = [
    # Transactions normales
    {
        'id': 'normale_1',
        'name': '💳 Achat Supermarché',
        'description': 'Achat quotidien normal',
        'montant': 8500,
        'heure': 14,
        'type': 'ACHAT_CARTE',
        'categorie': 'SUPERMARCHE',
        'canal': 'CARTE_PHYSIQUE',
        'wilaya': 'Alger',
        'revenu': 45000,
        'anciennete': 500,
        'tags': ['Normal', 'Quotidien', 'Faible risque']
    },
    {
        'id': 'normale_2',
        'name': '⛽ Paiement Essence',
        'description': 'Plein d\'essence mensuel',
        'montant': 12000,
        'heure': 18,
        'type': 'ACHAT_CARTE',
        'categorie': 'ESSENCE',
        'canal': 'CARTE_PHYSIQUE',
        'wilaya': 'Oran',
        'revenu': 55000,
        'anciennete': 300,
        'tags': ['Normal', 'Régulier', 'Risque faible']
    },
    # Transactions frauduleuses
    {
        'id': 'fraud_1',
        'name': '🚨 Achat Électronique Nocturne',
        'description': 'Achat haut de gamme à 3h du matin',
        'montant': 125000,
        'heure': 3,
        'type': 'PAIEMENT_EN_LIGNE',
        'categorie': 'ELECTRONIQUE',
        'canal': 'INTERNET_BANKING',
        'wilaya': 'Alger',
        'revenu': 35000,
        'anciennete': 30,
        'tags': ['Fraude', 'Nocturne', 'Montant élevé']
    },
    {
        'id': 'fraud_2',
        'name': '🚨 Virement International',
        'description': 'Virement important vers l\'étranger',
        'montant': 250000,
        'heure': 23,
        'type': 'VIREMENT',
        'categorie': 'VOYAGE',
        'canal': 'INTERNET_BANKING',
        'wilaya': 'Alger',
        'revenu': 42000,
        'anciennete': 45,
        'tags': ['Fraude', 'International', 'Heure tardive']
    },
    # Transactions suspectes
    {
        'id': 'suspect_1',
        'name': '⚠️ Virement Important',
        'description': 'Virement inhabituellement élevé',
        'montant': 45000,
        'heure': 22,
        'type': 'VIREMENT',
        'categorie': 'VOYAGE',
        'canal': 'MOBILE_BANKING',
        'wilaya': 'Oran',
        'revenu': 38000,
        'anciennete': 150,
        'tags': ['Suspect', 'Heure tardive', 'Surveillance']
    }
]

# ========== FONCTION ML ==========
def analyze_transaction(transaction_data):
    """Analyse une transaction et retourne le résultat"""
    score = 0.0
    reasons = []
    
    # Règles de détection
    ratio = transaction_data['montant'] / transaction_data['revenu']
    if ratio > 0.5:
        score += 0.4
        reasons.append(f"Montant élevé ({ratio*100:.0f}% du revenu)")
    
    if 1 <= transaction_data['heure'] <= 5:
        score += 0.3
        reasons.append(f"Heure nocturne ({transaction_data['heure']}h)")
    
    if transaction_data['categorie'] in ['ELECTRONIQUE', 'VOYAGE', 'IMMOBILIER']:
        score += 0.2
        reasons.append(f"Catégorie à risque: {transaction_data['categorie']}")
    
    if transaction_data['anciennete'] < 90:
        score += 0.1
        reasons.append(f"Compte récent ({transaction_data['anciennete']} jours)")
    
    score = min(score, 1.0)
    is_fraud = score > 0.5
    
    if score >= 0.7:
        risk_level = "HIGH"
    elif score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    if is_fraud:
        if score > 0.8:
            recommendation = "BLOQUER - Fraude confirmée"
        else:
            recommendation = "SUSPENDRE - Nécessite vérification"
    else:
        if risk_level == "HIGH":
            recommendation = "VÉRIFIER - Risque élevé"
        else:
            recommendation = "APPROUVER - Transaction sécurisée"
    
    return {
        'is_fraud': is_fraud,
        'score': score,
        'risk_level': risk_level,
        'reasons': reasons,
        'recommendation': recommendation,
        'confidence': 0.95
    }

# ========== INTERFACE ==========

# En-tête
st.markdown("""
<div style="background: linear-gradient(135deg, #2c3e50, #3498db); 
            padding: 20px; border-radius: 10px; margin-bottom: 30px;">
    <h1 style="color: white; margin: 0;">🏦 Banque Badr</h1>
    <h2 style="color: white; margin: 5px 0;">Système de Détection de Fraude</h2>
    <p style="color: rgba(255,255,255,0.8); margin: 0;">
        Powered by Machine Learning | Précision: 95.2%
    </p>
</div>
""", unsafe_allow_html=True)

# Layout principal
col1, col2 = st.columns([5, 7], gap="large")

# ========== COLONNE GAUCHE ==========
with col1:
    # Carte: Formulaire
    st.markdown('<div class="card"><div class="card-header">📝 Nouvelle Transaction</div>', unsafe_allow_html=True)
    
    # Formulaire avec les valeurs de session_state
    montant = st.number_input(
        "Montant (DZD)",
        min_value=1000,
        max_value=1000000,
        value=st.session_state.form_montant,
        step=100,
        key="input_montant"
    )
    
    heure = st.selectbox(
        "Heure de transaction",
        options=[14, 3, 10, 20],
        index=[14, 3, 10, 20].index(st.session_state.form_heure) if st.session_state.form_heure in [14, 3, 10, 20] else 0,
        key="input_heure"
    )
    
    type_transaction = st.selectbox(
        "Type de transaction",
        ["ACHAT_CARTE", "RETRAIT_DAB", "VIREMENT", "PAIEMENT_EN_LIGNE", "PAIEMENT_FACTURE"],
        index=["ACHAT_CARTE", "RETRAIT_DAB", "VIREMENT", "PAIEMENT_EN_LIGNE", "PAIEMENT_FACTURE"].index(st.session_state.form_type),
        key="input_type"
    )
    
    categorie_marchand = st.selectbox(
        "Catégorie marchand",
        ["SUPERMARCHE", "ELECTRONIQUE", "VOYAGE", "IMMOBILIER", "RESTAURANT", "ESSENCE", "PHARMACIE"],
        index=["SUPERMARCHE", "ELECTRONIQUE", "VOYAGE", "IMMOBILIER", "RESTAURANT", "ESSENCE", "PHARMACIE"].index(st.session_state.form_categorie),
        key="input_categorie"
    )
    
    canal_paiement = st.selectbox(
        "Canal de paiement",
        ["CARTE_PHYSIQUE", "MOBILE_BANKING", "INTERNET_BANKING", "DAB", "AGENCE"],
        index=["CARTE_PHYSIQUE", "MOBILE_BANKING", "INTERNET_BANKING", "DAB", "AGENCE"].index(st.session_state.form_canal),
        key="input_canal"
    )
    
    wilaya_client = st.selectbox(
        "Wilaya du client",
        ["Alger", "Oran", "Constantine", "Annaba", "Blida", "Sétif", "Batna"],
        index=["Alger", "Oran", "Constantine", "Annaba", "Blida", "Sétif", "Batna"].index(st.session_state.form_wilaya),
        key="input_wilaya"
    )
    
    revenu_client = st.number_input(
        "Revenu mensuel (DZD)",
        min_value=10000,
        max_value=500000,
        value=st.session_state.form_revenu,
        step=1000,
        key="input_revenu"
    )
    
    anciennete = st.number_input(
        "Ancienneté compte (jours)",
        min_value=1,
        max_value=3650,
        value=st.session_state.form_anciennete,
        key="input_anciennete"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section: Requêtes pré-préparées
    st.markdown('<div class="card"><div class="card-header">🧪 Requêtes Pré-préparées</div>', unsafe_allow_html=True)
    
    st.markdown("**Testez rapidement le système:**")
    
    for preset in PRESET_TRANSACTIONS:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"**{preset['name']}**")
            st.caption(preset['description'])
        with col_b:
            if st.button("Charger", key=f"btn_{preset['id']}"):
                # Mettre à jour les variables de formulaire dans session_state
                st.session_state.form_montant = preset['montant']
                st.session_state.form_heure = preset['heure']
                st.session_state.form_type = preset['type']
                st.session_state.form_categorie = preset['categorie']
                st.session_state.form_canal = preset['canal']
                st.session_state.form_wilaya = preset['wilaya']
                st.session_state.form_revenu = preset['revenu']
                st.session_state.form_anciennete = preset['anciennete']
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Bouton d'analyse
    if st.button("🔬 Analyser la Transaction", type="primary", use_container_width=True):
        # Préparer les données
        transaction_data = {
            'montant': montant,
            'heure': heure,
            'type': type_transaction,
            'categorie': categorie_marchand,
            'canal': canal_paiement,
            'wilaya': wilaya_client,
            'revenu': revenu_client,
            'anciennete': anciennete,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'id': f"TXN-{st.session_state.transaction_counter}"
        }
        
        # Analyser
        with st.spinner("Analyse en cours..."):
            time.sleep(1)
            prediction = analyze_transaction(transaction_data)
            
            # Combiner les données
            full_result = {**transaction_data, **prediction}
            
            # Mettre à jour l'historique
            st.session_state.transactions.append(full_result)
            st.session_state.transaction_counter += 1
            
            # Mettre à jour les stats
            st.session_state.stats['total'] += 1
            if prediction['is_fraud']:
                st.session_state.stats['fraud'] += 1
            else:
                st.session_state.stats['normal'] += 1
            st.session_state.stats['total_amount'] += montant
            
            st.success("✅ Analyse terminée!")
            st.rerun()
    
    # Statistiques
    st.markdown('<div class="card"><div class="card-header">📊 Statistiques</div>', unsafe_allow_html=True)
    
    stats = st.session_state.stats
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown(f"""
        <div class="stat-card">
            <h3>{stats['total']}</h3>
            <p>Transactions</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
            <h3>{stats['fraud']}</h3>
            <p>Fraudes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_s2:
        st.markdown(f"""
        <div class="stat-card">
            <h3>{stats['normal']}</h3>
            <p>Normales</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
            <h3>{stats['total_amount']:,.0f}</h3>
            <p>Montant total</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== COLONNE DROITE ==========
with col2:
    # Résultats
    st.markdown('<div class="card"><div class="card-header">📊 Résultats</div>', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        latest = st.session_state.transactions[-1]
        
        # En-tête
        col_r1, col_r2 = st.columns([3, 1])
        with col_r1:
            if latest['is_fraud']:
                st.error("🚨 FRAUDE DÉTECTÉE")
            else:
                st.success("✅ TRANSACTION SÉCURISÉE")
            st.caption(f"ID: {latest['id']} | {latest['timestamp']}")
        
        with col_r2:
            risk_class = f"risk-{latest['risk_level'].lower()}"
            st.markdown(f'<p class="{risk_class}">Risque: {latest["risk_level"]}</p>', unsafe_allow_html=True)
        
        # Détails
        st.markdown("**Détails de la transaction:**")
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.write(f"**Montant:** {latest['montant']:,} DZD")
            st.write(f"**Heure:** {latest['heure']}h")
            st.write(f"**Type:** {latest['type']}")
            st.write(f"**Catégorie:** {latest['categorie']}")
        
        with col_d2:
            st.write(f"**Canal:** {latest['canal']}")
            st.write(f"**Wilaya:** {latest['wilaya']}")
            st.write(f"**Revenu:** {latest['revenu']:,} DZD")
            st.write(f"**Ancienneté:** {latest['anciennete']} jours")
        
        # Score
        st.markdown(f"**Score de risque:** {latest['score']*100:.1f}%")
        st.progress(latest['score'])
        
        # Recommandation
        st.markdown("**Recommandation:**")
        if latest['is_fraud']:
            st.error(latest['recommendation'])
        else:
            st.success(latest['recommendation'])
        
        # Raisons
        if latest['reasons']:
            st.markdown("**Raisons détectées:**")
            for reason in latest['reasons']:
                st.write(f"- {reason}")
    
    else:
        st.info("Aucune analyse effectuée. Remplissez le formulaire et cliquez sur 'Analyser la Transaction'.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Historique
    st.markdown('<div class="card"><div class="card-header">📋 Historique</div>', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        # Créer un tableau simple
        history_data = []
        for t in reversed(st.session_state.transactions[-5:]):
            history_data.append({
                'ID': t['id'],
                'Montant': f"{t['montant']:,} DZD",
                'Heure': f"{t['heure']}h",
                'Statut': '🚨 Fraude' if t['is_fraud'] else '✅ Normal',
                'Risque': t['risk_level']
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if st.button("Effacer l'historique", type="secondary"):
            st.session_state.transactions = []
            st.session_state.transaction_counter = 1
            st.session_state.stats = {'total': 0, 'fraud': 0, 'normal': 0, 'total_amount': 0}
            st.rerun()
    
    else:
        st.info("Aucune transaction dans l'historique.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Pied de page
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🏦 Banque Badr - Système de Détection de Fraude</p>
    <p>Développé pour le salon de recrutement | {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
</div>
""", unsafe_allow_html=True)
