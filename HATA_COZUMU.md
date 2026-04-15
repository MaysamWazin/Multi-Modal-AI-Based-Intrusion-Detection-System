# 🔧 Hata Çözümü: NumPy/Pandas Uyumsuzluğu

## ✅ Çözüm: Virtual Environment Kullan

### 1. VS Code Terminal'de Virtual Environment Aktif Et

VS Code terminal'inde şu komutları çalıştır:

```bash
# Virtual environment aktif et
venv\Scripts\activate

# Python'un doğru kullanıldığını kontrol et
python --version
which python  # veya where python (Windows'ta)
```

**Önemli:** Terminal'de `(venv)` yazısı görünmeli!

### 2. VS Code'da Python Interpreter Seç

1. `Ctrl+Shift+P` bas
2. `Python: Select Interpreter` yaz
3. `.\venv\Scripts\python.exe` seç

### 3. Sistemi Çalıştır

```bash
python intelligent_ids.py
```

---

## 🚨 Hala Hata Alıyorsan

### Seçenek 1: Paketleri Yeniden Yükle

```bash
# Virtual environment aktif et
venv\Scripts\activate

# Eski paketleri kaldır
pip uninstall numpy pandas -y

# Yeniden yükle
pip install numpy pandas
```

### Seçenek 2: Uyumlu Versiyonları Yükle

```bash
venv\Scripts\activate
pip install numpy==1.24.3 pandas==2.0.3
```

### Seçenek 3: Tüm Paketleri Yeniden Yükle

```bash
venv\Scripts\activate
pip install --upgrade --force-reinstall -r requirements.txt
```

---

## ✅ Doğru Çalıştığından Emin Ol

Terminal'de şunu görüyorsan doğru:
```
(venv) PS C:\Users\Ras co\Desktop\IDS-Project>
```

**`(venv)` yazısı görünmeli!**

---

## 📝 VS Code Ayarları

VS Code'un otomatik olarak virtual environment'ı kullanması için:

1. `.vscode/settings.json` dosyası zaten oluşturuldu
2. VS Code'u yeniden başlat
3. Terminal açıldığında otomatik `(venv)` aktif olmalı

---

**Sorun devam ederse terminal çıktısını paylaş!**
