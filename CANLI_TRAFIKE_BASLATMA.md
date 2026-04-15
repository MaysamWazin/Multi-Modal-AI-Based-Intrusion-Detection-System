# 📡 Canlı Trafik İçin Başlatma Kılavuzu

## 🚀 Adımlar

### 1. Ana Sistemi Başlat (Terminal 1)

VS Code terminal'inde veya ayrı bir terminal'de:

```bash
venv\Scripts\activate
python intelligent_ids.py
```

Sistem başladıktan sonra:
- Dashboard: http://127.0.0.1:8000/dashboard
- API: http://127.0.0.1:8000

### 2. Canlı Agent'ı Başlat (Terminal 2)

**Yeni bir terminal aç** (VS Code'da ikinci terminal veya ayrı PowerShell):

```bash
cd "C:\Users\Ras co\Desktop\IDS-Project"
venv\Scripts\activate
python agent\live_agent_flow.py
```

**VEYA** batch dosyası ile:
```bash
start_live_agent.bat
```

### 3. Dashboard'da LIVE Moduna Geç

1. Dashboard'u aç: http://127.0.0.1:8000/dashboard
2. **📡 LIVE** butonuna tıkla
3. Canlı event'ler görünmeye başlayacak

---

## ⚠️ Önemli Notlar

### Admin Yetkisi
- Canlı trafik dinlemek için **admin yetkisi** gerekir
- VS Code'u veya terminal'i **yönetici olarak çalıştır** gerekebilir

### Ağ Arayüzü
- Agent varsayılan olarak **"WiFi"** arayüzünü dinler
- Farklı bir arayüz kullanmak için `agent/live_agent_flow.py` dosyasında `IFACE` değişkenini değiştir

### İki Terminal Gerekli
- **Terminal 1**: Ana sistem (`intelligent_ids.py`)
- **Terminal 2**: Canlı agent (`agent/live_agent_flow.py`)

---

## 🔧 Sorun Giderme

### "Permission denied" hatası
- Terminal'i **yönetici olarak çalıştır**
- Windows'ta: Sağ tık > "Run as administrator"

### "Interface not found" hatası
- Ağ arayüzünü kontrol et: `python -c "from scapy.all import get_if_list; print(get_if_list())"`
- `agent/live_agent_flow.py` dosyasında `IFACE` değerini güncelle

### Event'ler görünmüyor
- Ana sistem çalışıyor mu kontrol et
- LIVE moduna geçildi mi kontrol et
- Agent terminal'inde hata var mı kontrol et

---

## 📊 Beklenen Çıktı

Agent terminal'inde şöyle mesajlar görünmelidir:
```
Listening on IFACE=WiFi ...
[FLUSH] 5 flows
[FLUSH] 3 flows
```

Dashboard'da:
- Toplam olaylar artıyor
- Event timeline'da yeni event'ler görünüyor
- Source ve Destination IP'ler görünüyor

---

**Canlı trafik için iki terminal gerekli! 🚀**
