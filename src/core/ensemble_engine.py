"""
Ensemble Engine - Multiple ML algorithms for better performance
Uses voting/stacking to combine predictions from multiple models
"""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Any, Optional, List
from sklearn.ensemble import (
    RandomForestClassifier, 
    GradientBoostingClassifier,
    VotingClassifier,
    ExtraTreesClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier


class EnsembleEngine:
    """Ensemble model - combines multiple algorithms for better accuracy"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path) if model_path else None
        self.models = {}
        self.ensemble_model = None
        self.is_trained = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize multiple ML models"""
        # Base models for ensemble
        self.models = {
            "rf": RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced"
            ),
            "gb": GradientBoostingClassifier(
                n_estimators=100,
                max_depth=10,
                learning_rate=0.1,
                random_state=42
            ),
            "et": ExtraTreesClassifier(
                n_estimators=200,
                max_depth=20,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced"
            ),
            "lr": LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight="balanced",
                solver="lbfgs"
            ),
            "svm": SVC(
                probability=True,
                random_state=42,
                class_weight="balanced",
                kernel="rbf",
                gamma="scale"
            ),
            "mlp": MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
        }
        
        # Voting Classifier - combines all models
        self.ensemble_model = VotingClassifier(
            estimators=[
                ("rf", self.models["rf"]),
                ("gb", self.models["gb"]),
                ("et", self.models["et"]),
                ("lr", self.models["lr"]),
            ],
            voting="soft",  # Use probability voting
            weights=[2, 1, 2, 1]  # RF and ET get more weight
        )
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train ensemble model"""
        print("[Ensemble] Training ensemble model...")
        self.ensemble_model.fit(X_train, y_train)
        self.is_trained = True
        print("[Ensemble] Training complete!")
    
    def predict_proba(self, features: np.ndarray) -> float:
        """Get attack probability from ensemble"""
        if not self.is_trained:
            # Fallback: use simple heuristic
            return 0.3
        
        try:
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            # Get probability from ensemble
            proba = self.ensemble_model.predict_proba(features)[0]
            # Return probability of attack class (class 1)
            if len(proba) > 1:
                return float(proba[1])
            else:
                return float(proba[0])
        except Exception as e:
            print(f"[Ensemble] Prediction error: {e}")
            return 0.3
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Predict with ensemble and return detailed results"""
        if not self.is_trained:
            return {
                "probability": 0.3,
                "is_attack": 0,
                "risk_level": "low",
                "model_used": "ensemble_fallback"
            }
        
        try:
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            # Get probability
            proba = self.predict_proba(features)
            
            # Get individual model predictions for confidence
            individual_probs = []
            for name, model in self.models.items():
                try:
                    if hasattr(model, "predict_proba"):
                        prob = model.predict_proba(features)[0]
                        individual_probs.append(float(prob[1]) if len(prob) > 1 else float(prob[0]))
                except:
                    pass
            
            # Calculate confidence based on agreement
            if individual_probs:
                std_dev = np.std(individual_probs)
                confidence = 1.0 - min(std_dev, 0.5)  # Lower std = higher confidence
            else:
                confidence = proba
            
            # Risk level determination
            if proba >= 0.85:
                risk_level = "high"
                is_attack = 1
            elif proba >= 0.60:
                risk_level = "medium"
                is_attack = 0
            else:
                risk_level = "low"
                is_attack = 0
            
            return {
                "probability": float(proba),
                "is_attack": is_attack,
                "risk_level": risk_level,
                "model_used": "ensemble",
                "confidence": float(confidence),
                "individual_probs": individual_probs[:3]  # First 3 for debugging
            }
        except Exception as e:
            print(f"[Ensemble] Prediction error: {e}")
            return {
                "probability": 0.3,
                "is_attack": 0,
                "risk_level": "low",
                "model_used": "ensemble_error"
            }
    
    def save(self, path: str):
        """Save ensemble model"""
        if self.ensemble_model:
            joblib.dump(self.ensemble_model, path)
            print(f"[Ensemble] Model saved: {path}")
    
    def load(self, path: str):
        """Load ensemble model"""
        try:
            self.ensemble_model = joblib.load(path)
            self.is_trained = True
            print(f"[Ensemble] Model loaded: {path}")
        except Exception as e:
            print(f"[Ensemble] Load error: {e}")
            self.is_trained = False
