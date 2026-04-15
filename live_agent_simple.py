# live_agent_simple.py
# Canlı ağ trafiğini dinleyip ids_api_simple.py'ye gönderen ajan
# ve sonuçları SQLite veritabanına kaydeden modül

from scapy.all import sniff, IP, IFACES, get_if_list
import requests

from src.data.simple_features import simple_features_from_packet
from src.data.database import insert_live_event, init_db

# =========================
# KONFİGÜRASYON
# =========================

API_URL = "http://127.0.0.1:8000/predict"

# Windows için interface ismini görmek adına
print("INTERFACES:", get_if_list())

# IFACES.show() çıktısına göre index
# (istersen direkt "Wi-Fi" de yazabilirsin)
IFACE_INDEX = 13
IFACE = IFACES.dev_from_index(IFACE_INDEX)

# =========================
# RİSK İSTATİSTİKLERİ
# =========================

low_count = 0
medium_count = 0
high_count = 0
total_seen = 0


# =========================
# PAKET İŞLEME
# =========================

def handle_packet(pkt):
    global low_count, medium_count, high_count, total_seen

    # IP olmayan paketleri at
    if IP not in pkt:
        return

    # Feature çıkarımı
    feats = simple_features_from_packet(pkt)
    payload = {
        "features": feats.tolist()
    }

    # API'ye gönder
    try:
        res = requests.post(API_URL, json=payload, timeout=1.0)
        if res.status_code != 200:
            return
        data = res.json()
    except Exception:
        return

    # API cevabı
    prob = float(data.get("probability", 0.0))
    is_attack = int(data.get("is_attack", 0))
    risk = data.get("risk_level", "low")

    # Risk sınıflandırması
    if is_attack == 1:
        label = "SALDIRI (HIGH RISK)"
        high_count += 1
    elif risk == "medium":
        label = "ŞÜPHELİ (MEDIUM RISK)"
        medium_count += 1
    else:
        label = "NORMAL (LOW RISK)"
        low_count += 1

    total_seen += 1

    src_ip = pkt[IP].src
    dst_ip = pkt[IP].dst

    # Veritabanına kaydet
    insert_live_event(
        src_ip=src_ip,
        dst_ip=dst_ip,
        prob=prob,
        is_attack=is_attack,
        risk_level=risk
    )

    # Terminal çıktısı
    print(f"{src_ip} -> {dst_ip} | {label} | prob={prob:.3f}")

    # Her 20 pakette özet
    if total_seen % 20 == 0:
        print(
            f"--- ÖZET (toplam {total_seen} paket) --- "
            f"LOW={low_count}, MEDIUM={medium_count}, HIGH={high_count}"
        )


# =========================
# MAIN
# =========================

def main():
    init_db()

    print(f"[+] {IFACE.name} arayüzünde canlı trafik dinleniyor...")
    print(f"[+] IDS API: {API_URL}")
    print("[!] Durdurmak için CTRL+C")

    sniff(
        iface=IFACE.name,   # veya "Wi-Fi"
        prn=handle_packet,
        store=False
    )


if __name__ == "__main__":
    main()
