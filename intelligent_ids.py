"""
Intelligent IDS - Ana Sistem
Veri kaynağından bağımsız, akıllı saldırı tespit sistemi.
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional

# Flask ve diğer kütüphaneler
from flask import Flask, jsonify, render_template_string, request
import logging

# Proje modülleri
from src.core.data_source import (
    DataSource, LiveWiFiSource, CSVDatasetSource, CSVReplaySource, FlowData
)
from src.core.intelligence_engine import IntelligenceEngine
from src.flows.flow_aggregator import FlowAggregator
from src.data.database import init_db, insert_live_event, get_last_events

# Windows toast bildirimleri
try:
    from winotify import Notification, audio
    WIN_NOTIFY_OK = True
except:
    WIN_NOTIFY_OK = False

# ====== AYARLAR ======
CSV_DIR = Path("CSV")
TRAIN_CSV = CSV_DIR / "train.csv"
TEST_CSV = CSV_DIR / "test.csv"

# Model yolları
ML_MODEL_PATH = "simple_ids_rf.pkl"
DL_MODEL_PATH = "ids_cnn_lstm.h5"  # veya ids_cnn_lstm_enhanced.h5

# API ayarları
API_HOST = "127.0.0.1"
API_PORT = 8000

# ====== GLOBAL STATE ======
app = Flask(__name__)
intelligence_engine: Optional[IntelligenceEngine] = None
data_source: Optional[DataSource] = None
data_source_thread: Optional[threading.Thread] = None
flow_aggregator: Optional[FlowAggregator] = None

# Event storage - Mod bazlı ayrı listeler
EVENTS_DATASET_INTELLIGENCE: list = []
EVENTS_SIMULATED_LIVE: list = []
EVENTS_REAL_NETWORK: list = []
MAX_EVENTS = 2000

# Mod seçimi - Three distinct modes
# 1. DATASET_INTELLIGENCE: Full dataset evaluation with multi-class classification
# 2. SIMULATED_LIVE: Stream dataset row-by-row at 1 event/second (for demo)
# 3. REAL_NETWORK: Wi-Fi sniffing with anomaly-based detection only
CURRENT_MODE = "DATASET_INTELLIGENCE"  # DATASET_INTELLIGENCE, SIMULATED_LIVE, REAL_NETWORK
DATASET_PROCESSING_COMPLETE: bool = False  # Dataset mode runs once then freezes

# Metrikler (DATASET modu için) - Two modes: Streaming and Final
METRICS: dict = {
    "accuracy": 0.0,
    "precision": 0.0,
    "recall": 0.0,
    "f1_score": 0.0,
    "calculated": False,
    "processing": False,  # Remove permanent "Processing" state
    "total_samples": 0,
    "mode": "streaming",  # "streaming" or "final"
    "streaming_window_size": 1000,  # Rolling window size for streaming metrics
    "true_positives": 0,
    "true_negatives": 0,
    "false_positives": 0,
    "false_negatives": 0
}

# Dataset progress tracking
DATASET_PROGRESS: dict = {
    "processed": 0,
    "total": 0,
    "percent": 0.0,
    "is_complete": False
}

# Alert logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

alert_logger = logging.getLogger("ids_alerts")
alert_logger.setLevel(logging.INFO)
if not any(isinstance(h, logging.FileHandler) for h in alert_logger.handlers):
    fh = logging.FileHandler(LOG_DIR / "alerts.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    alert_logger.addHandler(fh)

LAST_ALERT_TS = 0.0
ALERT_COOLDOWN_SEC = 15


# ====== HELPER FUNCTIONS ======

def notify_windows(title: str, msg: str):
    """Windows toast bildirimi"""
    if not WIN_NOTIFY_OK:
        return
    try:
        toast = Notification(app_id="Intelligent-IDS", title=title, msg=msg)
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except Exception as e:
        print(f"[NOTIFY] failed: {e}")


def log_alert(event: dict):
    """Alert loglama"""
    decision = event.get("decision", {})
    flow = event.get("flow", {})
    
    if decision.get("is_attack", 0) == 1:
        rec = {
            "timestamp": event.get("timestamp"),
            "src_ip": flow.get("src_ip"),
            "dst_ip": flow.get("dst_ip"),
            "attack_type": decision.get("attack_type"),
            "confidence": decision.get("confidence"),
            "severity": decision.get("severity"),
            "rules": decision.get("rules_triggered", []),
        }
        alert_logger.info(str(rec))
        
        # Windows toast (HIGH severity için)
        if decision.get("severity") in ["HIGH", "CRITICAL"]:
            global LAST_ALERT_TS
            now = time.time()
            if now - LAST_ALERT_TS >= ALERT_COOLDOWN_SEC:
                notify_windows(
                    f"⚠️ IDS ALERT: {decision.get('attack_type', 'ATTACK')}",
                    f"{flow.get('src_ip', '')} → {flow.get('dst_ip', '')} | {decision.get('confidence', 0):.1%} confidence"
                )
                LAST_ALERT_TS = now


def process_flow(flow: FlowData, mode: str = None):
    """Flow'u işle ve event oluştur"""
    if intelligence_engine is None:
        return
    
    mode = mode or CURRENT_MODE
    
    try:
        # Intelligence engine ile işle
        result = intelligence_engine.process_flow(flow)
        
        # Mod bazlı event listesine ekle
        if mode == "DATASET_INTELLIGENCE" or mode == "DATASET":
            EVENTS_DATASET_INTELLIGENCE.append(result)
            if len(EVENTS_DATASET_INTELLIGENCE) > MAX_EVENTS:
                del EVENTS_DATASET_INTELLIGENCE[:len(EVENTS_DATASET_INTELLIGENCE) - MAX_EVENTS]
        elif mode == "SIMULATED_LIVE" or mode == "REPLAY":
            EVENTS_SIMULATED_LIVE.append(result)
            if len(EVENTS_SIMULATED_LIVE) > MAX_EVENTS:
                del EVENTS_SIMULATED_LIVE[:len(EVENTS_SIMULATED_LIVE) - MAX_EVENTS]
        elif mode == "REAL_NETWORK" or mode == "LIVE":
            EVENTS_REAL_NETWORK.append(result)
            if len(EVENTS_REAL_NETWORK) > MAX_EVENTS:
                del EVENTS_REAL_NETWORK[:len(EVENTS_REAL_NETWORK) - MAX_EVENTS]
        
        # Veritabanına kaydet (sadece REAL_NETWORK için)
        if mode == "REAL_NETWORK" or mode == "LIVE":
            decision = result.get("decision", {})
            insert_live_event(
                src_ip=flow.src_ip,
                dst_ip=flow.dst_ip,
                prob=decision.get("confidence", 0.0),
                is_attack=decision.get("is_attack", 0),
                risk_level=decision.get("risk_level", "low")
            )
        
        # Alert loglama (sadece REAL_NETWORK için)
        if mode == "REAL_NETWORK" or mode == "LIVE":
            log_alert(result)
            
    except Exception as e:
        print(f"[ERROR] Flow işleme hatası: {e}")


def data_source_worker():
    """Veri kaynağı worker thread"""
    global data_source, CURRENT_MODE, DATASET_PROCESSING_COMPLETE
    
    if data_source is None:
        return
    
    mode = data_source.get_name()
    CURRENT_MODE = mode
    print(f"[Data Source] Başlatılıyor: {mode}")
    
    # DATASET_INTELLIGENCE modunda: Run ONCE, then freeze
    if mode == "DATASET_INTELLIGENCE":
        DATASET_PROCESSING_COMPLETE = False
        processed_count = 0
        last_metrics_update = 0
        
        try:
            print("[DATASET_INTELLIGENCE] Processing dataset (one-time execution, shuffled for balanced distribution)...")
            start_time = time.time()
            
            for flow in data_source.get_flows():
                if data_source is None or not data_source.is_active():
                    break
                
                # Flow'u işle
                process_flow(flow, mode)
                processed_count += 1
                
                # Progress update with ETA
                if processed_count % 100 == 0:
                    elapsed = time.time() - start_time
                    progress = data_source.get_progress() if hasattr(data_source, 'get_progress') else None
                    
                    if progress and progress.get('total'):
                        percent = progress['percent']
                        eta_seconds = (elapsed / processed_count) * (progress['total'] - processed_count) if processed_count > 0 else 0
                        eta_min = int(eta_seconds // 60)
                        eta_sec = int(eta_seconds % 60)
                        print(f"[DATASET_INTELLIGENCE] Progress: {processed_count:,}/{progress['total']:,} ({percent:.1f}%) | ETA: {eta_min}m {eta_sec}s")
                    else:
                        rate = processed_count / elapsed if elapsed > 0 else 0
                        print(f"[DATASET_INTELLIGENCE] Processed {processed_count:,} flows... ({rate:.1f} flows/sec)")
                
                # Periodic metrics update (every 500 flows)
                if processed_count - last_metrics_update >= 500:
                    calculate_dataset_metrics()
                    last_metrics_update = processed_count
                    print(f"[DATASET_INTELLIGENCE] Intermediate metrics updated at {processed_count} flows")
            
            # Dataset processing complete - calculate final metrics
            elapsed_total = time.time() - start_time
            print(f"[DATASET_INTELLIGENCE] Processing complete: {processed_count:,} flows processed in {elapsed_total:.1f}s ({processed_count/elapsed_total:.1f} flows/sec)")
            calculate_dataset_metrics(streaming=False)  # Final metrics
            DATASET_PROCESSING_COMPLETE = True
            print("[DATASET_INTELLIGENCE] Dataset evaluation complete. Results frozen.")
            
        except Exception as e:
            print(f"[DATASET_INTELLIGENCE] Error: {e}")
            import traceback
            traceback.print_exc()
            DATASET_PROCESSING_COMPLETE = True
    
    # SIMULATED_LIVE modu: Stream dataset at 1 event/second (for demo)
    elif mode == "SIMULATED_LIVE":
        try:
            print("[SIMULATED_LIVE] Streaming dataset at 1 event/second (demo mode)...")
            for flow in data_source.get_flows():
                if data_source is None or not data_source.is_active():
                    break
                
                # Flow'u işle
                process_flow(flow, mode)
                
                # Emit one event per second (critical for demo)
                time.sleep(1.0)
        except Exception as e:
            print(f"[SIMULATED_LIVE] Error: {e}")
            import traceback
            traceback.print_exc()
    
    # REAL_NETWORK modu: Continuous Wi-Fi sniffing
    elif mode == "REAL_NETWORK":
        try:
            print("[REAL_NETWORK] Starting Wi-Fi traffic sniffing...")
            for flow in data_source.get_flows():
                if data_source is None or not data_source.is_active():
                    break
                
                # Flow'u işle
                process_flow(flow, mode)
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
        except Exception as e:
            print(f"[REAL_NETWORK] Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"[Data Source] Durduruldu: {mode}")


def start_data_source(mode: str):
    """Veri kaynağını başlat"""
    global data_source, data_source_thread, flow_aggregator, CURRENT_MODE, intelligence_engine
    
    # Önceki kaynağı durdur
    stop_data_source()
    
    CURRENT_MODE = mode
    
    # Initialize intelligence engine with correct mode
    if intelligence_engine is None or intelligence_engine.mode != mode:
        intelligence_engine = IntelligenceEngine(mode=mode)
        print(f"[IntelligenceEngine] Initialized for {mode} mode")
    
    if mode == "LIVE":
        # Canlı Wi-Fi trafik
        if flow_aggregator is None:
            flow_aggregator = FlowAggregator(window_sec=5, idle_timeout_sec=15)
        
        data_source = LiveWiFiSource(flow_aggregator)
        print("[Mode] LIVE - Canlı Wi-Fi trafik dinleniyor")
        
    elif mode == "DATASET_INTELLIGENCE" or mode == "DATASET":
        # CSV Dataset (offline test)
        # Priority: UNSW-NB15 (yeni eklenen) > CICIDS2017 > CICIDS2018
        unsw_test_path = Path("data/raw/UNSW_NB15_testing-set.csv")
        unsw_train_path = Path("data/raw/UNSW_NB15_training-set.csv")
        cicids2017_path = Path("data/raw/cicids2017_cleaned.csv")  # CICIDS2017: Attack Type column
        cicids2018_path = Path("data/raw/cic.csv")  # CICIDS2018: Label column with string values
        
        # Öncelik: UNSW-NB15 (yeni eklenen, çeşitli attack type'lar: Exploits, Fuzzers, DoS, Reconnaissance, etc.)
        if unsw_test_path.exists():
            # UNSW-NB15 kullan (attack_cat: Exploits, Fuzzers, DoS, Reconnaissance, Shellcode, Analysis, Backdoor, Worms, Normal)
            csv_path = unsw_test_path
            label_col = "label"  # Binary label (0=Normal, 1=Attack)
            attack_type_col = "attack_cat"  # Multi-class attack categories
            print(f"[Mode] DATASET_INTELLIGENCE - UNSW-NB15 Test Set: {csv_path}")
            print(f"[Mode] UNSW-NB15 attack types: Exploits, Fuzzers, DoS, Reconnaissance, Shellcode, Analysis, Backdoor, Worms, Normal")
            if unsw_train_path.exists():
                print(f"[Mode] Training set mevcut: {unsw_train_path} (model eğitimi için kullanılabilir)")
        elif cicids2017_path.exists():
            # CICIDS 2017 kullan (daha fazla attack type: DoS Hulk, PortScan, Bot, DDoS, Web Attack, Infiltration, etc.)
            csv_path = cicids2017_path
            label_col = "Attack Type"
            attack_type_col = "Attack Type"
            print(f"[Mode] DATASET_INTELLIGENCE - CICIDS 2017 verisi: {csv_path}")
            print(f"[Mode] CICIDS2017 attack types: DoS Hulk, PortScan, Bot, DDoS, Web Attack, Infiltration, etc.")
        elif cicids2018_path.exists():
            # CICIDS2018 kullan (Label kolonu: "Benign", "FTP-BruteForce", "SSH-Bruteforce", etc.)
            csv_path = cicids2018_path
            label_col = "Label"  # CICIDS2018'de Label kolonu string değerler içerir
            attack_type_col = "Label"  # Label kolonu hem label hem attack type içerir
            print(f"[Mode] DATASET_INTELLIGENCE - CICIDS2018 verisi: {csv_path}")
            print(f"[Mode] CICIDS2018 attack types: BENIGN, DoS, DDoS, Bot, PortScan, Web Attacks, BruteForce")
        else:
            print(f"[ERROR] Test CSV bulunamadı (UNSW-NB15, CICIDS2017 veya CICIDS2018)")
            return False
        
        # Memory-safe: max 10000 samples, chunk size 1000
        csv_dataset = CSVDatasetSource(
            str(csv_path), 
            label_col=label_col, 
            attack_type_col=attack_type_col,
            max_samples=10000,  # Limit for memory safety
            chunk_size=1000     # Process in chunks
        )
        # CRITICAL: Override get_name to return correct mode name
        csv_dataset.get_name = lambda: "DATASET_INTELLIGENCE"
        data_source = csv_dataset
        
    elif mode == "SIMULATED_LIVE":
        # Simulated Live Mode: Stream dataset row-by-row at 1 event/second (for demo)
        # Priority: UNSW-NB15 (yeni eklenen) > CICIDS2017 > CICIDS2018
        unsw_test_path = Path("data/raw/UNSW_NB15_testing-set.csv")
        cicids2017_path = Path("data/raw/cicids2017_cleaned.csv")
        cicids2018_path = Path("data/raw/cic.csv")
        
        # Priority: UNSW-NB15 (yeni eklenen, çeşitli attack type'lar)
        if unsw_test_path.exists():
            csv_path = unsw_test_path
            label_col = "label"
            attack_type_col = "attack_cat"
            print(f"[Mode] SIMULATED_LIVE - UNSW-NB15 streaming (1 event/sec): {csv_path}")
            print(f"[Mode] Attack types: Exploits, Fuzzers, DoS, Reconnaissance, Shellcode, Analysis, Backdoor, Worms, Normal")
        elif cicids2017_path.exists():
            csv_path = cicids2017_path
            label_col = "Attack Type"
            attack_type_col = "Attack Type"
            print(f"[Mode] SIMULATED_LIVE - CICIDS2017 streaming (1 event/sec): {csv_path}")
        elif cicids2018_path.exists():
            csv_path = cicids2018_path
            label_col = "Label"
            attack_type_col = "Label"
            print(f"[Mode] SIMULATED_LIVE - CICIDS2018 streaming (1 event/sec): {csv_path}")
            print(f"[Mode] Preserving all attack types: BENIGN, DoS, DDoS, Bot, PortScan, Web Attacks, BruteForce")
        else:
            print(f"[ERROR] Test CSV bulunamadı (UNSW-NB15, CICIDS2017 veya CICIDS2018)")
            return False
        
        # Load full dataset (no max_samples limit for simulated live)
        data_source = CSVDatasetSource(
            str(csv_path),
            label_col=label_col,
            attack_type_col=attack_type_col,
            max_samples=None,  # Load full dataset
            chunk_size=1000
        )
        
    elif mode == "REPLAY":  # Legacy mode, keep for compatibility
        # CSV Replay (canlı simülasyon)
        # Önce CICIDS 2017'yi kontrol et, yoksa UNSW-NB15 kullan
        cicids_path = Path("data/raw/cicids2017_cleaned.csv")
        unsw_path = TEST_CSV if TEST_CSV.exists() else Path("data/raw/UNSW_NB15_testing-set.csv")
        
        if cicids_path.exists():
            csv_path = cicids_path
            label_col = "Attack Type"
            attack_type_col = "Attack Type"
            print(f"[Mode] REPLAY - CICIDS 2017 canlı simülasyon: {csv_path}")
        elif unsw_path.exists():
            csv_path = unsw_path
            label_col = "label"
            attack_type_col = "attack_cat"
            print(f"[Mode] REPLAY - UNSW-NB15 canlı simülasyon: {csv_path}")
        else:
            print(f"[ERROR] Test CSV bulunamadı (CICIDS 2017 veya UNSW-NB15)")
            return False
        
        # CSVReplaySource also needs chunk-based processing
        # Create CSVDatasetSource first with memory-safe settings
        csv_dataset = CSVDatasetSource(
            str(csv_path),
            label_col=label_col,
            attack_type_col=attack_type_col,
            max_samples=10000,  # Limit for memory safety
            chunk_size=1000     # Process in chunks
        )
        data_source = CSVReplaySource(csv_dataset, replay_speed=1.0)
        
    else:
        print(f"[ERROR] Geçersiz mod: {mode}")
        return False
    
    # Worker thread başlat
    data_source_thread = threading.Thread(target=data_source_worker, daemon=True)
    data_source_thread.start()
    
    return True


def stop_data_source():
    """Veri kaynağını durdur"""
    global data_source, data_source_thread, CURRENT_MODE
    
    if data_source:
        if hasattr(data_source, "stop"):
            data_source.stop()
        data_source = None
    
    if data_source_thread and data_source_thread.is_alive():
        # Thread'i beklemek yerine None yap
        data_source_thread = None
    
    print("[Data Source] Durduruldu")


def calculate_dataset_metrics(streaming: bool = True):
    """
    Calculate performance metrics from EVENTS_DATASET
    
    Args:
        streaming: If True, calculate rolling window metrics. If False, calculate final full dataset metrics.
    """
    global METRICS, DATASET_PROGRESS
    
    # Use correct event list based on mode
    events_list = EVENTS_DATASET_INTELLIGENCE if CURRENT_MODE == "DATASET_INTELLIGENCE" else []
    
    if len(events_list) == 0:
        METRICS.update({
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "calculated": False,
            "processing": False,
            "total_samples": 0,
            "mode": "streaming" if streaming else "final"
        })
        return
    
    try:
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
        
        y_true = []
        y_pred = []
        
        # Determine which events to use
        if streaming:
            # Streaming: Use last N events (rolling window)
            window_size = METRICS.get("streaming_window_size", 1000)
            events_to_process = events_list[-window_size:] if len(events_list) > window_size else events_list
            METRICS["mode"] = "streaming"
            METRICS["processing"] = True  # Still processing
        else:
            # Final: Use all events
            events_to_process = events_list
            METRICS["mode"] = "final"
            METRICS["processing"] = False  # Processing complete
        
        for event in events_to_process:
            flow = event.get("flow", {})
            decision = event.get("decision", {})
            
            # CRITICAL: For metrics calculation:
            # - y_true: Ground truth from dataset labels (BENIGN=0, any attack=1)
            # - y_pred: Model prediction (for performance evaluation)
            
            # Get ground truth label from dataset
            ground_truth_label = None
            ground_truth_attack_type = decision.get("ground_truth", "")
            
            # Method 1: Try to get label from flow.label (if available)
            true_label = flow.get("label")
            if true_label is not None:
                try:
                    ground_truth_label = int(true_label)
                except (ValueError, TypeError):
                    pass
            
            # Method 2: Derive from ground truth attack_type (BENIGN -> 0, any attack -> 1)
            if ground_truth_label is None:
                if ground_truth_attack_type:
                    ground_truth_upper = ground_truth_attack_type.upper().strip()
                    # BENIGN, NORMAL, NORMAL TRAFFIC -> 0 (Normal)
                    # Any other attack type -> 1 (Attack)
                    if ground_truth_upper in ["NORMAL", "BENIGN", "NORMAL TRAFFIC", ""]:
                        ground_truth_label = 0  # Normal
                    else:
                        ground_truth_label = 1  # Attack (FTP-Patator, DoS, DDoS, etc.)
                else:
                    ground_truth_label = 0  # Default to Normal
            
            # y_true: Ground truth from dataset (for metrics)
            y_true.append(ground_truth_label)
            
            # y_pred: Model prediction (NOT ground truth status)
            # In dataset mode, decision["is_attack"] is ground truth (for display)
            # We need decision["predicted_is_attack"] for metrics
            pred_label = decision.get("predicted_is_attack")
            if pred_label is None:
                # Fallback: If predicted_is_attack not available, we can't calculate metrics properly
                # Skip this sample or use a default (but this shouldn't happen in dataset mode)
                print(f"[Metrics Warning] predicted_is_attack not found, skipping sample")
                y_true.pop()  # Remove the appended ground truth since we're skipping
                continue
            y_pred.append(int(pred_label))
        
        if len(y_true) > 0 and len(y_pred) > 0:
            # En az 10 örnek olmalı ve hem 0 hem 1 olmalı
            unique_labels = set(y_true)
            if len(y_true) >= 10 and len(unique_labels) > 1:
                accuracy = accuracy_score(y_true, y_pred)
                precision = precision_score(y_true, y_pred, zero_division=0)
                recall = recall_score(y_true, y_pred, zero_division=0)
                f1 = f1_score(y_true, y_pred, zero_division=0)
                
                # Confusion matrix
                cm = confusion_matrix(y_true, y_pred)
                tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
                
                METRICS.update({
                    "accuracy": float(accuracy),
                    "precision": float(precision),
                    "recall": float(recall),
                    "f1_score": float(f1),
                    "calculated": True,
                    "total_samples": len(y_true),
                    "true_positives": int(tp),
                    "true_negatives": int(tn),
                    "false_positives": int(fp),
                    "false_negatives": int(fn)
                })
                
                mode_str = "Streaming" if streaming else "Final"
                print(f"[Metrics {mode_str}] Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
                print(f"[Metrics {mode_str}] TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn} (Samples: {len(y_true)})")
            else:
                METRICS.update({
                    "accuracy": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1_score": 0.0,
                    "calculated": False,
                    "total_samples": len(y_true),
                    "unique_labels": len(unique_labels)
                })
                print(f"[Metrics] Yeterli veri yok (Samples: {len(y_true)}, Unique labels: {len(unique_labels)})")
        else:
            METRICS.update({
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "calculated": False,
                "total_samples": 0
            })
            print(f"[Metrics] Veri yok (y_true: {len(y_true)}, y_pred: {len(y_pred)})")
    except Exception as e:
        print(f"[Metrics] Hesaplama hatası: {e}")
        import traceback
        traceback.print_exc()
        METRICS = {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "calculated": False,
            "total_samples": 0
        }


# ====== FLASK ROUTES ======

@app.route("/")
def index():
    """Ana endpoint - sistem durumu"""
    # Mod bazlı event sayısı
    if CURRENT_MODE == "DATASET_INTELLIGENCE":
        events_count = len(EVENTS_DATASET_INTELLIGENCE)
    elif CURRENT_MODE == "SIMULATED_LIVE":
        events_count = len(EVENTS_SIMULATED_LIVE)
    elif CURRENT_MODE == "REAL_NETWORK":
        events_count = len(EVENTS_REAL_NETWORK)
    else:
        events_count = 0
    
    return jsonify({
        "service": "Intelligent IDS",
        "status": "running",
        "mode": CURRENT_MODE,
        "events_count": events_count
    })


@app.route("/mode/<mode>", methods=["POST"])
def set_mode(mode: str):
    """Mod değiştir"""
    valid_modes = ["DATASET_INTELLIGENCE", "SIMULATED_LIVE", "REAL_NETWORK"]
    mode_upper = mode.upper()
    
    # Legacy mode support
    if mode_upper == "DATASET":
        mode_upper = "DATASET_INTELLIGENCE"
    elif mode_upper == "LIVE":
        mode_upper = "REAL_NETWORK"
    elif mode_upper == "REPLAY":
        mode_upper = "SIMULATED_LIVE"
    
    if mode_upper in valid_modes:
        success = start_data_source(mode_upper)
        if success:
            return jsonify({"ok": True, "mode": mode_upper})
        else:
            return jsonify({"ok": False, "error": "Data source başlatılamadı"}), 400
    else:
        return jsonify({"ok": False, "error": f"Geçersiz mod. Geçerli modlar: {', '.join(valid_modes)}"}), 400


@app.route("/mode", methods=["GET"])
def get_mode():
    """Mevcut modu al"""
    return jsonify({"mode": CURRENT_MODE})


@app.route("/events", methods=["GET"])
def get_events():
    """Son event'leri al (mod bazlı)"""
    limit = int(request.args.get("limit", 200))
    mode = request.args.get("mode", CURRENT_MODE)
    
    # Support both new and legacy mode names
    if mode == "DATASET_INTELLIGENCE" or mode == "DATASET":
        events = EVENTS_DATASET_INTELLIGENCE[-limit:]
    elif mode == "SIMULATED_LIVE" or mode == "REPLAY":
        events = EVENTS_SIMULATED_LIVE[-limit:]
    elif mode == "REAL_NETWORK" or mode == "LIVE":
        events = EVENTS_REAL_NETWORK[-limit:]
    else:
        events = []
    
    return jsonify(events)


@app.route("/stats", methods=["GET"])
def get_stats():
    """İstatistikleri al (mod bazlı)"""
    mode = request.args.get("mode", CURRENT_MODE)
    
    # Support both new and legacy mode names
    if mode == "DATASET_INTELLIGENCE" or mode == "DATASET":
        events = EVENTS_DATASET_INTELLIGENCE
    elif mode == "SIMULATED_LIVE" or mode == "REPLAY":
        events = EVENTS_SIMULATED_LIVE
    elif mode == "REAL_NETWORK" or mode == "LIVE":
        events = EVENTS_REAL_NETWORK
    else:
        events = []
    
    total = len(events)
    low = medium = high = 0
    attacks = 0
    
    # Attack type distribution (for DATASET mode - CICIDS2017)
    attack_distribution = {}
    
    for ev in events:
        decision = ev.get("decision", {})
        risk = decision.get("risk_level", "low")
        if risk == "low":
            low += 1
        elif risk == "medium":
            medium += 1
        else:
            high += 1
        
        if decision.get("is_attack", 0) == 1:
            attacks += 1
            # Collect attack type distribution (preserve CICIDS2017 names)
            if mode == "DATASET_INTELLIGENCE" or mode == "DATASET":
                attack_type = decision.get("attack_type", "Unknown")
                if attack_type and attack_type != "NORMAL":
                    attack_distribution[attack_type] = attack_distribution.get(attack_type, 0) + 1
    
    # Metrics (only for DATASET_INTELLIGENCE mode, only if processing complete)
    metrics = None
    if mode == "DATASET_INTELLIGENCE" or mode == "DATASET":
        if DATASET_PROCESSING_COMPLETE:
            metrics = METRICS
        else:
            metrics = {"calculated": False, "processing": True}
    
    return jsonify({
        "total_events": total,
        "low_risk": low,
        "medium_risk": medium,
        "high_risk": high,
        "attacks": attacks,
        "mode": mode,
        "metrics": metrics,
        "attack_distribution": attack_distribution if (mode == "DATASET_INTELLIGENCE" or mode == "DATASET") else {},
        "processing_complete": DATASET_PROCESSING_COMPLETE if (mode == "DATASET_INTELLIGENCE" or mode == "DATASET") else True
    })


@app.route("/metrics", methods=["GET"])
def get_metrics():
    """Get performance metrics (DATASET mode only)"""
    if CURRENT_MODE != "DATASET":
        return jsonify({
            "error": "Metrics only available in DATASET mode",
            "mode": CURRENT_MODE
        }), 400
    
    return jsonify(METRICS)


@app.route("/progress", methods=["GET"])
def get_progress():
    """Get dataset processing progress"""
    if CURRENT_MODE != "DATASET":
        return jsonify({
            "error": "Progress only available in DATASET mode",
            "mode": CURRENT_MODE
        }), 400
    
    return jsonify(DATASET_PROGRESS)


@app.route("/ingest/flows", methods=["POST"])
def ingest_flows():
    """Live agent'dan flow'ları al (geriye uyumluluk için)"""
    data = request.get_json(silent=True) or {}
    flows = data.get("flows", [])
    
    if not isinstance(flows, list):
        return jsonify({"ok": False, "error": "'flows' list olmalı"}), 400
    
    added = 0
    for flow_dict in flows:
        try:
            # FlowData'ya çevir
            flow = FlowData(
                src_ip=flow_dict.get("src_ip", ""),
                dst_ip=flow_dict.get("dst_ip", ""),
                src_port=flow_dict.get("src_port", 0),
                dst_port=flow_dict.get("dst_port", 0),
                proto=flow_dict.get("proto", "IP"),
                duration=flow_dict.get("duration", 0.0),
                packets_fwd=flow_dict.get("packets_fwd", 0),
                packets_bwd=flow_dict.get("packets_bwd", 0),
                bytes_fwd=flow_dict.get("bytes_fwd", 0),
                bytes_bwd=flow_dict.get("bytes_bwd", 0),
                syn=flow_dict.get("syn", 0),
                ack=flow_dict.get("ack", 0),
                rst=flow_dict.get("rst", 0),
                fin=flow_dict.get("fin", 0),
                unique_dst_ports=flow_dict.get("unique_dst_ports", 0),
            )
            
            # İşle (LIVE modunda - agent'dan gelen flow'lar)
            process_flow(flow, "LIVE")
            added += 1
        except Exception as e:
            print(f"[INGEST] Flow işleme hatası: {e}")
            continue
    
    return jsonify({
        "ok": True,
        "count": len(flows),
        "added": added,
        "total_events": len(EVENTS_REAL_NETWORK) if CURRENT_MODE == "REAL_NETWORK" else len(EVENTS_SIMULATED_LIVE) if CURRENT_MODE == "SIMULATED_LIVE" else len(EVENTS_DATASET_INTELLIGENCE)
    })


# Dashboard HTML'i ayrı dosyadan yüklenecek
try:
    import sys
    import importlib.util
    # UTF-8 encoding ile yükle
    spec = importlib.util.spec_from_file_location("intelligent_ids_dashboard", "intelligent_ids_dashboard.py")
    dashboard_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dashboard_module)
    DASHBOARD_HTML = dashboard_module.DASHBOARD_HTML
    print("[✓] Dashboard template loaded successfully")
except Exception as e:
    print(f"[!] Dashboard template load error: {e}")
    import traceback
    traceback.print_exc()
    # Fallback: basit HTML
    DASHBOARD_HTML = "<html><body><h1>Intelligent IDS Dashboard</h1><p>Dashboard template yüklenemedi. Error: " + str(e) + "</p></body></html>"

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Ana dashboard"""
    return render_template_string(DASHBOARD_HTML)


# ====== INITIALIZATION ======

def initialize():
    """Sistemi başlat"""
    global intelligence_engine
    
    print("=" * 60)
    print("INTELLIGENT IDS - Initializing")
    print("=" * 60)
    
    # Veritabanı
    init_db()
    print("[✓] Database initialized")
    
    # Intelligence Engine (will be initialized based on mode)
    # Don't initialize here - will be set when mode is selected
    intelligence_engine = None
    print("[✓] Intelligence Engine will be initialized based on mode")
    
    # Varsayılan mod: DATASET_INTELLIGENCE (sunum için)
    start_data_source("DATASET_INTELLIGENCE")
    print("[✓] Data source started (DATASET_INTELLIGENCE mode)")
    
    print("=" * 60)
    print("System ready!")
    print(f"Dashboard: http://{API_HOST}:{API_PORT}/dashboard")
    print("=" * 60)


# ====== MAIN ======

if __name__ == "__main__":
    from flask import request
    
    initialize()
    app.run(host=API_HOST, port=API_PORT, debug=True, threaded=True)
