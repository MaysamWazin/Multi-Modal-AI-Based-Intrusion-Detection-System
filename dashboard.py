# dashboard.py
# Canlı IDS olayları için basit web dashboard

from flask import Flask, render_template_string
from src.data.database import get_last_events, init_db

app = Flask(__name__)


TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Akıllı IDS - Canlı Olaylar</title>
    <style>
        /* Cybersecurity Background Animation Layer */
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0f172a;
            color: #e5e7eb;
            margin: 0;
            padding: 20px;
            position: relative;
        }

        #cyberBg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
            overflow: hidden;
            background: #0f172a;
        }

        /* Lock/Shield Icons */
        .security-icon {
            position: absolute;
            opacity: 0.35;
            animation: float 20s infinite ease-in-out;
        }

        .security-icon svg {
            width: 80px;
            height: 80px;
            stroke: #93c5fd;
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
            0%, 100% { opacity: 0.25; }
            50% { opacity: 0.50; }
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
            stroke: #60a5fa;
            stroke-width: 2;
            opacity: 0.40;
            stroke-dasharray: 5, 5;
            animation: networkFlow 8s linear infinite;
        }

        @keyframes networkFlow {
            0% { stroke-dashoffset: 0; opacity: 0.35; }
            50% { opacity: 0.50; }
            100% { stroke-dashoffset: 20; opacity: 0.35; }
        }

        /* Data Flow Particles */
        .data-particle {
            position: absolute;
            width: 5px;
            height: 5px;
            background: #93c5fd;
            border-radius: 50%;
            opacity: 0.75;
            animation: dataFlow 15s infinite linear;
            box-shadow: 0 0 10px rgba(147, 197, 253, 1);
        }

        @keyframes dataFlow {
            0% {
                transform: translate(0, 0);
                opacity: 0;
            }
            10% {
                opacity: 0.85;
            }
            90% {
                opacity: 0.85;
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

        h1 {
            margin-bottom: 4px;
        }
        .subtitle {
            color: #9ca3af;
            font-size: 14px;
            margin-bottom: 16px;
        }
        .stats {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }
        .stat-card {
            background: #020617;
            border-radius: 12px;
            padding: 12px 16px;
            border: 1px solid #1f2937;
            font-size: 13px;
            backdrop-filter: blur(2px);
        }
        .stat-title {
            color: #9ca3af;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 4px;
        }
        .stat-value {
            font-size: 16px;
            font-weight: 600;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-top: 8px;
        }
        th, td {
            padding: 6px 8px;
            border-bottom: 1px solid #1f2937;
            text-align: left;
        }
        th {
            background: #020617;
            color: #9ca3af;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 11px;
        }
        .tag-low {
            background: rgba(34,197,94,0.1);
            color: #4ade80;
        }
        .tag-medium {
            background: rgba(234,179,8,0.1);
            color: #facc15;
        }
        .tag-high {
            background: rgba(248,113,113,0.1);
            color: #fca5a5;
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

    <h1>Akıllı IDS – Canlı Olaylar</h1>
    <div class="subtitle">
        Son {{ total }} canlı trafik kaydı gösteriliyor (en yeni en üstte).
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-title">Toplam Olay</div>
            <div class="stat-value">{{ total }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">Normal (Low Risk)</div>
            <div class="stat-value">{{ low_count }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">Şüpheli (Medium Risk)</div>
            <div class="stat-value">{{ medium_count }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">Saldırı (High Risk)</div>
            <div class="stat-value">{{ high_count }}</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Zaman</th>
                <th>Kaynak IP</th>
                <th>Hedef IP</th>
                <th>Risk</th>
                <th>Olasılık</th>
            </tr>
        </thead>
        <tbody>
        {% for ev in events %}
            <tr>
                <td>{{ ev.created_at }}</td>
                <td>{{ ev.src_ip }}</td>
                <td>{{ ev.dst_ip }}</td>
                <td>
                    {% if ev.risk_level == 'high' %}
                        <span class="tag tag-high">HIGH</span>
                    {% elif ev.risk_level == 'medium' %}
                        <span class="tag tag-medium">MEDIUM</span>
                    {% else %}
                        <span class="tag tag-low">LOW</span>
                    {% endif %}
                </td>
                <td>{{ "%.3f"|format(ev.prob) }}</td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


@app.route("/")
def index():
    init_db()
    rows = get_last_events(limit=50)

    # rows: (id, src_ip, dst_ip, prob, is_attack, risk_level, created_at)
    events = []
    low = medium = high = 0

    for row in rows:
        ev = {
            "id": row[0],
            "src_ip": row[1],
            "dst_ip": row[2],
            "prob": row[3],
            "is_attack": row[4],
            "risk_level": row[5],
            "created_at": row[6],
        }
        events.append(ev)

        if ev["risk_level"] == "high":
            high += 1
        elif ev["risk_level"] == "medium":
            medium += 1
        else:
            low += 1

    total = len(events)

    return render_template_string(
        TEMPLATE,
        events=events,
        total=total,
        low_count=low,
        medium_count=medium,
        high_count=high,
    )


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5001, debug=True)
