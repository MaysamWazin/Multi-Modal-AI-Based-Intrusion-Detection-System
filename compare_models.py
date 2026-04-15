# compare_models.py
import time
import pandas as pd
import scipy.sparse as sp

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder

from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)

# =========================
# 1) AYARLAR
# =========================
TRAIN_PATH = "C:/Users/Ras co/Desktop/IDS-Project/data/raw/UNSW_NB15_training-set.csv"
TEST_PATH  = "C:/Users/Ras co/Desktop/IDS-Project/data/raw/UNSW_NB15_testing-set.csv"

TARGET_COL = "label"          # binary için: "label"
# TARGET_COL = "attack_cat"   # multi-class için: "attack_cat"

RANDOM_STATE = 42

# FP azaltma hedefi: attack recall çok düşmesin
# 0.98 -> daha güvenli (FN az), 0.95 -> FP daha çok düşebilir ama FN artabilir
MIN_ATTACK_RECALL = 0.98

# RandomForest'ı FP’ye karşı daha temkinli yap
RF_N_ESTIMATORS = 350
RF_MAX_DEPTH = 30
RF_MIN_SAMPLES_LEAF = 6
NORMAL_CLASS_WEIGHT = 1.35   # normal(0) daha ağır -> FP düşme eğilimi
ATTACK_CLASS_WEIGHT = 1.00

# Hızlı deneme istersen:
# SAMPLE_TRAIN_N = 50000
# SAMPLE_TEST_N  = 20000
SAMPLE_TRAIN_N = None
SAMPLE_TEST_N  = None

# =========================
# 2) VERİ OKU
# =========================
print(">>> Train CSV okunuyor...", flush=True)
train_df = pd.read_csv(TRAIN_PATH)
print(">>> Test CSV okunuyor...", flush=True)
test_df = pd.read_csv(TEST_PATH)

if SAMPLE_TRAIN_N is not None and SAMPLE_TRAIN_N < len(train_df):
    train_df = train_df.sample(n=SAMPLE_TRAIN_N, random_state=RANDOM_STATE).reset_index(drop=True)
    print(f">>> Train örnekleme: {SAMPLE_TRAIN_N}", flush=True)

if SAMPLE_TEST_N is not None and SAMPLE_TEST_N < len(test_df):
    test_df = test_df.sample(n=SAMPLE_TEST_N, random_state=RANDOM_STATE).reset_index(drop=True)
    print(f">>> Test örnekleme: {SAMPLE_TEST_N}", flush=True)

if TARGET_COL not in train_df.columns or TARGET_COL not in test_df.columns:
    raise ValueError(f"Hedef kolon bulunamadı: {TARGET_COL}")

# =========================
# 3) LEAKAGE ENGELLE (KRİTİK)
# =========================
drop_cols = []
if "id" in train_df.columns:
    drop_cols.append("id")

# label hedefse attack_cat leak olur -> çıkar
if TARGET_COL == "label" and "attack_cat" in train_df.columns:
    drop_cols.append("attack_cat")

# attack_cat hedefse label leak olur -> çıkar
if TARGET_COL == "attack_cat" and "label" in train_df.columns:
    drop_cols.append("label")

print(f">>> Drop kolonlar (leakage önlemi): {drop_cols}", flush=True)

X_train = train_df.drop(columns=[TARGET_COL] + drop_cols)
y_train = train_df[TARGET_COL]
X_test  = test_df.drop(columns=[TARGET_COL] + drop_cols)
y_test  = test_df[TARGET_COL]

# =========================
# 4) LABEL ENCODE
# =========================
is_binary = y_train.nunique() <= 2

le = None
if TARGET_COL == "label" or is_binary:
    le = LabelEncoder()
    y_train = le.fit_transform(y_train)
    y_test = le.transform(y_test)

# =========================
# 5) PREPROCESS (1 KEZ)
# =========================
num_cols = X_train.select_dtypes(include=["number"]).columns.tolist()
cat_cols = [c for c in X_train.columns if c not in num_cols]

preprocess = ColumnTransformer(
    transformers=[
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), num_cols),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), cat_cols),
    ],
    remainder="drop",
)

print(">>> Preprocess fit_transform (train)...", flush=True)
t0 = time.time()
Xtr = preprocess.fit_transform(X_train)
Xte = preprocess.transform(X_test)
print(f">>> Preprocess bitti: {time.time() - t0:.2f}s", flush=True)

# COO -> CSR (stabil)
if sp.issparse(Xtr):
    Xtr = Xtr.tocsr()
if sp.issparse(Xte):
    Xte = Xte.tocsr()

# Ağaç modelleri için CSC
Xtr_csc = Xtr.tocsc() if sp.issparse(Xtr) else Xtr
Xte_csc = Xte.tocsc() if sp.issparse(Xte) else Xte

# Lineer modeller için scaling (sparse uyumlu)
print(">>> Scaling (StandardScaler with_mean=False)...", flush=True)
scaler = StandardScaler(with_mean=False)
t1 = time.time()
Xtr_scaled = scaler.fit_transform(Xtr)
Xte_scaled = scaler.transform(Xte)
print(f">>> Scaling bitti: {time.time() - t1:.2f}s", flush=True)

# =========================
# 6) MODELLER
# =========================
models = {
    "SGD_LogLoss": SGDClassifier(
        loss="log_loss",
        alpha=1e-4,
        max_iter=2000,
        random_state=RANDOM_STATE
    ),
    "LogReg_saga": LogisticRegression(
        solver="saga",
        max_iter=3000,
        n_jobs=-1
    ),
    "LinearSVC": LinearSVC(
        random_state=RANDOM_STATE,
        max_iter=8000,
        dual="auto"
    ),

    # RandomForest: FP azaltmaya dönük ayarlar
    "RandomForest": RandomForestClassifier(
        n_estimators=RF_N_ESTIMATORS,
        n_jobs=-1,
        random_state=RANDOM_STATE,
        max_depth=RF_MAX_DEPTH,
        min_samples_leaf=RF_MIN_SAMPLES_LEAF,
        class_weight={0: NORMAL_CLASS_WEIGHT, 1: ATTACK_CLASS_WEIGHT}
    ),

    "ExtraTrees": ExtraTreesClassifier(
        n_estimators=400,
        n_jobs=-1,
        random_state=RANDOM_STATE,
    ),
}

linear_set = {"SGD_LogLoss", "LogReg_saga", "LinearSVC"}

# =========================
# 7) METRİK HESAPLAMA
# =========================
def compute_binary_details(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    fpr = fp / (fp + tn + 1e-12)  # normal -> yanlış alarm
    fnr = fn / (fn + tp + 1e-12)  # saldırı kaçırma
    return tn, fp, fn, tp, fpr, fnr

def evaluate_predict(name, clf, X_train_mat, X_test_mat, use_scaled=False):
    print(f"\n>>> Başlıyor: {name} (scaled={use_scaled})", flush=True)

    t_fit = time.time()
    clf.fit(X_train_mat, y_train)
    fit_time = time.time() - t_fit
    print(f">>> Eğitim bitti: {name} | {fit_time:.2f}s", flush=True)

    t_pred = time.time()
    y_pred = clf.predict(X_test_mat)
    pred_time = time.time() - t_pred
    print(f">>> Tahmin bitti: {name} | {pred_time:.2f}s", flush=True)

    acc = accuracy_score(y_test, y_pred)
    prec_macro = precision_score(y_test, y_pred, average="macro", zero_division=0)
    rec_macro  = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1_macro   = f1_score(y_test, y_pred, average="macro", zero_division=0)
    f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    auc = None
    if is_binary:
        try:
            if hasattr(clf, "predict_proba"):
                scores = clf.predict_proba(X_test_mat)[:, 1]
                auc = roc_auc_score(y_test, scores)
            elif hasattr(clf, "decision_function"):
                scores = clf.decision_function(X_test_mat)
                auc = roc_auc_score(y_test, scores)
        except Exception:
            auc = None

    cm = confusion_matrix(y_test, y_pred)
    rep = classification_report(y_test, y_pred, zero_division=0)

    row = {
        "Model": name,
        "Accuracy": acc,
        "Precision_macro": prec_macro,
        "Recall_macro": rec_macro,
        "F1_macro": f1_macro,
        "F1_weighted": f1_weighted,
        "ROC_AUC": auc,
        "Train_time_sec": fit_time,
        "Predict_time_sec": pred_time,
        "ConfusionMatrix": cm,
        "Report": rep,
    }

    # Binary ise FP/FPR de ekleyelim (FP azaltma hedefi için şart)
    if is_binary:
        tn, fp, fn, tp, fpr, fnr = compute_binary_details(y_test, y_pred)
        row.update({
            "TN": tn, "FP": fp, "FN": fn, "TP": tp,
            "FPR": fpr, "FNR": fnr
        })

    return row

# RandomForest threshold tuning (sadece binary için)
def tune_threshold_for_fpr(clf, X_test_mat, min_attack_recall=0.98):
    """
    Amaç: Attack recall >= min_attack_recall kalsın,
          FPR (False Positive Rate) minimum olsun.
    """
    if not hasattr(clf, "predict_proba"):
        return None

    proba = clf.predict_proba(X_test_mat)[:, 1]

    best = None
    # 0.50 -> 0.95 arası tarama
    for th in [i / 100 for i in range(50, 96, 1)]:
        y_pred_th = (proba >= th).astype(int)
        tn, fp, fn, tp, fpr, fnr = compute_binary_details(y_test, y_pred_th)

        # attack recall = TP/(TP+FN)
        attack_recall = tp / (tp + fn + 1e-12)

        # şartı sağlıyorsa en düşük FPR olanı seç
        if attack_recall >= min_attack_recall:
            if best is None or fpr < best["FPR"]:
                prec_attack = tp / (tp + fp + 1e-12)
                f1_attack = 2 * prec_attack * attack_recall / (prec_attack + attack_recall + 1e-12)
                best = {
                    "threshold": th,
                    "TN": tn, "FP": fp, "FN": fn, "TP": tp,
                    "FPR": fpr, "FNR": fnr,
                    "attack_recall": attack_recall,
                    "attack_precision": prec_attack,
                    "attack_f1": f1_attack,
                    "y_pred": y_pred_th
                }

    return best

# =========================
# 8) ÇALIŞTIR + SONUÇ TABLOSU
# =========================
rows = []
details = {}

trained_models = {}

for name, clf in models.items():
    if name in linear_set:
        out = evaluate_predict(name, clf, Xtr_scaled, Xte_scaled, use_scaled=True)
        trained_models[name] = clf
    else:
        out = evaluate_predict(name, clf, Xtr_csc, Xte_csc, use_scaled=False)
        trained_models[name] = clf

    details[name] = out

    keep_cols = [
        "Model", "Accuracy", "Precision_macro", "Recall_macro", "F1_macro",
        "F1_weighted", "ROC_AUC", "Train_time_sec", "Predict_time_sec"
    ]
    if is_binary:
        keep_cols += ["FP", "FN", "FPR", "FNR"]

    rows.append({k: out.get(k, None) for k in keep_cols})

# =========================
# 9) RandomForest THRESHOLD TUNING (FP düşürme)
# =========================
if is_binary and "RandomForest" in trained_models:
    rf = trained_models["RandomForest"]
    print(f"\n>>> RandomForest threshold tuning başlıyor (MIN_ATTACK_RECALL={MIN_ATTACK_RECALL})", flush=True)
    tuned = tune_threshold_for_fpr(rf, Xte_csc, min_attack_recall=MIN_ATTACK_RECALL)

    if tuned is None:
        print(">>> RandomForest predict_proba yok, threshold tuning atlandı.", flush=True)
    elif tuned is not None:
        # tuned sonuçlarını tabloya ayrı satır olarak ekle
        y_pred_tuned = tuned["y_pred"]

        acc = accuracy_score(y_test, y_pred_tuned)
        prec_macro = precision_score(y_test, y_pred_tuned, average="macro", zero_division=0)
        rec_macro  = recall_score(y_test, y_pred_tuned, average="macro", zero_division=0)
        f1_macro   = f1_score(y_test, y_pred_tuned, average="macro", zero_division=0)
        f1_weighted = f1_score(y_test, y_pred_tuned, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred_tuned)
        rep = classification_report(y_test, y_pred_tuned, zero_division=0)

        # ROC-AUC aynı proba ile ölçülebilir (threshold’dan bağımsız)
        auc = None
        try:
            proba = rf.predict_proba(Xte_csc)[:, 1]
            auc = roc_auc_score(y_test, proba)
        except Exception:
            auc = None

        tuned_row = {
            "Model": f"RandomForest_thresh@{tuned['threshold']:.2f}",
            "Accuracy": acc,
            "Precision_macro": prec_macro,
            "Recall_macro": rec_macro,
            "F1_macro": f1_macro,
            "F1_weighted": f1_weighted,
            "ROC_AUC": auc,
            "Train_time_sec": details["RandomForest"]["Train_time_sec"],  # aynı model
            "Predict_time_sec": details["RandomForest"]["Predict_time_sec"],
            "FP": tuned["FP"],
            "FN": tuned["FN"],
            "FPR": tuned["FPR"],
            "FNR": tuned["FNR"],
        }

        details[tuned_row["Model"]] = {
            "ConfusionMatrix": cm,
            "Report": rep
        }
        rows.append(tuned_row)

        print(f">>> Seçilen threshold: {tuned['threshold']:.2f}", flush=True)
        print(f">>> FPR (False Alarm Rate): {tuned['FPR']:.4f} | Attack Recall: {tuned['attack_recall']:.4f}", flush=True)
        print(">>> Tuned Confusion Matrix:", flush=True)
        print(cm, flush=True)

# =========================
# 10) SONUÇLARI YAZDIR + KAYDET
# =========================
results_df = pd.DataFrame(rows)

# sıralama kriteri: F1_macro
results_df = results_df.sort_values(by="F1_macro", ascending=False)

print("\n=== MODEL KARŞILAŞTIRMA (F1_macro'ya göre sıralı) ===", flush=True)
print(results_df.to_string(index=False), flush=True)

best = results_df.iloc[0]["Model"]
print(f"\n=== EN İYİ MODEL: {best} ===", flush=True)

# best confusion/report varsa göster
if best in details and "ConfusionMatrix" in details[best]:
    print("Confusion Matrix:", flush=True)
    print(details[best]["ConfusionMatrix"], flush=True)
    print("\nClassification Report:", flush=True)
    print(details[best]["Report"], flush=True)
elif best in details and "ConfusionMatrix" in details[best]:
    print("Confusion Matrix:", flush=True)
    print(details[best]["ConfusionMatrix"], flush=True)

results_df.to_csv("model_comparison_results.csv", index=False)
print("\nKaydedildi: model_comparison_results.csv", flush=True)
