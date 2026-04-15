from sklearn.utils.class_weight import compute_class_weight



from src.data.loader import prepare_unsw_train_test
from src.models.cnn_lstm import build_cnn_lstm

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

import numpy as np

import pandas as pd


def main():
    train_path = "data/raw/UNSW_NB15_training-set.csv"
    test_path = "data/raw/UNSW_NB15_testing-set.csv"

    print("Veriler yükleniyor ve ön işleniyor...")
    X_train, X_test, y_train, y_test = prepare_unsw_train_test(train_path, test_path)

    print("Veriler hazır!")
    print("Eğitim X shape:", X_train.shape)
    print("Test X shape:", X_test.shape)

    # CNN-LSTM için reshape: (num_samples, time_steps, num_features)
    # time_steps = 1 seçiyoruz
    X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
    X_test = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))

    print("Yeni eğitim X shape (CNN-LSTM):", X_train.shape)
    print("Yeni test X shape (CNN-LSTM):", X_test.shape)

    # Modeli oluştur
    input_shape = (X_train.shape[1], X_train.shape[2])  # (1, 44)
    model = build_cnn_lstm(input_shape)
    model.summary()

    # Sınıf ağırlıklarını hesapla (dengesiz veri için)
    classes = np.unique(y_train)
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y_train
    )
    class_weight_dict = {int(cls): w for cls, w in zip(classes, class_weights)}

    print("Sınıf ağırlıkları:", class_weight_dict)

    # Modeli eğit (class_weight ile)
    print("Model eğitimi başlıyor...")
    history = model.fit(
        X_train,
        y_train,
        epochs=5,             # istersen sonra artırırsın
        batch_size=256,
        validation_data=(X_test, y_test),
        class_weight=class_weight_dict,   # <-- FARKLI OLAN KISIM
        verbose=1
    )


    # Test seti üzerinde değerlendirme
    print("Model test setinde değerlendiriliyor...")
    y_pred_prob = model.predict(X_test)
    y_pred = (y_pred_prob > 0.6).astype(int)

    print("Sınıflandırma raporu:")
    print(classification_report(y_test, y_pred, digits=4))

    print("Karmaşıklık matrisi:")
    print(confusion_matrix(y_test, y_pred))

    # Modeli kaydet
    model.save("ids_cnn_lstm.h5")
    print("Model 'ids_cnn_lstm.h5' olarak kaydedildi.")


if __name__ == "__main__":
    main()


