"""
Tez ve Poster için Akademik Görseller Oluşturucu
Bu script tez, poster ve jüri sunumu için gerekli tüm akademik şekilleri üretir.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Arrow
import numpy as np
from pathlib import Path
import seaborn as sns

OUTPUT_DIR = Path("poster_visuals")
OUTPUT_DIR.mkdir(exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9


def fig_1_system_architecture():
    """Şekil 1: Sistem Genel Mimarisi Diyagramı"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Renk paleti
    colors = {
        'data': '#E3F2FD',
        'process': '#BBDEFB',
        'ai': '#90CAF9',
        'rule': '#64B5F6',
        'decision': '#42A5F5',
        'dashboard': '#2196F3',
        'output': '#1976D2'
    }
    
    # Veri Kaynakları (Üst)
    sources_y = 8.5
    sources = [
        ("Dataset\nIntelligence\nMode", 2.5),
        ("Simulated\nLive Mode", 7),
        ("Real Network\nMode (Wi-Fi)", 11.5)
    ]
    
    for label, x in sources:
        box = FancyBboxPatch((x-1, sources_y-0.5), 2, 1,
                            boxstyle="round,pad=0.1", 
                            facecolor=colors['data'], 
                            edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, sources_y, label, ha='center', va='center', 
                fontsize=9, weight='bold')
    
    # Veri İşleme Katmanı
    process_y = 6.5
    process_box = FancyBboxPatch((1, process_y-0.4), 12, 0.8,
                                boxstyle="round,pad=0.15",
                                facecolor=colors['process'],
                                edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box)
    ax.text(7, process_y, "Feature Extraction & Preprocessing", 
            ha='center', va='center', fontsize=11, weight='bold')
    
    # Hibrit Tespit Katmanı
    detection_y = 4.5
    # Rule-Based
    rule_box = FancyBboxPatch((2, detection_y-0.6), 3.5, 1.2,
                             boxstyle="round,pad=0.1",
                             facecolor=colors['rule'],
                             edgecolor='black', linewidth=1.5)
    ax.add_patch(rule_box)
    ax.text(3.75, detection_y, "Rule-Based\nDetection", 
            ha='center', va='center', fontsize=10, weight='bold')
    
    # AI-Based
    ai_box = FancyBboxPatch((6.5, detection_y-0.6), 3.5, 1.2,
                           boxstyle="round,pad=0.1",
                           facecolor=colors['ai'],
                           edgecolor='black', linewidth=1.5)
    ax.add_patch(ai_box)
    ax.text(8.25, detection_y, "AI-Based\nDetection", 
            ha='center', va='center', fontsize=10, weight='bold')
    
    # Ensemble/Voting
    ensemble_box = FancyBboxPatch((10.5, detection_y-0.6), 2.5, 1.2,
                                 boxstyle="round,pad=0.1",
                                 facecolor=colors['decision'],
                                 edgecolor='black', linewidth=1.5)
    ax.add_patch(ensemble_box)
    ax.text(11.75, detection_y, "Ensemble\nVoting", 
            ha='center', va='center', fontsize=10, weight='bold')
    
    # Karar Katmanı
    decision_y = 2.5
    decision_box = FancyBboxPatch((4, decision_y-0.4), 6, 0.8,
                                 boxstyle="round,pad=0.15",
                                 facecolor=colors['decision'],
                                 edgecolor='black', linewidth=2)
    ax.add_patch(decision_box)
    ax.text(7, decision_y, "Final Decision Engine", 
            ha='center', va='center', fontsize=11, weight='bold')
    
    # Dashboard
    dashboard_y = 0.8
    dashboard_box = FancyBboxPatch((5, dashboard_y-0.4), 4, 0.8,
                                  boxstyle="round,pad=0.15",
                                  facecolor=colors['dashboard'],
                                  edgecolor='black', linewidth=2)
    ax.add_patch(dashboard_box)
    ax.text(7, dashboard_y, "Real-time Dashboard", 
            ha='center', va='center', fontsize=11, weight='bold', color='white')
    
    # Ok işaretleri
    for x in [2.5, 7, 11.5]:
        ax.arrow(x, sources_y-0.5, 0, -0.7, head_width=0.2, 
                head_length=0.15, fc='black', ec='black', lw=1.5)
    
    ax.arrow(7, process_y-0.4, 0, -0.7, head_width=0.3, 
            head_length=0.15, fc='black', ec='black', lw=1.5)
    
    for x in [3.75, 8.25, 11.75]:
        ax.arrow(x, detection_y-0.6, 0, -0.7, head_width=0.2, 
                head_length=0.15, fc='black', ec='black', lw=1.5)
    
    ax.arrow(7, decision_y-0.4, 0, -0.7, head_width=0.3, 
            head_length=0.15, fc='black', ec='black', lw=1.5)
    
    # Başlık
    ax.text(7, 9.7, "Intelligent IDS - System Architecture", 
            ha='center', va='center', fontsize=14, weight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig_1_system_architecture.png", 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Figure 1: System Architecture created")


def fig_2_workflow_modes():
    """Şekil 2: Sistem Çalışma Modları Akış Diyagramı"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.suptitle("System Operation Modes - Workflow Diagrams", 
                 fontsize=14, weight='bold', y=0.98)
    
    colors = ['#E1F5FE', '#B3E5FC', '#81D4FA']
    mode_names = ["Dataset Intelligence Mode", "Simulated Live Mode", "Real Network Mode"]
    
    for idx, (ax, color, mode_name) in enumerate(zip(axes, colors, mode_names)):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_title(mode_name, fontsize=11, weight='bold', pad=10)
        
        y_pos = 8
        if idx == 0:
            boxes = [
                ("CSV Dataset\n(Test Set)", 5, 8),
                ("Feature\nExtraction", 5, 6),
                ("Model\nInference", 5, 4),
                ("Metrics\nCalculation", 5, 2),
            ]
        elif idx == 1:
            boxes = [
                ("CSV Dataset\n(Streaming)", 5, 8),
                ("1 Event/sec\nGeneration", 5, 6),
                ("Real-time\nAnalysis", 5, 4),
                ("Event Log\nStorage", 5, 2),
            ]
        else:
            boxes = [
                ("Wi-Fi\nSniffing", 5, 8),
                ("Packet\nCapture", 5, 6),
                ("Instant\nAnalysis", 5, 4),
                ("Live Alerts", 5, 2),
            ]
        
        for label, x, y in boxes:
            box = FancyBboxPatch((x-1.5, y-0.6), 3, 1.2,
                                boxstyle="round,pad=0.1",
                                facecolor=color,
                                edgecolor='black', linewidth=1.5)
            ax.add_patch(box)
            ax.text(x, y, label, ha='center', va='center', 
                   fontsize=9, weight='bold')
            
            if y > 2:
                ax.arrow(x, y-0.6, 0, -0.9, head_width=0.25, 
                        head_length=0.15, fc='black', ec='black', lw=1.5)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig_2_workflow_modes.png", 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Figure 2: Workflow Modes created")


def fig_3_hybrid_detection():
    """Şekil 3: Hibrit Saldırı Tespit Mimarisi"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Input
    input_box = FancyBboxPatch((5, 8.5), 2, 0.8,
                              boxstyle="round,pad=0.1",
                              facecolor='#CFD8DC',
                              edgecolor='black', linewidth=1.5)
    ax.add_patch(input_box)
    ax.text(6, 8.9, "Network Flow\nData", ha='center', va='center', 
           fontsize=10, weight='bold')
    
    # İki paralel yol
    # Rule-Based (Sol)
    rule_y = 6
    rule_box = FancyBboxPatch((1.5, rule_y-0.8), 3.5, 1.6,
                             boxstyle="round,pad=0.1",
                             facecolor='#64B5F6',
                             edgecolor='black', linewidth=2)
    ax.add_patch(rule_box)
    ax.text(3.25, rule_y, "Rule-Based\nDetection\nEngine", 
           ha='center', va='center', fontsize=10, weight='bold')
    
    ax.text(2, rule_y-1.5, "• Port Scan Detection\n• SYN Flood Detection\n• DDoS Detection\n• RST Spike Detection", 
           ha='left', va='top', fontsize=8, style='italic')
    
    # AI-Based (Sağ)
    ai_y = 6
    ai_box = FancyBboxPatch((7, ai_y-0.8), 3.5, 1.6,
                           boxstyle="round,pad=0.1",
                           facecolor='#42A5F5',
                           edgecolor='black', linewidth=2)
    ax.add_patch(ai_box)
    ax.text(8.75, ai_y, "AI-Based\nDetection\nEngine", 
           ha='center', va='center', fontsize=10, weight='bold')
    
    ax.text(7.5, ai_y-1.5, "• RandomForest Classifier\n• CNN-LSTM Deep Model\n• Ensemble Voting\n• Multi-class Inference", 
           ha='left', va='top', fontsize=8, style='italic')
    
    # Ensemble/Voting
    ensemble_y = 3.5
    ensemble_box = FancyBboxPatch((4, ensemble_y-0.6), 4, 1.2,
                                 boxstyle="round,pad=0.1",
                                 facecolor='#2196F3',
                                 edgecolor='black', linewidth=2)
    ax.add_patch(ensemble_box)
    ax.text(6, ensemble_y, "Ensemble/Voting\nMechanism", 
           ha='center', va='center', fontsize=11, weight='bold', color='white')
    
    # Final Decision
    decision_y = 1.5
    decision_box = FancyBboxPatch((4.5, decision_y-0.5), 3, 1,
                                 boxstyle="round,pad=0.15",
                                 facecolor='#1976D2',
                                 edgecolor='black', linewidth=2.5)
    ax.add_patch(decision_box)
    ax.text(6, decision_y, "Final Decision\n& Risk Level", 
           ha='center', va='center', fontsize=11, weight='bold', color='white')
    
    # Oklar
    ax.arrow(6, 8.5, -2.25, -1.2, head_width=0.2, head_length=0.15, 
            fc='black', ec='black', lw=1.5)
    ax.arrow(6, 8.5, 1.75, -1.2, head_width=0.2, head_length=0.15, 
            fc='black', ec='black', lw=1.5)
    
    ax.arrow(3.25, rule_y-0.8, 1.25, -0.7, head_width=0.2, head_length=0.15, 
            fc='black', ec='black', lw=1.5)
    ax.arrow(8.75, ai_y-0.8, -1.5, -0.7, head_width=0.2, head_length=0.15, 
            fc='black', ec='black', lw=1.5)
    
    ax.arrow(6, ensemble_y-0.6, 0, -0.7, head_width=0.25, head_length=0.15, 
            fc='black', ec='black', lw=1.5)
    
    # Başlık
    ax.text(6, 9.7, "Hybrid Attack Detection Architecture", 
           ha='center', va='center', fontsize=14, weight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig_3_hybrid_detection.png", 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Figure 3: Hybrid Detection Architecture created")


def fig_4_preprocessing_pipeline():
    """Şekil 4: Veri Seti Ön İşleme ve Özellik Çıkarımı Süreci"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    colors = ['#FFF9C4', '#FFECB3', '#FFCCBC', '#C8E6C9', '#BBDEFB']
    
    steps = [
        ("CSV\nReading", 1.5),
        ("Data\nCleaning", 3.5),
        ("Feature\nSelection", 5.5),
        ("Label\nMapping", 7.5),
        ("Train/Test\nSplit", 9.5),
        ("Feature\nEngineering", 11.5),
        ("Model\nReady", 13)
    ]
    
    for idx, (label, x) in enumerate(steps):
        color_idx = min(idx, len(colors)-1)
        box = FancyBboxPatch((x-0.7, 2.5), 1.4, 1.5,
                            boxstyle="round,pad=0.1",
                            facecolor=colors[color_idx],
                            edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, 3.25, label, ha='center', va='center', 
               fontsize=9, weight='bold')
        
        if idx < len(steps) - 1:
            ax.arrow(x+0.7, 3.25, 0.5, 0, head_width=0.15, 
                    head_length=0.1, fc='black', ec='black', lw=1.5)
    
    # Alt detaylar
    details = [
        ("Raw CSV\n(UNSW-NB15,\nCICIDS2017)", 1.5, 1.2),
        ("Handle\nMissing\nValues", 3.5, 1.2),
        ("44 Features\nExtracted", 5.5, 1.2),
        ("Binary/Multi\nClass Labels", 7.5, 1.2),
        ("70/30 or\n80/20 Split", 9.5, 1.2),
        ("Normalization\n& Scaling", 11.5, 1.2),
        ("Processed\nDataset", 13, 1.2)
    ]
    
    for label, x, y in details:
        ax.text(x, y, label, ha='center', va='center', 
               fontsize=7, style='italic', color='#424242')
    
    ax.text(7, 5.2, "Data Preprocessing and Feature Extraction Pipeline", 
           ha='center', va='center', fontsize=13, weight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig_4_preprocessing_pipeline.png", 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Figure 4: Preprocessing Pipeline created")


def fig_5_model_architecture():
    """Şekil 5: Model Mimarisi Diyagramı"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle("Model Architectures", fontsize=14, weight='bold', y=0.98)
    
    # RandomForest
    ax1 = axes[0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title("RandomForest Classifier", fontsize=12, weight='bold', pad=10)
    
    # Input
    input_box = FancyBboxPatch((4, 8.5), 2, 0.8,
                              boxstyle="round,pad=0.1",
                              facecolor='#E1F5FE',
                              edgecolor='black', linewidth=1.5)
    ax1.add_patch(input_box)
    ax1.text(5, 8.9, "44 Features", ha='center', va='center', 
            fontsize=10, weight='bold')
    
    # Decision Trees
    trees_y = 6
    for i, x in enumerate([2, 5, 8]):
        tree_box = FancyBboxPatch((x-0.8, trees_y-0.8), 1.6, 1.6,
                                 boxstyle="round,pad=0.1",
                                 facecolor='#BBDEFB',
                                 edgecolor='black', linewidth=1.5)
        ax1.add_patch(tree_box)
        ax1.text(x, trees_y, f"Tree {i+1}", ha='center', va='center', 
                fontsize=9, weight='bold')
        ax1.arrow(5, 8.5, x-5, trees_y-7.3, head_width=0.15, 
                 head_length=0.1, fc='black', ec='black', lw=1.2)
    
    ax1.text(5, trees_y-1.2, "... (n_estimators=300)", ha='center', 
            va='center', fontsize=8, style='italic')
    
    # Voting
    vote_box = FancyBboxPatch((4, 3.5), 2, 0.8,
                             boxstyle="round,pad=0.1",
                             facecolor='#90CAF9',
                             edgecolor='black', linewidth=1.5)
    ax1.add_patch(vote_box)
    ax1.text(5, 3.9, "Voting", ha='center', va='center', 
            fontsize=10, weight='bold')
    
    # Output
    output_box = FancyBboxPatch((4, 1.5), 2, 0.8,
                               boxstyle="round,pad=0.1",
                               facecolor='#42A5F5',
                               edgecolor='black', linewidth=1.5)
    ax1.add_patch(output_box)
    ax1.text(5, 1.9, "Binary/Class\nProbability", ha='center', va='center', 
            fontsize=9, weight='bold', color='white')
    
    for x in [2, 5, 8]:
        ax1.arrow(x, trees_y-0.8, 3-x, 2.3, head_width=0.15, 
                 head_length=0.1, fc='black', ec='black', lw=1.2)
    
    ax1.arrow(5, 3.5, 0, -0.9, head_width=0.2, head_length=0.15, 
             fc='black', ec='black', lw=1.5)
    
    # CNN-LSTM
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title("CNN-LSTM Deep Learning Model", fontsize=12, weight='bold', pad=10)
    
    layers = [
        ("Input\n(1, 44)", 5, 8.5, '#E1F5FE'),
        ("Conv1D\n(32 filters,\nkernel=1)", 5, 7.2, '#BBDEFB'),
        ("Conv1D\n(64 filters,\nkernel=1)", 5, 5.9, '#90CAF9'),
        ("LSTM\n(64 units)", 5, 4.6, '#64B5F6'),
        ("Dropout\n(0.3)", 5, 3.3, '#E3F2FD'),
        ("Dense\n(64, ReLU)", 5, 2.2, '#42A5F5'),
        ("Output\n(Sigmoid)", 5, 1.2, '#1976D2')
    ]
    
    for label, x, y, color in layers:
        box = FancyBboxPatch((x-1.2, y-0.4), 2.4, 0.8,
                            boxstyle="round,pad=0.05",
                            facecolor=color,
                            edgecolor='black', linewidth=1.5)
        ax2.add_patch(box)
        ax2.text(x, y, label, ha='center', va='center', 
                fontsize=8.5, weight='bold')
        
        if y > 1.2:
            ax2.arrow(x, y-0.4, 0, -0.5, head_width=0.2, 
                     head_length=0.1, fc='black', ec='black', lw=1.5)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig_5_model_architecture.png", 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Figure 5: Model Architecture created")


def fig_6_dashboard_mockup():
    """Şekil 6: Dashboard Genel Görünümü (Mockup)"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Header
    header = FancyBboxPatch((0.5, 9), 13, 0.8,
                           boxstyle="round,pad=0.05",
                           facecolor='#2196F3',
                           edgecolor='black', linewidth=2)
    ax.add_patch(header)
    ax.text(7, 9.4, "Intelligent IDS Dashboard", 
           ha='center', va='center', fontsize=14, weight='bold', color='white')
    
    # Mode Selector
    mode_box = FancyBboxPatch((0.5, 7.8), 13, 0.6,
                             boxstyle="round,pad=0.05",
                             facecolor='#E3F2FD',
                             edgecolor='black', linewidth=1)
    ax.add_patch(mode_box)
    ax.text(7, 8.1, "Dataset Intelligence | Simulated Live | Real Network", 
           ha='center', va='center', fontsize=10, weight='bold')
    
    # Stats Grid
    stats_y = 6.5
    stats_labels = ["Active Source", "Total Events", "Attacks", "High Risk"]
    stats_values = ["DATASET", "12,543", "3,421", "892"]
    
    for idx, (label, value) in enumerate(zip(stats_labels, stats_values)):
        x = 1 + idx * 3.2
        stat_box = FancyBboxPatch((x, stats_y), 2.8, 1.2,
                                 boxstyle="round,pad=0.05",
                                 facecolor='#F5F5F5',
                                 edgecolor='black', linewidth=1)
        ax.add_patch(stat_box)
        ax.text(x+1.4, stats_y+0.7, label, ha='center', va='center', 
               fontsize=8, color='#666')
        ax.text(x+1.4, stats_y+0.3, value, ha='center', va='center', 
               fontsize=11, weight='bold')
    
    # Events Table
    table_box = FancyBboxPatch((0.5, 3), 8, 3.2,
                              boxstyle="round,pad=0.05",
                              facecolor='white',
                              edgecolor='black', linewidth=1.5)
    ax.add_patch(table_box)
    ax.text(4.5, 5.8, "Event Timeline", ha='center', va='center', 
           fontsize=11, weight='bold')
    
    # Table header
    headers = ["Time", "Source", "Destination", "Type", "Severity"]
    for idx, h in enumerate(headers):
        ax.text(1.2 + idx * 1.5, 5.4, h, ha='center', va='center', 
               fontsize=8, weight='bold')
        if idx < len(headers) - 1:
            ax.axvline(x=2.3 + idx * 1.5, ymin=0.32, ymax=0.61, 
                      color='gray', linewidth=0.5)
    
    # Sample rows
    samples = [
        ("10:23:15", "192.168.1.100", "10.0.0.5", "DoS Hulk", "HIGH"),
        ("10:23:12", "192.168.1.50", "10.0.0.3", "PortScan", "MEDIUM"),
        ("10:23:08", "192.168.1.200", "10.0.0.1", "Normal", "LOW"),
    ]
    
    for row_idx, row_data in enumerate(samples):
        y_pos = 4.8 - row_idx * 0.4
        for col_idx, data in enumerate(row_data):
            color = '#f44336' if data == "HIGH" else '#ff9800' if data == "MEDIUM" else '#4caf50' if data == "LOW" else 'black'
            ax.text(1.2 + col_idx * 1.5, y_pos, data, ha='center', va='center', 
                   fontsize=7, color=color, weight='bold' if col_idx == 4 else 'normal')
    
    # Metrics Panel
    metrics_box = FancyBboxPatch((9, 3), 4.5, 3.2,
                                boxstyle="round,pad=0.05",
                                facecolor='#F5F5F5',
                                edgecolor='black', linewidth=1.5)
    ax.add_patch(metrics_box)
    ax.text(11.25, 5.8, "Performance Metrics", ha='center', va='center', 
           fontsize=11, weight='bold')
    
    metrics = [
        ("Accuracy", 0.95),
        ("Precision", 0.92),
        ("Recall", 0.89),
        ("F1-Score", 0.90)
    ]
    
    for idx, (label, value) in enumerate(metrics):
        y_pos = 5.2 - idx * 0.6
        ax.text(9.8, y_pos, label, ha='left', va='center', fontsize=9)
        ax.text(12.5, y_pos, f"{value:.3f}", ha='right', va='center', 
               fontsize=10, weight='bold')
        
        # Progress bar
        bar = Rectangle((9.8, y_pos-0.1), value*2.3, 0.15,
                       facecolor='#4CAF50', edgecolor='black', linewidth=0.5)
        ax.add_patch(bar)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig_6_dashboard_mockup.png", 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Figure 6: Dashboard Mockup created")


def fig_7_attack_distribution():
    """Şekil 7: Saldırı Türlerine Göre Dağılım Grafiği"""
    # Örnek veri (gerçek veri kullanılabilir)
    attack_types = [
        "Normal", "DoS Hulk", "PortScan", "DDoS", 
        "Web Attack", "Bot", "FTP-Patator", "SSH-Patator"
    ]
    counts = [8500, 3200, 2800, 1500, 1200, 800, 600, 400]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Attack Type Distribution", fontsize=14, weight='bold')
    
    # Bar Chart
    colors = sns.color_palette("husl", len(attack_types))
    bars = ax1.barh(attack_types, counts, color=colors, edgecolor='black', linewidth=1)
    ax1.set_xlabel("Number of Samples", fontsize=11, weight='bold')
    ax1.set_ylabel("Attack Type", fontsize=11, weight='bold')
    ax1.set_title("Attack Distribution - Bar Chart", fontsize=12, weight='bold', pad=10)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax1.text(count + 100, i, str(count), va='center', 
                fontsize=9, weight='bold')
    
    # Pie Chart
    explode = [0.05 if at != "Normal" else 0 for at in attack_types]
    wedges, texts, autotexts = ax2.pie(counts, labels=attack_types, 
                                       colors=colors, explode=explode,
                                       autopct='%1.1f%%', startangle=90,
                                       textprops={'fontsize': 9, 'weight': 'bold'})
    for w in wedges:
        w.set_edgecolor('white')
        w.set_linewidth(1.5)
    ax2.set_title("Attack Distribution - Pie Chart", fontsize=12, weight='bold', pad=10)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig_7_attack_distribution.png", 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Figure 7: Attack Distribution created")


def fig_8_confusion_matrix():
    """Şekil 8: Confusion Matrix Görseli"""
    # Örnek confusion matrix (çok sınıflı)
    classes = ["Normal", "DoS\nHulk", "PortScan", "DDoS", "Web\nAttack", "Bot"]
    
    # Örnek veri
    cm = np.array([
        [4200, 45, 32, 12, 8, 3],
        [38, 3800, 120, 25, 15, 2],
        [28, 95, 3600, 85, 42, 10],
        [15, 42, 78, 3400, 35, 30],
        [12, 25, 38, 42, 3100, 83],
        [8, 15, 25, 55, 95, 2900]
    ])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Confusion Matrix Analysis", fontsize=14, weight='bold')
    
    # Multi-class Confusion Matrix
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
               xticklabels=classes, yticklabels=classes,
               cbar_kws={'label': 'Count'}, ax=ax1,
               linewidths=1, linecolor='gray', annot_kws={'size': 9, 'weight': 'bold'})
    ax1.set_xlabel("Predicted Label", fontsize=11, weight='bold')
    ax1.set_ylabel("True Label", fontsize=11, weight='bold')
    ax1.set_title("Multi-Class Confusion Matrix", fontsize=12, weight='bold', pad=10)
    
    # Binary Confusion Matrix
    binary_cm = np.array([
        [8500, 380],  # TN, FP
        [420, 7700]   # FN, TP
    ])
    
    binary_classes = ["Normal", "Attack"]
    sns.heatmap(binary_cm, annot=True, fmt='d', cmap='Greens',
               xticklabels=binary_classes, yticklabels=binary_classes,
               cbar_kws={'label': 'Count'}, ax=ax2,
               linewidths=2, linecolor='black', annot_kws={'size': 12, 'weight': 'bold'})
    ax2.set_xlabel("Predicted Label", fontsize=11, weight='bold')
    ax2.set_ylabel("True Label", fontsize=11, weight='bold')
    ax2.set_title("Binary Classification Confusion Matrix", fontsize=12, weight='bold', pad=10)
    
    # Binary labels
    ax2.text(0.5, 0.25, "TN", ha='center', va='center', fontsize=11, weight='bold', color='white')
    ax2.text(1.5, 0.25, "FP", ha='center', va='center', fontsize=11, weight='bold', color='white')
    ax2.text(0.5, 1.25, "FN", ha='center', va='center', fontsize=11, weight='bold', color='white')
    ax2.text(1.5, 1.25, "TP", ha='center', va='center', fontsize=11, weight='bold', color='white')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig_8_confusion_matrix.png", 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Figure 8: Confusion Matrix created")


def fig_9_performance_metrics():
    """Şekil 9: Performans Metrikleri Grafiği"""
    metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]
    values = [0.95, 0.92, 0.89, 0.90]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Performance Metrics Comparison", fontsize=14, weight='bold')
    
    # Bar Chart
    colors_bar = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
    bars = ax1.bar(metrics, values, color=colors_bar, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel("Score", fontsize=11, weight='bold')
    ax1.set_xlabel("Metric", fontsize=11, weight='bold')
    ax1.set_title("Performance Metrics - Bar Chart", fontsize=12, weight='bold', pad=10)
    ax1.set_ylim([0, 1.0])
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.axhline(y=0.9, color='green', linestyle='--', linewidth=1, 
               label='90% Threshold', alpha=0.7)
    ax1.legend()
    
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.3f}', ha='center', va='bottom', fontsize=10, weight='bold')
    
    # Line Chart with Multiple Models
    models = ["RandomForest", "CNN-LSTM", "Ensemble", "Multi-class"]
    acc = [0.93, 0.91, 0.95, 0.94]
    prec = [0.90, 0.88, 0.92, 0.91]
    rec = [0.87, 0.85, 0.89, 0.88]
    f1 = [0.88, 0.86, 0.90, 0.89]
    
    x = np.arange(len(models))
    width = 0.2
    
    ax2.bar(x - 1.5*width, acc, width, label='Accuracy', color='#4CAF50', edgecolor='black')
    ax2.bar(x - 0.5*width, prec, width, label='Precision', color='#2196F3', edgecolor='black')
    ax2.bar(x + 0.5*width, rec, width, label='Recall', color='#FF9800', edgecolor='black')
    ax2.bar(x + 1.5*width, f1, width, label='F1-Score', color='#9C27B0', edgecolor='black')
    
    ax2.set_ylabel("Score", fontsize=11, weight='bold')
    ax2.set_xlabel("Model", fontsize=11, weight='bold')
    ax2.set_title("Model Comparison - Performance Metrics", fontsize=12, weight='bold', pad=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(models)
    ax2.set_ylim([0, 1.0])
    ax2.legend(loc='upper right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig_9_performance_metrics.png", 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("[OK] Figure 9: Performance Metrics created")


def main():
    """Main function - Create all figures"""
    print("=" * 60)
    print("Starting Academic Visual Generation...")
    print("=" * 60)
    
    fig_1_system_architecture()
    fig_2_workflow_modes()
    fig_3_hybrid_detection()
    fig_4_preprocessing_pipeline()
    fig_5_model_architecture()
    fig_6_dashboard_mockup()
    fig_7_attack_distribution()
    fig_8_confusion_matrix()
    fig_9_performance_metrics()
    
    print("=" * 60)
    print(f"[OK] All figures created successfully!")
    print(f"[OK] Files saved to '{OUTPUT_DIR}' directory.")
    print("=" * 60)


if __name__ == "__main__":
    main()
