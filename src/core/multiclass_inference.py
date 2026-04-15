"""
Multi-Class Inference Engine
Uses trained multi-class model to predict attack types
"""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder


class MultiClassInference:
    """Multi-class classification inference engine"""
    
    def __init__(
        self,
        model_path: str = "multiclass_ids_model.pkl",
        scaler_path: str = "multiclass_scaler.pkl",
        label_encoder_path: str = "multiclass_label_encoder.pkl"
    ):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.label_encoder_path = Path(label_encoder_path)
        
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.is_loaded = False
        
        self._load_models()
    
    def _load_models(self):
        """Load trained models"""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                print(f"[MultiClass] Model loaded: {self.model_path}")
            else:
                print(f"[MultiClass] Model not found: {self.model_path}")
                return
            
            if self.scaler_path.exists():
                self.scaler = joblib.load(self.scaler_path)
                print(f"[MultiClass] Scaler loaded: {self.scaler_path}")
            else:
                print(f"[MultiClass] Scaler not found: {self.scaler_path}")
                return
            
            if self.label_encoder_path.exists():
                self.label_encoder = joblib.load(self.label_encoder_path)
                print(f"[MultiClass] Label encoder loaded: {self.label_encoder_path}")
                print(f"[MultiClass] Classes: {list(self.label_encoder.classes_)}")
            else:
                print(f"[MultiClass] Label encoder not found: {self.label_encoder_path}")
                return
            
            self.is_loaded = True
            print("[MultiClass] All models loaded successfully!")
            
        except Exception as e:
            print(f"[MultiClass] Load error: {e}")
            import traceback
            traceback.print_exc()
            self.is_loaded = False
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Predict attack type and return detailed results"""
        if not self.is_loaded:
            return {
                "attack_type": "UNKNOWN",
                "confidence": 0.0,
                "is_attack": 0,
                "risk_level": "low",
                "all_probabilities": {}
            }
        
        try:
            # Ensure float32
            if features.dtype != np.float32:
                features = features.astype(np.float32)
            
            # Reshape if needed
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict
            predicted_class_idx = self.model.predict(features_scaled)[0]
            predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]
            
            # CRITICAL: Use predict_proba() for confidence calculation
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Create probability dictionary
            all_probs = {}
            for idx, class_name in enumerate(self.label_encoder.classes_):
                all_probs[class_name] = float(probabilities[idx])
            
            # Get confidence (max probability for multiclass)
            # Normalized confidence = max(predict_proba)
            confidence = float(np.max(probabilities))
            raw_confidence = confidence  # For multiclass, raw = max probability
            
            # Determine if attack
            is_attack = 1 if predicted_class.upper() != "NORMAL" else 0
            
            # Risk level
            if confidence >= 0.85:
                risk_level = "high"
            elif confidence >= 0.60:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "attack_type": predicted_class,  # Original attack type name
                "confidence": confidence,  # Normalized confidence (max probability)
                "raw_confidence": raw_confidence,  # Raw confidence
                "is_attack": is_attack,
                "risk_level": risk_level,
                "all_probabilities": all_probs,
                "model_used": "multiclass"
            }
            
        except Exception as e:
            print(f"[MultiClass] Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "attack_type": "ERROR",
                "confidence": 0.0,
                "is_attack": 0,
                "risk_level": "low",
                "all_probabilities": {},
                "model_used": "error"
            }
    
    def get_top_predictions(self, features: np.ndarray, top_k: int = 3) -> list:
        """Get top K predictions with probabilities"""
        if not self.is_loaded:
            return []
        
        try:
            if features.dtype != np.float32:
                features = features.astype(np.float32)
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            features_scaled = self.scaler.transform(features)
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Get top K
            top_indices = np.argsort(probabilities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                class_name = self.label_encoder.classes_[idx]
                prob = float(probabilities[idx])
                results.append({
                    "attack_type": class_name,
                    "probability": prob
                })
            
            return results
            
        except Exception as e:
            print(f"[MultiClass] Top predictions error: {e}")
            return []
