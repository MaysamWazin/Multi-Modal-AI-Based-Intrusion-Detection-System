"""
Multi-Class Classification Trainer for CICIDS2017
Trains a model to classify all attack types (DoS Hulk, DDoS, PortScan, Bot, Web Attacks, etc.)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import joblib
from collections import Counter

from src.core.intelligence_engine import FeatureEngine
from src.core.data_source import FlowData

# Paths
CICIDS_PATH = Path("data/raw/cicids2017_cleaned.csv")
MODEL_PATH = "multiclass_ids_model.pkl"
SCALER_PATH = "multiclass_scaler.pkl"
LABEL_ENCODER_PATH = "multiclass_label_encoder.pkl"
MAX_SAMPLES = 50000  # Limit for training speed

def load_and_prepare_data(path: Path, max_samples: int = None):
    """Load CICIDS2017 and prepare features"""
    print(f"[*] Loading CICIDS2017 from {path}...")
    
    chunks = []
    chunk_size = 10000
    total_loaded = 0
    
    for chunk in pd.read_csv(path, chunksize=chunk_size, low_memory=True):
        chunks.append(chunk)
        total_loaded += len(chunk)
        if max_samples and total_loaded >= max_samples:
            break
    
    df = pd.concat(chunks, ignore_index=True)
    if max_samples and len(df) > max_samples:
        df = df.sample(n=max_samples, random_state=42)
    
    print(f"[*] Loaded {len(df)} samples")
    
    # Extract features and labels
    feature_engine = FeatureEngine()
    features_list = []
    attack_types = []
    
    for idx, row in df.iterrows():
        try:
            # Create FlowData
            flow_dict = {
                "src_ip": f"10.0.0.{idx % 255}",
                "dst_ip": f"10.0.1.{idx % 255}",
                "src_port": int(row.get("Source Port", 0) or 0),
                "dst_port": int(row.get("Destination Port", 0) or 0),
                "proto": "TCP",
                "duration": float(row.get("Flow Duration", 0.0) or 0.0),
                "packets_fwd": int(row.get("Total Fwd Packets", 0) or 0),
                "packets_bwd": int(row.get("Total Bwd Packets", 0) or 0),
                "bytes_fwd": int(row.get("Total Length of Fwd Packets", 0) or 0),
                "bytes_bwd": int(row.get("Total Length of Bwd Packets", 0) or 0),
                "syn": 0, "ack": 0, "rst": 0, "fin": 0, "unique_dst_ports": 0
            }
            
            flow = FlowData(**flow_dict)
            features = feature_engine.extract_features(flow)
            features_list.append(features)
            
            # Get attack type
            attack_type = row.get("Attack Type", "Normal Traffic")
            if pd.notna(attack_type):
                attack_type_str = str(attack_type).strip()
                if attack_type_str.lower() in ["normal traffic", "normal", "benign"]:
                    attack_types.append("NORMAL")
                else:
                    attack_types.append(attack_type_str)  # Preserve original name
            else:
                attack_types.append("NORMAL")
                
        except Exception as e:
            print(f"[!] Error at row {idx}: {e}")
            continue
    
    X = np.array(features_list, dtype=np.float32)
    y = np.array(attack_types)
    
    print(f"[*] Features shape: {X.shape}")
    print(f"[*] Attack type distribution:")
    for atype, count in Counter(y).most_common():
        print(f"  {atype}: {count}")
    
    return X, y

def main():
    """Main training function"""
    print("=" * 70)
    print("CICIDS2017 Multi-Class Classification Training")
    print("=" * 70)
    
    if not CICIDS_PATH.exists():
        print(f"[ERROR] File not found: {CICIDS_PATH}")
        return
    
    # Load data
    X, y = load_and_prepare_data(CICIDS_PATH, max_samples=MAX_SAMPLES)
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"\n[*] Number of classes: {len(label_encoder.classes_)}")
    print(f"[*] Classes: {list(label_encoder.classes_)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\n[*] Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    print("\n[*] Training models...")
    
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=25,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )
    
    gb = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=10,
        learning_rate=0.1,
        random_state=42
    )
    
    # Voting classifier
    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("gb", gb)],
        voting="soft",
        weights=[2, 1]
    )
    
    print("[*] Fitting ensemble model...")
    ensemble.fit(X_train_scaled, y_train)
    
    # Evaluate
    print("\n[*] Evaluating...")
    y_pred = ensemble.predict(X_test_scaled)
    y_pred_proba = ensemble.predict_proba(X_test_scaled)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f} (weighted)")
    print(f"Recall:    {recall:.4f} (weighted)")
    print(f"F1 Score:  {f1:.4f} (weighted)")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix Shape: {cm.shape}")
    
    # Per-class metrics
    print("\nPer-Class Metrics:")
    print(classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    ))
    
    # Save models
    joblib.dump(ensemble, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)
    
    print("\n" + "=" * 70)
    print(f"[+] Model saved: {MODEL_PATH}")
    print(f"[+] Scaler saved: {SCALER_PATH}")
    print(f"[+] Label encoder saved: {LABEL_ENCODER_PATH}")
    print("=" * 70)

if __name__ == "__main__":
    main()
