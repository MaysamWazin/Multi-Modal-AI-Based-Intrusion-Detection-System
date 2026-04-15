import pandas as pd
from src.data.database import init_db, insert_alert, DB_PATH

from flask import Flask, render_template_string, jsonify
from tensorflow.keras.models import load_model
from datetime import datetime

import numpy as np
import sqlite3

from src.data.loader import prepare_unsw

# ====== AYARLAR ======
DATA_PATH = "data/raw/UNSW_NB15_testing-set.csv"  # gerekirse ismini değiştir
MODEL_PATH = "ids_cnn_lstm.h5"
THRESHOLD = 0.6

# Ham CSV'den saldırı tiplerini oku
raw_df = pd.read_csv(DATA_PATH)

if "attack_cat" in raw_df.columns:
    ATTACK_TYPES = raw_df["attack_cat"].astype(str).values
else:
    ATTACK_TYPES = np.array(["unknown"] * len(raw_df))

# Özellikleri ve label'ı hazırla (preprocess uygulanmış)
X_raw, y_raw = prepare_unsw(DATA_PATH)
X = X_raw.reshape((X_raw.shape[0], 1, X_raw.shape[1]))
y = y_raw

model = load_model(MODEL_PATH)

# Veritabanı
init_db()

app = Flask(__name__)

current_idx = 0  # sıradaki paketin index'i


def get_stats_and_last_alerts(limit: int = 10):
    """
    SQLite veritabanından genel istatistikleri ve son N alert kaydını döner.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Toplam alert sayısı
    cur.execute("SELECT COUNT(*) FROM alerts;")
    total = cur.fetchone()[0]

    # Toplam saldırı / normal sayısı
    cur.execute("SELECT COUNT(*) FROM alerts WHERE is_attack = 1;")
    attacks = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM alerts WHERE is_attack = 0;")
    normals = cur.fetchone()[0]

    # Son alertler (en son eklenenler)
    cur.execute(
        """
        SELECT created_at, sample_idx, is_attack, probability, true_label, attack_type
        FROM alerts
        ORDER BY id DESC
        LIMIT ?;
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()

    last_alerts = []
    for r in rows:
        created_at, sample_idx, is_attack, prob, true_label, attack_type = r
        last_alerts.append({
            "created_at": created_at,
            "sample_idx": sample_idx,
            "is_attack": is_attack,
            "probability": prob,
            "true_label": true_label,
            "attack_type": attack_type,
        })

    return total, attacks, normals, last_alerts


TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Akıllı IDS Demo</title>
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0f172a;
            color: #e5e7eb;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 24px 0;
        }
        .layout {
            display: grid;
            grid-template-columns: 520px 520px;
            gap: 24px;
        }
        .card {
            background: #020617;
            border-radius: 18px;
            padding: 24px 28px;
            box-shadow: 0 20px 40px rgba(15, 23, 42, 0.7);
            border: 1px solid #1f2937;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }
        .badge-normal {
            background: rgba(22, 163, 74, 0.1);
            color: #4ade80;
            border: 1px solid rgba(74, 222, 128, 0.4);
        }
        .badge-attack {
            background: rgba(220, 38, 38, 0.1);
            color: #fca5a5;
            border: 1px solid rgba(248, 113, 113, 0.5);
        }
        .title {
            font-size: 22px;
            margin-top: 12px;
            margin-bottom: 4px;
        }
        .subtitle {
            font-size: 13px;
            color: #9ca3af;
            margin-bottom: 16px;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }
        .metric {
            background: #020617;
            border-radius: 12px;
            padding: 10px 12px;
            border: 1px solid #111827;
        }
        .metric-label {
            font-size: 11px;
            color: #9ca3af;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .metric-value {
            font-size: 15px;
            font-weight: 600;
        }
        .metric-good {
            color: #4ade80;
        }
        .metric-bad {
            color: #f87171;
        }
        .footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
            font-size: 12px;
            color: #6b7280;
        }
        .buttons {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 12px;
        }
        .btn {
            border: none;
            border-radius: 999px;
            padding: 8px 16px;
            font-size: 13px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: white;
        }
        .btn-secondary {
            background: #020617;
            color: #e5e7eb;
            border: 1px solid #374151;
        }
        .dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: #22c55e;
        }
        .section-title {
            font-size: 16px;
            margin-bottom: 8px;
        }
        .stats-row {
            display: flex;
            gap: 12px;
            font-size: 13px;
            margin-bottom: 8px;
            color: #9ca3af;
        }
        .stat-pill {
            padding: 4px 10px;
            border-radius: 999px;
            background: #020617;
            border: 1px solid #111827;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }
        th, td {
            padding: 6px 8px;
            text-align: left;
            border-bottom: 1px solid #1f2937;
        }
        th {
            color: #9ca3af;
            font-weight: 500;
        }
        tr.attack-row td {
            color: #fecaca;
        }
        tr.normal-row td {
            color: #bbf7d0;
        }
        .pill-attack {
            padding: 2px 8px;
            border-radius: 999px;
            background: rgba(220, 38, 38, 0.15);
            border: 1px solid rgba(248, 113, 113, 0.6);
            color: #fecaca;
            font-size: 11px;
        }
        .pill-normal {
            padding: 2px 8px;
            border-radius: 999px;
            background: rgba(22, 163, 74, 0.15);
            border: 1px solid rgba(74, 222, 128, 0.6);
            color: #bbf7d0;
            font-size: 11px;
        }
    </style>
</head>
<body>
    <div class="layout">
        <!-- Sol: Canlı paket kartı -->
        <div class="card">
            <div>
                <span id="badge" class="badge {% if pred == 1 %}badge-attack{% else %}badge-normal{% endif %}">
                    {% if pred == 1 %}Saldırı Tespit Edildi{% else %}Normal Trafik{% endif %}
                </span>
                <h1 class="title">Akıllı IDS – Canlı Trafik Analizi</h1>
                <div class="subtitle">
                    Model her paket/akış kaydını gerçek zamanlı analiz eder. Aşağıdaki bilgiler son işlenen kayda aittir.
                </div>
            </div>

            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Model Çıkışı (Olasılık)</div>
                    <div id="prob" class="metric-value {% if prob >= threshold %}metric-bad{% else %}metric-good{% endif %}">
                        {{ prob_str }}
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">Model Kararı</div>
                    <div id="pred" class="metric-value {% if pred == 1 %}metric-bad{% else %}metric-good{% endif %}">
                        {% if pred == 1 %} SALDIRI {% else %} NORMAL {% endif %}
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">Gerçek Etiket</div>
                    <div id="true_label" class="metric-value">
                        {% if true_label == 1 %} Saldırı {% else %} Normal {% endif %}
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">Saldırı Tipi</div>
                    <div id="attack_type" class="metric-value">
                        {% if true_label == 1 %} {{ attack_type }} {% else %} - {% endif %}
                    </div>
                </div>
            </div>

            <div class="footer">
                <div>
                    Paket ID: <strong id="idx">#{{ idx }}</strong>  
                    •  Zaman: <span id="time">{{ time_str }}</span>
                </div>
                <div>
                    Eşik (threshold): <strong id="thresh">{{ threshold }}</strong>  
                    •  Toplam kayıt: <strong id="total">{{ total }}</strong>
                </div>
            </div>

            <div class="buttons">
                <button class="btn btn-secondary" onclick="location.reload()">
                    Paneli Yenile
                </button>
                <button class="btn btn-secondary" onclick="fetchRandom()">
                    <span class="dot"></span>
                    Rastgele Paket
                </button>
                <button class="btn btn-primary" onclick="fetchNext()">
                    Sonraki Paketi Analiz Et
                </button>
            </div>
        </div>

        <!-- Sağ: Veritabanı istatistikleri ve son alarmlar -->
        <div class="card">
            <h2 class="section-title">Merkezi IDS Kayıtları</h2>
            <div class="subtitle">
                IDS servisine gelen tüm kararlar (dashboard, agent, API çağrıları) ortak veritabanında saklanır.
            </div>

            <div class="stats-row">
                <div class="stat-pill">
                    Toplam Alarm: <strong>{{ total_alerts }}</strong>
                </div>
                <div class="stat-pill">
                    Saldırı: <strong>{{ total_attacks }}</strong>
                </div>
                <div class="stat-pill">
                    Normal: <strong>{{ total_normals }}</strong>
                </div>
            </div>

            <div class="subtitle" style="margin-top: 12px;">
                Son 10 Alarm Kaydı
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Zaman</th>
                        <th>Tür</th>
                        <th>Olasılık</th>
                        <th>Gerçek</th>
                        <th>Saldırı Tipi</th>
                        <th>Sample ID</th>
                    </tr>
                </thead>
                <tbody>
                    {% if last_alerts %}
                        {% for a in last_alerts %}
                            <tr class="{% if a.is_attack == 1 %}attack-row{% else %}normal-row{% endif %}">
                                <td>{{ a.created_at }}</td>
                                <td>
                                    {% if a.is_attack == 1 %}
                                        <span class="pill-attack">Saldırı</span>
                                    {% else %}
                                        <span class="pill-normal">Normal</span>
                                    {% endif %}
                                </td>
                                <td>{{ "%.3f"|format(a.probability) }}</td>
                                <td>
                                    {% if a.true_label == 1 %}
                                        Saldırı
                                    {% elif a.true_label == 0 %}
                                        Normal
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>{{ a.attack_type }}</td>
                                <td>{% if a.sample_idx >= 0 %}#{{ a.sample_idx }}{% else %}-{% endif %}</td>
                            </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="6">Henüz kayıt yok.</td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function updateFromData(data) {
            const probEl = document.getElementById("prob");
            const predEl = document.getElementById("pred");
            const trueEl = document.getElementById("true_label");
            const idxEl = document.getElementById("idx");
            const timeEl = document.getElementById("time");
            const badgeEl = document.getElementById("badge");
            const attackEl = document.getElementById("attack_type");

            probEl.textContent = data.prob.toFixed(3);
            predEl.textContent = data.pred === 1 ? "SALDIRI" : "NORMAL";
            trueEl.textContent = data.true_label === 1 ? "Saldırı" : "Normal";
            idxEl.textContent = "#" + data.idx;
            timeEl.textContent = data.time;
            attackEl.textContent = data.pred === 1 ? data.attack_type : "-";

            // renkler
            if (data.pred === 1) {
                predEl.classList.remove("metric-good");
                predEl.classList.add("metric-bad");
                badgeEl.classList.remove("badge-normal");
                badgeEl.classList.add("badge-attack");
                badgeEl.textContent = "Saldırı Tespit Edildi";
            } else {
                predEl.classList.remove("metric-bad");
                predEl.classList.add("metric-good");
                badgeEl.classList.remove("badge-attack");
                badgeEl.classList.add("badge-normal");
                badgeEl.textContent = "Normal Trafik";
            }

            if (data.prob >= data.threshold) {
                probEl.classList.remove("metric-good");
                probEl.classList.add("metric-bad");
            } else {
                probEl.classList.remove("metric-bad");
                probEl.classList.add("metric-good");
            }
        }

        async function fetchNext() {
            try {
                const res = await fetch("/api/next");
                const data = await res.json();
                await updateFromData(data);
            } catch (e) {
                console.error(e);
            }
        }

        async function fetchRandom() {
            try {
                const res = await fetch("/api/random");
                const data = await res.json();
                await updateFromData(data);
            } catch (e) {
                console.error(e);
            }
        }

        // Canlı akış istersen:
        // setInterval(fetchNext, 1000);
    </script>

</body>
</html>
"""


def get_prediction(idx: int):
    sample = X[idx: idx + 1]
    prob = float(model.predict(sample, verbose=0)[0][0])
    pred = 1 if prob > THRESHOLD else 0
    true_label = int(y[idx])
    attack_type = ATTACK_TYPES[idx]
    return prob, pred, true_label, attack_type


@app.route("/")
def index():
    global current_idx
    prob, pred, true_label, attack_type = get_prediction(current_idx)
    now = datetime.now().strftime("%H:%M:%S")

    total_alerts, total_attacks, total_normals, last_alerts = get_stats_and_last_alerts(10)

    return render_template_string(
        TEMPLATE,
        idx=current_idx,
        prob=prob,
        prob_str=f"{prob:.3f}",
        pred=pred,
        true_label=true_label,
        attack_type=attack_type,
        threshold=THRESHOLD,
        total=len(y),
        time_str=now,
        total_alerts=total_alerts,
        total_attacks=total_attacks,
        total_normals=total_normals,
        last_alerts=last_alerts,
    )


@app.route("/api/next")
def api_next():
    global current_idx
    current_idx = (current_idx + 1) % len(y)
    prob, pred, true_label, attack_type = get_prediction(current_idx)
    now = datetime.now().strftime("%H:%M:%S")

    # Veritabanına logla
    insert_alert(
        sample_idx=current_idx,
        is_attack=pred,
        prob=prob,
        true_label=true_label,
        attack_type=attack_type,
    )

    return jsonify({
        "idx": int(current_idx),
        "prob": float(prob),
        "pred": int(pred),
        "true_label": int(true_label),
        "attack_type": attack_type,
        "time": now,
        "threshold": THRESHOLD,
        "total": int(len(y))
    })


@app.route("/api/random")
def api_random():
    global current_idx
    current_idx = int(np.random.randint(0, len(y)))
    prob, pred, true_label, attack_type = get_prediction(current_idx)
    now = datetime.now().strftime("%H:%M:%S")

    insert_alert(
        sample_idx=current_idx,
        is_attack=pred,
        prob=prob,
        true_label=true_label,
        attack_type=attack_type,
    )

    return jsonify({
        "idx": int(current_idx),
        "prob": float(prob),
        "pred": int(pred),
        "true_label": int(true_label),
        "attack_type": attack_type,
        "time": now,
        "threshold": THRESHOLD,
        "total": int(len(y))
    })


if __name__ == "__main__":
    app.run(debug=True)
