# 4. UYGULAMA VE GERÇEKLEŞTİRİM

Bu bölüm, geliştirilen akıllı saldırı tespit sisteminin teknik implementasyonu, kullanılan teknolojiler, kod yapısı, arayüz tasarımı, sistem entegrasyonu ve çalışma yapısını detaylı bir şekilde açıklar.

---

## 4.1. Kullanılan Teknolojiler

Sistem geliştirme sürecinde modern ve güvenilir teknolojiler seçilmiştir. Aşağıda kullanılan teknolojiler ve amaçları listelenmektedir:

### 4.1.1. Programlama Dili ve Platform

**Python 3.8+**
- **Amaç**: Ana programlama dili
- **Neden Seçildi**: 
  - Zengin kütüphane ekosistemi (machine learning, network analysis)
  - Hızlı prototipleme imkanı
  - Topluluk desteği
  - Cross-platform uyumluluk
- **Kullanım Alanları**: Tüm sistem modülleri, API sunucusu, veri işleme, model eğitimi

### 4.1.2. Web Framework ve API Geliştirme

**Flask 2.x**
- **Amaç**: RESTful API sunucusu ve web dashboard
- **Kullanım Alanları**:
  - REST API endpoint'leri (`/dashboard`, `/events`, `/ingest/flows`, `/stats`, `/mode`)
  - HTML template rendering (`render_template_string`)
  - JSON response handling (`jsonify`)
  - Multi-threaded request handling (`threaded=True`)
- **Seçim Nedeni**: Hafif, esnek, minimal setup gereksinimi

### 4.1.3. Makine Öğrenmesi ve Derin Öğrenme Kütüphaneleri

**scikit-learn (sklearn)**
- **Versiyon**: 1.7.2
- **Kullanım Alanları**:
  - RandomForestClassifier (makine öğrenmesi modeli)
  - GradientBoostingClassifier, ExtraTreesClassifier, SVM, LogisticRegression, MLPClassifier (ensemble modelleri)
  - VotingClassifier (ensemble mekanizması)
  - StandardScaler, LabelEncoder (veri ön işleme)
  - Accuracy, Precision, Recall, F1 Score hesaplamaları
  - Confusion Matrix oluşturma
- **Amaç**: Klasik makine öğrenmesi algoritmaları ve metrik hesaplama

**TensorFlow / Keras**
- **Versiyon**: TensorFlow 2.x
- **Kullanım Alanları**:
  - CNN-LSTM derin öğrenme modeli mimarisi
  - Model eğitimi ve kaydetme (`.h5` formatı)
  - Model yükleme ve inference
  - Callback'ler (EarlyStopping, ModelCheckpoint, ReduceLROnPlateau)
- **Amaç**: Zaman serisi tabanlı derin öğrenme tespiti

**NumPy**
- **Amaç**: Sayısal hesaplamalar, array işlemleri
- **Kullanım**: Feature vektörleri, matematiksel işlemler

**Pandas**
- **Amaç**: Veri manipülasyonu ve analizi
- **Kullanım**: CSV okuma/yazma, DataFrame işlemleri, veri preprocessing

**Joblib**
- **Amaç**: Model serialization (`.pkl` formatı)
- **Kullanım**: RandomForest ve ensemble model kaydetme/yükleme

### 4.1.4. Ağ Analizi ve Paket Yakalama

**Scapy**
- **Versiyon**: 2.6.1
- **Amaç**: Canlı ağ trafiği yakalama ve analiz
- **Kullanım Alanları**:
  - Wi-Fi interface'lerinde paket sniffing (`sniff()`)
  - IP, TCP, UDP, ICMP paket ayrıştırma
  - Flow bilgisi çıkarımı (IP, port, protokol, flags)
- **Modüller**: `scapy.all` (IP, TCP, UDP, ICMP, sniff, IFACES)

### 4.1.5. Veritabanı

**SQLite**
- **Amaç**: Olay kayıtları ve alert saklama
- **Kullanım**:
  - `sqlite3` Python modülü (Python standart kütüphanesi)
  - Tablolar: `alerts`, `live_events`
- **Neden Seçildi**: Dosya tabanlı, setup gerektirmez, hafif

### 4.1.6. Görselleştirme ve Analiz

**Matplotlib**
- **Amaç**: Akademik şekiller ve grafikler
- **Kullanım**: Confusion matrix, metrik grafikleri, dağılım grafikleri

**Seaborn**
- **Amaç**: İstatistiksel veri görselleştirme
- **Kullanım**: Heatmap'ler, distribution grafikleri

### 4.1.7. Sistem Bildirimleri

**winotify**
- **Amaç**: Windows işletim sistemi toast bildirimleri
- **Kullanım**: Yüksek risk saldırılarında kullanıcı bildirimi
- **Özellikler**: Ses desteği, otomatik kapanma

### 4.1.8. İletişim ve Entegrasyon

**Requests**
- **Amaç**: HTTP istekleri (agent → API iletişimi)
- **Kullanım**: Agent'ların API'ye flow gönderme

### 4.1.9. Frontend Teknolojileri

**HTML5 / CSS3 / JavaScript (Vanilla)**
- **Amaç**: Web dashboard arayüzü
- **Özellikler**:
  - Responsive tasarım (CSS Grid, Flexbox)
  - Real-time güncelleme (JavaScript `fetch` API, `setInterval`)
  - CSS Animations (cybersecurity background animasyonları)
  - SVG animasyonları (network lines, security icons)
- **Framework**: Vanilla JavaScript (dış kütüphane yok)

### 4.1.10. Geliştirme Ortamı ve Araçlar

**Git**
- **Amaç**: Versiyon kontrolü

**Python Virtual Environment (venv)**
- **Amaç**: Bağımlılık izolasyonu

**Requirements.txt**
- **İçerik**: Proje bağımlılıkları
  ```
  numpy
  pandas
  scikit-learn
  tensorflow
  matplotlib
  seaborn
  xgboost
  joblib
  flask
  scapy
  winotify
  requests
  ```

---

## 4.2. Kod Yapısı

Sistem, modüler ve sürdürülebilir bir kod yapısına sahiptir. Proje, katmanlı mimari (layered architecture) prensiplerine uygun olarak geliştirilmiştir.

### 4.2.1. Proje Klasör Yapısı

```
IDS-Project/
├── intelligent_ids.py              # Ana sistem giriş noktası
├── intelligent_ids_dashboard.py    # Dashboard HTML template
├── src/                            # Ana proje modülleri
│   ├── core/                       # Çekirdek motor
│   │   ├── intelligence_engine.py  # Intelligence Engine (çekirdek motor)
│   │   ├── data_source.py          # Veri kaynağı abstract layer
│   │   ├── ensemble_engine.py      # Ensemble model yönetimi
│   │   └── multiclass_inference.py # Multi-class inference
│   ├── data/                       # Veri işleme
│   │   ├── database.py             # SQLite veritabanı işlemleri
│   │   ├── loader.py               # CSV yükleme ve preprocessing
│   │   ├── preprocess.py           # Veri ön işleme fonksiyonları
│   │   └── simple_features.py      # Canlı trafik feature çıkarımı
│   ├── flows/                      # Flow işleme
│   │   ├── flow_aggregator.py      # Paket → Flow birleştirme
│   │   └── features.py             # Flow feature veri yapısı
│   ├── models/                     # Model tanımları
│   │   ├── cnn_lstm.py             # CNN-LSTM model mimarisi
│   │   └── cnn_lstm_enhanced.py    # Geliştirilmiş CNN-LSTM
│   └── evaluation/                 # Metrik hesaplama
│       └── metrics_calculator.py   # Akademik metrikler
├── agent/                          # Canlı trafik agent'ları
│   └── live_agent_flow.py          # Flow-based agent
├── data/                           # Veri dosyaları
│   ├── raw/                        # Ham CSV veri setleri
│   ├── db/                         # SQLite veritabanı dosyaları
│   └── recorded/                   # Kaydedilmiş trafik
├── CSV/                            # İşlenmiş CSV dosyaları
│   ├── train.csv
│   └── test.csv
├── logs/                           # Log dosyaları
│   └── alerts.log
├── poster_visuals/                 # Akademik görseller
├── train_*.py                      # Model eğitim scriptleri
└── requirements.txt                # Python bağımlılıkları
```

### 4.2.2. Ana Modüller ve Sınıflar

#### 4.2.2.1. Ana Sistem (`intelligent_ids.py`)

**Dosya Boyutu**: 878 satır

**Ana Bileşenler**:
- **Flask Application**: `app = Flask(__name__)`
- **Global State**: 
  - `intelligence_engine`: IntelligenceEngine instance
  - `data_source`: DataSource instance (LiveWiFiSource, CSVDatasetSource, CSVReplaySource)
  - `CURRENT_MODE`: Sistem modu (DATASET_INTELLIGENCE, SIMULATED_LIVE, REAL_NETWORK)
  - `EVENTS_*`: Mod bazlı event listeleri
  - `METRICS`: Performans metrikleri dictionary'si

**API Endpoint'leri**:
```python
@app.route("/")                    # Ana sayfa
@app.route("/dashboard")           # Dashboard HTML
@app.route("/mode/<mode>", methods=["POST"])  # Mod değiştirme
@app.route("/mode", methods=["GET"])          # Mevcut mod
@app.route("/events", methods=["GET"])        # Event listesi
@app.route("/stats", methods=["GET"])         # İstatistikler
@app.route("/metrics", methods=["GET"])       # Performans metrikleri
@app.route("/progress", methods=["GET"])      # İşlem ilerlemesi
@app.route("/ingest/flows", methods=["POST"]) # Flow ingestion
```

**Ana Fonksiyonlar**:
- `initialize()`: Sistem başlatma
- `start_data_source(mode)`: Veri kaynağı başlatma
- `process_flow(flow, source_type)`: Flow işleme
- `calculate_streaming_metrics()`: Streaming metrik hesaplama

**Threading**:
- `data_source_thread`: Veri kaynağı işleme thread'i (arka plan)
- `threaded=True`: Flask multi-threaded request handling

#### 4.2.2.2. Intelligence Engine (`src/core/intelligence_engine.py`)

**Dosya Boyutu**: ~638 satır

**Ana Sınıflar**:

1. **RollingConfidenceBuffer**
   - Amaç: Confidence skorlarını yumuşatma (smoothing)
   - Özellikler: Rolling window (varsayılan: 20)

2. **FeatureEngine**
   - Amaç: Flow verisini 44 boyutlu feature vektörüne çevirme
   - Metodlar:
     - `extract_features(flow: FlowData) -> np.ndarray`: Feature çıkarımı
     - Feature isimleri: `["src_ip_last", "dst_ip_last", "sport", "dsport", "proto", "dur", "total_bytes", "total_pkts", ...]` (44 özellik)

3. **RuleEngine**
   - Amaç: Kural tabanlı saldırı tespiti
   - Tespit Edilen Saldırılar:
     - Port Scan: `unique_dst_ports > 5`
     - SYN Flood: `syn > 10 and packets_fwd > syn * 0.8`
     - DDoS: `packets_fwd > 100 and duration < 1.0`
   - Risk Seviyesi Belirleme:
     - `low`: Normal trafik
     - `medium`: Şüpheli pattern'ler
     - `high`: Açık saldırı belirtileri

4. **MLInference**
   - Amaç: RandomForest modeli ile tahmin
   - Model Yükleme: `joblib.load(ML_MODEL_PATH)`
   - Inference: `model.predict_proba(features)[0][1]`
   - Confidence: `probability`

5. **DLInference**
   - Amaç: CNN-LSTM modeli ile tahmin
   - Model Yükleme: `tensorflow.keras.models.load_model(DL_MODEL_PATH)`
   - Inference: `model.predict(features_reshaped)[0][0]`
   - Input Shape: `(1, 1, 44)` (time_steps=1, features=44)

6. **DecisionEngine**
   - Amaç: Rule-based ve AI-based sonuçları birleştirme
   - Karar Mantığı:
     ```python
     if rule_risk == "high":
         final_risk = "high"
         confidence = max(ml_prob, dl_prob)
     elif rule_risk == "medium":
         final_risk = "medium" if avg_prob > 0.5 else "low"
     else:
         final_risk = "high" if avg_prob > 0.7 else "low"
     ```

7. **IntelligenceEngine**
   - Amaç: Tüm pipeline'ı yöneten ana sınıf
   - Pipeline:
     ```
     FlowData → FeatureEngine → ML/DL Inference → RuleEngine → DecisionEngine → Output
     ```
   - Metodlar:
     - `process_flow(flow: FlowData) -> dict`: Flow işleme ve tahmin

#### 4.2.2.3. Data Source (`src/core/data_source.py`)

**Dosya Boyutu**: ~803 satır

**Ana Sınıflar**:

1. **FlowData** (Dataclass)
   - Amaç: Normalize edilmiş flow veri formatı
   - Alanlar:
     - `src_ip`, `dst_ip`, `src_port`, `dst_port`, `proto`
     - `duration`, `packets_fwd`, `packets_bwd`, `bytes_fwd`, `bytes_bwd`
     - `syn`, `ack`, `rst`, `fin`, `unique_dst_ports`
     - `timestamp`, `label`, `attack_type`

2. **DataSource** (Abstract Base Class)
   - Amaç: Veri kaynağından bağımsız interface
   - Metodlar:
     - `__iter__()`: Iterator protocol
     - `__next__() -> FlowData`: Sonraki flow'u döndürme

3. **LiveWiFiSource**
   - Amaç: Canlı Wi-Fi trafik kaynağı
   - Teknoloji: Scapy (`sniff()`)
   - Entegrasyon: FlowAggregator ile paketleri flow'lara birleştirme
   - Thread: Arka plan thread'inde çalışır

4. **CSVDatasetSource**
   - Amaç: CSV dataset kaynağı (offline evaluation)
   - Veri Formatı: UNSW-NB15, CICIDS2017 uyumlu
   - İşlem: Satır satır okuma, FlowData'ya dönüştürme

5. **CSVReplaySource**
   - Amaç: CSV verisini canlı simülasyon olarak oynatma
   - Özellik: Time delay ile gerçekçi simülasyon (1 event/saniye)

#### 4.2.2.4. Flow Aggregator (`src/flows/flow_aggregator.py`)

**Dosya Boyutu**: ~174 satır

**Ana Sınıflar**:

1. **FlowState** (Dataclass)
   - Amaç: Flow durumunu takip etme
   - Alanlar:
     - `key`: `(src_ip, dst_ip, src_port, dst_port, proto)` tuple
     - `start_ts`, `last_ts`: Zaman damgaları
     - `packets_fwd`, `packets_bwd`, `bytes_fwd`, `bytes_bwd`
     - `syn`, `ack`, `rst`, `fin`
     - `dst_ports_seen`: Set[int]

2. **FlowAggregator**
   - Amaç: Paketleri flow'lara birleştirme
   - Parametreler:
     - `window_sec`: Aggregation window (varsayılan: 5 saniye)
     - `idle_timeout_sec`: Flow timeout (varsayılan: 15 saniye)
   - Metodlar:
     - `add_packet(...)`: Paket ekleme
     - `flush()`: Tamamlanan flow'ları döndürme
     - `should_flush()`: Flush zamanı kontrolü

#### 4.2.2.5. Veritabanı (`src/data/database.py`)

**Dosya Boyutu**: ~116 satır

**Fonksiyonlar**:
- `init_db()`: Tablo oluşturma
- `insert_live_event(...)`: Canlı olay kaydetme
- `get_last_events(limit: int)`: Son N olayı getirme
- `insert_alert(...)`: Alert kaydetme

**Tablo Yapıları**:
```sql
-- alerts tablosu
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    sample_idx INTEGER,
    is_attack INTEGER,
    prob REAL,
    true_label INTEGER,
    attack_type TEXT,
    created_at TEXT
);

-- live_events tablosu
CREATE TABLE live_events (
    id INTEGER PRIMARY KEY,
    src_ip TEXT,
    dst_ip TEXT,
    prob REAL,
    is_attack INTEGER,
    risk_level TEXT,
    created_at TEXT
);
```

### 4.2.3. Kod Organizasyon Prensipleri

**1. Separation of Concerns (SoC)**
- Her modül tek bir sorumluluğa sahip
- Core logic, data access, presentation ayrılmış

**2. Dependency Injection**
- IntelligenceEngine, DataSource bağımsız kullanılabilir
- Test edilebilirlik artırılmış

**3. Abstract Base Classes**
- `DataSource` ABC ile tüm veri kaynakları aynı interface'i kullanır

**4. Type Hints**
- Python type hints kullanılmış (kod okunabilirliği)

**5. Modular Design**
- `src/` klasörü altında modüller mantıklı şekilde gruplanmış

---

## 4.3. Arayüz Tasarımı

Sistem, modern ve kullanıcı dostu bir web arayüzüne sahiptir. Dashboard, responsive tasarım prensiplerine uygun olarak geliştirilmiştir.

### 4.3.1. Dashboard Mimarisi

**Dosya**: `intelligent_ids_dashboard.py` (~1014 satır HTML/CSS/JS)

**Teknoloji Stack**:
- **Backend**: Flask `render_template_string()` ile HTML servisi
- **Frontend**: Vanilla HTML5/CSS3/JavaScript (framework yok)
- **İletişim**: RESTful API (`/events`, `/stats`, `/mode`)

### 4.3.2. Görsel Tasarım Özellikleri

#### 4.3.2.1. Renk Paleti

**Dark Theme** (Ana Dashboard):
- **Arka Plan**: `#0a0e27` (koyu mavi)
- **Kartlar**: `#020617` (siyah-mavi)
- **Border**: `#1f2937` (gri)
- **Text**: `#e5e7eb` (açık gri)
- **Accent**: `#60a5fa` (mavi), `#93c5fd` (açık mavi)
- **Success**: `#4ade80` (yeşil)
- **Warning**: `#facc15` (sarı)
- **Danger**: `#fca5a5` (kırmızı)

**Light Theme** (Alternatif Dashboard):
- **Arka Plan**: `#f8f9fa` (açık gri)
- **Kartlar**: `#fff` (beyaz)
- **Border**: `#ddd` (açık gri)

#### 4.3.2.2. Typography

- **Font Family**: System UI fonts (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`)
- **Font Sizes**: 
  - Başlık: 22-24px
  - Alt başlık: 13-14px
  - Metin: 12-14px
  - Küçük metin: 11px

#### 4.3.2.3. Layout ve Grid Sistemi

**CSS Grid Kullanımı**:
```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
}
```

**Responsive Design**:
- Desktop: 4 sütunlu grid
- Tablet: 2 sütunlu grid (`@media (max-width: 1100px)`)
- Mobile: 1 sütunlu grid (`@media (max-width: 650px)`)

### 4.3.3. Dashboard Bileşenleri

#### 4.3.3.1. Header (Üst Kısım)

**İçerik**:
- Sistem başlığı: "Intelligent IDS - Akıllı Saldırı Tespit Sistemi"
- Mod seçici (Radio buttons):
  - Dataset Intelligence
  - Simulated Live
  - Real Network
- Durum göstergesi (aktif mod vurgulaması)

**Tasarım**: 
- Koyu arka plan, açık metin
- Radio button'lar custom styled

#### 4.3.3.2. Statistics Cards (İstatistik Kartları)

**Gösterilen Metrikler**:
- Toplam Olay Sayısı
- Low Risk (Normal) Sayısı
- Medium Risk (Şüpheli) Sayısı
- High Risk (Saldırı) Sayısı
- İşlem İlerlemesi (Dataset modu için)

**Tasarım**:
- Kart bazlı tasarım (`stat-card` class)
- Backdrop filter blur efekti
- Renk kodlu badge'ler

#### 4.3.3.3. Event Timeline Tablosu

**Kolonlar**:
- Zaman (Timestamp)
- Kaynak IP (Src IP)
- Hedef IP (Dst IP)
- Protokol (TCP/UDP/ICMP)
- Portlar (Src → Dst)
- Risk Seviyesi (Low/Medium/High badge)
- Olasılık (Probability skoru)
- Süre (Duration)
- Byte/Paket Sayıları
- Tespit Edilen Kurallar

**Özellikler**:
- Real-time güncelleme (2 saniyede bir)
- Risk seviyesine göre renk kodlama
- Scroll desteği (max 200 event)
- Modal popup ile detay görüntüleme

#### 4.3.3.4. Metrik Panelleri (Dataset Modu İçin)

**Confusion Matrix**:
- Görsel heatmap (HTML table)
- True Positive, True Negative, False Positive, False Negative
- Renk kodlu (yeşil: doğru, kırmızı: yanlış)

**Performance Metrics**:
- Accuracy
- Precision
- Recall
- F1 Score
- Bar chart görselleştirme

**Attack Distribution**:
- Saldırı türlerine göre dağılım listesi
- Sayısal ve yüzdesel gösterim

#### 4.3.3.5. Cybersecurity Background Animasyonu

**Özellikler**:

1. **Security Icons (Kilit/Kalkan)**
   - 8 adet SVG ikonu
   - `float` animasyonu (20-40 saniye loop)
   - `pulse` animasyonu (4-6 saniye loop)
   - Opacity: 0.25-0.50 (hafif görünürlük)

2. **Network Lines**
   - 8 adet SVG çizgisi
   - `networkFlow` animasyonu (8-10 saniye loop)
   - Dashed line efekti (`stroke-dasharray`)
   - Opacity animasyonu (0.35-0.50)

3. **Data Flow Particles**
   - 8 adet parçacık
   - `dataFlow` animasyonu (15-18 saniye loop)
   - Linear hareket (CSS `transform: translate()`)
   - Glow efekti (`box-shadow`)

**CSS Animasyon Kodları**:
```css
@keyframes float {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    25% { transform: translate(40px, -40px) rotate(5deg); }
    50% { transform: translate(-30px, 30px) rotate(-5deg); }
    75% { transform: translate(30px, 40px) rotate(3deg); }
}

@keyframes networkFlow {
    0% { stroke-dashoffset: 0; opacity: 0.35; }
    50% { opacity: 0.50; }
    100% { stroke-dashoffset: 24; opacity: 0.35; }
}

@keyframes dataFlow {
    0% { transform: translate(0, 0); opacity: 0; }
    10% { opacity: 0.85; }
    90% { opacity: 0.85; }
    100% { transform: translate(var(--dx), var(--dy)); opacity: 0; }
}
```

**Performans Optimizasyonu**:
- `position: fixed` ile arka plan layer'ı
- `z-index: -1` ile içerik üzerinde
- `pointer-events: none` ile etkileşimi engelleme
- CSS hardware acceleration (`transform`, `opacity`)

### 4.3.4. JavaScript Fonksiyonalitesi

#### 4.3.4.1. Real-time Güncelleme

```javascript
// Her 2 saniyede bir event listesini güncelle
setInterval(async () => {
    await loadEvents();
}, 2000);
```

#### 4.3.4.2. API İletişimi

```javascript
async function loadEvents() {
    const res = await fetch("/events");
    const data = await res.json();
    // DOM güncelleme
}
```

#### 4.3.4.3. Mod Değiştirme

```javascript
async function changeMode(mode) {
    await fetch(`/mode/${mode}`, { method: "POST" });
    location.reload();
}
```

#### 4.3.4.4. Event Filtreleme

- Risk seviyesine göre filtreleme
- IP/Port arama
- Gerçek zamanlı filtreleme (client-side)

### 4.3.5. Kullanıcı Deneyimi (UX) Özellikleri

**1. Responsive Design**
- Desktop, tablet, mobile uyumlu
- Breakpoint'ler: 1100px, 650px

**2. Loading States**
- İşlem ilerlemesi gösterimi (Dataset modu)
- "Processing..." durumu

**3. Error Handling**
- API hatalarında console log
- Kullanıcıya bilgi mesajları

**4. Accessibility**
- Semantic HTML kullanımı
- Renk kontrastı (WCAG uyumlu)
- Keyboard navigation desteği

**5. Performance**
- Lazy loading (sadece görünen event'ler)
- Efficient DOM updates
- Minimal re-render

---

## 4.4. Sistem Entegrasyonu

Sistem, modüler mimarisi sayesinde farklı bileşenlerin sorunsuz entegrasyonuna olanak sağlar. Aşağıda sistem entegrasyonu detayları açıklanmaktadır.

### 4.4.1. Modüller Arası Entegrasyon

#### 4.4.1.1. Flask API ↔ Intelligence Engine

**İletişim Yöntemi**: Doğrudan Python object reference

**Akış**:
```
Flask Route (/ingest/flows)
    ↓
process_flow(flow_data)
    ↓
intelligence_engine.process_flow(flow)
    ↓
FeatureEngine → MLInference → DLInference → RuleEngine → DecisionEngine
    ↓
Result Dictionary
    ↓
Flask JSON Response
```

**Kod Örneği**:
```python
@app.route("/ingest/flows", methods=["POST"])
def ingest_flows():
    flows = request.json.get("flows", [])
    for flow_dict in flows:
        flow = FlowData(**flow_dict)
        result = intelligence_engine.process_flow(flow)
        # Event kaydetme, metrik güncelleme
```

#### 4.4.1.2. Data Source ↔ Intelligence Engine

**İletişim Yöntemi**: Iterator pattern ve threading

**Akış**:
```
Data Source Thread
    ↓
for flow in data_source:
    ↓
intelligence_engine.process_flow(flow)
    ↓
Event Listesi Güncelleme
    ↓
Veritabanı Kaydı
```

**Thread Yönetimi**:
```python
data_source_thread = threading.Thread(
    target=process_data_source,
    daemon=True
)
data_source_thread.start()
```

#### 4.4.1.3. Flow Aggregator ↔ Data Source

**İletişim Yöntemi**: Callback fonksiyonu

**Akış** (Canlı Trafik Modu):
```
Scapy sniff() → Paket Yakalama
    ↓
FlowAggregator.add_packet()
    ↓
Flow Tamamlama (timeout)
    ↓
FlowAggregator.flush()
    ↓
LiveWiFiSource → FlowData
    ↓
Intelligence Engine
```

**Kod Örneği**:
```python
def on_pkt(pkt):
    if IP in pkt:
        flow_aggregator.add_packet(
            src_ip=pkt[IP].src,
            dst_ip=pkt[IP].dst,
            ...
        )
        if flow_aggregator.should_flush():
            flows = flow_aggregator.flush()
            # Flow'ları işle
```

### 4.4.2. Dış Sistem Entegrasyonları

#### 4.4.2.1. Agent → API Entegrasyonu

**Teknoloji**: HTTP POST (RESTful API)

**Akış**:
```
Agent (live_agent_flow.py)
    ↓
Scapy ile paket yakalama
    ↓
FlowAggregator ile flow oluşturma
    ↓
HTTP POST /ingest/flows
    ↓
Flask API
    ↓
Intelligence Engine
    ↓
JSON Response
```

**Kod Örneği (Agent)**:
```python
import requests

flows = flow_aggregator.flush()
response = requests.post(
    "http://127.0.0.1:8000/ingest/flows",
    json={"flows": [flow.to_dict() for flow in flows]}
)
```

**API Endpoint**:
```python
@app.route("/ingest/flows", methods=["POST"])
def ingest_flows():
    flows = request.json.get("flows", [])
    # İşleme
    return jsonify({"ok": True, "count": len(flows)})
```

#### 4.4.2.2. Veritabanı Entegrasyonu

**Teknoloji**: SQLite3 (Python standard library)

**Kullanım Alanları**:
- Event kayıtları (`insert_live_event()`)
- Alert kayıtları (`insert_alert()`)
- Event sorgulama (`get_last_events()`)

**Bağlantı Yönetimi**:
```python
def get_connection():
    return sqlite3.connect(DB_PATH)

def insert_live_event(...):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO live_events ...")
    conn.commit()
    conn.close()
```

**Thread Safety**: Her çağrıda yeni bağlantı açılır (thread-safe)

#### 4.4.2.3. Model Dosyaları Entegrasyonu

**Model Formatları**:
- **RandomForest**: `.pkl` (Joblib)
- **CNN-LSTM**: `.h5` (Keras/TensorFlow)
- **Scaler**: `.pkl` (Joblib)
- **Label Encoder**: `.pkl` (Joblib)

**Yükleme Mekanizması**:
```python
# RandomForest
import joblib
ml_model = joblib.load("simple_ids_rf.pkl")

# CNN-LSTM
from tensorflow.keras.models import load_model
dl_model = load_model("ids_cnn_lstm.h5")

# Scaler
scaler = joblib.load("ensemble_scaler.pkl")
```

**Lazy Loading**: Model'ler sınıf başlatma sırasında yüklenir (singleton pattern)

### 4.4.3. Veri Akışı Entegrasyonu

#### 4.4.3.1. Dataset Intelligence Modu

```
CSV Dosyası (test.csv)
    ↓
CSVDatasetSource.__iter__()
    ↓
Satır satır okuma
    ↓
FlowData oluşturma
    ↓
IntelligenceEngine.process_flow()
    ↓
Tahmin + Ground Truth karşılaştırma
    ↓
METRICS dictionary güncelleme
    ↓
Event listesi (EVENTS_DATASET_INTELLIGENCE)
    ↓
Dashboard görüntüleme
```

#### 4.4.3.2. Simulated Live Modu

```
CSV Dosyası (test.csv)
    ↓
CSVReplaySource.__iter__()
    ↓
Satır satır okuma (1 saniye delay)
    ↓
FlowData oluşturma
    ↓
IntelligenceEngine.process_flow()
    ↓
Tahmin
    ↓
Event listesi (EVENTS_SIMULATED_LIVE)
    ↓
Dashboard görüntüleme (real-time)
```

#### 4.4.3.3. Real Network Modu

```
Wi-Fi Interface
    ↓
Scapy sniff()
    ↓
Paket yakalama
    ↓
FlowAggregator.add_packet()
    ↓
Flow tamamlama (timeout)
    ↓
FlowAggregator.flush()
    ↓
LiveWiFiSource.__iter__()
    ↓
FlowData oluşturma
    ↓
IntelligenceEngine.process_flow()
    ↓
Tahmin
    ↓
Event listesi (EVENTS_REAL_NETWORK)
    ↓
Veritabanı kaydı
    ↓
Dashboard görüntüleme (real-time)
```

### 4.4.4. Hata Yönetimi ve Güvenilirlik

**1. Exception Handling**
- Try-except blokları kritik noktalarda
- Hata loglama (`logging` modülü)
- Kullanıcıya bilgilendirme (console, API response)

**2. Graceful Degradation**
- Model yüklenemezse hata mesajı (sistem çalışmaya devam eder)
- Veritabanı bağlantı hatası durumunda bellek tabanlı çalışma
- Agent bağlantı hatası durumunda retry mekanizması

**3. Resource Management**
- Thread'lerin düzgün kapanması (`daemon=True`)
- Veritabanı bağlantılarının kapatılması
- Bellek yönetimi (event listesi limiti: MAX_EVENTS = 2000)

---

## 4.5. Çalışma Yapısı

Sistem, üç farklı çalışma modunda çalışabilmektedir. Her mod, farklı kullanım senaryoları için optimize edilmiştir.

### 4.5.1. Sistem Başlatma Süreci

**Dosya**: `intelligent_ids.py` → `initialize()`

**Adımlar**:

1. **Veritabanı Başlatma**
   ```python
   init_db()  # Tablo oluşturma (yoksa)
   ```

2. **Intelligence Engine Hazırlığı**
   ```python
   intelligence_engine = None  # Mod seçildikten sonra initialize edilecek
   ```

3. **Varsayılan Mod Başlatma**
   ```python
   start_data_source("DATASET_INTELLIGENCE")  # Varsayılan mod
   ```

4. **Flask Sunucusu Başlatma**
   ```python
   app.run(host=API_HOST, port=API_PORT, debug=True, threaded=True)
   ```

**Çıktı**:
```
============================================================
INTELLIGENT IDS - Initializing
============================================================
[✓] Database initialized
[✓] Intelligence Engine will be initialized based on mode
[✓] Data source started (DATASET_INTELLIGENCE mode)
============================================================
System ready!
Dashboard: http://127.0.0.1:8000/dashboard
============================================================
```

### 4.5.2. Çalışma Modları

#### 4.5.2.1. Dataset Intelligence Modu

**Amaç**: Offline dataset değerlendirmesi ve akademik metrik hesaplama

**Başlatma**:
```python
POST /mode/DATASET_INTELLIGENCE
```

**Çalışma Akışı**:
1. `CSVDatasetSource` oluşturma (`CSV/test.csv`)
2. Tüm satırları okuma (thread'de)
3. Her flow için:
   - Intelligence Engine ile tahmin
   - Ground truth ile karşılaştırma (label varsa)
   - Metrik güncelleme (TP, TN, FP, FN)
   - Event listesine ekleme
4. İşlem tamamlandığında:
   - Final metrikleri hesaplama
   - Confusion matrix oluşturma

**Özellikler**:
- Toplu işlem (batch processing)
- Ground truth karşılaştırması
- Detaylı metrik hesaplama
- İlerleme takibi (`/progress` endpoint)

**Kullanım Senaryosu**: Model değerlendirmesi, akademik çalışmalar, performans analizi

#### 4.5.2.2. Simulated Live Modu

**Amaç**: Dataset'i canlı trafik simülasyonu olarak oynatma

**Başlatma**:
```python
POST /mode/SIMULATED_LIVE
```

**Çalışma Akışı**:
1. `CSVReplaySource` oluşturma (`CSV/test.csv`)
2. Satır satır okuma (1 saniye delay ile)
3. Her flow için:
   - Intelligence Engine ile tahmin
   - Event listesine ekleme (real-time)
4. Sürekli işlem (dataset bitene kadar)

**Özellikler**:
- Gerçek zamanlı simülasyon
- Demo amaçlı kullanım
- Time delay ile gerçekçi akış

**Kullanım Senaryosu**: Sunumlar, demo gösterimleri, eğitim amaçlı

#### 4.5.2.3. Real Network Modu

**Amaç**: Canlı ağ trafiğini gerçek zamanlı analiz

**Başlatma**:
```python
POST /mode/REAL_NETWORK
```

**Çalışma Akışı**:
1. `LiveWiFiSource` oluşturma
2. `FlowAggregator` başlatma
3. Scapy ile paket sniffing (arka plan thread'de)
4. Her paket için:
   - FlowAggregator'a ekleme
   - Flow tamamlama kontrolü
5. Flow tamamlandığında:
   - Intelligence Engine ile tahmin
   - Veritabanına kaydetme (`insert_live_event()`)
   - Event listesine ekleme (real-time)

**Özellikler**:
- Gerçek zamanlı paket yakalama
- Flow aggregation
- Veritabanı kaydı
- Sürekli işlem (sonsuz döngü)

**Kullanım Senaryosu**: Canlı ağ izleme, gerçek zamanlı saldırı tespiti

### 4.5.3. Flow İşleme Pipeline'ı

**Fonksiyon**: `process_flow(flow: FlowData, source_type: str)`

**Pipeline Adımları**:

```
1. Feature Extraction (FeatureEngine)
   Input: FlowData
   Output: 44 boyutlu feature vector
   
2. Machine Learning Inference (MLInference)
   Input: Feature vector
   Output: Probability (0-1)
   
3. Deep Learning Inference (DLInference)
   Input: Feature vector (reshaped: 1, 1, 44)
   Output: Probability (0-1)
   
4. Rule-Based Detection (RuleEngine)
   Input: FlowData
   Output: Risk level (low/medium/high), Detected rules
   
5. Decision Engine
   Input: ML prob, DL prob, Rule risk
   Output: Final risk level, Confidence, Explanation
   
6. Event Storage
   - Event listesine ekleme
   - Veritabanı kaydı (REAL_NETWORK modu)
   - Metrik güncelleme (DATASET_INTELLIGENCE modu)
```

**Kod Akışı**:
```python
def process_flow(flow: FlowData, source_type: str):
    # Intelligence Engine ile işleme
    result = intelligence_engine.process_flow(flow)
    
    # Event oluşturma
    event = {
        "ts": time.time(),
        "flow": flow.to_dict(),
        "prediction": result,
        "rules": result.get("rules", [])
    }
    
    # Mod bazlı event listesine ekleme
    if CURRENT_MODE == "DATASET_INTELLIGENCE":
        EVENTS_DATASET_INTELLIGENCE.append(event)
    elif CURRENT_MODE == "SIMULATED_LIVE":
        EVENTS_SIMULATED_LIVE.append(event)
    else:  # REAL_NETWORK
        EVENTS_REAL_NETWORK.append(event)
        insert_live_event(...)  # Veritabanı kaydı
```

### 4.5.4. Threading ve Eşzamanlılık

**1. Flask Threading**
- `threaded=True`: Her HTTP isteği ayrı thread'de
- Eşzamanlı API çağrıları desteklenir

**2. Data Source Thread**
- Arka plan thread'de veri kaynağı işleme
- `daemon=True`: Ana program kapanınca otomatik kapanır
- Thread-safe event listesi kullanımı

**3. Agent Thread (Opsiyonel)**
- Agent'lar kendi process'lerinde çalışır
- HTTP API ile iletişim (asenkron)

### 4.5.5. Performans Optimizasyonları

**1. Event Listesi Limiti**
- `MAX_EVENTS = 2000`: Bellek kullanımını sınırlama
- FIFO (First In, First Out) prensibi

**2. Lazy Model Loading**
- Model'ler sadece gerektiğinde yüklenir
- Singleton pattern ile tek instance

**3. Batch Processing** (Dataset Modu)
- Toplu işlem ile verimlilik artışı
- Streaming metrik hesaplama (tüm dataset bitmeden)

**4. CSS Hardware Acceleration**
- Dashboard animasyonları GPU'da çalışır
- `transform` ve `opacity` kullanımı

### 4.5.6. Hata Yönetimi ve İzleme

**1. Logging Sistemi**
- `logging` modülü ile loglama
- Alert logları: `logs/alerts.log`
- Yüksek risk olayları kaydedilir

**2. Exception Handling**
- Try-except blokları kritik noktalarda
- Hata mesajları console'a yazılır
- API response'larında hata bilgisi

**3. Health Check**
- `/stats` endpoint'i ile sistem durumu
- Event sayıları, mod bilgisi

---

## 4.6. Özet

Bu bölümde, geliştirilen akıllı saldırı tespit sisteminin teknik implementasyonu detaylı olarak açıklanmıştır. Sistem, modern teknolojiler kullanılarak modüler bir yapıda geliştirilmiştir. Flask tabanlı RESTful API, Intelligence Engine ile entegre çalışarak hibrit tespit mekanizması sunmaktadır. Dashboard, responsive tasarım ve gerçek zamanlı güncelleme özellikleri ile kullanıcı dostu bir arayüz sağlamaktadır. Sistem, üç farklı çalışma modunda (Dataset Intelligence, Simulated Live, Real Network) çalışabilmekte ve farklı kullanım senaryolarına uyum sağlamaktadır.
