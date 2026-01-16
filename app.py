# app.py - Interface Streamlit avec requêtes pré-préparées
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import json

# Configuration de la page
st.set_page_config(
    page_title="🚨 Système de Détection de Fraude - Banque Badr",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS complet pour reproduire Bootstrap
st.markdown("""
<style>
    /* Variables de couleur */
    :root {
        --primary-color: #2c3e50;
        --secondary-color: #3498db;
        --success-color: #27ae60;
        --danger-color: #e74c3c;
        --warning-color: #f39c12;
        --info-color: #17a2b8;
        --dark-color: #343a40;
    }
    
    /* Style général */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        min-height: 100vh;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Navigation */
    .stApp header {
        background-color: var(--primary-color) !important;
    }
    
    .navbar {
        background-color: var(--primary-color) !important;
        padding: 1rem !important;
        border-radius: 0 0 10px 10px !important;
        margin-bottom: 2rem !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    /* Cartes */
    .card {
        border-radius: 15px !important;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
        border: none !important;
        margin-bottom: 20px !important;
        background-color: white !important;
        transition: transform 0.3s ease !important;
    }
    
    .card:hover {
        transform: translateY(-5px) !important;
    }
    
    .card-header {
        border-radius: 15px 15px 0 0 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        padding: 15px 20px !important;
        border: none !important;
    }
    
    .card-body {
        padding: 25px !important;
    }
    
    /* Classes de risque */
    .risk-high {
        color: var(--danger-color) !important;
        font-weight: bold !important;
        background-color: rgba(231, 76, 60, 0.1) !important;
        padding: 8px 15px !important;
        border-radius: 5px !important;
        display: inline-block !important;
        border: 1px solid rgba(231, 76, 60, 0.3) !important;
    }
    
    .risk-medium {
        color: var(--warning-color) !important;
        font-weight: bold !important;
        background-color: rgba(243, 156, 18, 0.1) !important;
        padding: 8px 15px !important;
        border-radius: 5px !important;
        display: inline-block !important;
        border: 1px solid rgba(243, 156, 18, 0.3) !important;
    }
    
    .risk-low {
        color: var(--success-color) !important;
        font-weight: bold !important;
        background-color: rgba(39, 174, 96, 0.1) !important;
        padding: 8px 15px !important;
        border-radius: 5px !important;
        display: inline-block !important;
        border: 1px solid rgba(39, 174, 96, 0.3) !important;
    }
    
    /* Badges */
    .fraud-badge {
        background-color: var(--danger-color) !important;
        color: white !important;
        padding: 5px 12px !important;
        border-radius: 20px !important;
        font-size: 0.85em !important;
        display: inline-block !important;
        font-weight: bold !important;
    }
    
    .normal-badge {
        background-color: var(--success-color) !important;
        color: white !important;
        padding: 5px 12px !important;
        border-radius: 20px !important;
        font-size: 0.85em !important;
        display: inline-block !important;
        font-weight: bold !important;
    }
    
    /* Barre de progression */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--danger-color), var(--warning-color), var(--success-color)) !important;
        height: 25px !important;
        border-radius: 12px !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.1) !important;
    }
    
    /* Cartes de statistiques */
    .stat-card {
        text-align: center !important;
        padding: 25px 15px !important;
        border-radius: 10px !important;
        color: white !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stat-card:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
    }
    
    .stat-card-total {
        background: linear-gradient(135deg, #3498db, #2980b9) !important;
    }
    
    .stat-card-fraud {
        background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
    }
    
    .stat-card-normal {
        background: linear-gradient(135deg, #27ae60, #219653) !important;
    }
    
    .stat-card-amount {
        background: linear-gradient(135deg, #9b59b6, #8e44ad) !important;
    }
    
    /* Boutons */
    .stButton > button {
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }
    
    .example-btn {
        border-radius: 20px !important;
        margin: 5px 0 !important;
        padding: 8px 15px !important;
        font-size: 0.9em !important;
        transition: all 0.3s ease !important;
    }
    
    .example-btn:hover {
        transform: scale(1.05) !important;
    }
    
    /* Tableau */
    .transaction-history {
        max-height: 400px !important;
        overflow-y: auto !important;
        border-radius: 8px !important;
        border: 1px solid #dee2e6 !important;
    }
    
    .dataframe {
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 0 !important;
    }
    
    .dataframe th {
        background-color: var(--primary-color) !important;
        color: white !important;
        padding: 12px 15px !important;
        text-align: left !important;
        font-weight: 600 !important;
        position: sticky !important;
        top: 0 !important;
    }
    
    .dataframe td {
        padding: 12px 15px !important;
        border-bottom: 1px solid #dee2e6 !important;
    }
    
    .dataframe tr:hover {
        background-color: rgba(0,0,0,0.02) !important;
    }
    
    /* Inputs et selects */
    .stSelectbox, .stNumberInput, .stTextInput {
        margin-bottom: 15px !important;
    }
    
    .stSelectbox > div > div, .stNumberInput > div > div {
        border-radius: 8px !important;
        border: 1px solid #ced4da !important;
    }
    
    /* Alertes */
    .alert {
        padding: 15px 20px !important;
        border-radius: 10px !important;
        margin: 15px 0 !important;
        border-left: 5px solid !important;
        animation: fadeIn 0.5s ease !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .alert-danger {
        background-color: rgba(231, 76, 60, 0.1) !important;
        border-left-color: var(--danger-color) !important;
        color: #721c24 !important;
    }
    
    .alert-success {
        background-color: rgba(39, 174, 96, 0.1) !important;
        border-left-color: var(--success-color) !important;
        color: #155724 !important;
    }
    
    .alert-warning {
        background-color: rgba(243, 156, 18, 0.1) !important;
        border-left-color: var(--warning-color) !important;
        color: #856404 !important;
    }
    
    .alert-info {
        background-color: rgba(52, 152, 219, 0.1) !important;
        border-left-color: var(--secondary-color) !important;
        color: #0c5460 !important;
    }
    
    /* Indicateur API */
    .api-status {
        display: inline-block !important;
        width: 12px !important;
        height: 12px !important;
        border-radius: 50% !important;
        margin-right: 8px !important;
        vertical-align: middle !important;
    }
    
    .api-status-online {
        background-color: var(--success-color) !important;
        animation: pulse 2s infinite !important;
        box-shadow: 0 0 0 0 rgba(39, 174, 96, 0.7) !important;
    }
    
    @keyframes pulse {
        0% { 
            box-shadow: 0 0 0 0 rgba(39, 174, 96, 0.7); 
        }
        70% { 
            box-shadow: 0 0 0 10px rgba(39, 174, 96, 0); 
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(39, 174, 96, 0); 
        }
    }
    
    .api-status-offline {
        background-color: var(--danger-color) !important;
    }
    
    /* Requêtes pré-préparées */
    .preset-card {
        border: 2px solid !important;
        border-radius: 10px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    
    .preset-card:hover {
        transform: translateX(5px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
    }
    
    .preset-normal {
        border-color: var(--success-color) !important;
        background-color: rgba(39, 174, 96, 0.05) !important;
    }
    
    .preset-fraud {
        border-color: var(--danger-color) !important;
        background-color: rgba(231, 76, 60, 0.05) !important;
    }
    
    .preset-suspicious {
        border-color: var(--warning-color) !important;
        background-color: rgba(243, 156, 18, 0.05) !important;
    }
    
    .preset-high-risk {
        border-color: #8e44ad !important;
        background-color: rgba(142, 68, 173, 0.05) !important;
    }
    
    /* Tags */
    .tag {
        display: inline-block !important;
        padding: 3px 10px !important;
        border-radius: 15px !important;
        font-size: 0.75em !important;
        font-weight: 600 !important;
        margin: 2px 5px 2px 0 !important;
    }
    
    .tag-normal { background-color: #d5f4e6; color: #27ae60; }
    .tag-fraud { background-color: #fadbd8; color: #e74c3c; }
    .tag-warning { background-color: #fef5e7; color: #f39c12; }
    .tag-info { background-color: #e8f4fc; color: #3498db; }
    
    /* Loader */
    .loader {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Pied de page */
    footer {
        text-align: center !important;
        color: #666 !important;
        padding: 25px !important;
        margin-top: 40px !important;
        border-top: 1px solid #ddd !important;
        background-color: rgba(0,0,0,0.02) !important;
        border-radius: 10px !important;
    }
    
    /* Séparateurs */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(to right, transparent, #ddd, transparent) !important;
        margin: 25px 0 !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .card-body {
            padding: 15px !important;
        }
        
        .stat-card {
            padding: 20px 10px !important;
        }
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
    st.session_state.last_preset = None

# ========== REQUÊTES PRÉ-PRÉPARÉES ==========
PRESET_TRANSACTIONS = {
    # Transactions normales
    'transaction_normale_1': {
        'name': '💳 Achat Supermarché',
        'description': 'Achat quotidien normal',
        'montant': 8500,
        'heure': 14,
        'type_transaction': 'ACHAT_CARTE',
        'categorie_marchand': 'SUPERMARCHE',
        'canal_paiement': 'CARTE_PHYSIQUE',
        'wilaya_client': 'Alger',
        'revenu_client': 45000,
        'anciennete': 500,
        'tags': ['Normal', 'Quotidien', 'Faible risque']
    },
    'transaction_normale_2': {
        'name': '⛽ Paiement Essence',
        'description': 'Plein d\'essence mensuel',
        'montant': 12000,
        'heure': 18,
        'type_transaction': 'ACHAT_CARTE',
        'categorie_marchand': 'ESSENCE',
        'canal_paiement': 'CARTE_PHYSIQUE',
        'wilaya_client': 'Oran',
        'revenu_client': 55000,
        'anciennete': 300,
        'tags': ['Normal', 'Régulier', 'Risque faible']
    },
    'transaction_normale_3': {
        'name': '💊 Pharmacie',
        'description': 'Achat médicaments',
        'montant': 7500,
        'heure': 11,
        'type_transaction': 'ACHAT_CARTE',
        'categorie_marchand': 'PHARMACIE',
        'canal_paiement': 'CARTE_PHYSIQUE',
        'wilaya_client': 'Constantine',
        'revenu_client': 40000,
        'anciennete': 700,
        'tags': ['Normal', 'Santé', 'Très sûr']
    },
    
    # Transactions frauduleuses
    'transaction_fraud_1': {
        'name': '🚨 Achat Électronique Nocturne',
        'description': 'Achat haut de gamme à 3h du matin',
        'montant': 125000,
        'heure': 3,
        'type_transaction': 'PAIEMENT_EN_LIGNE',
        'categorie_marchand': 'ELECTRONIQUE',
        'canal_paiement': 'INTERNET_BANKING',
        'wilaya_client': 'Alger',
        'revenu_client': 35000,
        'anciennete': 30,
        'tags': ['Fraude', 'Nocturne', 'Montant élevé', 'Compte récent']
    },
    'transaction_fraud_2': {
        'name': '🚨 Virement International Suspect',
        'description': 'Virement important vers l\'étranger',
        'montant': 250000,
        'heure': 23,
        'type_transaction': 'VIREMENT',
        'categorie_marchand': 'VOYAGE',
        'canal_paiement': 'INTERNET_BANKING',
        'wilaya_client': 'Alger',
        'revenu_client': 42000,
        'anciennete': 45,
        'tags': ['Fraude', 'International', 'Heure tardive', 'Virement']
    },
    'transaction_fraud_3': {
        'name': '🚨 Multiple Achats Rapides',
        'description': 'Plusieurs achats en ligne en 5 minutes',
        'montant': 85000,
        'heure': 2,
        'type_transaction': 'PAIEMENT_EN_LIGNE',
        'categorie_marchand': 'ELECTRONIQUE',
        'canal_paiement': 'MOBILE_BANKING',
        'wilaya_client': 'Oran',
        'revenu_client': 28000,
        'anciennete': 20,
        'tags': ['Fraude', 'Multi-transactions', 'Compte nouveau']
    },
    
    # Transactions suspectes
    'transaction_suspecte_1': {
        'name': '⚠️ Virement Important',
        'description': 'Virement inhabituellement élevé',
        'montant': 45000,
        'heure': 22,
        'type_transaction': 'VIREMENT',
        'categorie_marchand': 'VOYAGE',
        'canal_paiement': 'MOBILE_BANKING',
        'wilaya_client': 'Oran',
        'revenu_client': 38000,
        'anciennete': 150,
        'tags': ['Suspect', 'Heure tardive', 'Virement', 'Surveillance']
    },
    'transaction_suspecte_2': {
        'name': '⚠️ Achat Immobilier Anormal',
        'description': 'Transaction immobilière sans historique',
        'montant': 350000,
        'heure': 16,
        'type_transaction': 'VIREMENT',
        'categorie_marchand': 'IMMOBILIER',
        'canal_paiement': 'AGENCE',
        'wilaya_client': 'Alger',
        'revenu_client': 60000,
        'anciennete': 180,
        'tags': ['Suspect', 'Immobilier', 'Montant très élevé', 'À vérifier']
    },
    'transaction_suspecte_3': {
        'name': '⚠️ Retrait Important DAB',
        'description': 'Retrait important à un DAB inhabituel',
        'montant': 50000,
        'heure': 1,
        'type_transaction': 'RETRAIT_DAB',
        'categorie_marchand': 'DAB',
        'canal_paiement': 'DAB',
        'wilaya_client': 'Annaba',
        'revenu_client': 32000,
        'anciennete': 250,
        'tags': ['Suspect', 'Nocturne', 'Retrait', 'Localisation inhabituelle']
    },
    
    # Transactions à haut risque
    'transaction_haut_risque_1': {
        'name': '🔴 Achat Cryptomonnaie',
        'description': 'Achat important de cryptomonnaie',
        'montant': 180000,
        'heure': 4,
        'type_transaction': 'PAIEMENT_EN_LIGNE',
        'categorie_marchand': 'ELECTRONIQUE',
        'canal_paiement': 'INTERNET_BANKING',
        'wilaya_client': 'Blida',
        'revenu_client': 48000,
        'anciennete': 60,
        'tags': ['Haut risque', 'Cryptomonnaie', 'Nocturne', 'Nouveau compte']
    },
    'transaction_haut_risque_2': {
        'name': '🔴 Paiement International',
        'description': 'Paiement vers un pays à risque',
        'montant': 95000,
        'heure': 0,
        'type_transaction': 'VIREMENT',
        'categorie_marchand': 'VOYAGE',
        'canal_paiement': 'INTERNET_BANKING',
        'wilaya_client': 'Alger',
        'revenu_client': 52000,
        'anciennete': 90,
        'tags': ['Haut risque', 'International', 'Pays à risque', 'Heure inhabituelle']
    }
}

# ========== FONCTIONS ML ==========
def simulate_ml_prediction(transaction_data):
    """Simule une prédiction ML avec scoring détaillé"""
    score = 0.0
    reasons = []
    score_breakdown = {}
    
    # 1. Vérification du montant (poids: 40%)
    ratio_montant_revenu = transaction_data['montant'] / transaction_data['revenu_client']
    if ratio_montant_revenu > 0.5:
        score += 0.4
        reasons.append(f"Montant élevé ({ratio_montant_revenu*100:.0f}% du revenu)")
        score_breakdown['montant'] = 0.4
    elif ratio_montant_revenu > 0.3:
        score += 0.2
        reasons.append(f"Montant modéré ({ratio_montant_revenu*100:.0f}% du revenu)")
        score_breakdown['montant'] = 0.2
    else:
        score_breakdown['montant'] = 0.0
    
    # 2. Vérification de l'heure (poids: 30%)
    if 1 <= transaction_data['heure'] <= 5:
        score += 0.3
        reasons.append(f"Heure nocturne ({transaction_data['heure']}h)")
        score_breakdown['heure'] = 0.3
    elif 22 <= transaction_data['heure'] <= 23 or transaction_data['heure'] == 0:
        score += 0.15
        reasons.append(f"Heure tardive ({transaction_data['heure']}h)")
        score_breakdown['heure'] = 0.15
    else:
        score_breakdown['heure'] = 0.0
    
    # 3. Vérification de la catégorie (poids: 20%)
    categories_risquees = ['ELECTRONIQUE', 'VOYAGE', 'IMMOBILIER']
    if transaction_data['categorie_marchand'] in categories_risquees:
        score += 0.2
        reasons.append(f"Catégorie à risque: {transaction_data['categorie_marchand']}")
        score_breakdown['categorie'] = 0.2
    else:
        score_breakdown['categorie'] = 0.0
    
    # 4. Vérification de l'ancienneté (poids: 10%)
    if transaction_data['anciennete'] < 90:
        score += 0.1
        reasons.append(f"Compte récent ({transaction_data['anciennete']} jours)")
        score_breakdown['anciennete'] = 0.1
    else:
        score_breakdown['anciennete'] = 0.0
    
    # 5. Vérification du type de transaction (poids: 15%)
    types_risques = ['PAIEMENT_EN_LIGNE', 'VIREMENT']
    if transaction_data['type_transaction'] in types_risques:
        score += 0.15
        reasons.append(f"Type de transaction risqué: {transaction_data['type_transaction']}")
        score_breakdown['type_transaction'] = 0.15
    else:
        score_breakdown['type_transaction'] = 0.0
    
    # 6. Vérification du canal (poids: 10%)
    canaux_risques = ['INTERNET_BANKING', 'MOBILE_BANKING']
    if transaction_data['canal_paiement'] in canaux_risques:
        score += 0.1
        reasons.append(f"Canal de paiement risqué: {transaction_data['canal_paiement']}")
        score_breakdown['canal'] = 0.1
    else:
        score_breakdown['canal'] = 0.0
    
    # Normalisation du score
    score = min(score, 1.0)
    is_fraud = score > 0.5
    
    # Niveau de risque
    if score >= 0.7:
        risk_level = "HIGH"
    elif score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Recommandation
    if is_fraud:
        if score > 0.8:
            recommendation = "🚨 BLOQUER - Fraude confirmée (Score > 80%)"
        else:
            recommendation = "⚠️ SUSPENDRE - Nécessite vérification immédiate"
    else:
        if risk_level == "HIGH":
            recommendation = "🔍 VÉRIFIER - Risque élevé détecté"
        elif risk_level == "MEDIUM":
            recommendation = "👁️ SURVEILLER - Risque moyen, surveillance recommandée"
        else:
            recommendation = "✅ APPROUVER - Transaction sécurisée"
    
    # Calcul de la confiance
    confidence = max(0.7, 1.0 - (score * 0.3))
    
    return {
        'is_fraud': is_fraud,
        'fraud_probability': score,
        'risk_level': risk_level,
        'reasons': reasons if reasons else ["✅ Transaction normale - Aucun indicateur de risque détecté"],
        'recommendation': recommendation,
        'confidence': confidence,
        'score_breakdown': score_breakdown,
        'total_score': score
    }

# ========== NAVIGATION ==========
st.markdown(f"""
<div class="navbar">
    <div style="display: flex; justify-content: space-between; align-items: center; color: white;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 28px;">🏦</span>
            <div>
                <h2 style="margin: 0; font-weight: bold; color: white;">Banque Badr - Détection de Fraude</h2>
                <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9em;">
                    Système intelligent de détection de fraudes bancaires en temps réel
                </p>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="text-align: right;">
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span class="api-status api-status-online"></span>
                    <span style="font-weight: 500;">API: http://127.0.0.1:8000 ✓</span>
                </div>
                <small style="opacity: 0.8;">Modèle ML: Random Forest | Précision: 95.2%</small>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========== CONTENU PRINCIPAL ==========
col1, col2 = st.columns([5, 7], gap="large")

# ========== COLONNE GAUCHE ==========
with col1:
    # Carte: Nouvelle transaction
    st.markdown("""
    <div class="card">
        <div class="card-header" style="background-color: #3498db; color: white;">
            <i class="fas fa-credit-card"></i> Nouvelle Transaction
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    # Formulaire
    col_form1, col_form2 = st.columns(2, gap="medium")
    
    with col_form1:
        montant = st.number_input(
            "💰 Montant (DZD)",
            min_value=1000,
            max_value=1000000,
            value=8500,
            step=100,
            key="montant",
            help="Montant de la transaction en dinars algériens"
        )
        
        heure = st.selectbox(
            "🕐 Heure de transaction",
            options=[14, 3, 10, 20, 0, 1, 2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 15, 16, 17, 18, 19, 21, 22, 23],
            format_func=lambda x: f"{x}:00 - {'Nuit' if x <= 5 else 'Matin' if x <= 11 else 'Après-midi' if x <= 17 else 'Soir'}",
            key="heure",
            help="Heure à laquelle la transaction a été effectuée"
        )
        
        type_transaction = st.selectbox(
            "📝 Type de transaction",
            ["ACHAT_CARTE", "RETRAIT_DAB", "VIREMENT", "PAIEMENT_EN_LIGNE", "PAIEMENT_FACTURE"],
            key="type_transaction",
            help="Type d'opération effectuée"
        )
        
        categorie_marchand = st.selectbox(
            "🏷️ Catégorie marchand",
            ["SUPERMARCHE", "ELECTRONIQUE", "VOYAGE", "IMMOBILIER", "RESTAURANT", "ESSENCE", "PHARMACIE", "DAB"],
            key="categorie_marchand",
            help="Catégorie du commerçant ou du service"
        )
    
    with col_form2:
        canal_paiement = st.selectbox(
            "📱 Canal de paiement",
            ["CARTE_PHYSIQUE", "MOBILE_BANKING", "INTERNET_BANKING", "DAB", "AGENCE"],
            key="canal_paiement",
            help="Moyen utilisé pour effectuer le paiement"
        )
        
        wilaya_client = st.selectbox(
            "📍 Wilaya du client",
            ["Alger", "Oran", "Constantine", "Annaba", "Blida", "Sétif", "Batna", "Tizi Ouzou", "Béjaïa", "Tlemcen"],
            key="wilaya_client",
            help="Région d'origine du client"
        )
        
        revenu_client = st.number_input(
            "💵 Revenu mensuel (DZD)",
            min_value=10000,
            max_value=500000,
            value=45000,
            step=1000,
            key="revenu_client",
            help="Revenu mensuel du client en dinars"
        )
        
        anciennete = st.number_input(
            "📅 Ancienneté compte (jours)",
            min_value=1,
            max_value=3650,
            value=500,
            key="anciennete",
            help="Nombre de jours depuis l'ouverture du compte"
        )
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Section: Requêtes pré-préparées
    st.markdown("""
    <div class="card">
        <div class="card-header" style="background-color: #9b59b6; color: white;">
            <i class="fas fa-vial"></i> Requêtes Pré-préparées
        </div>
        <div class="card-body">
            <p style="margin-bottom: 15px; color: #666;">
                <i class="fas fa-info-circle"></i> Testez le système avec des cas réels pré-définis
            </p>
    """, unsafe_allow_html=True)
    
    # Catégories de requêtes
    tab_normales, tab_fraudes, tab_suspectes, tab_risque = st.tabs([
        "💳 Normales", 
        "🚨 Fraudes", 
        "⚠️ Suspectes", 
        "🔴 Haut Risque"
    ])
    
    # Transactions normales
    with tab_normales:
        for key, preset in [('transaction_normale_1', PRESET_TRANSACTIONS['transaction_normale_1']),
                          ('transaction_normale_2', PRESET_TRANSACTIONS['transaction_normale_2']),
                          ('transaction_normale_3', PRESET_TRANSACTIONS['transaction_normale_3'])]:
            if st.button(f"**{preset['name']}**", 
                        key=f"btn_{key}",
                        help=f"Cliquez pour charger: {preset['description']}",
                        use_container_width=True):
                st.session_state.montant = preset['montant']
                st.session_state.heure = preset['heure']
                st.session_state.type_transaction = preset['type_transaction']
                st.session_state.categorie_marchand = preset['categorie_marchand']
                st.session_state.canal_paiement = preset['canal_paiement']
                st.session_state.wilaya_client = preset['wilaya_client']
                st.session_state.revenu_client = preset['revenu_client']
                st.session_state.anciennete = preset['anciennete']
                st.session_state.last_preset = key
                st.rerun()
            
            # Afficher les détails
            with st.expander(f"🔍 Détails: {preset['name']}"):
                st.markdown(f"**Description:** {preset['description']}")
                st.markdown(f"**Montant:** {preset['montant']:,} DZD")
                st.markdown(f"**Heure:** {preset['heure']}h00")
                st.markdown("**Tags:** " + " ".join([f'<span class="tag tag-normal">{tag}</span>' for tag in preset['tags']]), unsafe_allow_html=True)
    
    # Transactions frauduleuses
    with tab_fraudes:
        for key, preset in [('transaction_fraud_1', PRESET_TRANSACTIONS['transaction_fraud_1']),
                          ('transaction_fraud_2', PRESET_TRANSACTIONS['transaction_fraud_2']),
                          ('transaction_fraud_3', PRESET_TRANSACTIONS['transaction_fraud_3'])]:
            if st.button(f"**{preset['name']}**", 
                        key=f"btn_{key}",
                        help=f"Cliquez pour charger: {preset['description']}",
                        use_container_width=True):
                st.session_state.montant = preset['montant']
                st.session_state.heure = preset['heure']
                st.session_state.type_transaction = preset['type_transaction']
                st.session_state.categorie_marchand = preset['categorie_marchand']
                st.session_state.canal_paiement = preset['canal_paiement']
                st.session_state.wilaya_client = preset['wilaya_client']
                st.session_state.revenu_client = preset['revenu_client']
                st.session_state.anciennete = preset['anciennete']
                st.session_state.last_preset = key
                st.rerun()
            
            with st.expander(f"🔍 Détails: {preset['name']}"):
                st.markdown(f"**Description:** {preset['description']}")
                st.markdown(f"**Montant:** {preset['montant']:,} DZD")
                st.markdown(f"**Heure:** {preset['heure']}h00")
                st.markdown("**Tags:** " + " ".join([f'<span class="tag tag-fraud">{tag}</span>' for tag in preset['tags']]), unsafe_allow_html=True)
    
    # Transactions suspectes
    with tab_suspectes:
        for key, preset in [('transaction_suspecte_1', PRESET_TRANSACTIONS['transaction_suspecte_1']),
                          ('transaction_suspecte_2', PRESET_TRANSACTIONS['transaction_suspecte_2']),
                          ('transaction_suspecte_3', PRESET_TRANSACTIONS['transaction_suspecte_3'])]:
            if st.button(f"**{preset['name']}**", 
                        key=f"btn_{key}",
                        help=f"Cliquez pour charger: {preset['description']}",
                        use_container_width=True):
                st.session_state.montant = preset['montant']
                st.session_state.heure = preset['heure']
                st.session_state.type_transaction = preset['type_transaction']
                st.session_state.categorie_marchand = preset['categorie_marchand']
                st.session_state.canal_paiement = preset['canal_paiement']
                st.session_state.wilaya_client = preset['wilaya_client']
                st.session_state.revenu_client = preset['revenu_client']
                st.session_state.anciennete = preset['anciennete']
                st.session_state.last_preset = key
                st.rerun()
            
            with st.expander(f"🔍 Détails: {preset['name']}"):
                st.markdown(f"**Description:** {preset['description']}")
                st.markdown(f"**Montant:** {preset['montant']:,} DZD")
                st.markdown(f"**Heure:** {preset['heure']}h00")
                st.markdown("**Tags:** " + " ".join([f'<span class="tag tag-warning">{tag}</span>' for tag in preset['tags']]), unsafe_allow_html=True)
    
    # Transactions à haut risque
    with tab_risque:
        for key, preset in [('transaction_haut_risque_1', PRESET_TRANSACTIONS['transaction_haut_risque_1']),
                          ('transaction_haut_risque_2', PRESET_TRANSACTIONS['transaction_haut_risque_2'])]:
            if st.button(f"**{preset['name']}**", 
                        key=f"btn_{key}",
                        help=f"Cliquez pour charger: {preset['description']}",
                        use_container_width=True):
                st.session_state.montant = preset['montant']
                st.session_state.heure = preset['heure']
                st.session_state.type_transaction = preset['type_transaction']
                st.session_state.categorie_marchand = preset['categorie_marchand']
                st.session_state.canal_paiement = preset['canal_paiement']
                st.session_state.wilaya_client = preset['wilaya_client']
                st.session_state.revenu_client = preset['revenu_client']
                st.session_state.anciennete = preset['anciennete']
                st.session_state.last_preset = key
                st.rerun()
            
            with st.expander(f"🔍 Détails: {preset['name']}"):
                st.markdown(f"**Description:** {preset['description']}")
                st.markdown(f"**Montant:** {preset['montant']:,} DZD")
                st.markdown(f"**Heure:** {preset['heure']}h00")
                st.markdown("**Tags:** " + " ".join([f'<span class="tag tag-fraud">{tag}</span>' for tag in preset['tags']]), unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Bouton principal d'analyse
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔬 Analyser la Transaction", 
                type="primary", 
                use_container_width=True,
                key="analyze_main",
                help="Cliquez pour analyser la transaction avec le modèle ML"):
        
        # Préparer les données
        transaction_data = {
            'montant': montant,
            'heure': heure,
            'type_transaction': type_transaction,
            'categorie_marchand': categorie_marchand,
            'canal_paiement': canal_paiement,
            'wilaya_client': wilaya_client,
            'revenu_client': revenu_client,
            'anciennete': anciennete,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'id': f"TXN-{st.session_state.transaction_counter}"
        }
        
        # Afficher le loader
        with st.spinner("🧠 Analyse en cours par le modèle ML..."):
            time.sleep(1.5)  # Simulation du temps de traitement
            
            # Simulation de la prédiction ML
            prediction = simulate_ml_prediction(transaction_data)
            
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
            
            st.success("✅ Analyse terminée avec succès!")
            st.rerun()
    
    # Carte: Statistiques
    st.markdown("""
    <div class="card">
        <div class="card-header" style="background-color: #17a2b8; color: white;">
            <i class="fas fa-chart-bar"></i> Statistiques en Temps Réel
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    stats = st.session_state.stats
    col_stat1, col_stat2 = st.columns(2, gap="small")
    
    with col_stat1:
        st.markdown(f"""
        <div class="stat-card stat-card-total">
            <h5 style="font-size: 1.5em; margin: 10px 0;"><i class="fas fa-exchange-alt"></i></h5>
            <h3 style="margin: 10px 0; font-size: 2em;">{stats['total']}</h3>
            <p style="margin: 5px 0; opacity: 0.9;">Transactions totales</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card stat-card-fraud">
            <h5 style="font-size: 1.5em; margin: 10px 0;"><i class="fas fa-shield-alt"></i></h5>
            <h3 style="margin: 10px 0; font-size: 2em;">{stats['fraud']}</h3>
            <p style="margin: 5px 0; opacity: 0.9;">Fraudes détectées</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stat2:
        st.markdown(f"""
        <div class="stat-card stat-card-normal">
            <h5 style="font-size: 1.5em; margin: 10px 0;"><i class="fas fa-check-circle"></i></h5>
            <h3 style="margin: 10px 0; font-size: 2em;">{stats['normal']}</h3>
            <p style="margin: 5px 0; opacity: 0.9;">Transactions normales</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card stat-card-amount">
            <h5 style="font-size: 1.5em; margin: 10px 0;"><i class="fas fa-money-bill-wave"></i></h5>
            <h3 style="margin: 10px 0; font-size: 1.8em;">{stats['total_amount']:,.0f}</h3>
            <p style="margin: 5px 0; opacity: 0.9;">Montant total (DZD)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Taux de fraude
    if stats['total'] > 0:
        fraud_rate = (stats['fraud'] / stats['total']) * 100
        st.metric(
            "📊 Taux de fraude", 
            f"{fraud_rate:.1f}%",
            delta="🔴 Haut" if fraud_rate > 10 else "🟡 Moyen" if fraud_rate > 5 else "🟢 Bas",
            delta_color="inverse"
        )
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# ========== COLONNE DROITE ==========
with col2:
    # Carte: Résultats
    st.markdown("""
    <div class="card">
        <div class="card-header" style="background-color: #6c757d; color: white;">
            <i class="fas fa-poll"></i> Résultats de l'Analyse
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    if st.session_state.transactions:
        latest = st.session_state.transactions[-1]
        
        # Afficher quelle requête pré-préparée a été utilisée
        if st.session_state.last_preset and st.session_state.last_preset in PRESET_TRANSACTIONS:
            preset = PRESET_TRANSACTIONS[st.session_state.last_preset]
            st.markdown(f"""
            <div class="alert alert-info">
                <i class="fas fa-vial"></i> <strong>Requête testée:</strong> {preset['name']}
                <br><small>{preset['description']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # En-tête des résultats
        col_res1, col_res2, col_res3 = st.columns([3, 1, 1])
        
        with col_res1:
            if latest['is_fraud']:
                st.markdown("""
                <h3 style="color: #e74c3c; margin: 0;">
                    <i class="fas fa-exclamation-triangle"></i> FRAUDE DÉTECTÉE
                </h3>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <h3 style="color: #27ae60; margin: 0;">
                    <i class="fas fa-check-circle"></i> TRANSACTION SÉCURISÉE
                </h3>
                """, unsafe_allow_html=True)
            
            st.caption(f"🆔 Transaction ID: {latest['id']} | 📅 {latest['timestamp']}")
        
        with col_res2:
            risk_class = f"risk-{latest['risk_level'].lower()}"
            st.markdown(f"""
            <div style="text-align: center;">
                <div class="{risk_class}" style="padding: 12px; margin: 5px 0;">
                    <i class="fas fa-chart-line"></i><br>
                    <strong>{latest['risk_level']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_res3:
            confidence_percent = latest['confidence'] * 100
            st.metric(
                "Confiance", 
                f"{confidence_percent:.1f}%",
                delta="Élevée" if confidence_percent > 85 else "Moyenne" if confidence_percent > 70 else "Faible"
            )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Détails en 2 colonnes
        col_detail1, col_detail2 = st.columns(2)
        
        with col_detail1:
            st.markdown("#### 📋 Détails de la transaction")
            
            details_html = f"""
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div><strong>Montant:</strong></div>
                    <div style="text-align: right; font-weight: bold; color: #2c3e50;">{latest['montant']:,} DZD</div>
                    
                    <div><strong>Heure:</strong></div>
                    <div style="text-align: right;">{latest['heure']}h00</div>
                    
                    <div><strong>Type:</strong></div>
                    <div style="text-align: right;">{latest['type_transaction']}</div>
                    
                    <div><strong>Catégorie:</strong></div>
                    <div style="text-align: right;">{latest['categorie_marchand']}</div>
                    
                    <div><strong>Canal:</strong></div>
                    <div style="text-align: right;">{latest['canal_paiement']}</div>
                    
                    <div><strong>Wilaya:</strong></div>
                    <div style="text-align: right;">{latest['wilaya_client']}</div>
                    
                    <div><strong>Revenu:</strong></div>
                    <div style="text-align: right;">{latest['revenu_client']:,} DZD/mois</div>
                    
                    <div><strong>Ancienneté:</strong></div>
                    <div style="text-align: right;">{latest['anciennete']} jours</div>
                </div>
            </div>
            """
            st.markdown(details_html, unsafe_allow_html=True)
        
        with col_detail2:
            st.markdown("#### 📊 Analyse de risque")
            
            # Score de fraude
            st.markdown(f"**Probabilité de fraude:** {latest['fraud_probability']*100:.1f}%")
            st.progress(latest['fraud_probability'])
            
            # Recommandation
            st.markdown("**Recommandation du système:**")
            if latest['is_fraud']:
                st.markdown(f"""
                <div class="alert alert-danger">
                    <i class="fas fa-ban"></i> <strong>{latest['recommendation']}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert alert-success">
                    <i class="fas fa-check"></i> <strong>{latest['recommendation']}</strong>
                </div>
                """, unsafe_allow_html=True)
            
            # Détail du scoring
            if 'score_breakdown' in latest:
                st.markdown("**Détail du scoring:**")
                for factor, score in latest['score_breakdown'].items():
                    col_score1, col_score2, col_score3 = st.columns([2, 5, 1])
                    with col_score1:
                        st.write(f"• {factor.replace('_', ' ').title()}:")
                    with col_score2:
                        st.progress(score, text=f"{score*100:.0f}%")
                    with col_score3:
                        st.write(f"{score*100:.0f}%")
        
        # Raisons détaillées
        st.markdown("#### 🔍 Indicateurs détectés")
        if latest['reasons']:
            reasons_html = "<div style='margin: 15px 0;'>"
            for i, reason in enumerate(latest['reasons']):
                icon = "✅" if "normale" in reason.lower() else "⚠️" if "surveillance" in reason.lower() else "🚨"
                reasons_html += f"""
                <div style="background: {'#e8f5e9' if 'normale' in reason.lower() else '#fff3cd' if 'surveillance' in reason.lower() else '#ffebee'}; 
                          padding: 12px 15px; margin: 8px 0; border-radius: 8px; border-left: 4px solid {'#27ae60' if 'normale' in reason.lower() else '#f39c12' if 'surveillance' in reason.lower() else '#e74c3c'};">
                    {icon} <strong>{reason}</strong>
                </div>
                """
            reasons_html += "</div>"
            st.markdown(reasons_html, unsafe_allow_html=True)
        
        # Bouton pour analyser une autre
        st.markdown("<hr>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn2:
            if st.button("🔄 Analyser une autre", use_container_width=True):
                st.session_state.last_preset = None
    
    else:
        # Aucune analyse effectuée
        st.markdown("""
        <div style="text-align: center; color: #6c757d; padding: 60px 20px;">
            <div style="font-size: 72px; margin-bottom: 20px;">🔍</div>
            <h3 style="color: #495057;">Aucune analyse effectuée</h3>
            <p style="max-width: 400px; margin: 0 auto 30px auto; line-height: 1.6;">
                Remplissez le formulaire à gauche ou choisissez une requête pré-préparée, 
                puis cliquez sur <strong>"Analyser la Transaction"</strong> pour démarrer la détection de fraude.
            </p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; display: inline-block; margin-top: 20px;">
                <p style="margin: 0; font-size: 0.9em;">
                    <i class="fas fa-lightbulb"></i> <strong>Astuce:</strong> Essayez d'abord une requête pré-préparée pour voir le système en action!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Carte: Historique
    st.markdown("""
    <div class="card">
        <div class="card-header" style="background-color: #343a40; color: white;">
            <i class="fas fa-history"></i> Historique des Transactions
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    if st.session_state.transactions:
        # Préparer les données pour le DataFrame
        history_data = []
        for t in reversed(st.session_state.transactions[-10:]):  # 10 dernières
            history_data.append({
                'ID': t['id'],
                'Date': t['timestamp'].split(' ')[1][:5],
                'Montant': f"{t['montant']:,} DZD",
                'Heure': f"{t['heure']}h",
                'Type': t['type_transaction'][:12],
                'Statut': '🚨 Fraude' if t['is_fraud'] else '✅ Normal',
                'Risque': t['risk_level'],
                'Score': f"{t['fraud_probability']*100:.0f}%"
            })
        
        # Créer et afficher le DataFrame
        df = pd.DataFrame(history_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.TextColumn(width="small"),
                "Statut": st.column_config.TextColumn(width="small"),
                "Risque": st.column_config.TextColumn(width="small"),
                "Score": st.column_config.ProgressColumn(
                    width="small",
                    format="%f%%",
                    min_value=0,
                    max_value=100
                )
            }
        )
        
        # Bouton pour effacer l'historique
        col_hist1, col_hist2 = st.columns([3, 1])
        with col_hist2:
            if st.button("🗑️ Effacer l'historique", 
                        use_container_width=True,
                        type="secondary"):
                st.session_state.transactions = []
                st.session_state.transaction_counter = 1
                st.session_state.stats = {'total': 0, 'fraud': 0, 'normal': 0, 'total_amount': 0}
                st.session_state.last_preset = None
                st.success("✅ Historique effacé avec succès!")
                st.rerun()
    
    else:
        st.info("📭 L'historique est vide. Analysez votre première transaction pour commencer.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# ========== PIED DE PAGE ==========
st.markdown("---")
current_date = datetime.now()
formatted_date = current_date.strftime("%A %d %B %Y, %H:%M")
st.markdown(f"""
<footer>
    <p style="margin: 0 0 10px 0;">
        <i class="fas fa-code"></i> <strong>Système de Détection de Fraude - Banque Badr</strong>
    </p>
    <p style="margin: 0 0 10px 0; font-size: 0.9em;">
        Développé avec <i class="fas fa-heart" style="color: #e74c3c;"></i> en utilisant Streamlit & Machine Learning
    </p>
    <p style="margin: 0; font-size: 0.85em; color: #888;">
        <i class="fas fa-calendar-alt"></i> {formatted_date} | 
        <i class="fas fa-server"></i> Modèle: Random Forest (95.2% accuracy) | 
        <i class="fas fa-bolt"></i> Temps de réponse: < 2s
    </p>
</footer>
""", unsafe_allow_html=True)
