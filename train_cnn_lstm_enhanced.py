"""
Enhanced CNN-LSTM Training Script
train.csv üzerinden model eğitimi yapar.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

from src.data.loader import prepare_unsw_train_test
from src.models.cnn_lstm_enhanced import build_cnn_lstm_enhanced, get_callbacks


def main():
    # CSV dosya yolları
    csv_dir = Path("CSV")
    train_path = csv_dir / "train.csv"
    test_path = csv_dir / "test.csv"
    
    # Eğer CSV/ klasöründe yoksa, data/raw/ altından al
    if not train_path.exists():
        train_path = Path("data/raw/UNSW_NB15_training-set.csv")
    if not test_path.exists():
        test_path = Path("data/raw/UNSW_NB15_testing-set.csv")
    
    print("=" * 60)
    print("ENHANCED CNN-LSTM MODEL TRAINING")
    print("=" * 60)
    print(f"Train CSV: {train_path}")
    print(f"Test CSV: {test_path}")
    print()
    
    # Verileri yükle
    print("[1/5] Veriler yükleniyor ve ön işleniyor...")
    try:
        X_train, X_test, y_train, y_test = prepare_unsw_train_test(
            str(train_path),
            str(test_path),
            label_col="label"
        )
        print(f"✓ Eğitim verisi: {X_train.shape}")
        print(f"✓ Test verisi: {X_test.shape}")
    except Exception as e:
        print(f"✗ Veri yükleme hatası: {e}")
        return
    
    # CNN-LSTM için reshape: (num_samples, time_steps, num_features)
    # time_steps = 1 (tek zaman adımı) veya sequence oluştur
    print("\n[2/5] Veriler CNN-LSTM formatına dönüştürülüyor...")
    
    # Seçenek 1: Tek zaman adımı (basit)
    time_steps = 1
    X_train_seq = X_train.reshape((X_train.shape[0], time_steps, X_train.shape[1]))
    X_test_seq = X_test.reshape((X_test.shape[0], time_steps, X_test.shape[1]))
    
    print(f"✓ Eğitim shape: {X_train_seq.shape}")
    print(f"✓ Test shape: {X_test_seq.shape}")
    
    # Model oluştur
    print("\n[3/5] Model oluşturuluyor...")
    input_shape = (X_train_seq.shape[1], X_train_seq.shape[2])
    model = build_cnn_lstm_enhanced(input_shape, num_classes=1)
    
    print("\nModel Özeti:")
    model.summary()
    
    # Sınıf ağırlıkları (dengesiz veri için)
    print("\n[4/5] Sınıf ağırlıkları hesaplanıyor...")
    classes = np.unique(y_train)
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y_train
    )
    class_weight_dict = {int(cls): float(w) for cls, w in zip(classes, class_weights)}
    print(f"✓ Sınıf ağırlıkları: {class_weight_dict}")
    
    # Callbacks
    model_path = "ids_cnn_lstm_enhanced.h5"
    callbacks = get_callbacks(model_path, patience=5)
    
    # Model eğitimi
    print("\n[5/5] Model eğitimi başlıyor...")
    print("-" * 60)
    
    history = model.fit(
        X_train_seq,
        y_train,
        epochs=20,  # İstersen artır
        batch_size=256,
        validation_data=(X_test_seq, y_test),
        class_weight=class_weight_dict,
        callbacks=callbacks,
        verbose=1
    )
    
    print("\n" + "=" * 60)
    print("EĞİTİM TAMAMLANDI")
    print("=" * 60)
    
    # Test seti üzerinde değerlendirme
    print("\n[EVALUATION] Test seti üzerinde değerlendirme...")
    y_pred_prob = model.predict(X_test_seq, verbose=0)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten()
    
    # Metrikler
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print("\n" + "-" * 60)
    print("PERFORMANCE METRICS")
    print("-" * 60)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:   {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print()
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred, digits=4))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Modeli kaydet
    model.save(model_path)
    print(f"\n✓ Model kaydedildi: {model_path}")
    
    # Metrikleri kaydet
    metrics_path = "training_metrics.txt"
    with open(metrics_path, "w", encoding="utf-8") as f:
        f.write("ENHANCED CNN-LSTM TRAINING METRICS\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Accuracy:  {accuracy:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall:   {recall:.4f}\n")
        f.write(f"F1 Score: {f1:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(classification_report(y_test, y_pred, digits=4))
        f.write("\n\nConfusion Matrix:\n")
        f.write(str(confusion_matrix(y_test, y_pred)))
    
    print(f"✓ Metrikler kaydedildi: {metrics_path}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
