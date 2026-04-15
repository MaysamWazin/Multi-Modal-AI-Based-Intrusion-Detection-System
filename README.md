# 🛡️ Intelligent IDS - Akıllı Saldırı Tespit Sistemi

**Multi-Source Intelligent Intrusion Detection System**

Bu proje, veri kaynağından bağımsız, akıllı bir saldırı tespit sistemi (IDS) sunar. Sistem, canlı Wi-Fi trafiği, CSV dataset'leri ve CSV replay modlarını destekleyerek, offline training ve online inference mimarisi ile çalışır.

---

## 📋 İçindekiler

- [Özellikler](#özellikler)
- [Mimari](#mimari)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Akademik Değerlendirme](#akademik-değerlendirme)
- [Proje Yapısı](#proje-yapısı)
- [Teknik Detaylar](#teknik-detaylar)

---

## ✨ Özellikler

### 🎯 Ana Özellikler

- **Multi-Source Architecture**: Canlı trafik, CSV dataset ve CSV replay desteği
- **Intelligent Core Engine**: Feature Engineering → Time-Series Buffer → ML/DL Inference → Decision Engine pipeline
- **Hybrid ML/DL Approach**: RandomForest (ML) + CNN-LSTM (Deep Learning) ensemble
- **Real-time Dashboard**: Modern, responsive web arayüzü
- **Academic Metrics**: Accuracy, Precision, Recall, F1 Score hesaplama
- **Rule-based Detection**: Port scan, SYN flood, DDoS tespiti
- **Attack Classification**: Saldırı tipi belirleme ve severity seviyesi

### 🔄 Çalışma Modları

1. **LIVE Mode**: Canlı Wi-Fi trafik dinleme ve analiz
2. **DATASET Mode**: CSV test verisi üzerinden offline değerlendirme
3. **REPLAY Mode**: CSV verisini canlı simülasyon olarak oynatma

---

## 🏗️ Mimari

### Veri Kaynağından Bağımsız Mimari

```
┌─────────────────────────────────────────────────────────┐
│              Data Source Layer                           │
├─────────────────────────────────────────────────────────┤
│  Live Wi-Fi  │  CSV Dataset  │  CSV Replay             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│           Normalized Flow Format                         │
│     (Tek ve ortak flow/feature formatı)                 │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│         Intelligent Core Engine                          │
├─────────────────────────────────────────────────────────┤
│  1. Feature Engineering                                 │
│  2. Time-Series Buffer                                  │
│  3. ML Inference (RandomForest)                         │
│  4. DL Inference (CNN-LSTM)                             │
│  5. Anomaly Detection                                   │
│  6. Rule Engine                                         │
│  7. Decision Engine                                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Decision Output                             │
│  • is_attack                                            │
│  • attack_type                                          │
│  • confidence                                           │
│  • severity                                             │
│  • explanation                                          │
└─────────────────────────────────────────────────────────┘
```

### CNN-LSTM Model Mimarisi

```
Input (time_steps, features)
    ↓
Conv1D (64 filters, kernel=3) → BatchNorm → Dropout
    ↓
Conv1D (128 filters, kernel=5) → BatchNorm → Dropout
    ↓
Conv1D (128 filters, kernel=3) → BatchNorm
    ↓
    ├─→ GlobalMaxPooling1D ──┐
    │                         │
    └─→ LSTM (128) ───────────┼─→ Feature Fusion
         ↓                     │
    LSTM (64) ─────────────────┘
         ↓
    Dense (128) → BatchNorm → Dropout
         ↓
    Dense (64) → Dropout
         ↓
    Output (sigmoid)
```

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.8+
- Windows 10/11 (Windows toast bildirimleri için)
- Admin yetkisi (Wi-Fi sniffing için)

### Adımlar

1. **Repository'yi klonlayın veya indirin**

2. **Virtual environment oluşturun** (önerilir)
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Bağımlılıkları yükleyin**
```bash
pip install -r requirements.txt
```

4. **CSV klasörünü hazırlayın**
   - `CSV/train.csv` - Model eğitimi için
   - `CSV/test.csv` - Test ve değerlendirme için
   
   Eğer CSV klasörü yoksa, `data/raw/` altındaki UNSW-NB15 dosyaları otomatik kullanılacaktır.

---

## 📖 Kullanım

### 1. Model Eğitimi

#### RandomForest Modeli
```bash
python train_simple_ids.py
```

#### CNN-LSTM Modeli (Enhanced)
```bash
python train_cnn_lstm_enhanced.py
```

### 2. Ana Sistem Başlatma

```bash
python intelligent_ids.py
```

Sistem varsayılan olarak **DATASET** modunda başlar (sunum için uygun).

### 3. Dashboard Erişimi

Tarayıcıda açın:
```
http://127.0.0.1:8000/dashboard
```

### 4. Mod Değiştirme

Dashboard üzerinden veya API ile:
```bash
# LIVE moduna geç
curl -X POST http://127.0.0.1:8000/mode/LIVE

# DATASET moduna geç
curl -X POST http://127.0.0.1:8000/mode/DATASET

# REPLAY moduna geç
curl -X POST http://127.0.0.1:8000/mode/REPLAY
```

### 5. Akademik Metrikleri Hesaplama

```bash
python evaluate_metrics.py
```

Metrikler konsola yazdırılır ve `evaluation_metrics.json` dosyasına kaydedilir.

---

## 📊 Akademik Değerlendirme

### Metrikler

Sistem aşağıdaki metrikleri hesaplar:

- **Accuracy**: Genel doğruluk oranı
- **Precision**: Pozitif tahminlerin doğruluğu
- **Recall**: Gerçek pozitiflerin tespit oranı
- **F1 Score**: Precision ve Recall'un harmonik ortalaması
- **Confusion Matrix**: Detaylı sınıflandırma matrisi

### Test Senaryosu

1. `test.csv` dosyası yüklenir
2. Her flow için tahmin yapılır
3. Gerçek label'lar ile karşılaştırılır
4. Metrikler hesaplanır ve raporlanır

---

## 📁 Proje Yapısı

```
IDS-Project/
├── CSV/                          # CSV dataset klasörü
│   ├── train.csv                 # Eğitim verisi
│   └── test.csv                  # Test verisi
├── src/
│   ├── core/                     # Core intelligence engine
│   │   ├── data_source.py        # Veri kaynağı katmanı
│   │   └── intelligence_engine.py # Akıllı zeka motoru
│   ├── models/                   # ML/DL modelleri
│   │   ├── cnn_lstm.py           # Basit CNN-LSTM
│   │   └── cnn_lstm_enhanced.py  # Geliştirilmiş CNN-LSTM
│   ├── flows/                    # Flow işleme
│   │   ├── features.py           # Feature extraction
│   │   └── flow_aggregator.py    # Flow aggregation
│   ├── data/                     # Veri işleme
│   │   ├── loader.py             # CSV loader
│   │   ├── preprocess.py         # Ön işleme
│   │   └── database.py           # Veritabanı
│   └── evaluation/              # Değerlendirme
│       └── metrics_calculator.py # Metrik hesaplama
├── intelligent_ids.py           # Ana sistem
├── intelligent_ids_dashboard.py  # Dashboard template
├── train_cnn_lstm_enhanced.py   # CNN-LSTM eğitim
├── evaluate_metrics.py          # Metrik hesaplama scripti
├── requirements.txt              # Python bağımlılıkları
└── README.md                     # Bu dosya
```

---

## 🔧 Teknik Detaylar

### Offline Training + Online Inference

- **Training**: `train.csv` üzerinden modeller eğitilir
- **Inference**: Canlı trafik veya test verisi üzerinden tahmin yapılır
- **Hybrid Approach**: ML ve DL modelleri birlikte kullanılır

### Zaman Serisi Analizi

- **Time-Series Buffer**: Son N flow'u buffer'da tutar
- **Sequence Generation**: CNN-LSTM için sequence oluşturur
- **Temporal Patterns**: Zaman serisi bağımlılıklarını yakalar

### Feature Engineering

8 temel feature:
1. Source IP son okteti
2. Destination IP son okteti
3. Source port
4. Destination port
5. Protocol (normalize edilmiş)
6. Duration
7. Total bytes
8. Total packets

### Rule Engine

- **Port Scan Detection**: Çok sayıda farklı port
- **SYN Flood Detection**: Yüksek SYN paket sayısı
- **DDoS Detection**: Çok yüksek paket hızı
- **RST Spike Detection**: Anormal RST paket sayısı

---

## 🎓 Akademik & Endüstriyel Dil

### Kullanılan Terimler

- **Multi-Source Intelligent IDS**: Çoklu kaynaklı akıllı IDS
- **Offline Training + Online Inference**: Çevrimdışı eğitim, çevrimiçi çıkarım
- **Time-Series Analysis**: Zaman serisi analizi
- **CNN-LSTM Integration**: Evrişimli sinir ağı ve LSTM entegrasyonu
- **Hybrid ML/DL Approach**: Hibrit makine öğrenmesi ve derin öğrenme yaklaşımı
- **Real-time & Test Scenarios**: Gerçek zamanlı ve test senaryoları

### Sunum İçin Öneriler

1. **DATASET Mode**: Kontrollü test senaryoları için
2. **REPLAY Mode**: Canlı simülasyon gösterimi için
3. **LIVE Mode**: Gerçek zamanlı trafik analizi için

---

## 📝 Notlar

- Sistem, model dosyalarının yokluğunda da çalışır (fallback mekanizması)
- Windows toast bildirimleri için `winotify` gerekir (opsiyonel)
- Wi-Fi sniffing için admin yetkisi gerekir
- CSV dosyaları otomatik algılanır ve normalize edilir

---

## 🔮 Gelecek Geliştirmeler

- [ ] Daha fazla saldırı tipi desteği
- [ ] AutoML entegrasyonu
- [ ] Distributed processing
- [ ] Cloud deployment
- [ ] Mobile app

---

## 📄 Lisans

Bu proje akademik/araştırma amaçlıdır.

---

## 👥 Katkıda Bulunanlar

Proje geliştiricileri tarafından oluşturulmuştur.

---

**🛡️ Intelligent IDS - Akıllı Saldırı Tespit Sistemi**
