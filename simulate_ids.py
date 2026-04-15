import time
from datetime import datetime

import numpy as np
from tensorflow.keras.models import load_model

from src.data.loader import prepare_unsw


def run_simulation(
    data_path="data/raw/UNSW_NB15_testing-set.csv",
    model_path="ids_cnn_lstm.h5",
    threshold=0.6,
    delay=0.002,
):
    """
    IDS simülasyonu: Test verisini sanki ağdan geliyormuş gibi satır satır işler.
    """
    print("[*] Veri yükleniyor ve ön işleniyor...")
    X, y = prepare_unsw(data_path)
    X = X.reshape((X.shape[0], 1, X.shape[1]))

    print("[*] Model yükleniyor...")
    model = load_model(model_path)

    print("[*] Simülasyon başlıyor...")
    print(f"Toplam kayıt sayısı: {len(y)}")
    print(f"Kullanılan eşik değeri (threshold): {threshold}")
    print("-" * 60)

    for i in range(len(y)):
        sample = X[i : i + 1]  # tek kayıt
        prob = float(model.predict(sample, verbose=0)[0][0])
        pred = 1 if prob > threshold else 0
        true_label = int(y[i])

        now = datetime.now().strftime("%H:%M:%S")

        if pred == 1:
            status = "ALERT: SALDIRI TESPİT EDİLDİ"
        else:
            status = "NORMAL TRAFİK"

        print(
            f"[{now}] idx={i:6d}  tahmin={pred}  gerçek={true_label}  "
            f"olasılık={prob:.3f}  -> {status}"
        )

        # Demo için bekleme süresi (akışı yavaşlatmak için)
        time.sleep(delay)

    print("[*] Simülasyon bitti.")


if __name__ == "__main__":
    run_simulation()
