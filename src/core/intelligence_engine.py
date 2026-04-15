"""
Intelligent IDS Core Engine
Tüm veri kaynaklarından gelen flow'ları işleyen akıllı zeka motoru.

Pipeline:
Input → Feature Engineering → Time-Series Buffer → ML/DL Inference → 
Anomaly Detection → Rule Engine → Decision Engine → Output
"""

from typing import List, Dict, Any, Optional, Deque
from collections import deque
import numpy as np
import joblib
from pathlib import Path

from ..core.data_source import FlowData
from ..flows.features import FlowFeatures


class RollingConfidenceBuffer:
    """Rolling confidence buffer for smoothing confidence scores"""
    
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.confidence_history: Deque[float] = deque(maxlen=window_size)
    
    def add(self, confidence: float):
        """Add new confidence score"""
        self.confidence_history.append(confidence)
    
    def get_smoothed(self) -> float:
        """Get smoothed confidence (mean of last N predictions)"""
        if len(self.confidence_history) == 0:
            return 0.0
        return float(np.mean(list(self.confidence_history)))
    
    def get_raw(self) -> Optional[float]:
        """Get most recent raw confidence"""
        if len(self.confidence_history) == 0:
            return None
        return float(self.confidence_history[-1])


class FeatureEngine:
    """Feature Engineering - Flow verisini model için hazırlar"""
    
    def __init__(self):
        self.feature_names = [
            "src_ip_last", "dst_ip_last", "sport", "dsport", 
            "proto", "dur", "total_bytes", "total_pkts"
        ]
    
    def ip_last_octet(self, ip: str) -> float:
        """IP'nin son okteti"""
        try:
            return float(str(ip).split(".")[-1])
        except:
            return 0.0
    
    def extract_features(self, flow: FlowData) -> np.ndarray:
        """Flow'dan 8 feature çıkar (RandomForest için)"""
        src_ip_last = self.ip_last_octet(flow.src_ip)
        dst_ip_last = self.ip_last_octet(flow.dst_ip)
        sport = float(flow.src_port)
        dsport = float(flow.dst_port)
        proto = 0.0  # Eğitimde hep 0.0
        dur = float(flow.duration)
        total_bytes = float(flow.bytes_fwd + flow.bytes_bwd)
        total_pkts = float(flow.packets_fwd + flow.packets_bwd)
        
        # float32 kullan (memory saving)
        return np.array([src_ip_last, dst_ip_last, sport, dsport, proto, dur, total_bytes, total_pkts], dtype=np.float32)
    
    def extract_features_for_dl(self, flow: FlowData) -> np.ndarray:
        """Deep Learning için daha fazla feature"""
        feats = self.extract_features(flow)
        # Ek feature'lar eklenebilir
        return feats


class TimeSeriesBuffer:
    """Zaman serisi buffer - CNN-LSTM için sequence oluşturur"""
    
    def __init__(self, sequence_length: int = 10):
        self.sequence_length = sequence_length
        self.buffer: Deque[np.ndarray] = deque(maxlen=sequence_length)
    
    def add(self, features: np.ndarray):
        """Feature ekle"""
        self.buffer.append(features)
    
    def get_sequence(self) -> Optional[np.ndarray]:
        """Sequence döndür (eğer yeterli veri varsa)"""
        if len(self.buffer) < self.sequence_length:
            return None
        
        # (sequence_length, num_features) shape - float32 kullan (memory saving)
        return np.array(list(self.buffer), dtype=np.float32)
    
    def clear(self):
        """Buffer'ı temizle"""
        self.buffer.clear()


class RuleEngine:
    """Rule-based detection engine"""
    
    def __init__(self):
        self.rules = []
    
    def evaluate(self, flow: FlowData) -> List[str]:
        """Flow üzerinde kuralları değerlendir"""
        hits = []
        
        pps = (flow.packets_fwd + flow.packets_bwd) / max(flow.duration, 0.001)
        syn = flow.syn
        unique_ports = flow.unique_dst_ports
        rst = flow.rst
        
        # Port scan şüphesi
        if unique_ports >= 20:
            hits.append("PORT_SCAN_SUSPECT")
        
        # SYN flood şüphesi
        if syn >= 30 and pps >= 50:
            hits.append("SYN_FLOOD_SUSPECT")
        
        # RST spike
        if rst >= 20:
            hits.append("RST_SPIKE")
        
        # DDoS şüphesi (çok yüksek paket hızı)
        if pps >= 1000:
            hits.append("DDOS_SUSPECT")
        
        return hits


class MLInference:
    """Machine Learning inference engine - Enhanced with ensemble support"""
    
    def __init__(self, model_path: str = "simple_ids_rf.pkl", use_ensemble: bool = True):
        self.model_path = Path(model_path)
        self.model = None
        self.use_ensemble = use_ensemble
        self.ensemble_engine = None
        
        # Try to load ensemble first, fallback to single model
        if use_ensemble:
            try:
                from .ensemble_engine import EnsembleEngine
                ensemble_path = Path("ensemble_ids_model.pkl")
                if ensemble_path.exists():
                    self.ensemble_engine = EnsembleEngine()
                    self.ensemble_engine.load(str(ensemble_path))
                    print("[ML Inference] Ensemble model loaded")
            except Exception as e:
                print(f"[ML Inference] Ensemble load failed, using single model: {e}")
        
        self._load_model()
    
    def _load_model(self):
        """Modeli yükle"""
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                print(f"[ML Inference] Model yüklendi: {self.model_path}")
            except Exception as e:
                print(f"[ML Inference] Model yüklenemedi: {e}")
                self.model = None
        else:
            print(f"[ML Inference] Model dosyası bulunamadı: {self.model_path}")
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Tahmin yap - Ensemble veya single model"""
        # Try ensemble first if available
        if self.use_ensemble and self.ensemble_engine and self.ensemble_engine.is_trained:
            try:
                if features.dtype != np.float32:
                    features = features.astype(np.float32)
                result = self.ensemble_engine.predict(features)
                return result
            except Exception as e:
                print(f"[ML Inference] Ensemble prediction error, using single model: {e}")
        
        # Fallback to single model
        if self.model is None:
            # Fallback: rastgele tahmin (demo için)
            return {
                "probability": 0.3,
                "is_attack": 0,
                "risk_level": "low",
                "model_used": "fallback"
            }
        
        try:
            # float32 kullan (memory saving)
            if features.dtype != np.float32:
                features = features.astype(np.float32)
            x = features.reshape(1, -1)
            
            # CRITICAL: Use predict_proba() for confidence calculation
            if hasattr(self.model, "predict_proba"):
                proba_raw = self.model.predict_proba(x)[0]
                # Binary classification: confidence = max(p_attack, p_normal)
                # NOT abs(p_attack - p_normal) because that gives 0.0 when model is uncertain (50-50)
                if len(proba_raw) == 2:
                    p_normal = float(proba_raw[0])
                    p_attack = float(proba_raw[1])
                    # Confidence = max probability (how confident the model is in its prediction)
                    proba = max(p_attack, p_normal)  # Use max, not abs difference
                    raw_confidence = float(p_attack)  # Raw attack probability
                else:
                    # Multi-class: use max probability
                    proba = float(np.max(proba_raw))
                    raw_confidence = proba
            else:
                # Fallback: if no predict_proba, use predict (less reliable)
                pred = self.model.predict(x)[0]
                proba = float(pred) if isinstance(pred, (int, float)) else 0.5
                raw_confidence = proba
                print("[ML Inference Warning] Model does not support predict_proba(), using predict()")
            
            # Risk seviyesi - Optimize edilmiş threshold'lar (Better balance)
            # Note: proba is now max(p_attack, p_normal), so it ranges from 0.5 (uncertain) to 1.0 (very confident)
            if proba >= 0.80:  # High confidence
                risk_level = "high"
                is_attack = 1 if raw_confidence >= 0.5 else 0  # Attack if p_attack >= 0.5
            elif proba >= 0.65:  # Medium confidence
                risk_level = "medium"
                is_attack = 1 if raw_confidence >= 0.5 else 0
            else:
                risk_level = "low"
                is_attack = 0  # Low confidence -> treat as normal
            
            return {
                "probability": proba,  # Confidence = max(p_attack, p_normal)
                "raw_confidence": raw_confidence,  # Raw attack probability
                "is_attack": is_attack,
                "risk_level": risk_level,
                "model_used": "randomforest"
            }
        except Exception as e:
            print(f"[ML Inference] Tahmin hatası: {e}")
            return {
                "probability": 0.0,
                "is_attack": 0,
                "risk_level": "low",
                "model_used": "error"
            }


class DLInference:
    """Deep Learning (CNN-LSTM) inference engine"""
    
    def __init__(self, model_path: str = "ids_cnn_lstm.h5"):
        self.model_path = Path(model_path)
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Modeli yükle"""
        if self.model_path.exists():
            try:
                from tensorflow.keras.models import load_model
                self.model = load_model(self.model_path)
                print(f"[DL Inference] CNN-LSTM model yüklendi: {self.model_path}")
            except Exception as e:
                print(f"[DL Inference] Model yüklenemedi: {e}")
                self.model = None
        else:
            print(f"[DL Inference] Model dosyası bulunamadı: {self.model_path}")
    
    def predict(self, sequence: np.ndarray) -> Dict[str, Any]:
        """Sequence üzerinden tahmin yap"""
        if self.model is None:
            return None  # DL kullanılamıyorsa None döndür
        
        try:
            # Sequence shape: (sequence_length, num_features)
            # Model input shape: (batch, time_steps, features)
            # Eğer model (1, features) bekliyorsa, son elemanı al
            if sequence.shape[0] == 1:
                x = sequence
            else:
                # Son elemanı al veya ortalamasını al
                x = sequence[-1:].reshape(1, 1, sequence.shape[1])
            
            proba = float(self.model.predict(x, verbose=0)[0][0])
            
            # Risk seviyesi - Optimize edilmiş threshold'lar (False Positive azaltmak için)
            if proba >= 0.90:  # 0.90 - çok yüksek confidence
                risk_level = "high"
                is_attack = 1
            elif proba >= 0.60:  # 0.60 - orta seviye
                risk_level = "medium"
                is_attack = 0
            else:
                risk_level = "low"
                is_attack = 0
            
            return {
                "probability": proba,
                "is_attack": is_attack,
                "risk_level": risk_level,
                "model_type": "CNN-LSTM"
            }
        except Exception as e:
            print(f"[DL Inference] Tahmin hatası: {e}")
            return None


class DecisionEngine:
    """Final decision engine - tüm sonuçları birleştirir"""
    
    def __init__(self):
        # Optimize edilmiş threshold'lar - False Positive'leri azaltmak için
        # CICIDS 2017 için daha yüksek threshold'lar
        self.thresh_low = 0.60   # 0.50'den 0.60'a yükseltildi (daha az false positive)
        self.thresh_high = 0.90  # 0.85'ten 0.90'a yükseltildi (daha az false positive)
    
    def decide(
        self,
        flow: FlowData,
        ml_pred: Dict[str, Any],
        dl_pred: Optional[Dict[str, Any]],
        rules: List[str]
    ) -> Dict[str, Any]:
        """Final karar ver"""
        
        # Önce ML tahminini al
        base_pred = ml_pred.copy()
        
        # DL tahmini varsa ve daha yüksek confidence varsa kullan
        if dl_pred and dl_pred.get("probability", 0) > base_pred.get("probability", 0):
            base_pred = dl_pred.copy()
            base_pred["model_used"] = "CNN-LSTM"
        else:
            base_pred["model_used"] = "RandomForest"
        
        # Rule-based düzeltmeler - Çok daha konservatif (false positive azaltmak için)
        if "SYN_FLOOD_SUSPECT" in rules and base_pred.get("probability", 0.0) >= 0.85:
            # Sadece çok yüksek confidence varsa rule'u uygula
            base_pred["risk_level"] = "high"
            base_pred["is_attack"] = 1
            base_pred["probability"] = max(base_pred.get("probability", 0.0), self.thresh_high)
        elif "PORT_SCAN_SUSPECT" in rules and base_pred.get("risk_level") == "low" and base_pred.get("probability", 0.0) >= 0.70:
            # Orta seviye risk için daha yüksek threshold
            base_pred["risk_level"] = "medium"
        elif "DDOS_SUSPECT" in rules and base_pred.get("probability", 0.0) >= 0.90:
            # DDoS için çok yüksek threshold
            base_pred["risk_level"] = "high"
            base_pred["is_attack"] = 1
            base_pred["probability"] = max(base_pred.get("probability", 0.0), self.thresh_high)
        
        # Attack type belirleme - PRESERVE original CICIDS2017 attack names
        attack_type = "NORMAL"
        if base_pred.get("is_attack", 0) == 1:
            # Önce CSV'den gelen attack type'ı kontrol et (CICIDS2017: DoS Hulk, PortScan, DDoS, Web Attack, etc.)
            if flow.attack_type and flow.attack_type.upper() != "NORMAL":
                # PRESERVE original attack name - don't collapse to generic
                attack_type = flow.attack_type  # Keep original format (e.g., "DoS Hulk", "PortScan", "DDoS", "Web Attack")
            else:
                # Live mode: Use "Generic Anomaly" if classification is uncertain
                # Dataset mode: Should have attack_type from CSV, but fallback to rule-based
                if not flow.attack_type or flow.attack_type.upper() == "NORMAL":
                    # Try rule-based detection
                    if "SYN_FLOOD_SUSPECT" in rules:
                        attack_type = "SYN Flood"
                    elif "PORT_SCAN_SUSPECT" in rules:
                        attack_type = "Port Scan"
                    elif "DDOS_SUSPECT" in rules:
                        attack_type = "DDoS"
                    else:
                        # Live mode fallback: Generic Anomaly
                        attack_type = "Generic Anomaly"
        else:
            # Normal trafik - CSV'den gelen attack type'ı kullan (eğer varsa)
            if flow.attack_type:
                at_lower = flow.attack_type.lower().strip()
                if at_lower in ["normal", "benign"]:
                    attack_type = "NORMAL"
                else:
                    # CSV'de attack var ama model normal dedi - düşük confidence ile göster
                    attack_type = flow.attack_type.upper()
        
        # Severity hesapla - Optimize edilmiş (False Positive azaltmak için)
        prob = base_pred.get("probability", 0.0)
        if prob >= 0.95:
            severity = "CRITICAL"
        elif prob >= 0.90:
            severity = "HIGH"
        elif prob >= 0.70:
            severity = "MEDIUM"
        elif prob >= 0.50:
            severity = "LOW"
        else:
            severity = "INFO"
        
        # Explanation oluştur
        explanation_parts = []
        if base_pred.get("is_attack", 0) == 1:
            explanation_parts.append(f"Attack detected with {prob:.1%} confidence")
            if rules:
                explanation_parts.append(f"Rules triggered: {', '.join(rules)}")
            explanation_parts.append(f"Type: {attack_type}")
        else:
            explanation_parts.append("Normal traffic")
        
        explanation = ". ".join(explanation_parts)
        
        return {
            "is_attack": base_pred.get("is_attack", 0),
            "attack_type": attack_type,
            "confidence": prob,
            "severity": severity,
            "risk_level": base_pred.get("risk_level", "low"),
            "explanation": explanation,
            "model_used": base_pred.get("model_used", "RandomForest"),
            "rules_triggered": rules,
        }


class IntelligenceEngine:
    """Hybrid AI-based IDS Core Engine - Separate pipelines for Dataset and Live"""
    
    def __init__(
        self,
        mode: str = "LIVE",
        ml_model_path: str = "simple_ids_rf.pkl",
        dl_model_path: str = "ids_cnn_lstm.h5",
        use_dl: bool = True
    ):
        """
        Initialize intelligence engine
        mode: "DATASET" for offline evaluation, "LIVE" for online detection
        """
        self.mode = mode
        self.feature_engine = FeatureEngine()
        self.time_series_buffer = TimeSeriesBuffer(sequence_length=10)
        self.rolling_confidence = RollingConfidenceBuffer(window_size=20)  # Rolling confidence buffer
        
        # Multi-class model for both modes
        try:
            from .multiclass_inference import MultiClassInference
            self.multiclass_inference = MultiClassInference()
            print(f"[IntelligenceEngine] Multi-class model loaded (mode: {mode})")
        except Exception as e:
            print(f"[IntelligenceEngine] Multi-class model not available: {e}")
            self.multiclass_inference = None
        
        # Fallback ML/DL inference
        self.ml_inference = MLInference(ml_model_path)
        self.dl_inference = DLInference(dl_model_path) if use_dl else None
        self.rule_engine = RuleEngine()
        self.decision_engine = DecisionEngine()
    
    def process_flow(self, flow: FlowData) -> Dict[str, Any]:
        """Process flow - Different pipelines for different modes"""
        
        # 1. Feature Engineering
        features = self.feature_engine.extract_features(flow)
        
        # DATASET_INTELLIGENCE MODE: Use multi-class model with ground truth
        if self.mode == "DATASET_INTELLIGENCE":
            return self._process_dataset_flow(flow, features)
        
        # SIMULATED_LIVE MODE: Use similarity-based prediction (like live but from dataset)
        elif self.mode == "SIMULATED_LIVE":
            return self._process_simulated_live_flow(flow, features)
        
        # REAL_NETWORK MODE: Anomaly-based detection only (no attack type classification)
        elif self.mode == "REAL_NETWORK":
            return self._process_real_network_flow(flow, features)
        
        # Default: Use similarity-based prediction (legacy LIVE mode)
        else:
            return self._process_live_flow(flow, features)
    
    def _process_dataset_flow(self, flow: FlowData, features: np.ndarray) -> Dict[str, Any]:
        """
        Process flow in DATASET mode - Ground truth ONLY for status/display
        Model predictions ONLY for metrics evaluation
        """
        # Get ground truth from flow (preserve original CICIDS2018/CICIDS2017 attack types)
        # CICIDS2018: "Benign", "FTP-BruteForce", "SSH-Bruteforce", "FTP-Patator", etc.
        # CICIDS2017: "Normal Traffic", "DoS Hulk", "PortScan", "DDoS", "Web Attack", etc.
        ground_truth = flow.attack_type if flow.attack_type else "NORMAL"
        
        # CRITICAL: Derive Status ONLY from ground truth labels
        # BENIGN -> Normal, Any attack label -> Attack
        ground_truth_upper = ground_truth.upper().strip()
        is_attack_from_ground_truth = 1 if ground_truth_upper not in ["NORMAL", "BENIGN", "NORMAL TRAFFIC", ""] else 0
        
        # Get model prediction (ONLY for metrics evaluation, NOT for status)
        model_prediction_for_metrics = None
        predicted_attack_type = None
        predicted_is_attack = None
        confidence = 0.0
        
        # Use multi-class model for prediction (for metrics only)
        if self.multiclass_inference and self.multiclass_inference.is_loaded:
            multiclass_pred = self.multiclass_inference.predict(features)
            predicted_attack_type = multiclass_pred["attack_type"]
            predicted_is_attack = multiclass_pred["is_attack"]
            confidence = multiclass_pred["confidence"]
            model_prediction_for_metrics = {
                "predicted_attack_type": predicted_attack_type,
                "predicted_is_attack": predicted_is_attack,
                "confidence": confidence,
                "all_probabilities": multiclass_pred.get("all_probabilities", {})
            }
        else:
            # Fallback to binary ML for prediction (for metrics only)
            ml_pred = self.ml_inference.predict(features)
            predicted_is_attack = ml_pred.get("is_attack", 0)
            # Get confidence - use raw_confidence if available, otherwise probability
            confidence = ml_pred.get("raw_confidence", ml_pred.get("probability", 0.0))
            # If confidence is 0.0, it means model is uncertain (50-50 split) - use minimum confidence
            if confidence == 0.0:
                confidence = 0.5  # Minimum confidence for uncertain predictions
            # For binary ML, we don't have specific attack type, use generic
            predicted_attack_type = "Generic Attack" if predicted_is_attack == 1 else "NORMAL"
            model_prediction_for_metrics = {
                "predicted_is_attack": predicted_is_attack,
                "predicted_attack_type": predicted_attack_type,
                "confidence": confidence,
                "raw_confidence": confidence
            }
        
        # Decision for Dataset Mode:
        # - attack_type: Ground truth (for display)
        # - is_attack: Ground truth (for status display)
        # - predicted_*: Model predictions (for metrics only)
        decision = {
            # DISPLAY: Use ground truth
            "attack_type": ground_truth,  # Show original attack type from dataset
            "is_attack": is_attack_from_ground_truth,  # Status from ground truth ONLY
            "risk_level": "high" if is_attack_from_ground_truth == 1 else "low",  # Match status to ground truth
            "ground_truth": ground_truth,  # Explicit ground truth label
            
            # METRICS: Model predictions (for evaluation only)
            "predicted_attack_type": predicted_attack_type,  # Model prediction (for metrics)
            "predicted_is_attack": predicted_is_attack,  # Model prediction (for metrics)
            "confidence": confidence,  # Model confidence
            
            # Additional info
            "all_probabilities": model_prediction_for_metrics.get("all_probabilities", {}),
            "model_used": "multiclass" if self.multiclass_inference and self.multiclass_inference.is_loaded else "binary_ml",
            "mode": "dataset"
        }
        
        result = {
            "flow": flow.to_dict(),
            "features": features.tolist(),
            "decision": decision,
            "timestamp": flow.timestamp,
        }
        
        return result
    
    def _process_live_flow(self, flow: FlowData, features: np.ndarray) -> Dict[str, Any]:
        """Process flow in LIVE mode - Similarity-based prediction with rolling confidence"""
        # Time-Series Buffer
        self.time_series_buffer.add(features)
        sequence = self.time_series_buffer.get_sequence()
        
        # Use multi-class model for similarity-based prediction
        if self.multiclass_inference and self.multiclass_inference.is_loaded:
            multiclass_pred = self.multiclass_inference.predict(features)
            
            # Get raw and smoothed confidence
            raw_confidence = multiclass_pred.get("raw_confidence", multiclass_pred.get("confidence", 0.0))
            self.rolling_confidence.add(raw_confidence)
            smoothed_confidence = self.rolling_confidence.get_smoothed()
            
            # Get top predictions for similarity
            top_predictions = self.multiclass_inference.get_top_predictions(features, top_k=3)
            
            # Determine explanation based on confidence
            # Don't show explanation for low confidence - just show percentage
            explanation = ""
            if smoothed_confidence >= 0.9:
                explanation = f"High confidence ({smoothed_confidence:.1%})"
            elif smoothed_confidence >= 0.6:
                explanation = f"Moderate confidence ({smoothed_confidence:.1%})"
            # Low confidence: no explanation, just show percentage with color
            
            # Decision - similarity-based
            decision = {
                "attack_type": multiclass_pred["attack_type"],  # Most similar attack type
                "confidence": smoothed_confidence,  # Smoothed confidence (rolling mean)
                "raw_confidence": raw_confidence,  # Raw confidence (current prediction)
                "is_attack": multiclass_pred["is_attack"],
                "risk_level": multiclass_pred["risk_level"],
                "similarity_predictions": top_predictions,  # Top 3 similar attacks
                "explanation": explanation,  # Confidence-based explanation
                "model_used": "multiclass_similarity",
                "mode": "live",
                "note": "Predicted based on similarity to trained attack patterns"
            }
        else:
            # Fallback to binary ML + rules
            ml_pred = self.ml_inference.predict(features)
            dl_pred = None
            if self.dl_inference and sequence is not None:
                dl_pred = self.dl_inference.predict(sequence)
            rules = self.rule_engine.evaluate(flow)
            decision = self.decision_engine.decide(flow, ml_pred, dl_pred, rules)
            
            # Add rolling confidence for binary ML
            raw_conf = ml_pred.get("raw_confidence", ml_pred.get("probability", 0.0))
            self.rolling_confidence.add(raw_conf)
            smoothed_conf = self.rolling_confidence.get_smoothed()
            
            decision["raw_confidence"] = raw_conf
            decision["confidence"] = smoothed_conf  # Use smoothed confidence
            decision["mode"] = "live"
            
            # Add explanation based on confidence
            # CRITICAL: Only mark as "Low certainty" if confidence < threshold (0.6)
            confidence_threshold = 0.6
            if smoothed_conf < confidence_threshold:
                decision["explanation"] = ""  # Don't show explanation for low confidence
            else:
                decision["explanation"] = decision.get("explanation", f"Confidence: {smoothed_conf:.1%}")
            
            decision["note"] = "Using binary classification (multi-class model not available)"
        
        result = {
            "flow": flow.to_dict(),
            "features": features.tolist(),
            "decision": decision,
            "timestamp": flow.timestamp,
        }
        
        return result
