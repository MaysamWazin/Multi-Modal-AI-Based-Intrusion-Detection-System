# src/data/simple_features.py

import numpy as np

PROTO_MAP = {
    "tcp": 6,
    "udp": 17,
    "icmp": 1,
}

def _ip_last_octet(ip: str) -> float:
    try:
        return float(ip.split(".")[-1])
    except Exception:
        return 0.0

def _proto_to_num(proto: str) -> float:
    if proto is None:
        return 0.0
    return float(PROTO_MAP.get(str(proto).lower(), 0))


def simple_features_from_unsw_row(row) -> np.ndarray:
    """
    UNSW-NB15 satırından 8 boyutlu basit feature vektörü üretir.
    row: pandas Series
    """
    src_ip_last = _ip_last_octet(row["srcip"])
    dst_ip_last = _ip_last_octet(row["dstip"])

    try:
        sport = float(row["sport"])
    except Exception:
        sport = 0.0

    try:
        dsport = float(row["dsport"])
    except Exception:
        dsport = 0.0

    proto = _proto_to_num(row.get("proto", ""))

    try:
        dur = float(row["dur"])
    except Exception:
        dur = 0.0

    try:
        sbytes = float(row["sbytes"])
    except Exception:
        sbytes = 0.0

    try:
        dbytes = float(row["dbytes"])
    except Exception:
        dbytes = 0.0

    total_bytes = sbytes + dbytes

    try:
        spkts = float(row["Spkts"])
    except Exception:
        spkts = 0.0

    try:
        dpkts = float(row["Dpkts"])
    except Exception:
        dpkts = 0.0

    total_pkts = spkts + dpkts

    feats = np.array([
        src_ip_last,
        dst_ip_last,
        sport,
        dsport,
        proto,
        dur,
        total_bytes,
        total_pkts,
    ], dtype=float)

    return feats


def simple_features_from_packet_info(
    src_ip: str,
    dst_ip: str,
    src_port: int,
    dst_port: int,
    length: int,
    proto_name: str = "tcp",
) -> np.ndarray:
    """
    Canlı trafikteki TEK paket için aynı 8 boyutlu feature vektörü.
    (Şimdilik paketi mini-flow gibi düşünüyoruz: pkts=1, dur=0)
    """
    src_ip_last = _ip_last_octet(src_ip)
    dst_ip_last = _ip_last_octet(dst_ip)

    sport = float(src_port or 0)
    dsport = float(dst_port or 0)
    proto = _proto_to_num(proto_name)

    dur = 0.0
    total_bytes = float(length or 0)
    total_pkts = 1.0

    feats = np.array([
        src_ip_last,
        dst_ip_last,
        sport,
        dsport,
        proto,
        dur,
        total_bytes,
        total_pkts,
    ], dtype=float)

    return feats
