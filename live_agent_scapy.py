from scapy.all import sniff, IP, TCP, UDP, ICMP, IFACES
import requests
from src.data.simple_features import simple_features_from_packet

API_URL = "http://127.0.0.1:8000/predict"

# Burada index kullanıyoruz (IFACES.show() çıktısına göre)
IFACE_INDEX = 13  # senin gerçek adaptörün
IFACE = IFACES.dev_from_index(IFACE_INDEX)

# KULLANDIĞIN ARAYÜZÜ BURAYA YAZ:
# Örn: "Wi-Fi" veya "Ethernet"
INTERFACE_NAME = "WiFi"


def build_features_from_packet(pkt):
    """
    DEMO amaçlı basit feature üretimi.
    Gerçek UNSW feature setiyle bire bir aynı değil;
    amaç: canlı trafikten feature üretip IDS servisine göndermek.
    """
    features = [0.0] * 44  # model 44 feature bekliyor

    # 0: paket boyu
    try:
        features[0] = float(len(pkt))
    except Exception:
        pass

    # IP varsa: src/dst son oktetleri
    if IP in pkt:
        ip_layer = pkt[IP]
        try:
            src_last = float(ip_layer.src.split(".")[-1])
            dst_last = float(ip_layer.dst.split(".")[-1])
            features[1] = src_last
            features[2] = dst_last
        except Exception:
            pass

    # TCP/UDP varsa: portlar
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


def handle_packet(pkt):
    try:
        features = build_features_from_packet(pkt)

        res = requests.post(API_URL, json={"features": features})
        out = res.json()

        is_attack = out.get("is_attack")
        prob = out.get("probability")
        is_anomaly = out.get("is_anomaly")

        src = "-"
        dst = "-"

        if IP in pkt:
            src = pkt[IP].src
            dst = pkt[IP].dst

        label = "SALDIRI" if is_attack == 1 else "NORMAL"
        anom = "ANOMALİ" if is_anomaly == 1 else "normal"

        print(f"{src} -> {dst} | {label} | {anom} | prob={prob:.3f}")

    except Exception as e:
        print("[HATA]:", e)



def main():
    print(f"[+] {IFACE.name} arayüzünde canlı trafik dinleniyor...")
    print(f"[+] IDS API: {API_URL}")
    print("[!] Durdurmak için CTRL+C")

    sniff(iface=IFACE, prn=handle_packet, store=False)


if __name__ == "__main__":
    main()
