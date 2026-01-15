import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import json

# Configuration de la page
st.set_page_config(
    page_title="Banque Badr - Détection de Fraude",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3498db;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .fraud-alert {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #e74c3c;
    }
    .normal-alert {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #27ae60;
    }
    .stProgress > div > div > div > div {
        background-color: #3498db;
    }
    .stButton > button {
        width: 100%;
        background-color: #3498db;
        color: white;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<h1 class="main-header">🏦 Banque Badr - Système Intelligent de Détection de Fraude</h1>', unsafe_allow_html=True)

# Initialisation de session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'simulation_mode' not in st.session_state:
    st.session_state.simulation_mode = True

# Fonction de simulation (pour Streamlit Cloud sans API)
def simulate_fraud_prediction(transaction_data):
    """Simule une prédiction de fraude basée sur des règles simples"""
    
    montant = transaction_data['montant_dzd']
    heure = transaction_data['heure_jour']
    categorie = transaction_data['categorie_marchand']
    anciennete = transaction_data['anciennete_client_jours']
    revenu = transaction_data['revenu_client']
    
    # Calcul du score de risque
    risk_score = 0.0
    reasons = []
    
    # Règle 1: Montant élevé
    if montant > revenu * 0.5:  # Plus de 50% du revenu mensuel
        risk_score += 0.4
        reasons.append(f"Montant élevé ({montant/revenu*100:.0f}% du revenu)")
    
    # Règle 2: Heure nocturne
    if 1 <= heure <= 5:  # Entre 1h et 5h du matin
        risk_score += 0.3
        reasons.append(f"Transaction nocturne ({heure}h)")
    
    # Règle 3: Catégorie risquée
    risky_categories = ['ELECTRONIQUE', 'VOYAGE', 'IMMOBILIER']
    if categorie in risky_categories:
        risk_score += 0.2
        reasons.append(f"Catégorie à risque: {categorie}")
    
    # Règle 4: Compte récent
    if anciennete < 90:  # Moins de 3 mois
        risk_score += 0.1
        reasons.append(f"Compte récent ({anciennete} jours)")
    
    # Règle 5: Montant très élevé
    if montant > 100000:
        risk_score += 0.3
        reasons.append(f"Montant très élevé: {montant:,.0f} DZD")
    
    # Normaliser le score
    risk_score = min(risk_score, 1.0)
    
    # Déterminer si c'est une fraude
    is_fraud = risk_score > 0.5
    
    # Niveau de risque
    if risk_score >= 0.7:
        risk_level = "HIGH"
    elif risk_score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Recommandation
    if is_fraud:
        if risk_score > 0.8:
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
    
    # Générer un ID de transaction
    transaction_id = f"TXN-{int(time.time() * 1000)}"
    
    return {
        "transaction_id": transaction_id,
        "is_fraud": is_fraud,
        "fraud_probability": risk_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "reasons": reasons if reasons else ["Transaction normale"]
    }

# Sidebar - Informations
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/bank.png", width=100)
    st.markdown("### ℹ️ Mode de fonctionnement")
    
    mode = st.radio(
        "Sélectionnez le mode:",
        ["🚀 Simulation (Recommandé)", "🔗 API Externe"],
        index=0
    )
    
    if "API" in mode:
        API_URL = st.text_input("URL de l'API", "http://127.0.0.1:8000")
        st.session_state.simulation_mode = False
    else:
        st.session_state.simulation_mode = True
        st.success("Mode simulation activé")
    
    st.markdown("---")
    st.markdown("### 📊 Statistiques")
    
    if st.session_state.transactions:
        total = len(st.session_state.transactions)
        fraud_count = sum(1 for t in st.session_state.transactions if t['is_fraud'])
        fraud_rate = (fraud_count / total * 100) if total > 0 else 0
        
        st.metric("Transactions analysées", total)
        st.metric("Fraudes détectées", fraud_count)
        st.metric("Taux de fraude", f"{fraud_rate:.1f}%")
    
    st.markdown("---")
    st.markdown("### 📁 Projet GitHub")
    st.markdown("""
    **Code source disponible:**
    [github.com/tonuser/projet-badr](https://github.com)
    
    **Technologies utilisées:**
    - Python & Streamlit
    - Machine Learning
    - Analyse de données
    - Visualisation
    """)

# Onglets principaux
tab1, tab2, tab3, tab4 = st.tabs(["🧪 Analyse", "📈 Dashboard", "📋 Historique", "📚 Documentation"])

# Onglet 1: Analyse de transaction
with tab1:
    st.markdown('<h2 class="sub-header">🧠 Analyse de Transaction</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Données de transaction")
        
        # Formulaire
        montant = st.number_input("Montant (DZD)", min_value=0.0, value=8500.0, step=100.0, key="montant_input")
        
        col1a, col1b = st.columns(2)
        with col1a:
            heure = st.slider("Heure", 0, 23, 14, key="heure_slider")
        with col1b:
            anciennete = st.number_input("Ancienneté (jours)", min_value=0, value=500, key="anciennete_input")
        
        type_transaction = st.selectbox(
            "Type de transaction",
            ["ACHAT_CARTE", "RETRAIT_DAB", "VIREMENT", "PAIEMENT_EN_LIGNE", "PAIEMENT_FACTURE"],
            key="type_select"
        )
        
        categorie = st.selectbox(
            "Catégorie marchand",
            ["SUPERMARCHE", "ELECTRONIQUE", "VOYAGE", "IMMOBILIER", "RESTAURANT", "ESSENCE", "PHARMACIE"],
            key="categorie_select"
        )
        
        canal = st.selectbox(
            "Canal de paiement",
            ["CARTE_PHYSIQUE", "MOBILE_BANKING", "INTERNET_BANKING", "DAB", "AGENCE"],
            key="canal_select"
        )
        
        wilaya = st.selectbox(
            "Wilaya du client",
            ["Alger", "Oran", "Constantine", "Annaba", "Blida", "Sétif", "Batna", "Mostaganem"],
            key="wilaya_select"
        )
        
        revenu = st.number_input("Revenu mensuel (DZD)", min_value=0.0, value=45000.0, step=1000.0, key="revenu_input")
    
    with col2:
        st.markdown("### ⚡ Actions rapides")
        
        # Exemples pré-définis
        st.markdown("**Exemples de test:**")
        
        col2a, col2b, col2c = st.columns(3)
        
        with col2a:
            if st.button("💳 Transaction normale", use_container_width=True, key="btn_normal"):
                st.session_state.montant_input = 8500.0
                st.session_state.heure_slider = 14
                st.session_state.type_select = "ACHAT_CARTE"
                st.session_state.categorie_select = "SUPERMARCHE"
                st.session_state.canal_select = "CARTE_PHYSIQUE"
                st.session_state.wilaya_select = "Alger"
                st.session_state.revenu_input = 45000.0
                st.session_state.anciennete_input = 500
                st.rerun()
        
        with col2b:
            if st.button("🚨 Transaction frauduleuse", use_container_width=True, key="btn_fraud"):
                st.session_state.montant_input = 125000.0
                st.session_state.heure_slider = 3
                st.session_state.type_select = "PAIEMENT_EN_LIGNE"
                st.session_state.categorie_select = "ELECTRONIQUE"
                st.session_state.canal_select = "INTERNET_BANKING"
                st.session_state.wilaya_select = "Alger"
                st.session_state.revenu_input = 35000.0
                st.session_state.anciennete_input = 30
                st.rerun()
        
        with col2c:
            if st.button("⚠️ Transaction suspecte", use_container_width=True, key="btn_suspicious"):
                st.session_state.montant_input = 45000.0
                st.session_state.heure_slider = 22
                st.session_state.type_select = "VIREMENT"
                st.session_state.categorie_select = "VOYAGE"
                st.session_state.canal_select = "MOBILE_BANKING"
                st.session_state.wilaya_select = "Oran"
                st.session_state.revenu_input = 38000.0
                st.session_state.anciennete_input = 150
                st.rerun()
        
        # Bouton d'analyse
        st.markdown("---")
        if st.button("🔍 Analyser la transaction", type="primary", use_container_width=True, key="btn_analyze"):
            with st.spinner("Analyse en cours..."):
                # Préparer les données
                transaction_data = {
                    "montant_dzd": montant,
                    "heure_jour": heure,
                    "type_transaction": type_transaction,
                    "categorie_marchand": categorie,
                    "canal_paiement": canal,
                    "wilaya_client": wilaya,
                    "revenu_client": revenu,
                    "anciennete_client_jours": anciennete
                }
                
                try:
                    if st.session_state.simulation_mode:
                        # Mode simulation
                        result = simulate_fraud_prediction(transaction_data)
                    else:
                        # Mode API (si configuré)
                        import requests
                        response = requests.post(
                            f"{API_URL}/predict",
                            json=transaction_data,
                            timeout=10
                        )
                        if response.status_code == 200:
                            result = response.json()
                        else:
                            st.error(f"Erreur API: {response.status_code}")
                            result = simulate_fraud_prediction(transaction_data)
                    
                    # Ajouter à l'historique
                    result['timestamp'] = datetime.now().isoformat()
                    result['montant'] = montant
                    result['heure'] = heure
                    st.session_state.transactions.append(result)
                    
                    # Afficher les résultats
                    st.markdown("---")
                    st.markdown("### 📊 Résultats de l'analyse")
                    
                    # Afficher l'alerte
                    if result['is_fraud']:
                        st.markdown(f"""
                        <div class="fraud-alert">
                            <h3>🚨 FRAUDE DÉTECTÉE</h3>
                            <p>Cette transaction présente des caractéristiques suspectes.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="normal-alert">
                            <h3>✅ TRANSACTION NORMALE</h3>
                            <p>Cette transaction semble légitime.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Métriques
                    col_met1, col_met2, col_met3 = st.columns(3)
                    with col_met1:
                        st.metric(
                            "Probabilité de fraude",
                            f"{result['fraud_probability']*100:.1f}%",
                            delta="Haute" if result['fraud_probability'] > 0.5 else "Basse"
                        )
                    
                    with col_met2:
                        st.metric("Niveau de risque", result['risk_level'])
                    
                    with col_met3:
                        st.metric("Recommandation", result['recommendation'])
                    
                    # Barre de progression
                    st.progress(float(result['fraud_probability']))
                    
                    # Raisons détaillées
                    if result.get('reasons'):
                        st.markdown("#### 📝 Raisons de la décision:")
                        for reason in result['reasons']:
                            st.write(f"- {reason}")
                    
                    st.success("✅ Analyse terminée avec succès!")
                    
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
                    st.info("Utilisation du mode simulation...")
                    # Fallback en mode simulation
                    result = simulate_fraud_prediction(transaction_data)
                    result['timestamp'] = datetime.now().isoformat()
                    result['montant'] = montant
                    result['heure'] = heure
                    st.session_state.transactions.append(result)
                    
                    if result['is_fraud']:
                        st.warning(f"🚨 Simulation: Fraude détectée ({result['fraud_probability']*100:.1f}%)")
                    else:
                        st.success(f"✅ Simulation: Transaction normale ({result['fraud_probability']*100:.1f}%)")

# Onglet 2: Dashboard
with tab2:
    st.markdown('<h2 class="sub-header">📈 Tableau de bord analytique</h2>', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        # Convertir en DataFrame
        df = pd.DataFrame(st.session_state.transactions)
        
        # Métriques générales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Transactions analysées", len(df))
        
        with col2:
            fraud_count = df['is_fraud'].sum()
            st.metric("Fraudes détectées", int(fraud_count))
        
        with col3:
            fraud_rate = (fraud_count / len(df) * 100) if len(df) > 0 else 0
            st.metric("Taux de fraude", f"{fraud_rate:.1f}%")
        
        with col4:
            avg_amount = df['montant'].mean() if 'montant' in df.columns else 0
            st.metric("Montant moyen", f"{avg_amount:,.0f} DZD")
        
        # Graphiques
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Pie chart: Fraude vs Non-fraude
            if 'is_fraud' in df.columns:
                fraud_counts = df['is_fraud'].value_counts()
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Normales', 'Fraudes'],
                    values=[fraud_counts.get(False, 0), fraud_counts.get(True, 0)],
                    hole=.3,
                    marker_colors=['#27ae60', '#e74c3c']
                )])
                fig_pie.update_layout(title="Répartition Fraude/Normale")
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_chart2:
            # Bar chart: Par heure
            if 'heure' in df.columns:
                hour_counts = df.groupby('heure').size().reset_index(name='count')
                fig_bar = px.bar(
                    hour_counts,
                    x='heure',
                    y='count',
                    title="Transactions par heure",
                    color='count',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Tableau détaillé
        st.markdown("#### 📋 Dernières transactions")
        if not df.empty:
            display_df = df.copy()
            if 'timestamp' in display_df.columns:
                display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%H:%M:%S')
            
            display_df['Statut'] = display_df['is_fraud'].apply(lambda x: '🚨 FRAUDE' if x else '✅ NORMAL')
            
            # Sélectionner les colonnes à afficher
            columns_to_show = ['timestamp', 'montant', 'heure', 'Statut', 'risk_level', 'fraud_probability']
            available_cols = [c for c in columns_to_show if c in display_df.columns]
            display_df = display_df[available_cols]
            
            if 'montant' in display_df.columns:
                display_df['montant'] = display_df['montant'].apply(lambda x: f"{x:,.0f} DZD")
            
            st.dataframe(display_df.head(10), use_container_width=True)
    
    else:
        st.info("Aucune transaction analysée. Allez dans l'onglet 'Analyse' pour commencer.")

# Onglet 3: Historique
with tab3:
    st.markdown('<h2 class="sub-header">📋 Historique complet</h2>', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        # Options de filtrage
        col_filt1, col_filt2, col_filt3 = st.columns(3)
        
        with col_filt1:
            filter_fraud = st.selectbox("Filtrer par type", ["Toutes", "Fraudes seulement", "Normales seulement"], key="filter_type")
        
        with col_filt2:
            min_amount = st.number_input("Montant minimum (DZD)", min_value=0.0, value=0.0, key="min_amount")
        
        with col_filt3:
            if st.button("🗑️ Effacer l'historique", key="btn_clear"):
                st.session_state.transactions = []
                st.rerun()
        
        # Appliquer les filtres
        filtered_df = pd.DataFrame(st.session_state.transactions)
        
        if filter_fraud == "Fraudes seulement":
            filtered_df = filtered_df[filtered_df['is_fraud'] == True]
        elif filter_fraud == "Normales seulement":
            filtered_df = filtered_df[filtered_df['is_fraud'] == False]
        
        if 'montant' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['montant'] >= min_amount]
        
        # Afficher le tableau
        if not filtered_df.empty:
            # Formater pour l'affichage
            display_df = filtered_df.copy()
            if 'timestamp' in display_df.columns:
                display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            display_df['Statut'] = display_df['is_fraud'].apply(lambda x: '🚨 FRAUDE' if x else '✅ NORMAL')
            
            # Sélectionner les colonnes à afficher
            columns_to_show = ['timestamp', 'montant', 'heure', 'Statut', 'risk_level', 'fraud_probability']
            available_cols = [c for c in columns_to_show if c in display_df.columns]
            display_df = display_df[available_cols]
            
            st.dataframe(display_df, use_container_width=True)
            
            # Bouton d'export
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger l'historique (CSV)",
                data=csv,
                file_name="historique_fraudes.csv",
                mime="text/csv",
                key="btn_download"
            )
        else:
            st.warning("Aucune transaction ne correspond aux filtres.")
    
    else:
        st.info("L'historique est vide. Analysez des transactions pour les voir apparaître ici.")

# Onglet 4: Documentation
with tab4:
    st.markdown('<h2 class="sub-header">📚 Documentation du Projet</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🏦 Système de Détection de Fraude - Banque Badr
    
    Ce projet démontre un système intelligent de détection de transactions frauduleuses 
    utilisant des algorithmes de Machine Learning, spécialement conçu pour le contexte bancaire algérien.
    
    #### 🎯 Objectifs du projet:
    1. **Détection en temps réel** des transactions frauduleuses
    2. **Analyse des patterns** spécifiques au marché algérien
    3. **Interface intuitive** pour les agents bancaires
    4. **Dashboard analytique** pour le monitoring
    
    #### 🛠️ Architecture technique:
    """)
    
    st.code("""
    Frontend (Streamlit) → API (FastAPI) → Modèle ML → Base de données
                          ↳ Simulation (pour démo)
    """, language="text")
    
    st.markdown("""
    #### 📊 Dataset utilisé:
    - **10,000 transactions** bancaires simulées
    - **Données réalistes** algériennes (DZD, wilayas)
    - **4.7% de taux de fraude** (moyenne industrielle)
    - **24 features** d'analyse
    
    #### 🚀 Déploiement:
    Cette application est déployée sur **Streamlit Cloud**.
    
    **Pour exécuter en local:**
    ```bash
    # Installation des dépendances
    pip install -r requirements.txt
    
    # Lancement de l'application
    streamlit run streamlit_app.py
    ```
    
    #### 📁 Structure du projet:
    """)
    
    project_structure = """
    projet-badr-fraud-detection/
    ├── streamlit_app.py          # Application principale
    ├── api_fraud_detection.py    # API FastAPI (pour usage local)
    ├── fraud_detection_model.pkl # Modèle ML entraîné
    ├── create_realistic_dataset.py # Génération du dataset
    ├── train_ml_model.py         # Entraînement du modèle
    ├── requirements.txt          # Dépendances Python
    ├── runtime.txt              # Version Python (3.11)
    └── README.md                # Documentation
    """
    
    st.code(project_structure, language="bash")
    
    st.markdown("---")
    st.markdown("#### 📞 Pour le salon de recrutement")
    st.markdown("""
    Ce projet a été développé pour démontrer mes compétences en:
    - **Data Science & Machine Learning**
    - **Développement Backend (FastAPI)**
    - **Développement Frontend (Streamlit)**
    - **Analyse de données bancaires**
    - **Déploiement d'applications cloud**
    
    **Technologies maîtrisées:** Python, Pandas, Scikit-learn, Streamlit, FastAPI, Git, GitHub
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d;">
    <p>🏦 Système de Détection de Fraude - Banque Badr | 
    Développé pour le salon de recrutement | 
    Date: {} | 
    Mode: {}</p>
</div>
""".format(
    datetime.now().strftime("%d/%m/%Y %H:%M"),
    "Simulation" if st.session_state.simulation_mode else "API"
), unsafe_allow_html=True)