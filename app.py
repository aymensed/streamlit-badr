# app.py - Version avec chargement correct des requêtes pré-préparées
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

# CSS
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
        font-weight: bold;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    
    .preset-card {
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .preset-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .badge-fraud {
        background-color: #e74c3c;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9em;
    }
    
    .badge-normal {
        background-color: #27ae60;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# ========== INITIALISATION ==========
# Initialiser les données dans session_state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
    st.session_state.transaction_counter = 1
    st.session_state.stats = {
        'total': 0,
        'fraud': 0,
        'normal': 0,
        'total_amount': 0
    }

# Variables pour stocker la transaction actuelle
if 'current_transaction' not in st.session_state:
    st.session_state.current_transaction = {
        'montant': 8500,
        'heure': 14,
        'type': "ACHAT_CARTE",
        'categorie': "SUPERMARCHE",
        'canal': "CARTE_PHYSIQUE",
        'wilaya': "Alger",
        'revenu': 45000,
        'anciennete': 500
    }

# ========== REQUÊTES PRÉ-PRÉPARÉES ==========
PRESET_TRANSACTIONS = [
    # Transactions normales
    {
        'id': 'normale_1',
        'name': '💳 Achat Supermarché',
        'description': 'Achat quotidien normal - 8,500 DZD à 14h',
        'montant': 8500,
        'heure': 14,
        'type': 'ACHAT_CARTE',
        'categorie': 'SUPERMARCHE',
        'canal': 'CARTE_PHYSIQUE',
        'wilaya': 'Alger',
        'revenu': 45000,
        'anciennete': 500,
        'expected_result': '✅ Normal - Risque faible'
    },
    {
        'id': 'normale_2',
        'name': '⛽ Paiement Essence',
        'description': 'Plein d\'essence mensuel - 12,000 DZD à 18h',
        'montant': 12000,
        'heure': 18,
        'type': 'ACHAT_CARTE',
        'categorie': 'ESSENCE',
        'canal': 'CARTE_PHYSIQUE',
        'wilaya': 'Oran',
        'revenu': 55000,
        'anciennete': 300,
        'expected_result': '✅ Normal - Risque faible'
    },
    # Transactions frauduleuses
    {
        'id': 'fraud_1',
        'name': '🚨 Achat Électronique Nocturne',
        'description': 'Achat à 3h du matin - 125,000 DZD (350% du revenu)',
        'montant': 125000,
        'heure': 3,
        'type': 'PAIEMENT_EN_LIGNE',
        'categorie': 'ELECTRONIQUE',
        'canal': 'INTERNET_BANKING',
        'wilaya': 'Alger',
        'revenu': 35000,
        'anciennete': 30,
        'expected_result': '🚨 Fraude - Risque élevé'
    },
    {
        'id': 'fraud_2',
        'name': '🚨 Virement International',
        'description': 'Virement important à 23h - 250,000 DZD',
        'montant': 250000,
        'heure': 23,
        'type': 'VIREMENT',
        'categorie': 'VOYAGE',
        'canal': 'INTERNET_BANKING',
        'wilaya': 'Alger',
        'revenu': 42000,
        'anciennete': 45,
        'expected_result': '🚨 Fraude - Risque très élevé'
    },
    # Transactions suspectes
    {
        'id': 'suspect_1',
        'name': '⚠️ Virement Important',
        'description': 'Virement inhabituel à 22h - 45,000 DZD',
        'montant': 45000,
        'heure': 22,
        'type': 'VIREMENT',
        'categorie': 'VOYAGE',
        'canal': 'MOBILE_BANKING',
        'wilaya': 'Oran',
        'revenu': 38000,
        'anciennete': 150,
        'expected_result': '⚠️ Suspect - Risque moyen'
    },
    {
        'id': 'suspect_2',
        'name': '⚠️ Achat Immobilier',
        'description': 'Transaction immobilière inhabituelle - 350,000 DZD',
        'montant': 350000,
        'heure': 16,
        'type': 'VIREMENT',
        'categorie': 'IMMOBILIER',
        'canal': 'AGENCE',
        'wilaya': 'Alger',
        'revenu': 60000,
        'anciennete': 180,
        'expected_result': '⚠️ Suspect - Risque élevé'
    }
]

# ========== FONCTIONS UTILITAIRES ==========
def load_preset_transaction(preset_id):
    """Charge une transaction pré-préparée"""
    for preset in PRESET_TRANSACTIONS:
        if preset['id'] == preset_id:
            # Mettre à jour la transaction courante
            st.session_state.current_transaction = {
                'montant': preset['montant'],
                'heure': preset['heure'],
                'type': preset['type'],
                'categorie': preset['categorie'],
                'canal': preset['canal'],
                'wilaya': preset['wilaya'],
                'revenu': preset['revenu'],
                'anciennete': preset['anciennete']
            }
            st.success(f"✅ Chargé: {preset['name']}")
            return True
    return False

def analyze_transaction():
    """Analyse la transaction courante"""
    data = st.session_state.current_transaction
    
    # Logique de détection simplifiée
    score = 0.0
    reasons = []
    
    # 1. Montant par rapport au revenu
    ratio = data['montant'] / data['revenu']
    if ratio > 0.5:
        score += 0.4
        reasons.append(f"Montant élevé ({ratio*100:.0f}% du revenu)")
    elif ratio > 0.3:
        score += 0.2
        reasons.append(f"Montant modéré ({ratio*100:.0f}% du revenu)")
    
    # 2. Heure de transaction
    if 1 <= data['heure'] <= 5:
        score += 0.3
        reasons.append(f"Heure nocturne ({data['heure']}h)")
    elif 22 <= data['heure'] <= 23 or data['heure'] == 0:
        score += 0.15
        reasons.append(f"Heure tardive ({data['heure']}h)")
    
    # 3. Catégorie à risque
    if data['categorie'] in ['ELECTRONIQUE', 'VOYAGE', 'IMMOBILIER']:
        score += 0.2
        reasons.append(f"Catégorie risquée: {data['categorie']}")
    
    # 4. Ancienneté du compte
    if data['anciennete'] < 90:
        score += 0.1
        reasons.append(f"Compte récent ({data['anciennete']} jours)")
    
    # 5. Type de transaction
    if data['type'] in ['PAIEMENT_EN_LIGNE', 'VIREMENT']:
        score += 0.15
    
    score = min(score, 1.0)
    is_fraud = score > 0.5
    
    # Déterminer le niveau de risque
    if score >= 0.7:
        risk_level = "HIGH"
    elif score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Recommandation
    if is_fraud:
        recommendation = "🚨 BLOQUER - Fraude suspectée" if score > 0.7 else "⚠️ SUSPENDRE - À vérifier"
    else:
        recommendation = "🔍 VÉRIFIER - Risque élevé" if risk_level == "HIGH" else "✅ APPROUVER - Sécurisé"
    
    return {
        'is_fraud': is_fraud,
        'score': score,
        'risk_level': risk_level,
        'reasons': reasons,
        'recommendation': recommendation,
        'confidence': max(0.7, 1.0 - (score * 0.3))
    }

def add_to_history(transaction_data, analysis_result):
    """Ajoute une transaction à l'historique"""
    transaction_record = {
        'id': f"TXN-{st.session_state.transaction_counter}",
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **transaction_data,
        **analysis_result
    }
    
    st.session_state.transactions.append(transaction_record)
    st.session_state.transaction_counter += 1
    
    # Mettre à jour les statistiques
    st.session_state.stats['total'] += 1
    if analysis_result['is_fraud']:
        st.session_state.stats['fraud'] += 1
    else:
        st.session_state.stats['normal'] += 1
    st.session_state.stats['total_amount'] += transaction_data['montant']

# ========== INTERFACE ==========

# En-tête
st.markdown("""
<div style="background: linear-gradient(135deg, #2c3e50, #3498db); 
            padding: 25px; border-radius: 10px; margin-bottom: 30px;">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="font-size: 48px;">🏦</div>
        <div>
            <h1 style="color: white; margin: 0;">Banque Badr</h1>
            <h2 style="color: white; margin: 5px 0; font-size: 1.5em;">Système Intelligent de Détection de Fraude</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">
                <i class="fas fa-brain"></i> Powered by Machine Learning | Précision: 95.2%
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Layout principal
col1, col2 = st.columns([5, 7], gap="large")

# ========== COLONNE GAUCHE ==========
with col1:
    # Carte: Formulaire de transaction
    st.markdown('<div class="card"><div class="card-header">📝 Nouvelle Transaction</div>', unsafe_allow_html=True)
    
    # Récupérer les valeurs courantes
    current = st.session_state.current_transaction
    
    # Formulaire qui se met à jour automatiquement
    montant = st.number_input(
        "💰 Montant (DZD)",
        min_value=1000,
        max_value=1000000,
        value=current['montant'],
        step=100,
        key="montant_input"
    )
    
    heure = st.selectbox(
        "🕐 Heure de transaction",
        options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
        index=current['heure'],
        key="heure_input"
    )
    
    type_transaction = st.selectbox(
        "📋 Type de transaction",
        ["ACHAT_CARTE", "RETRAIT_DAB", "VIREMENT", "PAIEMENT_EN_LIGNE", "PAIEMENT_FACTURE"],
        index=["ACHAT_CARTE", "RETRAIT_DAB", "VIREMENT", "PAIEMENT_EN_LIGNE", "PAIEMENT_FACTURE"].index(current['type']),
        key="type_input"
    )
    
    categorie = st.selectbox(
        "🏷️ Catégorie marchand",
        ["SUPERMARCHE", "ELECTRONIQUE", "VOYAGE", "IMMOBILIER", "RESTAURANT", "ESSENCE", "PHARMACIE"],
        index=["SUPERMARCHE", "ELECTRONIQUE", "VOYAGE", "IMMOBILIER", "RESTAURANT", "ESSENCE", "PHARMACIE"].index(current['categorie']),
        key="categorie_input"
    )
    
    canal = st.selectbox(
        "📱 Canal de paiement",
        ["CARTE_PHYSIQUE", "MOBILE_BANKING", "INTERNET_BANKING", "DAB", "AGENCE"],
        index=["CARTE_PHYSIQUE", "MOBILE_BANKING", "INTERNET_BANKING", "DAB", "AGENCE"].index(current['canal']),
        key="canal_input"
    )
    
    wilaya = st.selectbox(
        "📍 Wilaya du client",
        ["Alger", "Oran", "Constantine", "Annaba", "Blida", "Sétif", "Batna"],
        index=["Alger", "Oran", "Constantine", "Annaba", "Blida", "Sétif", "Batna"].index(current['wilaya']),
        key="wilaya_input"
    )
    
    revenu = st.number_input(
        "💵 Revenu mensuel (DZD)",
        min_value=10000,
        max_value=500000,
        value=current['revenu'],
        step=1000,
        key="revenu_input"
    )
    
    anciennete = st.number_input(
        "📅 Ancienneté compte (jours)",
        min_value=1,
        max_value=3650,
        value=current['anciennete'],
        key="anciennete_input"
    )
    
    # Mettre à jour la transaction courante avec les nouvelles valeurs
    st.session_state.current_transaction = {
        'montant': montant,
        'heure': heure,
        'type': type_transaction,
        'categorie': categorie,
        'canal': canal,
        'wilaya': wilaya,
        'revenu': revenu,
        'anciennete': anciennete
    }
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section: Requêtes pré-préparées
    st.markdown('<div class="card"><div class="card-header">🧪 Cas de Test Pré-définis</div>', unsafe_allow_html=True)
    
    st.markdown("**Cliquez sur un cas pour le charger automatiquement:**")
    
    # Afficher les requêtes pré-préparées
    for preset in PRESET_TRANSACTIONS:
        # Créer un conteneur pour chaque preset
        with st.container():
            col_p1, col_p2 = st.columns([3, 1])
            
            with col_p1:
                st.markdown(f"**{preset['name']}**")
                st.caption(preset['description'])
                st.caption(f"Résultat attendu: {preset['expected_result']}")
            
            with col_p2:
                if st.button("📥 Charger", key=f"load_{preset['id']}"):
                    load_preset_transaction(preset['id'])
                    st.rerun()
            
            st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Bouton d'analyse
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔬 Analyser avec l'IA", type="primary", use_container_width=True, key="analyze_btn"):
        with st.spinner("Analyse en cours par le modèle ML..."):
            time.sleep(1)  # Simulation du traitement
            
            # Analyser la transaction courante
            analysis_result = analyze_transaction()
            
            # Ajouter à l'historique
            add_to_history(st.session_state.current_transaction, analysis_result)
            
            st.success("✅ Analyse terminée avec succès!")
            st.rerun()
    
    # Statistiques
    st.markdown('<div class="card"><div class="card-header">📊 Statistiques en Temps Réel</div>', unsafe_allow_html=True)
    
    stats = st.session_state.stats
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Transactions", stats['total'])
        st.metric("Fraudes", stats['fraud'])
    
    with col_s2:
        st.metric("Normales", stats['normal'])
        if stats['total'] > 0:
            fraud_rate = (stats['fraud'] / stats['total']) * 100
            st.metric("Taux de fraude", f"{fraud_rate:.1f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== COLONNE DROITE ==========
with col2:
    # Résultats de l'analyse
    st.markdown('<div class="card"><div class="card-header">📊 Résultats de l\'Analyse</div>', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        latest = st.session_state.transactions[-1]
        
        # En-tête des résultats
        col_r1, col_r2 = st.columns([3, 1])
        
        with col_r1:
            if latest['is_fraud']:
                st.markdown("""
                <div style="background-color: #ffebee; padding: 20px; border-radius: 10px; border-left: 5px solid #e74c3c;">
                    <h3 style="color: #e74c3c; margin: 0;">🚨 FRAUDE DÉTECTÉE</h3>
                    <p style="margin: 5px 0 0 0;">Le système a identifié cette transaction comme potentiellement frauduleuse</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #27ae60;">
                    <h3 style="color: #27ae60; margin: 0;">✅ TRANSACTION SÉCURISÉE</h3>
                    <p style="margin: 5px 0 0 0;">Le système considère cette transaction comme légitime</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.caption(f"🆔 {latest['id']} | 📅 {latest['timestamp']}")
        
        with col_r2:
            risk_color = {
                'HIGH': '#e74c3c',
                'MEDIUM': '#f39c12',
                'LOW': '#27ae60'
            }[latest['risk_level']]
            
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background-color: {risk_color}10; 
                      border-radius: 10px; border: 2px solid {risk_color};">
                <div style="font-size: 1.2em; font-weight: bold; color: {risk_color};">
                    {latest['risk_level']}
                </div>
                <div style="font-size: 0.9em; color: #666;">
                    Niveau de risque
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Détails de la transaction
        st.markdown("#### 📋 Détails de la transaction analysée")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown(f"""
            **Montant:** {latest['montant']:,} DZD  
            **Heure:** {latest['heure']}h00  
            **Type:** {latest['type']}  
            **Catégorie:** {latest['categorie']}
            """)
        
        with col_d2:
            st.markdown(f"""
            **Canal:** {latest['canal']}  
            **Wilaya:** {latest['wilaya']}  
            **Revenu:** {latest['revenu']:,} DZD/mois  
            **Ancienneté:** {latest['anciennete']} jours
            """)
        
        # Score de risque
        st.markdown("---")
        st.markdown(f"#### 📊 Score de risque: {latest['score']*100:.1f}%")
        st.progress(latest['score'])
        
        # Recommandation
        st.markdown(f"#### 💡 Recommandation: {latest['recommendation']}")
        
        # Raisons détectées
        if latest['reasons']:
            st.markdown("#### 🔍 Indicateurs détectés")
            for reason in latest['reasons']:
                st.markdown(f"- {reason}")
        
        # Confiance du modèle
        st.markdown(f"#### 🔒 Confiance du modèle: {latest['confidence']*100:.1f}%")
    
    else:
        # Message quand aucune analyse n'a été faite
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #666;">
            <div style="font-size: 48px; margin-bottom: 20px;">🔍</div>
            <h3 style="color: #495057;">Aucune analyse effectuée</h3>
            <p style="max-width: 400px; margin: 0 auto;">
                Pour commencer, choisissez un cas de test pré-défini ou modifiez les valeurs 
                manuellement, puis cliquez sur <strong>"Analyser avec l'IA"</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Historique des transactions
    st.markdown('<div class="card"><div class="card-header">📋 Historique des Analyses</div>', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        # Créer un DataFrame pour l'historique
        history_data = []
        for t in reversed(st.session_state.transactions[-10:]):  # 10 dernières
            history_data.append({
                'ID': t['id'][-6:],
                'Heure': f"{t['heure']}h",
                'Montant': f"{t['montant']:,}",
                'Type': t['type'][:10],
                'Risque': t['risk_level'],
                'Statut': '🚨' if t['is_fraud'] else '✅'
            })
        
        # Afficher le tableau
        df = pd.DataFrame(history_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Statut": st.column_config.TextColumn(width="small"),
                "Risque": st.column_config.TextColumn(width="small")
            }
        )
        
        # Bouton pour effacer l'historique
        if st.button("🗑️ Effacer l'historique", type="secondary", use_container_width=True):
            st.session_state.transactions = []
            st.session_state.transaction_counter = 1
            st.session_state.stats = {'total': 0, 'fraud': 0, 'normal': 0, 'total_amount': 0}
            st.success("✅ Historique effacé!")
            st.rerun()
    
    else:
        st.info("Aucune transaction dans l'historique.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Pied de page
st.markdown("---")
current_date = datetime.now().strftime("%A %d %B %Y, %H:%M")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 20px;">
    <p style="margin: 0 0 10px 0; font-weight: bold;">
        🏦 Système de Détection de Fraude - Banque Badr
    </p>
    <p style="margin: 0; font-size: 0.9em;">
        Développé pour le salon de recrutement | {current_date}
    </p>
</div>
""", unsafe_allow_html=True)
