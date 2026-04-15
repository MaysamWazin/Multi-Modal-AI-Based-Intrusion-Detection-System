print(">>> train_simple_ids.py ÇALIŞTI")

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

TRAIN_PATH = "data/raw/UNSW_NB15_training-set.csv"
TEST_PATH = "data/raw/UNSW_NB15_testing-set.csv"
MODEL_PATH = "simple_ids_rf.pkl"


def normalize_name(name: str) -> str:
    return str(name).strip().lower().replace(" ", "").replace("_", "")


def build_feature_mapper(df: pd.DataFrame):
    """
    DataFrame kolonlarını normalize edip bir sözlük oluşturuyor:
    normalize_adi -> gerçek kolon adı
    """
    mapper = {}
    for col in df.columns:
        norm = normalize_name(col)
        mapper[norm] = col
    return mapper


def get_num(row, mapper, keys, default=0.0) -> float:
    """
    keys: örn. {"srcip", "sourceip"}
    mapper: normalize_adi -> gerçek kolon adı
    """
    for k in keys:
        nk = normalize_name(k)
        if nk in mapper:
            real_col = mapper[nk]
            val = row.get(real_col, None)
            if val is None or (isinstance(val, float) and np.isnan(val)):
                continue
            try:
                return float(val)
            except Exception:
                continue
    return default


def get_str(row, mapper, keys, default="") -> str:
    for k in keys:
        nk = normalize_name(k)
        if nk in mapper:
            real_col = mapper[nk]
            val = row.get(real_col, None)
            if val is None:
                continue
            return str(val)
    return default


def ip_last_octet(ip: str) -> float:
    try:
        return float(str(ip).split(".")[-1])
    except Exception:
        return 0.0


def simple_features_from_row(row, mapper) -> np.ndarray:
    """
    UNSW satırından 8 boyutlu feature çıkarır.
    Kolon isimleri farklı olsa bile normalize ederek bulmaya çalışır.
    """

    # IP'ler
    src_ip_raw = get_str(row, mapper, {"srcip", "sourceip"})
    dst_ip_raw = get_str(row, mapper, {"dstip", "destip", "destinationip"})
    src_ip_last = ip_last_octet(src_ip_raw)
    dst_ip_last = ip_last_octet(dst_ip_raw)

    # Portlar
    sport = get_num(row, mapper, {"sport", "srcport", "sourceport"})
    dsport = get_num(row, mapper, {"dsport", "dstport", "destport", "destinationport"})

    # Protokol (şimdilik yoksa 0 geçeriz)
    proto = 0.0

    # Süre
    dur = get_num(row, mapper, {"dur", "duration"})

    # Baytlar
    sbytes = get_num(row, mapper, {"sbytes", "srcbytes"})
    dbytes = get_num(row, mapper, {"dbytes", "dstbytes", "destbytes"})
    total_bytes = sbytes + dbytes

    # Paket sayıları
    spkts = get_num(row, mapper, {"spkts", "srcpkts"})
    dpkts = get_num(row, mapper, {"dpkts", "dstpkts", "destpkts"})
    total_pkts = spkts + dpkts

    feats = np.array([
        src_ip_last,
        dst_ip_last,
        sport,
        dsport,
        proto,
        dur,
        total_bytes,
        total_pkts,
    ], dtype=float)

    return feats


def build_X_y_from_unsw(csv_path: str):
    print(f"[*] {csv_path} okunuyor...")
    df = pd.read_csv(csv_path)

    print("[*] İlk 10 kolon ismi:", list(df.columns)[:10])

    if "label" not in df.columns:
        raise ValueError("UNSW CSV içinde 'label' kolonu bulunamadı.")

    y = df["label"].astype(int).values

    mapper = build_feature_mapper(df)
    print("[*] Normalize kolon isimleri örnek:", list(mapper.keys())[:10])

    feats_list = []
    for i, (_, row) in enumerate(df.iterrows()):
        feats = simple_features_from_row(row, mapper)
        feats_list.append(feats)
        if i < 3:
            print(f"Örnek {i} feature:", feats)

    X = np.vstack(feats_list)
    return X, y


def main():
    if not os.path.exists(TRAIN_PATH):
        print(f"Training dosyası bulunamadı: {TRAIN_PATH}")
        return

    if not os.path.exists(TEST_PATH):
        print(f"Test dosyası bulunamadı: {TEST_PATH}")
        return

    print("[*] Training verisi hazırlanıyor...")
    X_train, y_train = build_X_y_from_unsw(TRAIN_PATH)
    print("  X_train shape:", X_train.shape)
    print("  y_train shape:", y_train.shape)

    print("[*] Test verisi hazırlanıyor...")
    X_test, y_test = build_X_y_from_unsw(TEST_PATH)
    print("  X_test shape:", X_test.shape)
    print("  y_test shape:", y_test.shape)

    print("[*] RandomForest modeli eğitiliyor...")
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=16,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    print("[*] Test setinde değerlendirme:")
    y_pred = clf.predict(X_test)
    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred, digits=4))

    joblib.dump(clf, MODEL_PATH)
    print(f"[+] Model kaydedildi: {MODEL_PATH}")


if __name__ == "__main__":
    main()
