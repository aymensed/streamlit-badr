# streamlit_simple.py - Version garantie sans pandas/numpy
import streamlit as st
from datetime import datetime
import time

# Configuration
st.set_page_config(
    page_title="Banque Badr - Détection de Fraude",
    page_icon="🏦",
    layout="wide"
)

# CSS simple
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# Titre
st.title("🏦 Banque Badr - Détection de Fraude")
st.markdown("### Projet Machine Learning pour le Salon de Recrutement")

# Initialisation
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Fonction de simulation
def simulate_fraud(montant, heure, categorie, anciennete, revenu):
    """Simulation simple de détection de fraude"""
    score = 0.0
    raisons = []
    
    if montant > revenu * 0.5:
        score += 0.4
        raisons.append(f"Montant élevé ({montant/revenu*100:.0f}% du revenu)")
    
    if 1 <= heure <= 5:
        score += 0.3
        raisons.append(f"Heure nocturne ({heure}h)")
    
    if categorie in ['ELECTRONIQUE', 'VOYAGE', 'IMMOBILIER']:
        score += 0.2
        raisons.append(f"Catégorie à risque: {categorie}")
    
    if anciennete < 90:
        score += 0.1
        raisons.append(f"Compte récent ({anciennete} jours)")
    
    if montant > 100000:
        score += 0.3
        raisons.append(f"Montant très élevé: {montant:,.0f} DZD")
    
    score = min(score, 1.0)
    is_fraud = score > 0.5
    
    if score >= 0.7:
        niveau = "HIGH"
    elif score >= 0.4:
        niveau = "MEDIUM"
    else:
        niveau = "LOW"
    
    if is_fraud:
        if score > 0.8:
            recommandation = "BLOQUER - Fraude confirmée"
        else:
            recommandation = "SUSPENDRE - Nécessite vérification"
    else:
        if niveau == "HIGH":
            recommandation = "VÉRIFIER - Risque élevé"
        elif niveau == "MEDIUM":
            recommandation = "SURVEILLER - Risque moyen"
        else:
            recommandation = "APPROUVER - Risque faible"
    
    return {
        'id': f"TXN-{int(time.time() * 1000)}",
        'is_fraud': is_fraud,
        'score': score,
        'niveau': niveau,
        'recommandation': recommandation,
        'raisons': raisons if raisons else ["Transaction normale"],
        'montant': montant,
        'heure': heure,
        'timestamp': datetime.now().isoformat()
    }

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/bank.png", width=100)
    st.markdown("**📊 Statistiques**")
    
    if st.session_state.transactions:
        total = len(st.session_state.transactions)
        fraudes = sum(1 for t in st.session_state.transactions if t['is_fraud'])
        taux = (fraudes / total * 100) if total > 0 else 0
        
        st.metric("Transactions", total)
        st.metric("Fraudes", fraudes)
        st.metric("Taux", f"{taux:.1f}%")

# Interface principale
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 Nouvelle Transaction")
    
    montant = st.number_input("Montant (DZD)", 1000, 500000, 8500, 100)
    heure = st.slider("Heure", 0, 23, 14)
    categorie = st.selectbox("Catégorie", 
                           ["SUPERMARCHE", "ELECTRONIQUE", "VOYAGE", "IMMOBILIER", "RESTAURANT"])
    revenu = st.number_input("Revenu mensuel (DZD)", 10000, 500000, 45000, 1000)
    anciennete = st.number_input("Ancienneté (jours)", 1, 3650, 500)

with col2:
    st.markdown("### ⚡ Actions rapides")
    
    if st.button("💳 Transaction normale", use_container_width=True):
        montant = 8500
        heure = 14
        categorie = "SUPERMARCHE"
        revenu = 45000
        anciennete = 500
    
    if st.button("🚨 Transaction frauduleuse", use_container_width=True):
        montant = 125000
        heure = 3
        categorie = "ELECTRONIQUE"
        revenu = 35000
        anciennete = 30
    
    if st.button("⚠️ Transaction suspecte", use_container_width=True):
        montant = 45000
        heure = 22
        categorie = "VOYAGE"
        revenu = 38000
        anciennete = 150
    
    st.markdown("---")
    
    if st.button("🔍 Analyser la transaction", type="primary", use_container_width=True):
        resultat = simulate_fraud(montant, heure, categorie, anciennete, revenu)
        st.session_state.transactions.append(resultat)
        
        st.markdown("### 📊 Résultat")
        
        if resultat['is_fraud']:
            st.markdown("""
            <div class="fraud-alert">
                <h3>🚨 FRAUDE DÉTECTÉE</h3>
                <p>Transaction suspecte détectée.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="normal-alert">
                <h3>✅ TRANSACTION NORMALE</h3>
                <p>Transaction légitime.</p>
            </div>
            """, unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Score risque", f"{resultat['score']*100:.0f}%")
        with col_b:
            st.metric("Niveau", resultat['niveau'])
        with col_c:
            st.metric("Action", resultat['recommandation'].split(" - ")[0])
        
        st.progress(resultat['score'])
        
        if resultat['raisons']:
            st.markdown("**📝 Raisons :**")
            for raison in resultat['raisons']:
                st.write(f"- {raison}")

st.markdown("---")

# Historique
st.markdown("### 📋 Historique des transactions")

if st.session_state.transactions:
    for i, t in enumerate(reversed(st.session_state.transactions[-5:])):
        with st.container(border=True):
            cols = st.columns(4)
            with cols[0]:
                st.markdown(f"**ID:** {t['id']}")
            with cols[1]:
                st.markdown(f"**Montant:** {t['montant']:,} DZD")
            with cols[2]:
                st.markdown(f"**Heure:** {t['heure']}h")
            with cols[3]:
                if t['is_fraud']:
                    st.markdown("**Statut:** 🚨 Fraude")
                else:
                    st.markdown("**Statut:** ✅ Normal")
else:
    st.info("Aucune transaction analysée.")

st.markdown("---")

# Documentation
st.markdown("### 📚 À propos du projet")
st.markdown("""
**Projet complet disponible sur GitHub :**
- Dataset de 10,000 transactions algériennes
- Modèle ML Random Forest (95% précision)
- API FastAPI pour prédictions
- Dashboard interactif Streamlit
- Détection de 5 types de fraude

**Compétences démontrées :**
- Machine Learning & Data Science
- Développement API REST
- Analyse de données financières
- Déploiement d'applications
- Interface utilisateur moderne
""")

st.markdown("---")
st.markdown(f"*Développé pour le salon de recrutement - {datetime.now().strftime('%d/%m/%Y')}*")
