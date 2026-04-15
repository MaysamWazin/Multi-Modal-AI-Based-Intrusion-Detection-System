import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

INPUT_PATH = "data/recorded/live_baseline.csv"
MODEL_PATH = "anomaly_model.pkl"

def main():
    if not os.path.exists(INPUT_PATH):
        print("Önce record_live_baseline.py ile veri kaydetmelisin.")
        return

    X = np.loadtxt(INPUT_PATH, delimiter=",")
    print("Veri shape:", X.shape)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,  # verinin yaklaşık %5'i anomali varsayımı
        random_state=42,
    )
    model.fit(X)

    joblib.dump(model, MODEL_PATH)
    print(f"[+] Anomali modeli kaydedildi: {MODEL_PATH}")

if __name__ == "__main__":
    main()
