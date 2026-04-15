from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class FlowFeatures:
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    proto: str

    start_ts: float
    end_ts: float
    duration: float

    packets_fwd: int
    packets_bwd: int
    bytes_fwd: int
    bytes_bwd: int

    pps: float
    avg_pkt_size: float

    syn: int
    ack: int
    rst: int
    fin: int

    unique_dst_ports: int

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["duration"] = float(d["duration"])
        d["pps"] = float(d["pps"])
        d["avg_pkt_size"] = float(d["avg_pkt_size"])
        return d

def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0
