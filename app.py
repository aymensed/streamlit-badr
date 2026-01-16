# app.py - Interface Streamlit qui ressemble à votre HTML Bootstrap
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

# CSS pour reproduire exactement le design Bootstrap
st.markdown("""
<style>
    /* Variables de couleur racine */
    :root {
        --primary-color: #2c3e50;
        --secondary-color: #3498db;
        --success-color: #27ae60;
        --danger-color: #e74c3c;
        --warning-color: #f39c12;
    }
    
    /* Style général */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        min-height: 100vh;
    }
    
    /* Navigation */
    .stApp header {
        background-color: var(--primary-color) !important;
    }
    
    /* Cartes */
    .card {
        border-radius: 15px !important;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
        border: none !important;
        margin-bottom: 20px !important;
        background-color: white !important;
    }
    
    .card-header {
        border-radius: 15px 15px 0 0 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        padding: 15px 20px !important;
    }
    
    .card-body {
        padding: 20px !important;
    }
    
    /* Classes de risque */
    .risk-high {
        color: #e74c3c !important;
        font-weight: bold !important;
        background-color: rgba(231, 76, 60, 0.1) !important;
        padding: 5px 10px !important;
        border-radius: 5px !important;
        display: inline-block !important;
    }
    
    .risk-medium {
        color: #f39c12 !important;
        font-weight: bold !important;
        background-color: rgba(243, 156, 18, 0.1) !important;
        padding: 5px 10px !important;
        border-radius: 5px !important;
        display: inline-block !important;
    }
    
    .risk-low {
        color: #27ae60 !important;
        font-weight: bold !important;
        background-color: rgba(39, 174, 96, 0.1) !important;
        padding: 5px 10px !important;
        border-radius: 5px !important;
        display: inline-block !important;
    }
    
    /* Badges */
    .fraud-badge {
        background-color: #e74c3c !important;
        color: white !important;
        padding: 3px 8px !important;
        border-radius: 12px !important;
        font-size: 0.8em !important;
        display: inline-block !important;
    }
    
    .normal-badge {
        background-color: #27ae60 !important;
        color: white !important;
        padding: 3px 8px !important;
        border-radius: 12px !important;
        font-size: 0.8em !important;
        display: inline-block !important;
    }
    
    /* Barre de progression */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--secondary-color), var(--success-color)) !important;
        height: 25px !important;
        border-radius: 12px !important;
    }
    
    /* Cartes de statistiques */
    .stat-card {
        text-align: center !important;
        padding: 20px !important;
        border-radius: 10px !important;
        color: white !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
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
        transition: all 0.3s !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }
    
    /* Tableau */
    .transaction-table {
        max-height: 400px !important;
        overflow-y: auto !important;
    }
    
    table {
        width: 100% !important;
        border-collapse: collapse !important;
    }
    
    th {
        background-color: var(--primary-color) !important;
        color: white !important;
        padding: 12px !important;
        text-align: left !important;
    }
    
    td {
        padding: 12px !important;
        border-bottom: 1px solid #ddd !important;
    }
    
    tr:hover {
        background-color: #f5f5f5 !important;
    }
    
    /* Inputs */
    .stSelectbox, .stNumberInput, .stTextInput {
        margin-bottom: 10px !important;
    }
    
    /* Alertes */
    .alert {
        padding: 15px !important;
        border-radius: 10px !important;
        margin: 10px 0 !important;
        border-left: 5px solid !important;
    }
    
    .alert-danger {
        background-color: #f8d7da !important;
        border-left-color: #dc3545 !important;
        color: #721c24 !important;
    }
    
    .alert-success {
        background-color: #d4edda !important;
        border-left-color: #28a745 !important;
        color: #155724 !important;
    }
    
    .alert-warning {
        background-color: #fff3cd !important;
        border-left-color: #ffc107 !important;
        color: #856404 !important;
    }
    
    /* Boutons d'exemple */
    .example-btn {
        margin: 5px 0 !important;
        border-radius: 20px !important;
    }
    
    /* Indicateur API */
    .api-status {
        display: inline-block !important;
        width: 12px !important;
        height: 12px !important;
        border-radius: 50% !important;
        margin-right: 5px !important;
    }
    
    .api-status-online {
        background-color: #27ae60 !important;
        animation: pulse 2s infinite !important;
    }
    
    .api-status-offline {
        background-color: #e74c3c !important;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Conteneurs */
    .stContainer {
        padding: 0 !important;
    }
    
    /* Espacement */
    .st-emotion-cache-1y4p8pa {
        padding: 2rem 1rem !important;
    }
    
    /* Titres */
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-color) !important;
    }
    
    /* Pied de page */
    footer {
        text-align: center !important;
        color: #666 !important;
        padding: 20px !important;
        margin-top: 40px !important;
        border-top: 1px solid #ddd !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
    st.session_state.transaction_counter = 1
    st.session_state.stats = {
        'total': 0,
        'fraud': 0,
        'normal': 0,
        'total_amount': 0
    }

# Fonction de simulation ML
def simulate_ml_prediction(transaction_data):
    """Simule une prédiction ML"""
    score = 0.0
    reasons = []
    
    # Règles de détection
    if transaction_data['montant'] > transaction_data['revenu'] * 0.5:
        score += 0.4
        reasons.append(f"Montant élevé ({transaction_data['montant']/transaction_data['revenu']*100:.0f}% du revenu)")
    
    if 1 <= transaction_data['heure'] <= 5:
        score += 0.3
        reasons.append(f"Heure nocturne ({transaction_data['heure']}h)")
    
    if transaction_data['categorie'] in ['ELECTRONIQUE', 'VOYAGE', 'IMMOBILIER']:
        score += 0.2
        reasons.append(f"Catégorie à risque: {transaction_data['categorie']}")
    
    if transaction_data['anciennete'] < 90:
        score += 0.1
        reasons.append(f"Compte récent ({transaction_data['anciennete']} jours)")
    
    if transaction_data['type'] in ['PAIEMENT_EN_LIGNE', 'VIREMENT']:
        score += 0.15
    
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
            recommendation = "BLOQUER - Fraude confirmée"
        else:
            recommendation = "SUSPENDRE - Nécessite vérification"
    else:
        if risk_level == "HIGH":
            recommendation = "VÉRIFIER - Risque élevé"
        elif risk_level == "MEDIUM":
            recommendation = "SURVEILLER - Risque moyen"
        else:
            recommendation = "APPROUVER - Risque faible"
    
    return {
        'is_fraud': is_fraud,
        'fraud_probability': score,
        'risk_level': risk_level,
        'reasons': reasons if reasons else ["Transaction normale"],
        'recommendation': recommendation,
        'confidence': 0.95
    }

# ========== BARRE DE NAVIGATION ==========
st.markdown("""
<nav style="background-color: #2c3e50; padding: 1rem; border-radius: 0 0 10px 10px; margin-bottom: 2rem;">
    <div style="display: flex; justify-content: space-between; align-items: center; color: white;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 24px;">🏦</span>
            <h2 style="margin: 0; font-weight: bold; color: white;">Banque Badr - Détection de Fraude</h2>
        </div>
        <div style="display: flex; align-items: center; gap: 15px;">
            <div>
                <span class="api-status api-status-online"></span>
                <span>API: http://127.0.0.1:8000 ✓</span>
            </div>
            <button style="background: transparent; border: 1px solid white; color: white; padding: 5px 15px; border-radius: 5px; cursor: pointer;">
                <i class="fas fa-sync-alt"></i> Tester
            </button>
        </div>
    </div>
</nav>
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
    
    # Formulaire en 2 colonnes
    col_form1, col_form2 = st.columns(2, gap="medium")
    
    with col_form1:
        montant = st.number_input(
            "Montant (DZD)",
            min_value=1000,
            max_value=1000000,
            value=8500,
            step=100,
            key="montant"
        )
        
        heure = st.selectbox(
            "Heure de transaction",
            options=[14, 3, 10, 20],
            format_func=lambda x: f"{x}:00 - {'Après-midi' if x == 14 else 'Nuit' if x == 3 else 'Matin' if x == 10 else 'Soir'}",
            key="heure"
        )
        
        type_transaction = st.selectbox(
            "Type de transaction",
            ["ACHAT_CARTE", "RETRAIT_DAB", "VIREMENT", "PAIEMENT_EN_LIGNE", "PAIEMENT_FACTURE"],
            key="type_transaction"
        )
        
        categorie_marchand = st.selectbox(
            "Catégorie marchand",
            ["SUPERMARCHE", "ELECTRONIQUE", "VOYAGE", "IMMOBILIER", "RESTAURANT", "ESSENCE", "PHARMACIE"],
            key="categorie_marchand"
        )
    
    with col_form2:
        canal_paiement = st.selectbox(
            "Canal de paiement",
            ["CARTE_PHYSIQUE", "MOBILE_BANKING", "INTERNET_BANKING", "DAB", "AGENCE"],
            key="canal_paiement"
        )
        
        wilaya_client = st.selectbox(
            "Wilaya du client",
            ["Alger", "Oran", "Constantine", "Annaba", "Blida", "Sétif", "Batna"],
            key="wilaya_client"
        )
        
        revenu_client = st.number_input(
            "Revenu mensuel (DZD)",
            min_value=10000,
            max_value=500000,
            value=45000,
            step=1000,
            key="revenu_client"
        )
        
        anciennete = st.number_input(
            "Ancienneté compte (jours)",
            min_value=1,
            max_value=3650,
            value=500,
            key="anciennete"
        )
    
    # Bouton de vérification
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    if st.button("🔍 Vérifier la transaction", type="primary", use_container_width=True):
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
        
        # Simulation d'analyse
        with st.spinner("Analyse en cours..."):
            time.sleep(1)  # Simulation du temps de traitement
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
            
            st.success("✅ Analyse terminée!")
            st.rerun()
    
    # Boutons d'exemple
    st.markdown("""
    <div style="margin-top: 20px;">
        <p><strong>Exemples rapides:</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col_ex1, col_ex2, col_ex3 = st.columns(3, gap="small")
    
    with col_ex1:
        if st.button("🛒 Transaction normale", use_container_width=True, key="ex_normal"):
            st.session_state.montant = 8500
            st.session_state.heure = 14
            st.session_state.type_transaction = "ACHAT_CARTE"
            st.session_state.categorie_marchand = "SUPERMARCHE"
            st.session_state.canal_paiement = "CARTE_PHYSIQUE"
            st.session_state.wilaya_client = "Alger"
            st.session_state.revenu_client = 45000
            st.session_state.anciennete = 500
            st.rerun()
    
    with col_ex2:
        if st.button("🚨 Transaction frauduleuse", use_container_width=True, key="ex_fraud"):
            st.session_state.montant = 125000
            st.session_state.heure = 3
            st.session_state.type_transaction = "PAIEMENT_EN_LIGNE"
            st.session_state.categorie_marchand = "ELECTRONIQUE"
            st.session_state.canal_paiement = "INTERNET_BANKING"
            st.session_state.wilaya_client = "Alger"
            st.session_state.revenu_client = 35000
            st.session_state.anciennete = 30
            st.rerun()
    
    with col_ex3:
        if st.button("⚠️ Transaction suspecte", use_container_width=True, key="ex_suspicious"):
            st.session_state.montant = 45000
            st.session_state.heure = 22
            st.session_state.type_transaction = "VIREMENT"
            st.session_state.categorie_marchand = "VOYAGE"
            st.session_state.canal_paiement = "MOBILE_BANKING"
            st.session_state.wilaya_client = "Oran"
            st.session_state.revenu_client = 38000
            st.session_state.anciennete = 150
            st.rerun()
    
    # Carte: Statistiques
    st.markdown("""
    <div class="card" style="margin-top: 30px;">
        <div class="card-header" style="background-color: #17a2b8; color: white;">
            <i class="fas fa-chart-bar"></i> Statistiques
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    stats = st.session_state.stats
    col_stat1, col_stat2 = st.columns(2, gap="small")
    
    with col_stat1:
        st.markdown(f"""
        <div class="stat-card stat-card-total">
            <h5><i class="fas fa-exchange-alt"></i></h5>
            <h3>{stats['total']}</h3>
            <p>Transactions totales</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card stat-card-fraud">
            <h5><i class="fas fa-shield-alt"></i></h5>
            <h3>{stats['fraud']}</h3>
            <p>Fraudes détectées</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stat2:
        st.markdown(f"""
        <div class="stat-card stat-card-normal">
            <h5><i class="fas fa-check-circle"></i></h5>
            <h3>{stats['normal']}</h3>
            <p>Transactions normales</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card stat-card-amount">
            <h5><i class="fas fa-money-bill-wave"></i></h5>
            <h3>{stats['total_amount']:,.0f}</h3>
            <p>Montant total (DZD)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# ========== COLONNE DROITE ==========
with col2:
    # Carte: Résultats
    st.markdown("""
    <div class="card">
        <div class="card-header" style="background-color: #6c757d; color: white;">
            <i class="fas fa-poll"></i> Résultats de l'analyse
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    if st.session_state.transactions:
        latest = st.session_state.transactions[-1]
        
        # En-tête des résultats
        col_res1, col_res2 = st.columns([3, 1])
        with col_res1:
            if latest['is_fraud']:
                st.markdown("""
                <h4 style="color: #e74c3c;">
                    <i class="fas fa-exclamation-triangle"></i> FRAUDE DÉTECTÉE
                </h4>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <h4 style="color: #27ae60;">
                    <i class="fas fa-check-circle"></i> TRANSACTION SÉCURISÉE
                </h4>
                """, unsafe_allow_html=True)
            st.caption(f"Transaction ID: {latest['id']}")
        
        with col_res2:
            risk_class = f"risk-{latest['risk_level'].lower()}"
            st.markdown(f"""
            <div class="{risk_class}" style="text-align: center; padding: 10px;">
                <i class="fas fa-chart-line"></i><br>
                Risque: {latest['risk_level']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Détails de la transaction
        col_detail1, col_detail2 = st.columns(2)
        
        with col_detail1:
            st.markdown("**Détails de la transaction:**")
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
                <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                    <span>Montant:</span>
                    <span style="font-weight: bold;">{latest['montant']:,} DZD</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                    <span>Heure:</span>
                    <span>{latest['heure']}h00</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                    <span>Type:</span>
                    <span>{latest['type']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                    <span>Catégorie:</span>
                    <span>{latest['categorie']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_detail2:
            st.markdown("**Analyse de risque:**")
            
            # Barre de progression
            st.markdown("**Probabilité de fraude:**")
            progress_html = f"""
            <div style="background: #f0f0f0; border-radius: 12px; height: 25px; margin: 10px 0;">
                <div style="background: {'#e74c3c' if latest['is_fraud'] else '#27ae60'}; 
                          width: {latest['fraud_probability']*100}%; 
                          height: 100%; 
                          border-radius: 12px; 
                          display: flex; 
                          align-items: center; 
                          padding-left: 10px; 
                          color: white; 
                          font-weight: bold;">
                    {(latest['fraud_probability']*100):.1f}%
                </div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
            
            # Recommandation
            st.markdown("**Recommandation:**")
            if latest['is_fraud']:
                st.markdown(f"""
                <div class="alert alert-danger">
                    <i class="fas fa-ban"></i> {latest['recommendation']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert alert-success">
                    <i class="fas fa-check"></i> {latest['recommendation']}
                </div>
                """, unsafe_allow_html=True)
            
            # Raisons
            if latest['reasons']:
                st.markdown("**Raisons:**")
                reasons_html = "<div class='alert alert-warning'><ul style='margin-bottom: 0;'>"
                for raison in latest['reasons']:
                    reasons_html += f"<li>{raison}</li>"
                reasons_html += "</ul></div>"
                st.markdown(reasons_html, unsafe_allow_html=True)
        
        # Bouton pour analyser une autre
        st.markdown("---")
        if st.button("🔄 Analyser une autre transaction", use_container_width=True):
            pass  # Le formulaire reste affiché
    
    else:
        # Aucune analyse effectuée
        st.markdown("""
        <div style="text-align: center; color: #6c757d; padding: 40px;">
            <i class="fas fa-search" style="font-size: 48px; margin-bottom: 20px;"></i>
            <h5>Aucune analyse effectuée</h5>
            <p>Remplissez le formulaire et cliquez sur "Vérifier la transaction"</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Carte: Historique
    st.markdown("""
    <div class="card">
        <div class="card-header" style="background-color: #343a40; color: white;">
            <i class="fas fa-history"></i> Historique des transactions
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    if st.session_state.transactions:
        # Créer le tableau HTML
        table_html = """
        <div class="transaction-history">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Montant</th>
                        <th>Heure</th>
                        <th>Type</th>
                        <th>Statut</th>
                        <th>Risque</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Ajouter les 10 dernières transactions
        for t in reversed(st.session_state.transactions[-10:]):
            # Badge de statut
            badge = '<span class="fraud-badge">Fraude</span>' if t['is_fraud'] else '<span class="normal-badge">Normal</span>'
            
            # Classe de risque
            risk_class = f"risk-{t['risk_level'].lower()}"
            
            table_html += f"""
                <tr>
                    <td><small>{t['id']}</small></td>
                    <td><strong>{t['montant']:,} DZD</strong></td>
                    <td>{t['heure']}h00</td>
                    <td>{t['type']}</td>
                    <td>{badge}</td>
                    <td><span class="{risk_class}">{t['risk_level']}</span></td>
                </tr>
            """
        
        table_html += """
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(table_html, unsafe_allow_html=True)
        
        # Bouton pour effacer l'historique
        col_hist1, col_hist2 = st.columns([3, 1])
        with col_hist2:
            if st.button("🗑️ Effacer l'historique", use_container_width=True):
                st.session_state.transactions = []
                st.session_state.transaction_counter = 1
                st.session_state.stats = {'total': 0, 'fraud': 0, 'normal': 0, 'total_amount': 0}
                st.success("Historique effacé!")
                st.rerun()
    
    else:
        st.info("Aucune transaction dans l'historique.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# ========== PIED DE PAGE ==========
st.markdown("---")
current_date = datetime.now().strftime("%A %d %B %Y, %H:%M")
st.markdown(f"""
<footer>
    <p>
        <i class="fas fa-code"></i> Système de Détection de Fraude - Banque Badr | 
        Développé avec Streamlit & Machine Learning | 
        {current_date}
    </p>
</footer>
""", unsafe_allow_html=True)

# ========== REQUIREMENTS.TXT ==========
# Créer automatiquement le fichier requirements.txt
requirements_content = """pandas>=2.0.0
numpy>=1.24.0
streamlit>=1.28.0
"""

# Sauvegarder le fichier requirements.txt
import os
if not os.path.exists("requirements.txt"):
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
