from __future__ import annotations

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import requests
from scapy.all import sniff, IP, TCP, UDP
import pandas as pd
from src.flows.flow_aggregator import FlowAggregator

API_URL = "http://127.0.0.1:8000/ingest/flows"
IFACE = "WiFi"          # Scapy listende WiFi olarak görünüyor
WINDOW_SEC = 5



_original_DataFrame = pd.DataFrame

def DataFrame_hook(*args, **kwargs):
    df = _original_DataFrame(*args, **kwargs)
    try:
        if hasattr(df, "shape") and df.shape[0] > 10 and df.shape[1] > 5:
            print("FLOW COLUMNS:", df.columns.tolist())
            df.head(2000).to_csv("flow_sample.csv", index=False)
    except Exception as e:
        print("Flow dump error:", e)
    return df

pd.DataFrame = DataFrame_hook



def parse_flags(tcp_layer) -> dict:
    f = str(tcp_layer.flags)
    return {
        "SYN": int("S" in f),
        "ACK": int("A" in f),
        "RST": int("R" in f),
        "FIN": int("F" in f),
    }


def send_to_api(flows):
    if not flows:
        return
    try:
        r = requests.post(API_URL, json={"flows": flows}, timeout=5)
        if r.status_code >= 300:
            print("API error:", r.status_code, r.text[:200])
    except Exception as e:
        print("API send failed:", e)


def main():
    agg = FlowAggregator(window_sec=WINDOW_SEC, idle_timeout_sec=15)

    def on_pkt(pkt):
        if IP not in pkt:
            return

        ip = pkt[IP]
        src_ip, dst_ip = ip.src, ip.dst
        pkt_len = len(pkt)

        proto = "IP"
        src_port = 0
        dst_port = 0
        flags = None

        if TCP in pkt:
            t = pkt[TCP]
            proto = "TCP"
            src_port, dst_port = int(t.sport), int(t.dport)
            flags = parse_flags(t)
        elif UDP in pkt:
            u = pkt[UDP]
            proto = "UDP"
            src_port, dst_port = int(u.sport), int(u.dport)

        agg.add_packet(
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            proto=proto,
            pkt_len=pkt_len,
            tcp_flags=flags,
            ts=time.time(),
        )

        if agg.should_flush():
            flows = agg.flush()
            print(f"[FLUSH] {len(flows)} flows")
            send_to_api(flows)

    print(f"Listening on IFACE={IFACE} ...")
    sniff(iface=IFACE, prn=on_pkt, store=False)


if __name__ == "__main__":
    main()
