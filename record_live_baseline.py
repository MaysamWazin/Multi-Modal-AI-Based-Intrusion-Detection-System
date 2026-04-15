# record_live_baseline.py
from scapy.all import sniff, IP, TCP, UDP
import csv
import time

INTERFACE_NAME = "WiFi"  # sende neyse onu yaz
OUTPUT_PATH = "data/recorded/live_baseline.csv"

def build_features_from_packet(pkt):
    features = [0.0] * 44

    try:
        features[0] = float(len(pkt))
    except Exception:
        pass

    if IP in pkt:
        ip_layer = pkt[IP]
        try:
            src_last = float(ip_layer.src.split(".")[-1])
            dst_last = float(ip_layer.dst.split(".")[-1])
            features[1] = src_last
            features[2] = dst_last
        except Exception:
            pass

    if TCP in pkt:
        try:
            features[3] = float(pkt[TCP].sport)
            features[4] = float(pkt[TCP].dport)
        except Exception:
            pass
    elif UDP in pkt:
        try:
            features[3] = float(pkt[UDP].sport)
            features[4] = float(pkt[UDP].dport)
        except Exception:
            pass

    return features


def handle_packet(pkt, writer):
    feats = build_features_from_packet(pkt)
    writer.writerow(feats)


def main():
    print(f"[+] {INTERFACE_NAME} arayüzünde baseline trafik kaydediliyor...")
    print(f"[+] Çıktı dosyası: {OUTPUT_PATH}")
    print("[!] 1–2 dakika normal kullanım yap, sonra CTRL+C ile durdur.")

    # klasör yoksa elle oluşturman gerekebilir: data/recorded
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        # header olmadan direkt feature yazıyoruz
        def _cb(pkt):
            handle_packet(pkt, writer)

        sniff(
            iface=INTERFACE_NAME,
            prn=_cb,
            filter="tcp",
            store=False
        )

if __name__ == "__main__":
    main()
