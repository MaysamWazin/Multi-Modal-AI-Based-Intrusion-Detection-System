"""
Intelligent IDS Dashboard HTML Template
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligent IDS - Akıllı Saldırı Tespit Sistemi</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #0a0e27;
            color: #e5e7eb;
            padding: 20px;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Cybersecurity Background Animation Layer */
        #cyberBg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
            overflow: hidden;
            background: #0a0e27;
        }

        /* Lock/Shield Icons */
        .security-icon {
            position: absolute;
            opacity: 0.35;
            animation: float 20s infinite ease-in-out;
        }

        .security-icon svg {
            width: 100px;
            height: 100px;
            stroke: #93c5fd;
            fill: none;
            stroke-width: 2;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            25% { transform: translate(40px, -40px) rotate(5deg); }
            50% { transform: translate(-30px, 30px) rotate(-5deg); }
            75% { transform: translate(30px, 40px) rotate(3deg); }
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.25; }
            50% { opacity: 0.50; }
        }

        .security-icon:nth-child(1) { top: 8%; left: 3%; animation-delay: 0s; animation-duration: 28s; }
        .security-icon:nth-child(2) { top: 25%; right: 8%; animation-delay: -6s; animation-duration: 32s; }
        .security-icon:nth-child(3) { bottom: 30%; left: 10%; animation-delay: -12s; animation-duration: 30s; }
        .security-icon:nth-child(4) { bottom: 12%; right: 15%; animation-delay: -18s; animation-duration: 35s; }
        .security-icon:nth-child(5) { top: 45%; left: 48%; animation-delay: -9s; animation-duration: 40s; }
        .security-icon:nth-child(6) { top: 65%; right: 25%; animation-delay: -15s; animation-duration: 26s; }
        .security-icon:nth-child(7) { top: 15%; left: 75%; animation-delay: -3s; animation-duration: 33s; }
        .security-icon:nth-child(8) { bottom: 45%; right: 5%; animation-delay: -21s; animation-duration: 29s; }

        .security-icon:nth-child(odd) svg { animation: pulse 5s infinite ease-in-out; }
        .security-icon:nth-child(even) svg { animation: pulse 6s infinite ease-in-out; }

        /* Network Lines */
        .network-line {
            stroke: #60a5fa;
            stroke-width: 2;
            opacity: 0.40;
            stroke-dasharray: 6, 6;
            animation: networkFlow 10s linear infinite;
        }

        @keyframes networkFlow {
            0% { stroke-dashoffset: 0; opacity: 0.35; }
            50% { opacity: 0.50; }
            100% { stroke-dashoffset: 24; opacity: 0.35; }
        }

        /* Data Flow Particles */
        .data-particle {
            position: absolute;
            width: 5px;
            height: 5px;
            background: #93c5fd;
            border-radius: 50%;
            opacity: 0.75;
            animation: dataFlow 18s infinite linear;
            box-shadow: 0 0 10px rgba(147, 197, 253, 1);
        }

        @keyframes dataFlow {
            0% {
                transform: translate(0, 0);
                opacity: 0;
            }
            8% {
                opacity: 0.85;
            }
            92% {
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
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(15, 23, 42, 0.85);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
        }
        
        .header h1 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header .subtitle {
            color: #94a3b8;
            font-size: 14px;
        }
        
        .mode-selector {
            display: flex;
            gap: 12px;
            margin-top: 16px;
        }
        
        .mode-btn {
            padding: 10px 20px;
            border-radius: 8px;
            border: 2px solid transparent;
            background: rgba(30, 41, 59, 0.6);
            color: #e5e7eb;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
            font-size: 14px;
        }
        
        .mode-btn:hover {
            background: rgba(30, 41, 59, 0.8);
            border-color: #60a5fa;
        }
        
        .mode-btn.active {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            border-color: #60a5fa;
            color: white;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .stat-card {
            background: rgba(15, 23, 42, 0.85);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
        }
        
        .stat-card .label {
            color: #94a3b8;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        .stat-card .value {
            font-size: 28px;
            font-weight: 700;
            color: #e5e7eb;
        }
        
        .stat-card.highlight {
            border-color: #60a5fa;
            background: rgba(59, 130, 246, 0.1);
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 24px;
        }
        
        @media (max-width: 1200px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .events-panel {
            background: rgba(15, 23, 42, 0.85);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
        }
        
        .events-panel h2 {
            font-size: 20px;
            margin-bottom: 16px;
            color: #e5e7eb;
        }
        
        .events-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        
        .events-table th {
            text-align: left;
            padding: 12px 8px;
            color: #94a3b8;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .events-table td {
            padding: 12px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            color: #cbd5e1;
        }
        
        .events-table tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .badge.low {
            background: rgba(34, 197, 94, 0.2);
            color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        
        .badge.medium {
            background: rgba(234, 179, 8, 0.2);
            color: #facc15;
            border: 1px solid rgba(234, 179, 8, 0.3);
        }
        
        .badge.high {
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        .badge.critical {
            background: rgba(220, 38, 38, 0.3);
            color: #fca5a5;
            border: 1px solid rgba(220, 38, 38, 0.5);
        }
        
        .badge.attack {
            background: rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.5);
        }
        
        .badge.normal {
            background: rgba(34, 197, 94, 0.2);
            color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }
        
        .info-panel {
            background: rgba(15, 23, 42, 0.85);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
        }
        
        .info-panel h3 {
            font-size: 16px;
            margin-bottom: 12px;
            color: #e5e7eb;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 13px;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-item .key {
            color: #94a3b8;
        }
        
        .info-item .value {
            color: #e5e7eb;
            font-weight: 500;
        }
        
        .metrics-panel {
            background: rgba(15, 23, 42, 0.85);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
        }
        
        .metric-item {
            margin-bottom: 16px;
        }
        
        .metric-item:last-child {
            margin-bottom: 0;
        }
        
        .metric-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 12px;
            color: #94a3b8;
        }
        
        .metric-bar {
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .metric-fill {
            height: 100%;
            background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
            transition: width 0.3s;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #94a3b8;
        }
        
        .empty-state svg {
            width: 64px;
            height: 64px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #94a3b8;
        }
        
        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top: 3px solid #60a5fa;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .alert-banner {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 24px;
            display: none;
        }
        
        .alert-banner.show {
            display: block;
        }
        
        .alert-banner .alert-content {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .alert-banner .alert-icon {
            font-size: 24px;
        }
        
        .alert-banner .alert-text {
            flex: 1;
            font-size: 14px;
        }
        
        .mono {
            font-family: 'Courier New', monospace;
            font-size: 12px;
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
            <line class="network-line" x1="8%" y1="15%" x2="28%" y2="35%" style="animation-delay: 0s;"/>
            <line class="network-line" x1="72%" y1="20%" x2="88%" y2="42%" style="animation-delay: -2.5s;"/>
            <line class="network-line" x1="12%" y1="55%" x2="38%" y2="75%" style="animation-delay: -5s;"/>
            <line class="network-line" x1="65%" y1="60%" x2="82%" y2="80%" style="animation-delay: -1.5s;"/>
            <line class="network-line" x1="22%" y1="12%" x2="48%" y2="50%" style="animation-delay: -4s;"/>
            <line class="network-line" x1="78%" y1="32%" x2="58%" y2="70%" style="animation-delay: -6s;"/>
            <line class="network-line" x1="42%" y1="8%" x2="68%" y2="28%" style="animation-delay: -2s;"/>
            <line class="network-line" x1="18%" y1="68%" x2="32%" y2="88%" style="animation-delay: -4.5s;"/>
            <line class="network-line" x1="55%" y1="45%" x2="75%" y2="65%" style="animation-delay: -3s;"/>
            <line class="network-line" x1="35%" y1="25%" x2="52%" y2="45%" style="animation-delay: -1s;"/>
        </svg>

        <!-- Data Flow Particles -->
        <div class="data-particle" style="--dx: 250px; --dy: -180px; top: 18%; left: 8%; animation-delay: 0s;"></div>
        <div class="data-particle" style="--dx: -200px; --dy: 140px; top: 32%; right: 12%; animation-delay: -2.5s;"></div>
        <div class="data-particle" style="--dx: 280px; --dy: 220px; top: 48%; left: 18%; animation-delay: -5s;"></div>
        <div class="data-particle" style="--dx: -240px; --dy: -200px; top: 62%; right: 22%; animation-delay: -1.5s;"></div>
        <div class="data-particle" style="--dx: 320px; --dy: 120px; top: 28%; left: 38%; animation-delay: -3.5s;"></div>
        <div class="data-particle" style="--dx: -180px; --dy: 280px; top: 52%; right: 32%; animation-delay: -6s;"></div>
        <div class="data-particle" style="--dx: 220px; --dy: -240px; top: 72%; left: 28%; animation-delay: -2s;"></div>
        <div class="data-particle" style="--dx: -300px; --dy: 180px; top: 38%; right: 48%; animation-delay: -4s;"></div>
        <div class="data-particle" style="--dx: 260px; --dy: 150px; top: 55%; left: 45%; animation-delay: -1s;"></div>
        <div class="data-particle" style="--dx: -220px; --dy: -260px; top: 25%; right: 35%; animation-delay: -3s;"></div>
    </div>

    <div class="container">
        <div class="header">
            <h1>🛡️ Intelligent IDS</h1>
            <div class="subtitle">Akıllı Saldırı Tespit Sistemi - Multi-Source Intelligent Architecture</div>
            
            <div class="mode-selector">
                <button class="mode-btn" data-mode="DATASET_INTELLIGENCE" onclick="setMode('DATASET_INTELLIGENCE')">📊 Dataset Intelligence</button>
                <button class="mode-btn" data-mode="SIMULATED_LIVE" onclick="setMode('SIMULATED_LIVE')">▶️ Simulated Live</button>
                <button class="mode-btn" data-mode="REAL_NETWORK" onclick="setMode('REAL_NETWORK')">📡 Real Network</button>
            </div>
        </div>
        
        <div class="alert-banner" id="alertBanner">
            <div class="alert-content">
                <div class="alert-icon">🚨</div>
                <div class="alert-text" id="alertText"></div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Active Data Source</div>
                <div class="value" id="activeSource">-</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Events</div>
                <div class="value" id="totalEvents">0</div>
            </div>
            <div class="stat-card highlight">
                <div class="label">Attacks Detected</div>
                <div class="value" id="attacksCount">0</div>
            </div>
            <div class="stat-card">
                <div class="label">High Risk</div>
                <div class="value" id="highRisk">0</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="events-panel">
                <h2>Event Timeline</h2>
                <div id="eventsContainer">
                    <div class="loading">
                        <div class="spinner"></div>
                        <div>Loading events...</div>
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="info-panel">
                    <h3>System Information</h3>
                    <div class="info-item">
                        <span class="key">Mode:</span>
                        <span class="value" id="currentMode">-</span>
                    </div>
                    <div class="info-item">
                        <span class="key">Status:</span>
                        <span class="value" id="systemStatus">Active</span>
                    </div>
                    <div class="info-item">
                        <span class="key">Last Update:</span>
                        <span class="value" id="lastUpdate">-</span>
                    </div>
                </div>
                
                <div class="metrics-panel">
                    <h3>Performance Metrics <span id="metricsMode" style="font-size: 12px; color: #94a3b8;">(DATASET only)</span></h3>
                    <div id="metricsContainer">
                        <div class="metric-item">
                            <div class="metric-label">
                                <span>Accuracy</span>
                                <span id="metricAccuracy">-</span>
                            </div>
                            <div class="metric-bar">
                                <div class="metric-fill" id="metricAccuracyBar" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">
                                <span>Precision</span>
                                <span id="metricPrecision">-</span>
                            </div>
                            <div class="metric-bar">
                                <div class="metric-fill" id="metricPrecisionBar" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">
                                <span>Recall</span>
                                <span id="metricRecall">-</span>
                            </div>
                            <div class="metric-bar">
                                <div class="metric-fill" id="metricRecallBar" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">
                                <span>F1 Score</span>
                                <span id="metricF1">-</span>
                            </div>
                            <div class="metric-bar">
                                <div class="metric-fill" id="metricF1Bar" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    <div id="confusionMatrixContainer" style="margin-top: 20px; display: none;">
                        <div style="margin-bottom: 8px; font-weight: 600; font-size: 12px; color: #94a3b8;">Confusion Matrix:</div>
                        <div id="confusionMatrix" style="font-size: 10px; font-family: monospace; overflow-x: auto;"></div>
                    </div>
                    <div id="attackDistribution" style="margin-top: 20px; font-size: 12px; color: #94a3b8;">
                        <div style="margin-bottom: 8px; font-weight: 600;">Attack Distribution:</div>
                        <div id="attackDistList" style="max-height: 150px; overflow-y: auto;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentMode = 'DATASET_INTELLIGENCE';
        let events = [];
        let updateInterval;
        
        // Mod değiştir
        async function setMode(mode) {
            try {
                const response = await fetch(`/mode/${mode}`, { method: 'POST' });
                const data = await response.json();
                if (data.ok) {
                    currentMode = mode;
                    updateModeButtons();
                    loadEvents();
                }
            } catch (error) {
                console.error('Mode change error:', error);
            }
        }
        
        // Mod butonlarını güncelle
        function updateModeButtons() {
            document.querySelectorAll('.mode-btn').forEach(btn => {
                if (btn.dataset.mode === currentMode) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }
        
        // Event'leri yükle
        async function loadEvents() {
            try {
                const [eventsRes, statsRes, modeRes] = await Promise.all([
                    fetch(`/events?limit=100&mode=${currentMode}`),
                    fetch(`/stats?mode=${currentMode}`),
                    fetch('/mode')
                ]);
                
                const eventsData = await eventsRes.json();
                const statsData = await statsRes.json();
                const modeData = await modeRes.json();
                
                events = eventsData;
                currentMode = modeData.mode || currentMode;
                
                updateStats(statsData);
                updateEvents(events);
                updateModeButtons();
                updateMetrics(statsData);
            } catch (error) {
                console.error('Load error:', error);
            }
        }
        
        // İstatistikleri güncelle
        function updateStats(stats) {
            document.getElementById('activeSource').textContent = stats.mode || '-';
            document.getElementById('totalEvents').textContent = stats.total_events || 0;
            document.getElementById('attacksCount').textContent = stats.attacks || 0;
            document.getElementById('highRisk').textContent = stats.high_risk || 0;
            document.getElementById('currentMode').textContent = stats.mode || '-';
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            
            // Show attack distribution for DATASET_INTELLIGENCE mode
            if ((currentMode === 'DATASET_INTELLIGENCE' || currentMode === 'DATASET') && stats.attack_distribution) {
                const dist = stats.attack_distribution;
                const distList = document.getElementById('attackDistList');
                if (Object.keys(dist).length > 0) {
                    let html = '';
                    const sorted = Object.entries(dist).sort((a, b) => b[1] - a[1]);
                    sorted.forEach(([type, count]) => {
                        html += `<div style="margin-bottom: 4px;">${type}: <strong>${count}</strong></div>`;
                    });
                    distList.innerHTML = html;
                } else {
                    distList.innerHTML = '<div style="color: #64748b;">No attacks detected yet</div>';
                }
            } else {
                document.getElementById('attackDistList').innerHTML = '<div style="color: #64748b;">N/A (DATASET mode only)</div>';
            }
        }
        
        // Event'leri göster
        function updateEvents(eventsList) {
            const container = document.getElementById('eventsContainer');
            
            if (eventsList.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div>📭</div>
                        <div>No events yet. Waiting for data...</div>
                    </div>
                `;
                return;
            }
            
            // Son 50 event'i göster (en yeni en üstte)
            const recentEvents = eventsList.slice(-50).reverse();
            
            let html = '<table class="events-table"><thead><tr>';
            html += '<th>Time</th><th>Source</th><th>Destination</th><th>Attack Type</th><th>Severity</th><th>Status</th>';
            html += '</tr></thead><tbody>';
            
            recentEvents.forEach(ev => {
                const flow = ev.flow || {};
                const decision = ev.decision || {};
                const timestamp = new Date((ev.timestamp || Date.now() / 1000) * 1000);
                
                // Get attack type - preserve original CICIDS2018/CICIDS2017 attack names
                // Do NOT collapse to generic - show exact attack types from dataset
                let attackType = decision.attack_type || 'NORMAL';
                let groundTruth = decision.ground_truth || null;
                let mode = decision.mode || currentMode;
                
                // In Dataset Intelligence Mode: Use ground truth attack type (preserve original names)
                // Examples: "DoS Hulk", "FTP-BruteForce", "PortScan", "Bot", "DDoS", "Web Attack", "SSH-Bruteforce", etc.
                if ((mode === 'dataset' || mode === 'dataset_intelligence') && groundTruth) {
                    attackType = groundTruth;  // Use exact ground truth label
                }
                
                // Format attack type: Only replace underscores with spaces, preserve original case and format
                // Do NOT convert to uppercase or collapse to generic
                if (attackType !== 'NORMAL' && attackType !== 'Generic Attack' && attackType !== 'GENERIC_ATTACK' && attackType !== 'Generic Anomaly') {
                    attackType = attackType.replace(/_/g, ' ');  // Only replace underscores
                    // Preserve original format: "DoS Hulk", "FTP-BruteForce", "PortScan", "Bot", etc.
                }
                
                // Get confidence: Show both raw and smoothed (if available)
                const rawConfidence = decision.raw_confidence !== undefined ? (decision.raw_confidence * 100) : null;
                const smoothedConfidence = (decision.confidence || 0) * 100;
                const confidence = smoothedConfidence;  // Use smoothed for display
                
                // Format confidence display - show percentage, mark low confidence with color only
                const confidenceLabel = `${confidence.toFixed(1)}%`;
                const isLowConfidence = confidence < 60;  // For styling only, not for label
                
                const severity = decision.severity || decision.risk_level || 'INFO';
                const isAttack = decision.is_attack || 0;
                
                // Get explanation (if available)
                const explanation = decision.explanation || '';
                
                const severityClass = severity.toLowerCase();
                const attackBadge = isAttack ? 'attack' : 'normal';
                
                // Color code attack types - support all CICIDS2018/CICIDS2017 attack types
                let attackTypeClass = '';
                const attackTypeUpper = attackType.toUpperCase();
                
                // DoS attacks (DoS Hulk, DDoS, etc.)
                if (attackTypeUpper.includes('DOS') || attackTypeUpper.includes('DDOS')) {
                    attackTypeClass = 'style="color: #f87171;"';
                }
                // Port Scan attacks (PortScan, Port Scan, etc.)
                else if (attackTypeUpper.includes('PORTSCAN') || attackTypeUpper.includes('PORT SCAN')) {
                    attackTypeClass = 'style="color: #fbbf24;"';
                }
                // Web attacks (Web Attack, etc.)
                else if (attackTypeUpper.includes('WEB ATTACK') || attackTypeUpper.includes('WEB')) {
                    attackTypeClass = 'style="color: #fb923c;"';
                }
                // Brute Force attacks (FTP-BruteForce, SSH-Bruteforce, FTP-Patator, etc.)
                else if (attackTypeUpper.includes('BRUTEFORCE') || attackTypeUpper.includes('BRUTE FORCE') || attackTypeUpper.includes('PATATOR')) {
                    attackTypeClass = 'style="color: #ef4444;"';
                }
                // Bot attacks
                else if (attackTypeUpper.includes('BOT')) {
                    attackTypeClass = 'style="color: #dc2626;"';
                }
                // Normal traffic
                else if (attackType === 'NORMAL' || attackTypeUpper === 'BENIGN' || attackTypeUpper === 'NORMAL TRAFFIC') {
                    attackTypeClass = 'style="color: #4ade80;"';
                }
                // Other attacks (default red)
                else if (attackTypeUpper !== 'NORMAL' && attackTypeUpper !== 'BENIGN') {
                    attackTypeClass = 'style="color: #f87171;"';
                }
                
                // Show similarity predictions for LIVE mode
                let similarityInfo = '';
                if (mode === 'live' && decision.similarity_predictions) {
                    const top3 = decision.similarity_predictions.slice(0, 3);
                    similarityInfo = `<div style="font-size: 10px; color: #94a3b8; margin-top: 2px;">Similar: ${top3.map(p => `${p.attack_type} (${(p.probability * 100).toFixed(0)}%)`).join(', ')}</div>`;
                }
                
                // Show ground truth for DATASET mode
                let groundTruthInfo = '';
                if (mode === 'dataset' && groundTruth && groundTruth !== attackType) {
                    groundTruthInfo = `<div style="font-size: 10px; color: #fbbf24; margin-top: 2px;">Ground Truth: ${groundTruth}</div>`;
                }
                
                html += `<tr>`;
                html += `<td class="mono">${timestamp.toLocaleTimeString()}</td>`;
                html += `<td class="mono">${flow.src_ip || '-'}</td>`;
                html += `<td class="mono">${flow.dst_ip || '-'}</td>`;
                html += `<td ${attackTypeClass}>${attackType}${similarityInfo}${groundTruthInfo}</td>`;
                
                html += `<td><span class="badge ${severityClass}">${severity}</span></td>`;
                
                // Status: Show explanation only if available and meaningful
                let statusHtml = `<span class="badge ${attackBadge}">${isAttack ? 'ATTACK' : 'NORMAL'}</span>`;
                if (explanation && explanation.length > 0 && !explanation.includes('Uncertain') && !explanation.includes('Low certainty')) {
                    statusHtml += `<div style="font-size: 9px; color: #94a3b8; margin-top: 2px;">${explanation}</div>`;
                }
                html += `<td>${statusHtml}</td>`;
                html += `</tr>`;
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
            
            // Son attack varsa alert göster
            const lastAttack = recentEvents.find(ev => ev.decision?.is_attack === 1);
            if (lastAttack) {
                showAlert(lastAttack);
            }
        }
        
        // Alert göster
        function showAlert(event) {
            const banner = document.getElementById('alertBanner');
            const text = document.getElementById('alertText');
            const decision = event.decision || {};
            const flow = event.flow || {};
            
            text.textContent = `🚨 ${decision.attack_type || 'ATTACK'} detected: ${flow.src_ip || ''} → ${flow.dst_ip || ''} (${(decision.confidence || 0) * 100}% confidence)`;
            banner.classList.add('show');
            
            setTimeout(() => {
                banner.classList.remove('show');
            }, 10000);
        }
        
        // Metrikleri güncelle
        function updateMetrics(stats) {
            const metrics = stats.metrics || {};
            const metricsPanel = document.getElementById('metricsPanel');
            
            // Show/hide metrics panel based on mode
            if (currentMode === 'DATASET_INTELLIGENCE' || currentMode === 'DATASET') {
                if (metricsPanel) metricsPanel.style.display = 'block';
            } else {
                if (metricsPanel) metricsPanel.style.display = 'none';
            }
            
            // Only show metrics for DATASET_INTELLIGENCE mode
            if ((currentMode === 'DATASET_INTELLIGENCE' || currentMode === 'DATASET') && metrics.calculated) {
                // Metrikleri göster
                const accuracy = (metrics.accuracy || 0) * 100;
                const precision = (metrics.precision || 0) * 100;
                const recall = (metrics.recall || 0) * 100;
                const f1 = (metrics.f1_score || 0) * 100;
                
                document.getElementById('metricAccuracy').textContent = accuracy.toFixed(2) + '%';
                document.getElementById('metricPrecision').textContent = precision.toFixed(2) + '%';
                document.getElementById('metricRecall').textContent = recall.toFixed(2) + '%';
                document.getElementById('metricF1').textContent = f1.toFixed(2) + '%';
                
                document.getElementById('metricAccuracyBar').style.width = accuracy + '%';
                document.getElementById('metricPrecisionBar').style.width = precision + '%';
                document.getElementById('metricRecallBar').style.width = recall + '%';
                document.getElementById('metricF1Bar').style.width = f1 + '%';
                
                // Show confusion matrix
                if (metrics.confusion_matrix && metrics.confusion_matrix_labels) {
                    displayConfusionMatrix(metrics.confusion_matrix, metrics.confusion_matrix_labels);
                }
                
                // Show binary confusion matrix info
                if (metrics.true_positives !== undefined) {
                    const cmInfo = `TP: ${metrics.true_positives}, TN: ${metrics.true_negatives}, FP: ${metrics.false_positives}, FN: ${metrics.false_negatives}`;
                    console.log('Binary Confusion Matrix:', cmInfo);
                }
            } else if ((currentMode === 'DATASET_INTELLIGENCE' || currentMode === 'DATASET') && metrics.processing) {
                // Still processing
                document.getElementById('metricAccuracy').textContent = 'Processing...';
                document.getElementById('metricPrecision').textContent = 'Processing...';
                document.getElementById('metricRecall').textContent = 'Processing...';
                document.getElementById('metricF1').textContent = 'Processing...';
                const cmContainer = document.getElementById('confusionMatrixContainer');
                if (cmContainer) cmContainer.style.display = 'none';
            } else {
                // Not DATASET mode or no metrics
                document.getElementById('metricAccuracy').textContent = '-';
                document.getElementById('metricPrecision').textContent = '-';
                document.getElementById('metricRecall').textContent = '-';
                document.getElementById('metricF1').textContent = '-';
                
                document.getElementById('metricAccuracyBar').style.width = '0%';
                document.getElementById('metricPrecisionBar').style.width = '0%';
                document.getElementById('metricRecallBar').style.width = '0%';
                document.getElementById('metricF1Bar').style.width = '0%';
                const cmContainer = document.getElementById('confusionMatrixContainer');
                if (cmContainer) cmContainer.style.display = 'none';
            }
        }
        
        // Confusion Matrix Display
        function displayConfusionMatrix(cm, labels) {
            const container = document.getElementById('confusionMatrix');
            const cmContainer = document.getElementById('confusionMatrixContainer');
            
            if (!cm || !labels || labels.length === 0 || !container || !cmContainer) {
                if (cmContainer) cmContainer.style.display = 'none';
                return;
            }
            
            cmContainer.style.display = 'block';
            
            // Create table
            let html = '<table style="border-collapse: collapse; font-size: 9px; width: 100%;">';
            
            // Header row
            html += '<tr><th style="border: 1px solid #444; padding: 4px; background: #1e293b;">Predicted →</th>';
            labels.forEach(label => {
                const shortLabel = label.length > 10 ? label.substring(0, 10) + '...' : label;
                html += `<th style="border: 1px solid #444; padding: 4px; background: #1e293b; text-align: center; min-width: 50px;" title="${label}">${shortLabel}</th>`;
            });
            html += '</tr>';
            
            // Data rows
            const maxValue = Math.max(...cm.flat());
            labels.forEach((label, i) => {
                const shortLabel = label.length > 10 ? label.substring(0, 10) + '...' : label;
                html += `<tr><th style="border: 1px solid #444; padding: 4px; background: #1e293b; text-align: right;" title="${label}">${shortLabel}</th>`;
                labels.forEach((_, j) => {
                    const value = cm[i] && cm[i][j] ? cm[i][j] : 0;
                    const intensity = maxValue > 0 ? Math.min(1, value / maxValue) : 0;
                    const bgColor = `rgba(59, 130, 246, ${intensity * 0.5 + 0.1})`;
                    html += `<td style="border: 1px solid #444; padding: 4px; text-align: center; background: ${bgColor};">${value}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</table>';
            container.innerHTML = html;
        }
        
        // İlk yükleme
        loadEvents();
        updateModeButtons();
        
        // Otomatik güncelleme
        updateInterval = setInterval(loadEvents, 2000);
    </script>
</body>
</html>
"""
