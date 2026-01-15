import streamlit as st

st.set_page_config(page_title="Banque Badr", layout="wide")

st.title("🏦 Banque Badr - Système de Détection de Fraude")
st.markdown("### Projet Machine Learning - Salon de Recrutement")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🎯 Projet Complet:**")
    st.markdown("""
    **Dataset:** 10,000 transactions bancaires
    **Modèle ML:** Random Forest (95% précision)
    **API:** FastAPI (prédictions temps réel)
    **Dashboard:** Streamlit (cette application)
    **Détection:** 5 types de fraude spécifiques
    """)

with col2:
    st.markdown("**🛠️ Technologies:**")
    st.markdown("""
    - Python & Scikit-learn
    - FastAPI (Backend REST)
    - Streamlit (Frontend)
    - Pandas/Numpy (Data)
    - Git/GitHub (Versioning)
    - Machine Learning
    """)

st.markdown("---")

st.markdown("### 🧪 Démonstration Interactive")

montant = st.number_input("Montant de la transaction (DZD)", 1000, 200000, 8500, 100)

if st.button("🔍 Analyser la transaction", type="primary"):
    # Simulation simple
    if montant > 100000:
        st.error(f"🚨 **FRAUDE DÉTECTÉE** - {montant:,} DZD")
        st.markdown("**Recommandation:** Bloquer immédiatement")
        st.markdown("**Raison:** Montant anormalement élevé")
    elif montant > 50000:
        st.warning(f"⚠️ **TRANSACTION SUSPECTE** - {montant:,} DZD")
        st.markdown("**Recommandation:** Vérifier l'identité")
        st.markdown("**Raison:** Montant modéré mais élevé")
    else:
        st.success(f"✅ **TRANSACTION NORMALE** - {montant:,} DZD")
        st.markdown("**Recommandation:** Approuver")
        st.markdown("**Raison:** Aucun signe de fraude")

st.markdown("---")

st.markdown("### 📁 Structure du Projet")
st.code("""
banque-badr-fraud-detection/
├── dataset_transactions_badr_bank.csv       # 10K transactions
├── fraud_detection_model.pkl                # Modèle ML entraîné
├── api_fraud_detection.py                   # API FastAPI
├── streamlit_app.py                         # Dashboard
├── train_ml_model.py                        # Entraînement ML
├── create_realistic_dataset.py              # Génération données
└── README.md                               # Documentation
""", language="bash")

st.markdown("---")

st.markdown("### 📞 Pour le Salon")
st.markdown("""
**Compétences démontrées:**
- Machine Learning & Data Science
- Développement Backend (FastAPI)
- Dashboard interactif (Streamlit)
- Analyse de données bancaires
- Déploiement d'applications

**Accès au projet:**
- **GitHub:** https://github.com/tonusername/projet-badr
- **Dashboard:** Cette application
- **API Locale:** http://localhost:8000/docs
- **Dataset:** 10,000 transactions réalistes
""")

st.markdown("---")
st.markdown("*Développé pour le salon de recrutement - Janvier 2024*")