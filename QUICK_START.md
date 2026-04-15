# 🚀 Hızlı Başlangıç Kılavuzu

## 1. Kurulum

```bash
# Virtual environment oluştur (önerilir)
python -m venv venv
venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

## 2. CSV Dosyalarını Hazırla

CSV klasörü otomatik oluşturulmuştur. Eğer yoksa:

```bash
# CSV klasörü oluştur
mkdir CSV

# Train ve test dosyalarını kopyala (eğer yoksa)
copy data\raw\UNSW_NB15_training-set.csv CSV\train.csv
copy data\raw\UNSW_NB15_testing-set.csv CSV\test.csv
```

## 3. Model Eğitimi (Opsiyonel)

### RandomForest Modeli
```bash
python train_simple_ids.py
```

### CNN-LSTM Modeli (Enhanced)
```bash
python train_cnn_lstm_enhanced.py
```

**Not**: Model dosyaları yoksa sistem fallback mekanizması ile çalışır.

## 4. Sistemi Başlat

```bash
python intelligent_ids.py
```

Sistem varsayılan olarak **DATASET** modunda başlar (sunum için uygun).

## 5. Dashboard'a Eriş

Tarayıcıda aç:
```
http://127.0.0.1:8000/dashboard
```

## 6. Mod Değiştir

Dashboard üzerinden:
- **📡 LIVE**: Canlı Wi-Fi trafik (admin yetkisi gerekir)
- **📊 DATASET**: CSV test verisi (sunum için ideal)
- **▶️ REPLAY**: CSV canlı simülasyon

## 7. Akademik Metrikleri Hesapla

```bash
python evaluate_metrics.py
```

Metrikler konsola yazdırılır ve `evaluation_metrics.json` dosyasına kaydedilir.

---

## ⚡ Hızlı Test

1. Sistemi başlat: `python intelligent_ids.py`
2. Dashboard'u aç: `http://127.0.0.1:8000/dashboard`
3. DATASET modunda event'ler otomatik görünecek
4. REPLAY moduna geçerek canlı simülasyon izle

---

## 🎯 Sunum İçin Öneriler

- **DATASET Mode**: Kontrollü test senaryoları göster
- **REPLAY Mode**: Canlı simülasyon göster
- Dashboard'da metrikleri ve event timeline'ı göster
- Attack detection örnekleri göster

---

## ❓ Sorun Giderme

### Model dosyaları bulunamıyor
- Sistem fallback ile çalışır, sorun değil
- Model eğitimi yaparak daha iyi sonuçlar alabilirsin

### CSV dosyaları bulunamıyor
- `data/raw/` altındaki UNSW-NB15 dosyaları otomatik kullanılır
- Veya `CSV/` klasörüne train.csv ve test.csv ekle

### Dashboard boş görünüyor
- DATASET veya REPLAY moduna geç
- Event'ler birkaç saniye içinde görünecek

---

**🛡️ Intelligent IDS - Hızlı Başlangıç**
