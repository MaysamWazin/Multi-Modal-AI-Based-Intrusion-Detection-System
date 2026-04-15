from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np

from sklearn.ensemble import IsolationForest
import joblib
import os

from src.data.database import init_db, insert_alert

MODEL_PATH = "ids_cnn_lstm.h5"
ANOMALY_MODEL_PATH = "anomaly_model.pkl"
THRESHOLD = 0.6

print("[*] CNN-LSTM modeli yükleniyor (API)...")
clf_model = load_model(MODEL_PATH)

anomaly_model = None
if os.path.exists(ANOMALY_MODEL_PATH):
    print("[*] Anomali modeli yükleniyor...")
    anomaly_model = joblib.load(ANOMALY_MODEL_PATH)
else:
    print("[!] Uyarı: anomaly_model.pkl bulunamadı, anomali skoru üretilemeyecek.")

init_db()

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    features = data.get("features", None)
    if features is None:
        return jsonify({"error": "features alanı gerekli"}), 400

    # --- CNN-LSTM saldırı tahmini ---
    x = np.array(features, dtype=float).reshape(1, 1, -1)
    prob = float(clf_model.predict(x, verbose=0)[0][0])
    pred = 1 if prob > THRESHOLD else 0

    # --- Anomali modeli ---
    anomaly_score = None
    is_anomaly = None
    if anomaly_model is not None:
        x_flat = np.array(features, dtype=float).reshape(1, -1)
        ia_pred = anomaly_model.predict(x_flat)[0]  # -1 = anomali, 1 = normal
        score = anomaly_model.decision_function(x_flat)[0]
        anomaly_score = float(score)
        is_anomaly = 1 if ia_pred == -1 else 0

    # Veritabanına logla (şimdilik attack_type unknown)
    insert_alert(
        sample_idx=-1,
        is_attack=pred,
        prob=prob,
        true_label=-1,
        attack_type="unknown",
    )

    return jsonify({
        "probability": prob,
        "is_attack": pred,
        "anomaly_score": anomaly_score,
        "is_anomaly": is_anomaly,
    }), 200


if __name__ == "__main__":
    app.run(port=8000, debug=True)
