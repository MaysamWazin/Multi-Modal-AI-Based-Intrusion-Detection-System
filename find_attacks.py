from src.data.loader import prepare_unsw

DATA_PATH = "data/raw/UNSW_NB15_testing-set.csv"

X_raw, y_raw = prepare_unsw(DATA_PATH)

attack_indices = [i for i, lbl in enumerate(y_raw) if lbl == 1]

print("Toplam saldırı sayısı:", len(attack_indices))
print("İlk 50 saldırı indexi:", attack_indices[:50])
