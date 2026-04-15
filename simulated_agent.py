import time
import requests
from src.data.loader import prepare_unsw

API_URL = "http://127.0.0.1:8000/predict"
DATA_PATH = "data/raw/UNSW_NB15_testing-set.csv"

print("[*] Veri yükleniyor ve ön işleniyor...")
X_raw, y_raw = prepare_unsw(DATA_PATH)
n_samples = X_raw.shape[0]
print(f"[*] Toplam kayıt: {n_samples}")

# Saldırı olan indexleri bul
attack_indices = [i for i, lbl in enumerate(y_raw) if lbl == 1]
print(f"[*] Toplam saldırı sayısı: {len(attack_indices)}")

# Çok uzun sürmesin diye ilk 100 saldırıya bakalım
attack_indices = attack_indices[:100]

correct = 0
total = len(attack_indices)

for i in attack_indices:
    features = X_raw[i].tolist()
    true_label = int(y_raw[i])   # burada hep 1 olacak zaten

    try:
        res = requests.post(API_URL, json={"features": features})
        out = res.json()

        pred = out.get("is_attack")
        prob = out.get("probability")

        if pred == 1:
            correct += 1

        print(
            f"[{i:05d}] true={true_label}  pred={pred}  prob={prob:.3f}"
        )

    except Exception as e:
        print(f"[{i}] Hata: {e}")

    time.sleep(0.05)

print("\n--- SALDIRI ÖZETİ ---")
print(f"İncelenen saldırı kaydı sayısı : {total}")
print(f"Modelin saldırı diyebildiği    : {correct}")
print(f"Başarı oranı (attack recall)   : {correct/total:.3f}")
