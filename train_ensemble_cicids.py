"""
Train Ensemble Model for CICIDS2017
Uses multiple algorithms for better performance
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

from src.core.ensemble_engine import EnsembleEngine
from src.core.intelligence_engine import FeatureEngine

# Paths
CICIDS_PATH = Path("data/raw/cicids2017_cleaned.csv")
MODEL_PATH = "ensemble_ids_model.pkl"
MAX_SAMPLES = 50000  # Limit for training speed

def load_cicids_data(path: Path, max_samples: int = None):
    """Load CICIDS2017 data"""
    print(f"[*] Loading CICIDS2017 data from {path}...")
    
    # Load in chunks
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
    return df

def prepare_features(df: pd.DataFrame, feature_ e: FeatureEngine):
    """Extract features from CICIDS2017 data"""
    print("[*] Extracting features...")
    
    features_list = []
    labels = []
    
    for idx, row in df.iterrows():
        try:
            # Create FlowData-like structure
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
                "syn": 0,
                "ack": 0,
                "rst": 0,
                "fin": 0,
                "unique_dst_ports": 0
            }
            
            # Create FlowData object
            from src.core.data_source import FlowData
            flow = FlowData(**flow_dict)
            
            # Extract features
            features = feature_engine.extract_features(flow)
            features_list.append(features)
            
            # Get label
            attack_type = row.get("Attack Type", "Normal Traffic")
            if attack_type and str(attack_type).lower() not in ["normal traffic", "normal", "benign"]:
                labels.append(1)  # Attack
            else:
                labels.append(0)  # Normal
            
        except Exception as e:
            print(f"[!] Error processing row {idx}: {e}")
            continue
    
    X = np.array(features_list, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)
    
    print(f"[*] Features shape: {X.shape}, Labels shape: {y.shape}")
    print(f"[*] Attack samples: {np.sum(y)}, Normal samples: {len(y) - np.sum(y)}")
    
    return X, y

def main():
    """Main training function"""
    print("=" * 60)
    print("CICIDS2017 Ensemble Model Training")
    print("=" * 60)
    
    # Load data
    if not CICIDS_PATH.exists():
        print(f"[ERROR] CICIDS2017 file not found: {CICIDS_PATH}")
        return
    
    df = load_cicids_data(CICIDS_PATH, max_samples=MAX_SAMPLES)
    
    # Prepare features
    feature_engine = FeatureEngine()
    X, y = prepare_features(df, feature_engine)
    
    # Split data
    print("[*] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"[*] Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Scale features
    print("[*] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train ensemble
    print("[*] Training ensemble model...")
    ensemble = EnsembleEngine()
    ensemble.train(X_train_scaled, y_train)
    
    # Evaluate
    print("[*] Evaluating model...")
    y_pred = []
    for x in X_test_scaled:
        result = ensemble.predict(x.reshape(1, -1))
        y_pred.append(result["is_attack"])
    
    y_pred = np.array(y_pred)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"TP: {tp}, TN: {tn}")
    print(f"FP: {fp}, FN: {fn}")
    print("=" * 60)
    
    # Save model
    ensemble.save(MODEL_PATH)
    joblib.dump(scaler, "ensemble_scaler.pkl")
    print(f"\n[+] Model saved: {MODEL_PATH}")
    print(f"[+] Scaler saved: ensemble_scaler.pkl")

if __name__ == "__main__":
    main()
