# ids_api_simple.py
# Basit RandomForest tabanlı IDS API
# - Flow ingest
# - Rule engine
# - Dashboard (/dashboard)
# - Events (/events)
# - Windows toast (HIGH)
# - HIGH log -> logs/alerts.log
from __future__ import annotations

import os
import json
import time
import logging
import pandas as pd

import joblib
import numpy as np
from flask import Flask, request, jsonify, render_template_string

# --- Windows Toast (winotify) ---
try:
    from winotify import Notification, audio
    WIN_NOTIFY_OK = True
except Exception:
    WIN_NOTIFY_OK = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = "simple_ids_rf.pkl"

THRESH_LOW = 0.30
THRESH_HIGH = 0.75

app = Flask(__name__)

model = joblib.load(MODEL_PATH)

EVENTS: list[dict] = []
MAX_EVENTS = 2000

# --- Alert logging ---
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

alert_logger = logging.getLogger("ids_alerts")
alert_logger.setLevel(logging.INFO)

# handler duplicate olmasın
if not any(isinstance(h, logging.FileHandler) for h in alert_logger.handlers):
    fh = logging.FileHandler(os.path.join(LOG_DIR, "alerts.log"), encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    alert_logger.addHandler(fh)

# Bildirim spam olmasın
LAST_ALERT_TS = 0.0
ALERT_COOLDOWN_SEC = 15  # 15 saniyede bir toast


def notify_windows(title: str, msg: str):
    if not WIN_NOTIFY_OK:
        return
    try:
        toast = Notification(app_id="IDS-Project", title=title, msg=msg)
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except Exception:
        pass


def log_high_alert(flow: dict, pred: dict, rules: list[str]):
    rec = {
        "ts": time.time(),
        "src_ip": flow.get("src_ip"),
        "dst_ip": flow.get("dst_ip"),
        "src_port": flow.get("src_port"),
        "dst_port": flow.get("dst_port"),
        "proto": flow.get("proto"),
        "risk_level": pred.get("risk_level"),
        "probability": pred.get("probability"),
        "rules": rules,
    }
    alert_logger.info(json.dumps(rec, ensure_ascii=False))
    return rec


def classify_risk(prob: float) -> str:
    if prob >= THRESH_HIGH:
        return "high"
    elif prob >= THRESH_LOW:
        return "medium"
    else:
        return "low"


def ip_last_octet(ip: str) -> float:
    try:
        return float(str(ip).split(".")[-1])
    except Exception:
        return 0.0


def flow_to_features(flow: dict) -> list[float]:
    """
    train_simple_ids.py ile aynı 8 feature sırası:
    [src_ip_last, dst_ip_last, sport, dsport, proto, dur, total_bytes, total_pkts]
    """
    src_ip_last = ip_last_octet(flow.get("src_ip", ""))
    dst_ip_last = ip_last_octet(flow.get("dst_ip", ""))

    sport = float(flow.get("src_port", 0))
    dsport = float(flow.get("dst_port", 0))

    # Eğitimde proto hep 0.0 -> canlıda da 0 (uyum)
    proto = 0.0

    dur = float(flow.get("duration", 0))

    total_bytes = float(flow.get("bytes_fwd", 0)) + float(flow.get("bytes_bwd", 0))
    total_pkts = float(flow.get("packets_fwd", 0)) + float(flow.get("packets_bwd", 0))

    return [src_ip_last, dst_ip_last, sport, dsport, proto, dur, total_bytes, total_pkts]


def is_whitelisted(flow: dict) -> bool:
    dst_ip = str(flow.get("dst_ip", ""))
    dst_port = int(flow.get("dst_port", 0) or 0)
    proto = str(flow.get("proto", "")).upper()

    # mDNS multicast (UDP 5353)
    if dst_ip == "224.0.0.251" and dst_port == 5353 and proto == "UDP":
        return True

    # Aynı multicast hedefte port 0 / proto IP gibi görünenler
    if dst_ip == "224.0.0.251":
        return True

    return False


def predict_features8(features8: list[float]) -> dict:
    x = np.array(features8, dtype=float).reshape(1, -1)
    proba = float(model.predict_proba(x)[0][1])
    risk = classify_risk(proba)
    is_attack = 1 if risk == "high" else 0
    return {"probability": proba, "risk_level": risk, "is_attack": is_attack}


def rule_engine(flow: dict) -> list[str]:
    hits: list[str] = []
    pps = float(flow.get("pps", 0))
    syn = int(flow.get("syn", 0))
    unique_ports = int(flow.get("unique_dst_ports", 0))
    rst = int(flow.get("rst", 0))

    # Port scan şüphesi: kısa sürede çok farklı port
    if unique_ports >= 20:
        hits.append("PORT_SCAN_SUSPECT")

    # SYN flood şüphesi
    if syn >= 30 and pps >= 50:
        hits.append("SYN_FLOOD_SUSPECT")

    # RST spike
    if rst >= 20:
        hits.append("RST_SPIKE")

    return hits

def detect_attack_type(pred: dict, rules: list[str]) -> str:
    if pred.get("risk_level") != "high":
        return "NORMAL"

    if "SYN_FLOOD_SUSPECT" in rules:
        return "SYN_FLOOD"
    if "PORT_SCAN_SUSPECT" in rules:
        return "PORT_SCAN"
    if "RST_SPIKE" in rules:
        return "RST_SPIKE"

    return "GENERIC_ATTACK"

def apply_rules_to_prediction(pred: dict, rules: list[str]) -> dict:
    if "SYN_FLOOD_SUSPECT" in rules:
        pred = {
            **pred,
            "risk_level": "high",
            "is_attack": 1,
            "probability": max(float(pred.get("probability", 0.0)), THRESH_HIGH),
        }
    elif "PORT_SCAN_SUSPECT" in rules and pred.get("risk_level") == "low":
        pred = {**pred, "risk_level": "medium"}
    return pred


def dump_flow_sample_once(flows: list):
    """İlk gelen batch'te kolonları yazdırır ve flow_sample.csv kaydeder (tek sefer)."""
    global _FLOW_DUMPED
    if not DEBUG_FLOW_DUMP or _FLOW_DUMPED:
        return

    try:
        print("[DUMP] called | flows_len=", len(flows), "| cwd=", os.getcwd(), flush=True)

        if isinstance(flows, list) and len(flows) > 0 and isinstance(flows[0], dict):
            df_dbg = pd.DataFrame(flows)
            print("[DUMP] FLOW COLUMNS:", df_dbg.columns.tolist(), flush=True)

            df_dbg.head(FLOW_DUMP_MAX_ROWS).to_csv(FLOW_DUMP_PATH, index=False)
            print("[DUMP] Saved:", FLOW_DUMP_PATH, flush=True)

            _FLOW_DUMPED = True
        else:
            # flows boşsa veya dict değilse bunu görmemiz lazım
            t0 = type(flows[0]).__name__ if isinstance(flows, list) and len(flows) else "empty"
            print("[DUMP] flows[0] type:", t0, flush=True)

    except Exception as e:
        print("[DUMP] error:", e, flush=True)


@app.route("/", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "ids_api_simple"})


@app.route("/routes", methods=["GET"])
def routes():
    return jsonify(sorted([str(r) for r in app.url_map.iter_rules()]))


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    if "features" not in data:
        return jsonify({"error": "JSON içinde 'features' alanı bekleniyor."}), 400

    feats = data["features"]

    try:
        feats = np.array(feats, dtype=float).reshape(1, -1)
    except Exception as e:
        return jsonify({"error": f"features dönüştürülemedi: {e}"}), 400

    try:
        proba = float(model.predict_proba(feats)[0][1])
    except Exception:
        pred_label = model.predict(feats)[0]
        proba = float(pred_label)

    risk = classify_risk(proba)
    is_attack = 1 if risk == "high" else 0

    return jsonify({
        "probability": proba,
        "is_attack": is_attack,
        "risk_level": risk,
        "thresholds": {"low": THRESH_LOW, "high": THRESH_HIGH},
    })


@app.route("/ingest/flows", methods=["POST"])
def ingest_flows():
    global LAST_ALERT_TS

    data = request.get_json(silent=True) or {}
    flows = data.get("flows", [])

    if not isinstance(flows, list):
        return jsonify({"ok": False, "error": "'flows' list olmalı"}), 400

    # DEBUG: kolonları yaz + örnek CSV kaydet (tek sefer)
    dump_flow_sample_once(flows)

    added = 0
    for f in flows:
        try:
            feats8 = flow_to_features(f)

            # 1) ML tahmini
            if is_whitelisted(f):
                pred = {"probability": 0.0, "risk_level": "low", "is_attack": 0}
            else:
                pred = predict_features8(feats8)

            # 2) Rules
            rules = rule_engine(f)
            pred = apply_rules_to_prediction(pred, rules)

            # 3) Event
            EVENTS.append({
                "ts": time.time(),
                "flow": f,
                "features8": feats8,
                "prediction": pred,
                "rules": rules,
            })
            added += 1

            # 4) HIGH: log + toast (toast cooldown)
            if pred.get("risk_level") == "high":
                # log her HIGH için yazsın
                log_high_alert(f, pred, rules)

                now = time.time()
                if now - LAST_ALERT_TS >= ALERT_COOLDOWN_SEC:
                    src = str(f.get("src_ip", ""))
                    dst = str(f.get("dst_ip", ""))
                    dport = f.get("dst_port", 0)
                    proto = str(f.get("proto", "")).upper()
                    rules_txt = ", ".join(rules) if rules else "ML"
                    notify_windows(
                        "⚠️ IDS ALERT: HIGH RISK",
                        f"{proto} {src} -> {dst}:{dport} | {rules_txt}",
                    )
                    LAST_ALERT_TS = now

        except Exception:
            continue

    if len(EVENTS) > MAX_EVENTS:
        del EVENTS[:len(EVENTS) - MAX_EVENTS]

    print(f"[INGEST] flows={len(flows)} added={added} total={len(EVENTS)}")
    return jsonify({"ok": True, "count": len(flows), "added": added, "total_events": len(EVENTS)})


@app.route("/events", methods=["GET"])
def events():
    return jsonify(EVENTS[-200:])


DASHBOARD_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>IDS Dashboard</title>
  <style>
    /* Cybersecurity Background Animation Layer */
    body { 
      font-family: Arial, sans-serif; 
      margin: 20px; 
      position: relative;
      background: #f8f9fa;
    }
    html { overflow-y: scroll; }

    #cyberBg {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: -1;
      pointer-events: none;
      overflow: hidden;
      background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* Lock/Shield Icons */
    .security-icon {
      position: absolute;
      opacity: 0.30;
      animation: float 20s infinite ease-in-out;
    }

    .security-icon svg {
      width: 80px;
      height: 80px;
      stroke: #60a5fa;
      fill: none;
      stroke-width: 2;
    }

    @keyframes float {
      0%, 100% { transform: translate(0, 0) rotate(0deg); }
      25% { transform: translate(30px, -30px) rotate(5deg); }
      50% { transform: translate(-20px, 20px) rotate(-5deg); }
      75% { transform: translate(20px, 30px) rotate(3deg); }
    }

    @keyframes pulse {
      0%, 100% { opacity: 0.20; }
      50% { opacity: 0.45; }
    }

    .security-icon:nth-child(1) { top: 10%; left: 5%; animation-delay: 0s; animation-duration: 25s; }
    .security-icon:nth-child(2) { top: 30%; right: 10%; animation-delay: -5s; animation-duration: 30s; }
    .security-icon:nth-child(3) { bottom: 25%; left: 15%; animation-delay: -10s; animation-duration: 28s; }
    .security-icon:nth-child(4) { bottom: 15%; right: 20%; animation-delay: -15s; animation-duration: 32s; }
    .security-icon:nth-child(5) { top: 50%; left: 50%; animation-delay: -8s; animation-duration: 35s; }
    .security-icon:nth-child(6) { top: 70%; right: 30%; animation-delay: -12s; animation-duration: 27s; }

    .security-icon:nth-child(odd) svg { animation: pulse 4s infinite ease-in-out; }
    .security-icon:nth-child(even) svg { animation: pulse 5s infinite ease-in-out; }

    /* Network Lines */
    .network-line {
      position: absolute;
      stroke: #60a5fa;
      stroke-width: 2;
      opacity: 0.35;
      stroke-dasharray: 5, 5;
      animation: networkFlow 8s linear infinite;
    }

    @keyframes networkFlow {
      0% { stroke-dashoffset: 0; opacity: 0.30; }
      50% { opacity: 0.45; }
      100% { stroke-dashoffset: 20; opacity: 0.30; }
    }

    /* Data Flow Particles */
    .data-particle {
      position: absolute;
      width: 5px;
      height: 5px;
      background: #60a5fa;
      border-radius: 50%;
      opacity: 0.70;
      animation: dataFlow 15s infinite linear;
      box-shadow: 0 0 10px rgba(96, 165, 250, 0.9);
    }

    @keyframes dataFlow {
      0% {
        transform: translate(0, 0);
        opacity: 0;
      }
      10% {
        opacity: 0.80;
      }
      90% {
        opacity: 0.80;
      }
      100% {
        transform: translate(var(--dx), var(--dy));
        opacity: 0;
      }
    }

    /* Content Layer - ensure it's above background */
    body > *:not(#cyberBg) {
      position: relative;
      z-index: 1;
    }

    .card { 
      padding:10px 12px; 
      border:1px solid #ddd; 
      border-radius:10px; 
      background:#fff; 
      position: relative;
      backdrop-filter: blur(1px);
    }
    input, select { padding:8px; border-radius:8px; border:1px solid #ccc; }
    button { padding:8px 12px; border-radius:8px; border:1px solid #bbb; background:#fff; cursor:pointer; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }

    .row-high { background: #ffe5e5; }
.row-medium { background: #fff3cd; }
.row-low { background: #f4f6f8; }

    .row {
      display: grid;
      grid-template-columns: repeat(4, minmax(240px, 1fr));
      gap: 12px;
      align-items: stretch;
      margin-bottom: 12px;
    }
    @media (max-width: 1100px){
      .row { grid-template-columns: repeat(2, minmax(240px, 1fr)); }
    }
    @media (max-width: 650px){
      .row { grid-template-columns: 1fr; }
    }

    #spark { max-width: 100%; overflow: hidden; white-space: nowrap; }

    .tableWrap {
      border:1px solid #eee;
      border-radius:12px;
      padding:6px;
      overflow:auto;
    }

    table { width:100%; border-collapse: collapse; margin-top: 6px; table-layout: fixed; }
    th, td {
      border-bottom:1px solid #eee;
      padding:8px;
      text-align:left;
      font-size: 14px;
      overflow:hidden;
      text-overflow:ellipsis;
      white-space:nowrap;
    }

    .badge { padding:3px 8px; border-radius:999px; border:1px solid #ddd; }
    .low { background:#f6f6f6; }
    .medium { background:#fff3cd; border-color:#ffe69c; }
    .high { background:#f8d7da; border-color:#f1aeb5; }

    tr.clickable:hover { background: #fafafa; }

    th:nth-child(1), td:nth-child(1) { width: 90px; }
    th:nth-child(2), td:nth-child(2) { width: 140px; }
    th:nth-child(3), td:nth-child(3) { width: 140px; }
    th:nth-child(4), td:nth-child(4) { width: 60px; }
    th:nth-child(5), td:nth-child(5) { width: 120px; }
    th:nth-child(6), td:nth-child(6) { width: 80px; }
    th:nth-child(7), td:nth-child(7) { width: 70px; }
    th:nth-child(8), td:nth-child(8) { width: 70px; }
    th:nth-child(9), td:nth-child(9) { width: 70px; }
    th:nth-child(10), td:nth-child(10){ width: 60px; }
    th:nth-child(11), td:nth-child(11){ width: 220px; }

    /* ALERT BAR */
    #alertBar{
      display:none;
      background:#b02a37;
      color:white;
      padding:10px 12px;
      border-radius:12px;
      margin:12px 0;
    }
    #alertBar button{
      background:white;
      border:1px solid #eee;
      border-radius:8px;
      padding:6px 10px;
      cursor:pointer;
      margin-left:6px;
    }
  </style>
</head>
<body>
  <!-- Cybersecurity Background Animation -->
  <div id="cyberBg">
    <!-- Security Icons (Locks & Shields) -->
    <div class="security-icon">
      <svg viewBox="0 0 24 24">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        <path d="M12 13v4"/>
        <path d="M12 9a2 2 0 0 1 2 2"/>
      </svg>
    </div>
    <div class="security-icon">
      <svg viewBox="0 0 24 24">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    </div>
    <div class="security-icon">
      <svg viewBox="0 0 24 24">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
      </svg>
    </div>
    <div class="security-icon">
      <svg viewBox="0 0 24 24">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        <path d="M12 13v4"/>
        <path d="M12 9a2 2 0 0 1 2 2"/>
      </svg>
    </div>
    <div class="security-icon">
      <svg viewBox="0 0 24 24">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    </div>
    <div class="security-icon">
      <svg viewBox="0 0 24 24">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
      </svg>
    </div>

    <!-- Network Lines (SVG) -->
    <svg style="position: absolute; width: 100%; height: 100%; top: 0; left: 0;">
      <line class="network-line" x1="10%" y1="20%" x2="30%" y2="40%" style="animation-delay: 0s;"/>
      <line class="network-line" x1="70%" y1="25%" x2="85%" y2="45%" style="animation-delay: -2s;"/>
      <line class="network-line" x1="15%" y1="60%" x2="40%" y2="80%" style="animation-delay: -4s;"/>
      <line class="network-line" x1="60%" y1="65%" x2="80%" y2="85%" style="animation-delay: -1s;"/>
      <line class="network-line" x1="25%" y1="15%" x2="50%" y2="55%" style="animation-delay: -3s;"/>
      <line class="network-line" x1="75%" y1="35%" x2="55%" y2="75%" style="animation-delay: -5s;"/>
      <line class="network-line" x1="45%" y1="10%" x2="65%" y2="30%" style="animation-delay: -1.5s;"/>
      <line class="network-line" x1="20%" y1="70%" x2="35%" y2="90%" style="animation-delay: -3.5s;"/>
    </svg>

    <!-- Data Flow Particles -->
    <div class="data-particle" style="--dx: 200px; --dy: -150px; top: 20%; left: 10%; animation-delay: 0s;"></div>
    <div class="data-particle" style="--dx: -180px; --dy: 120px; top: 35%; right: 15%; animation-delay: -2s;"></div>
    <div class="data-particle" style="--dx: 250px; --dy: 200px; top: 50%; left: 20%; animation-delay: -4s;"></div>
    <div class="data-particle" style="--dx: -220px; --dy: -180px; top: 65%; right: 25%; animation-delay: -1s;"></div>
    <div class="data-particle" style="--dx: 300px; --dy: 100px; top: 30%; left: 40%; animation-delay: -3s;"></div>
    <div class="data-particle" style="--dx: -150px; --dy: 250px; top: 55%; right: 35%; animation-delay: -5s;"></div>
    <div class="data-particle" style="--dx: 180px; --dy: -200px; top: 75%; left: 30%; animation-delay: -2.5s;"></div>
    <div class="data-particle" style="--dx: -280px; --dy: 150px; top: 40%; right: 50%; animation-delay: -1.5s;"></div>
  </div>

  <h2>IDS Dashboard</h2>

  <div id="alertBar">
    <b>🚨 ALERT (HIGH)</b>
    <span id="alertText" class="mono" style="margin-left:10px"></span>
    <span style="float:right;">
      <button onclick="openLatestHigh()">Open</button>
      <button onclick="dismissAlert()">Dismiss</button>
    </span>
  </div>

  <div class="row">
    <div class="card">
      <b>Auto refresh:</b> <span id="tick">-</span> sn
    </div>

    <div class="card">
      <b>Counts:</b>
      Low <span id="cLow">0</span> ·
      Medium <span id="cMed">0</span> ·
      High <span id="cHigh">0</span>
    </div>

    <div class="card" style="min-width:260px">
      <b>Top High Src IP</b>
      <div id="topIps" class="mono" style="margin-top:6px"></div>
    </div>

    <div class="card" style="min-width:260px">
      <b>Last 60s</b>
      <div id="spark" class="mono" style="margin-top:6px"></div>
    </div>

    <div class="card">
      <b>Risk</b><br/>
      <select id="risk">
        <option value="all">all</option>
        <option value="low">low</option>
        <option value="medium">medium</option>
        <option value="high">high</option>
      </select>
    </div>

    <div class="card">
      <b>Search (ip/port)</b><br/>
      <input id="q" placeholder="10.87.0.1 or 443" />
    </div>

    <div class="card">
      <b>Actions</b><br/>
      <button onclick="loadEvents()">Refresh</button>
    </div>
  </div>

  <div class="tableWrap">
    <table>
      <thead>
        <tr>
          <th>Time</th>
          <th>Src</th>
          <th>Dst</th>
          <th>Proto</th>
          <th>Ports</th>
          <th>Risk</th>
          <th>Prob</th>
          <th>Dur</th>
          <th>Bytes</th>
          <th>Pkts</th>
          <th>Rules</th>
        </tr>
      </thead>
      <tbody id="rows"></tbody>
    </table>
  </div>

  <!-- Modal -->
  <div id="modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,.35); padding:30px;">
    <div style="background:white; border-radius:14px; padding:16px; max-width:900px; margin:auto; max-height:80vh; overflow:auto;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0">Event Details</h3>
        <button onclick="closeModal()">Close</button>
      </div>
      <pre id="modalPre" class="mono" style="white-space:pre-wrap;"></pre>
    </div>
  </div>

<script>
let sec = 0;
let lastData = [];
let history = []; // last 60 seconds counts

let latestHighIndex = -1;
let dismissUntil = 0;

function dismissAlert(){
  dismissUntil = Date.now() + 60000; // 60sn gizle
  document.getElementById("alertBar").style.display = "none";
}

function openLatestHigh(){
  if(latestHighIndex >= 0) openModalByIndex(latestHighIndex);
}

function fmtTime(ts){
  const d = new Date(ts*1000);
  return d.toLocaleTimeString();
}

function badge(r){
  return `<span class="badge ${r}">${r}</span>`;
}

function closeModal(){
  document.getElementById("modal").style.display = "none";
}

function openModalByIndex(i){
  const obj = lastData[i];
  document.getElementById("modalPre").textContent = JSON.stringify(obj, null, 2);
  document.getElementById("modal").style.display = "block";
}

function matchQ(ev, q){
  if(!q) return true;
  q = q.toLowerCase();
  const f = ev.flow || {};
  const s = [
    f.src_ip, f.dst_ip,
    String(f.src_port ?? ""), String(f.dst_port ?? "")
  ].join(" ").toLowerCase();
  return s.includes(q);
}

function updateTopIps(data){
  const counts = {};
  data.forEach(ev => {
    const r = ev.prediction?.risk_level;
    if(r === "high"){
      const ip = ev.flow?.src_ip || "unknown";
      counts[ip] = (counts[ip] || 0) + 1;
    }
  });
  const top = Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,5);
  document.getElementById("topIps").innerHTML =
    top.length ? top.map(([ip,c])=>`${ip} (${c})`).join("<br/>") : "-";
}

function updateSpark(cLow,cMed,cHigh){
  history.push({t:Date.now(), low:cLow, med:cMed, high:cHigh});
  history = history.filter(x => Date.now() - x.t < 60000);

  const highs = history.map(x => x.high).slice(-60);
  const maxv = Math.max(1, ...highs);

  const levels = "▁▂▃▄▅▆▇█";
  const line = highs.map(v => {
    const idx = Math.min(7, Math.round((v / maxv) * 7));
    return levels[idx];
  }).join("");

  document.getElementById("spark").textContent = line;
}

function updateAlertBar(data){
  latestHighIndex = -1;
  for(let i = data.length - 1; i >= 0; i--){
    const r = data[i].prediction?.risk_level;
    if(r === "high"){
      latestHighIndex = i;
      break;
    }
  }

  const bar = document.getElementById("alertBar");
  if(latestHighIndex < 0 || Date.now() < dismissUntil){
    bar.style.display = "none";
    return;
  }

  const ev = data[latestHighIndex];
  const ageSec = (Date.now()/1000) - (ev.ts || 0);

  // sadece son 60 saniyedeki HIGH'ı bar'da göster
  if(ageSec >= 60){
    bar.style.display = "none";
    return;
  }

  const f = ev.flow || {};
  const p = ev.prediction || {};
  const rules = (ev.rules && ev.rules.length) ? ev.rules.join(", ") : "ML";

  document.getElementById("alertText").textContent =
    `${f.proto||""} ${f.src_ip||""}:${f.src_port||0} -> ${f.dst_ip||""}:${f.dst_port||0} | prob=${(p.probability??0).toFixed(3)} | ${rules}`;

  bar.style.display = "block";
}

async function loadEvents(){
  const res = await fetch("/events");
  const data = await res.json();
  lastData = data;

  updateAlertBar(data);

  const risk = document.getElementById("risk").value;
  const q = document.getElementById("q").value.trim();

  let cLow=0,cMed=0,cHigh=0;

  data.forEach(ev => {
    const r = ev.prediction?.risk_level || "low";
    if(r === "low") cLow++;
    if(r === "medium") cMed++;
    if(r === "high") cHigh++;
  });

  document.getElementById("cLow").innerText = cLow;
  document.getElementById("cMed").innerText = cMed;
  document.getElementById("cHigh").innerText = cHigh;

  updateTopIps(data);
  updateSpark(cLow,cMed,cHigh);

  // index kaybetmeden filtre
  const idxs = [];
  for(let i=0;i<data.length;i++){
    const ev = data[i];
    const r = ev.prediction?.risk_level || "low";
    if(risk !== "all" && r !== risk) continue;
    if(!matchQ(ev, q)) continue;
    idxs.push(i);
  }
  idxs.reverse(); // newest first

  const rows = idxs.slice(0,200).map(i => {
    const ev = data[i];
    const f = ev.flow || {};
    const p = ev.prediction || {};
    let rules = (ev.rules && ev.rules.length) ? ev.rules.join(", ") : "-";
    if(rules.length > 40) rules = rules.slice(0, 40) + "...";
    const bytes = (Number(f.bytes_fwd||0)+Number(f.bytes_bwd||0));
    const pkts  = (Number(f.packets_fwd||0)+Number(f.packets_bwd||0));
    return `
      <tr class="clickable" style="cursor:pointer" onclick="openModalByIndex(${i})">
        <td>${fmtTime(ev.ts || 0)}</td>
        <td class="mono">${f.src_ip || ""}</td>
        <td class="mono">${f.dst_ip || ""}</td>
        <td>${f.proto || ""}</td>
        <td class="mono">${f.src_port || 0} → ${f.dst_port || 0}</td>
        <td>${badge(p.risk_level || "low")}</td>
        <td>${(p.probability ?? 0).toFixed(3)}</td>
        <td>${(f.duration ?? 0).toFixed(3)}</td>
        <td>${bytes}</td>
        <td>${pkts}</td>
        <td class="mono">${rules}</td>
      </tr>
    `;
  }).join("");

  document.getElementById("rows").innerHTML = rows;
}

setInterval(() => {
  sec = (sec + 1) % 999;
  document.getElementById("tick").innerText = sec;
}, 1000);

setInterval(() => {
  loadEvents();
}, 2000);

loadEvents();
</script>
</body>
</html>
"""


@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template_string(DASHBOARD_HTML)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
