# === ÉTAPE 3.1: IMPORTATIONS ===
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import json
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("🚀 API FASTAPI - SYSTÈME DE DÉTECTION DE FRAUDE")
print("=" * 60)
print("Initialisation...")

# === ÉTAPE 3.2: INITIALISATION DE L'APP ===
app = FastAPI(
    title="API de Détection de Fraude Bancaire",
    description="API pour détecter les transactions frauduleuses en temps réel - Banque Badr",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ÉTAPE 3.3: CHARGEMENT DES MODÈLES ===
print("📂 Chargement des modèles et encodeurs...")

try:
    # Charger le modèle ML
    model = joblib.load('fraud_detection_model.pkl')
    print("   ✅ Modèle ML chargé")
    
    # Charger l'encodeur
    encoder = joblib.load('onehot_encoder.pkl')
    print("   ✅ Encodeur chargé")
    
    # Charger les infos des features
    with open('features_info.json', 'r', encoding='utf-8') as f:
        features_info = json.load(f)
    print("   ✅ Features info chargées")
    
    # Charger les métriques
    with open('model_metrics.json', 'r', encoding='utf-8') as f:
        metrics = json.load(f)
    print("   ✅ Métriques chargées")
    
except Exception as e:
    print(f"❌ Erreur lors du chargement: {e}")
    raise RuntimeError(f"Impossible de charger les modèles: {e}")

# === ÉTAPE 3.4: DÉFINITION DES MODÈLES PYDANTIC ===

class Transaction(BaseModel):
    """Modèle pour une transaction individuelle"""
    montant_dzd: float = Field(..., gt=0, description="Montant en DZD")
    heure_jour: int = Field(..., ge=0, le=23, description="Heure de la transaction (0-23)")
    type_transaction: str = Field(..., description="Type de transaction")
    categorie_marchand: str = Field(..., description="Catégorie du marchand")
    canal_paiement: str = Field(..., description="Canal de paiement")
    wilaya_client: str = Field(..., description="Wilaya du client")
    revenu_client: float = Field(..., gt=0, description="Revenu mensuel du client")
    anciennete_client_jours: int = Field(..., ge=0, description="Ancienneté du compte en jours")
    
    # Features calculées (optionnelles - peuvent être calculées automatiquement)
    montant_anormal_score: Optional[float] = None
    heure_inhabituelle: Optional[int] = None
    localisation_etrangere: Optional[int] = None
    categorie_risquee: Optional[int] = None
    ratio_montant_revenu: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "montant_dzd": 8500.0,
                "heure_jour": 14,
                "type_transaction": "ACHAT_CARTE",
                "categorie_marchand": "SUPERMARCHE",
                "canal_paiement": "CARTE_PHYSIQUE",
                "wilaya_client": "Alger",
                "revenu_client": 45000.0,
                "anciennete_client_jours": 500,
                "montant_anormal_score": 0.2,
                "heure_inhabituelle": 0,
                "localisation_etrangere": 0,
                "categorie_risquee": 0,
                "ratio_montant_revenu": 0.15
            }
        }

class BatchTransactions(BaseModel):
    """Modèle pour un batch de transactions"""
    transactions: List[Transaction]
    
    class Config:
        schema_extra = {
            "example": {
                "transactions": [
                    {
                        "montant_dzd": 8500.0,
                        "heure_jour": 14,
                        "type_transaction": "ACHAT_CARTE",
                        "categorie_marchand": "SUPERMARCHE",
                        "canal_paiement": "CARTE_PHYSIQUE",
                        "wilaya_client": "Alger",
                        "revenu_client": 45000.0,
                        "anciennete_client_jours": 500
                    },
                    {
                        "montant_dzd": 125000.0,
                        "heure_jour": 3,
                        "type_transaction": "PAIEMENT_EN_LIGNE",
                        "categorie_marchand": "ELECTRONIQUE",
                        "canal_paiement": "INTERNET_BANKING",
                        "wilaya_client": "Alger",
                        "revenu_client": 35000.0,
                        "anciennete_client_jours": 30
                    }
                ]
            }
        }

class FraudCheckResponse(BaseModel):
    """Réponse de vérification de fraude"""
    transaction_id: Optional[str] = None
    is_fraud: bool
    fraud_probability: float
    risk_level: str
    risk_score: float
    reasons: List[str]
    recommendation: str
    features_used: Dict[str, Any]
    model_confidence: float
    
    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "TXN_123456",
                "is_fraud": False,
                "fraud_probability": 0.12,
                "risk_level": "LOW",
                "risk_score": 0.3,
                "reasons": ["Transaction normale"],
                "recommendation": "Approuver la transaction",
                "features_used": {
                    "montant_dzd": 8500.0,
                    "heure_inhabituelle": 0
                },
                "model_confidence": 0.88
            }
        }

class BatchFraudCheckResponse(BaseModel):
    """Réponse pour batch de transactions"""
    results: List[FraudCheckResponse]
    summary: Dict[str, Any]
    processing_time_ms: float

class HealthCheck(BaseModel):
    """Réponse de santé de l'API"""
    status: str
    model_loaded: bool
    model_name: str
    model_metrics: Dict[str, Any]
    timestamp: str
    version: str

# === ÉTAPE 3.5: FONCTIONS UTILITAIRES ===

def calculate_features(transaction: Transaction) -> Transaction:
    """Calcule les features additionnelles si non fournies"""
    
    # Si les features calculées ne sont pas fournies, les calculer
    if transaction.montant_anormal_score is None:
        # Calcul simple du score d'anomalie (à adapter selon la logique métier)
        montant_moyen = transaction.revenu_client * 0.1  # 10% du revenu comme moyenne
        transaction.montant_anormal_score = abs(transaction.montant_dzd - montant_moyen) / max(montant_moyen, 1)
    
    if transaction.heure_inhabituelle is None:
        # Heure inhabituelle: entre 1h et 5h du matin
        transaction.heure_inhabituelle = 1 if 1 <= transaction.heure_jour <= 5 else 0
    
    if transaction.localisation_etrangere is None:
        # Pour simplifier, on considère que toutes les transactions sont en Algérie
        # Dans une vraie implémentation, on aurait un champ 'pays'
        transaction.localisation_etrangere = 0
    
    if transaction.categorie_risquee is None:
        # Catégories considérées comme risquées
        categories_risquees = ['VOYAGE', 'ELECTRONIQUE', 'IMMOBILIER']
        transaction.categorie_risquee = 1 if transaction.categorie_marchand in categories_risquees else 0
    
    if transaction.ratio_montant_revenu is None:
        transaction.ratio_montant_revenu = transaction.montant_dzd / max(transaction.revenu_client, 1)
    
    return transaction

def prepare_features(transaction: Transaction) -> pd.DataFrame:
    """Prépare les features pour la prédiction"""
    
    # Calculer les features si besoin
    transaction = calculate_features(transaction)
    
    # Créer un DataFrame avec toutes les features de base
    data = {
        'montant_dzd': [transaction.montant_dzd],
        'heure_jour': [transaction.heure_jour],
        'montant_anormal_score': [transaction.montant_anormal_score],
        'ratio_montant_revenu': [transaction.ratio_montant_revenu],
        'anciennete_client_jours': [transaction.anciennete_client_jours],
        'revenu_client': [transaction.revenu_client],
        'heure_inhabituelle': [transaction.heure_inhabituelle],
        'localisation_etrangere': [transaction.localisation_etrangere],
        'categorie_risquee': [transaction.categorie_risquee],
        'type_transaction': [transaction.type_transaction],
        'categorie_marchand': [transaction.categorie_marchand],
        'canal_paiement': [transaction.canal_paiement],
        'wilaya_client': [transaction.wilaya_client]
    }
    
    df = pd.DataFrame(data)
    
    # Séparer les features numériques/binaires des catégorielles
    numerical_features = features_info['numerical_features']
    binary_features = features_info['binary_features']
    categorical_features = features_info['categorical_features']
    
    # Features numériques et binaires
    numerical_binary_df = df[numerical_features + binary_features]
    
    # Features catégorielles à encoder
    categorical_df = df[categorical_features]
    
    # Encoder les catégorielles
    categorical_encoded = encoder.transform(categorical_df)
    categorical_encoded_df = pd.DataFrame(
        categorical_encoded, 
        columns=encoder.get_feature_names_out(categorical_features)
    )
    
    # Combiner toutes les features
    final_df = pd.concat([numerical_binary_df.reset_index(drop=True), 
                         categorical_encoded_df], axis=1)
    
    # S'assurer que toutes les colonnes attendues sont présentes
    expected_columns = features_info['all_features']
    for col in expected_columns:
        if col not in final_df.columns:
            final_df[col] = 0
    
    # Réorganiser les colonnes dans le bon ordre
    final_df = final_df[expected_columns]
    
    return final_df

def analyze_fraud_reasons(transaction: Transaction, fraud_probability: float) -> List[str]:
    """Analyse les raisons potentielles de fraude"""
    reasons = []
    
    # Vérifier différentes conditions de risque
    if fraud_probability > 0.7:
        reasons.append("Probabilité de fraude très élevée")
    
    if transaction.montant_anormal_score > 3:
        reasons.append(f"Montant anormal (score: {transaction.montant_anormal_score:.2f})")
    
    if transaction.heure_inhabituelle == 1:
        reasons.append("Transaction à heure inhabituelle")
    
    if transaction.localisation_etrangere == 1:
        reasons.append("Transaction depuis l'étranger")
    
    if transaction.categorie_risquee == 1:
        reasons.append("Catégorie de marchand à haut risque")
    
    if transaction.ratio_montant_revenu > 0.5:
        reasons.append(f"Montant élevé par rapport au revenu ({transaction.ratio_montant_revenu:.2%})")
    
    if transaction.anciennete_client_jours < 90:
        reasons.append("Compte client récent")
    
    if not reasons and fraud_probability < 0.3:
        reasons.append("Transaction normale")
    
    return reasons

def get_recommendation(is_fraud: bool, risk_level: str, fraud_probability: float) -> str:
    """Génère une recommandation basée sur le risque"""
    if is_fraud:
        if fraud_probability > 0.8:
            return "BLOQUER - Fraude confirmée"
        elif fraud_probability > 0.6:
            return "SUSPENDRE - Nécessite vérification manuelle"
        else:
            return "SURVEILLER - Risque modéré"
    else:
        if risk_level == "HIGH":
            return "VÉRIFIER - Risque élevé détecté"
        elif risk_level == "MEDIUM":
            return "SURVEILLER - Risque moyen"
        else:
            return "APPROUVER - Risque faible"

def get_risk_level(fraud_probability: float) -> tuple:
    """Détermine le niveau de risque"""
    if fraud_probability >= 0.7:
        return "HIGH", 0.9
    elif fraud_probability >= 0.4:
        return "MEDIUM", 0.6
    elif fraud_probability >= 0.2:
        return "LOW", 0.3
    else:
        return "VERY_LOW", 0.1

# === ÉTAPE 3.6: ENDPOINTS DE L'API ===

@app.get("/", tags=["Root"])
async def root():
    """Endpoint racine"""
    return {
        "message": "Bienvenue sur l'API de Détection de Fraude - Banque Badr",
        "version": "1.0.0",
        "docs": "/docs",
        "health_check": "/health"
    }

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Vérifie la santé de l'API et du modèle"""
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_name": metrics.get("best_model", "Random Forest"),
        "model_metrics": metrics.get("test_metrics", {}),
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/model/info", tags=["Model"])
async def get_model_info():
    """Retourne des informations sur le modèle entraîné"""
    return {
        "model_name": metrics.get("best_model"),
        "performance_metrics": metrics.get("test_metrics"),
        "training_info": metrics.get("training_info"),
        "features_count": len(features_info.get("all_features", [])),
        "model_loaded": True
    }

@app.post("/predict", response_model=FraudCheckResponse, tags=["Prediction"])
async def predict_fraud(transaction: Transaction):
    """
    Prédit si une transaction est frauduleuse
    
    - **montant_dzd**: Montant en DZD
    - **heure_jour**: Heure de la transaction (0-23)
    - **type_transaction**: Type de transaction
    - **categorie_marchand**: Catégorie du marchand
    - **canal_paiement**: Canal de paiement
    - **wilaya_client**: Wilaya du client
    - **revenu_client**: Revenu mensuel du client
    - **anciennete_client_jours**: Ancienneté du compte en jours
    """
    
    try:
        start_time = datetime.now()
        
        # Préparer les features
        features_df = prepare_features(transaction)
        
        # Faire la prédiction
        fraud_probability = model.predict_proba(features_df)[0][1]
        is_fraud = fraud_probability > 0.5  # Seuil à 50%
        
        # Analyser le risque
        risk_level, risk_score = get_risk_level(fraud_probability)
        
        # Analyser les raisons
        reasons = analyze_fraud_reasons(transaction, fraud_probability)
        
        # Générer une recommandation
        recommendation = get_recommendation(is_fraud, risk_level, fraud_probability)
        
        # Calculer le temps de traitement
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Features utilisées (simplifiées pour la réponse)
        features_used = {
            "montant_dzd": float(transaction.montant_dzd),
            "heure_jour": transaction.heure_jour,
            "montant_anormal_score": float(transaction.montant_anormal_score or 0),
            "heure_inhabituelle": transaction.heure_inhabituelle or 0,
            "localisation_etrangere": transaction.localisation_etrangere or 0,
            "categorie_risquee": transaction.categorie_risquee or 0,
            "ratio_montant_revenu": float(transaction.ratio_montant_revenu or 0)
        }
        
        # Générer un ID de transaction
        transaction_id = f"TXN_{int(datetime.now().timestamp() * 1000)}"
        
        return {
            "transaction_id": transaction_id,
            "is_fraud": bool(is_fraud),
            "fraud_probability": float(fraud_probability),
            "risk_level": risk_level,
            "risk_score": float(risk_score),
            "reasons": reasons,
            "recommendation": recommendation,
            "features_used": features_used,
            "model_confidence": float(model.predict_proba(features_df)[0].max())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )

@app.post("/predict/batch", response_model=BatchFraudCheckResponse, tags=["Prediction"])
async def predict_batch_fraud(batch: BatchTransactions):
    """
    Prédit la fraude pour un batch de transactions
    """
    try:
        start_time = datetime.now()
        results = []
        
        for i, transaction in enumerate(batch.transactions):
            # Préparer les features
            features_df = prepare_features(transaction)
            
            # Faire la prédiction
            fraud_probability = model.predict_proba(features_df)[0][1]
            is_fraud = fraud_probability > 0.5
            
            # Analyser le risque
            risk_level, risk_score = get_risk_level(fraud_probability)
            
            # Analyser les raisons
            reasons = analyze_fraud_reasons(transaction, fraud_probability)
            
            # Générer une recommandation
            recommendation = get_recommendation(is_fraud, risk_level, fraud_probability)
            
            # Features utilisées
            features_used = {
                "montant_dzd": float(transaction.montant_dzd),
                "heure_jour": transaction.heure_jour,
                "montant_anormal_score": float(transaction.montant_anormal_score or 0),
                "heure_inhabituelle": transaction.heure_inhabituelle or 0
            }
            
            results.append({
                "transaction_id": f"BATCH_TXN_{i+1}",
                "is_fraud": bool(is_fraud),
                "fraud_probability": float(fraud_probability),
                "risk_level": risk_level,
                "risk_score": float(risk_score),
                "reasons": reasons,
                "recommendation": recommendation,
                "features_used": features_used,
                "model_confidence": float(model.predict_proba(features_df)[0].max())
            })
        
        # Calculer les statistiques du batch
        fraud_count = sum(1 for r in results if r["is_fraud"])
        avg_probability = np.mean([r["fraud_probability"] for r in results])
        
        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "results": results,
            "summary": {
                "total_transactions": len(results),
                "fraudulent_transactions": fraud_count,
                "fraud_rate": f"{(fraud_count / len(results)) * 100:.2f}%",
                "average_fraud_probability": float(avg_probability),
                "high_risk_count": sum(1 for r in results if r["risk_level"] == "HIGH"),
                "medium_risk_count": sum(1 for r in results if r["risk_level"] == "MEDIUM"),
                "low_risk_count": sum(1 for r in results if r["risk_level"] in ["LOW", "VERY_LOW"])
            },
            "processing_time_ms": float(processing_time_ms)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors du traitement du batch: {str(e)}"
        )

@app.get("/features/importance", tags=["Model"])
async def get_features_importance():
    """Retourne l'importance des features du modèle"""
    try:
        if hasattr(model, 'feature_importances_'):
            importance_dict = dict(zip(
                features_info.get('all_features', []),
                model.feature_importances_.tolist()
            ))
            
            # Trier par importance décroissante
            sorted_importance = sorted(
                importance_dict.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 seulement
            
            return {
                "top_features": [
                    {"feature": feat, "importance": imp}
                    for feat, imp in sorted_importance
                ],
                "total_features": len(importance_dict)
            }
        else:
            return {
                "message": "Le modèle ne supporte pas l'importance des features",
                "model_type": type(model).__name__
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des importances: {str(e)}"
        )

@app.get("/test/example", tags=["Testing"])
async def test_example():
    """Retourne des exemples de transactions pour tester l'API"""
    
    examples = {
        "normal_transaction": {
            "montant_dzd": 8500.0,
            "heure_jour": 14,
            "type_transaction": "ACHAT_CARTE",
            "categorie_marchand": "SUPERMARCHE",
            "canal_paiement": "CARTE_PHYSIQUE",
            "wilaya_client": "Alger",
            "revenu_client": 45000.0,
            "anciennete_client_jours": 500,
            "montant_anormal_score": 0.2,
            "heure_inhabituelle": 0,
            "localisation_etrangere": 0,
            "categorie_risquee": 0,
            "ratio_montant_revenu": 0.15
        },
        "fraudulent_transaction": {
            "montant_dzd": 125000.0,
            "heure_jour": 3,
            "type_transaction": "PAIEMENT_EN_LIGNE",
            "categorie_marchand": "ELECTRONIQUE",
            "canal_paiement": "INTERNET_BANKING",
            "wilaya_client": "Alger",
            "revenu_client": 35000.0,
            "anciennete_client_jours": 30,
            "montant_anormal_score": 8.5,
            "heure_inhabituelle": 1,
            "localisation_etrangere": 1,
            "categorie_risquee": 1,
            "ratio_montant_revenu": 2.5
        },
        "suspicious_transaction": {
            "montant_dzd": 45000.0,
            "heure_jour": 22,
            "type_transaction": "VIREMENT",
            "categorie_marchand": "VOYAGE",
            "canal_paiement": "MOBILE_BANKING",
            "wilaya_client": "Oran",
            "revenu_client": 38000.0,
            "anciennete_client_jours": 150,
            "montant_anormal_score": 3.2,
            "heure_inhabituelle": 0,
            "localisation_etrangere": 0,
            "categorie_risquee": 1,
            "ratio_montant_revenu": 1.18
        }
    }
    
    return {
        "examples": examples,
        "instructions": "Utilisez ces exemples avec l'endpoint /predict",
        "note": "Les valeurs calculées peuvent être omises, elles seront calculées automatiquement"
    }

# === ÉTAPE 3.7: SCRIPT DE DÉMARRAGE ===
