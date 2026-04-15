from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple, Set, Optional, List
import time

from .features import FlowFeatures, safe_div

FlowKey = Tuple[str, str, int, int, str]  # (src_ip, dst_ip, src_port, dst_port, proto)


@dataclass
class FlowState:
    key: FlowKey
    start_ts: float
    last_ts: float

    packets_fwd: int = 0
    packets_bwd: int = 0
    bytes_fwd: int = 0
    bytes_bwd: int = 0

    syn: int = 0
    ack: int = 0
    rst: int = 0
    fin: int = 0

    dst_ports_seen: Set[int] = field(default_factory=set)

    def update(
        self,
        direction: str,
        pkt_len: int,
        flags: Optional[dict],
        dst_port: int,
        ts: float,
    ):
        self.last_ts = ts

        if direction == "fwd":
            self.packets_fwd += 1
            self.bytes_fwd += pkt_len
        else:
            self.packets_bwd += 1
            self.bytes_bwd += pkt_len

        if dst_port:
            self.dst_ports_seen.add(int(dst_port))

        if flags:
            self.syn += int(flags.get("SYN", 0))
            self.ack += int(flags.get("ACK", 0))
            self.rst += int(flags.get("RST", 0))
            self.fin += int(flags.get("FIN", 0))


class FlowAggregator:
    """
    Packet'ları flow bazında biriktirir ve belirli aralıklarla (window_sec) feature üretip flush eder.
    """

    def __init__(
        self,
        window_sec: int = 5,
        idle_timeout_sec: int = 15,
        min_duration_sec: float = 0.05,  # ✅ pps sapıtmasın diye
    ):
        self.window_sec = float(window_sec)
        self.idle_timeout_sec = float(idle_timeout_sec)
        self.min_duration_sec = float(min_duration_sec)

        self._flows: Dict[FlowKey, FlowState] = {}
        self._window_start = time.time()

    def _now(self) -> float:
        return time.time()

    def add_packet(
        self,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        proto: str,
        pkt_len: int,
        tcp_flags: Optional[dict] = None,
        ts: Optional[float] = None,
    ):
        ts = ts or self._now()

        src_port = int(src_port or 0)
        dst_port = int(dst_port or 0)
        proto = str(proto)

        key: FlowKey = (src_ip, dst_ip, src_port, dst_port, proto)
        rev_key: FlowKey = (dst_ip, src_ip, dst_port, src_port, proto)

        # reverse flow varsa onu "bwd" say
        if rev_key in self._flows:
            state = self._flows[rev_key]
            direction = "bwd"
        else:
            state = self._flows.get(key)
            direction = "fwd"

        if state is None:
            state = FlowState(key=key, start_ts=ts, last_ts=ts)
            self._flows[key] = state

        state.update(direction=direction, pkt_len=int(pkt_len), flags=tcp_flags, dst_port=dst_port, ts=ts)

    def should_flush(self) -> bool:
        return (self._now() - self._window_start) >= self.window_sec

    def flush(self) -> List[dict]:
        """
        Window dolduysa veya flow idle olduysa feature üretir ve döndürür.
        Dönen list elemanları: FlowFeatures.to_dict()
        """
        now = self._now()
        out: List[dict] = []
        keys_to_delete: List[FlowKey] = []

        window_elapsed = (now - self._window_start) >= self.window_sec

        for k, st in self._flows.items():
            idle = (now - st.last_ts) >= self.idle_timeout_sec

            # window dolmadıysa ve idle değilse flush etme
            if not (window_elapsed or idle):
                continue

            duration = max(st.last_ts - st.start_ts, self.min_duration_sec)

            total_packets = st.packets_fwd + st.packets_bwd
            total_bytes = st.bytes_fwd + st.bytes_bwd

            src_ip, dst_ip, src_port, dst_port, proto = st.key

            feats = FlowFeatures(
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                proto=proto,
                start_ts=st.start_ts,
                end_ts=st.last_ts,
                duration=duration,
                packets_fwd=st.packets_fwd,
                packets_bwd=st.packets_bwd,
                bytes_fwd=st.bytes_fwd,
                bytes_bwd=st.bytes_bwd,
                pps=safe_div(total_packets, duration),
                avg_pkt_size=safe_div(total_bytes, total_packets),
                syn=st.syn,
                ack=st.ack,
                rst=st.rst,
                fin=st.fin,
                unique_dst_ports=len(st.dst_ports_seen),
            )

            out.append(feats.to_dict())
            keys_to_delete.append(k)

        # flush edilenleri sil
        for k in keys_to_delete:
            self._flows.pop(k, None)

        # window geçtiyse window başlangıcını güncelle
        if window_elapsed:
            self._window_start = now

        return out
