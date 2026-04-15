"""
Poster Görselleri Oluşturma Scripti (Basit Versiyon - Pandas Olmadan)
Tüm görselleri otomatik olarak oluşturur
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalış
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Türkçe karakter desteği
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# Çıktı klasörü
OUTPUT_DIR = Path("poster_visuals")
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("POSTER GORSELLERI OLUSTURULUYOR...")
print("=" * 70)

# ============================================================================
# 1. MODEL PERFORMANS TABLOSU
# ============================================================================
print("\n[1/7] Model Performans Tablosu olusturuluyor...")

try:
    # Tablo verileri
    headers = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score']
    data = [
        ['RandomForest\n(Binary)', '95.2%', '94.1%', '96.3%', '95.2%'],
        ['VotingClassifier\n(Multi-class)', '94.8%', '93.5%', '95.7%', '94.6%']
    ]
    
    # Tablo görseli
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=data,
                     colLabels=headers,
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Başlık stil
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Satır renkleri
    for i in range(1, len(data) + 1):
        for j in range(len(headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#D9E1F2')
            else:
                table[(i, j)].set_facecolor('#FFFFFF')
    
    plt.title('Model Performance Comparison', fontsize=16, fontweight='bold', pad=20)
    plt.savefig(OUTPUT_DIR / '1_performance_table.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("OK Tablo olusturuldu: 1_performance_table.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 2. CONFUSION MATRIX (BINARY)
# ============================================================================
print("\n[2/7] Confusion Matrix (Binary) olusturuluyor...")

try:
    # Örnek confusion matrix
    cm_binary = np.array([[8500, 200],   # TN, FP
                          [150, 9150]])  # FN, TP
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Matplotlib ile heatmap
    im = ax.imshow(cm_binary, cmap='Blues', aspect='auto', vmin=0, vmax=cm_binary.max())
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Normal', 'Attack'], fontsize=12, fontweight='bold')
    ax.set_yticklabels(['Normal', 'Attack'], fontsize=12, fontweight='bold')
    
    # Değerleri yaz
    for i in range(2):
        for j in range(2):
            text = ax.text(j, i, str(cm_binary[i, j]),
                         ha="center", va="center", color="white" if cm_binary[i, j] > cm_binary.max()/2 else "black",
                         fontsize=16, fontweight='bold')
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Count', fontsize=12, fontweight='bold')
    
    ax.set_title('Confusion Matrix - Binary Classification\n(RandomForest)', 
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '2_confusion_matrix_binary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("OK Confusion Matrix (Binary) olusturuldu: 2_confusion_matrix_binary.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 3. CONFUSION MATRIX (MULTI-CLASS)
# ============================================================================
print("\n[3/7] Confusion Matrix (Multi-class) olusturuluyor...")

try:
    # Örnek confusion matrix (9 sınıf)
    classes = ['Normal', 'DoS', 'DDoS', 'PortScan', 'Web Attack', 
               'BruteForce', 'Bot', 'Exploits', 'Fuzzers']
    
    # Rastgele örnek matrix
    np.random.seed(42)
    cm_multi = np.random.randint(50, 500, size=(9, 9))
    # Diagonal'i daha yüksek yap
    for i in range(9):
        cm_multi[i, i] = np.random.randint(800, 1200)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Matplotlib ile heatmap
    im = ax.imshow(cm_multi, cmap='Blues', aspect='auto', vmin=0, vmax=cm_multi.max())
    ax.set_xticks(range(len(classes)))
    ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels(classes, fontsize=10)
    
    # Değerleri yaz (sadece büyük değerler)
    threshold = cm_multi.max() / 3
    for i in range(len(classes)):
        for j in range(len(classes)):
            if cm_multi[i, j] > threshold:
                text = ax.text(j, i, str(cm_multi[i, j]),
                             ha="center", va="center", 
                             color="white" if cm_multi[i, j] > cm_multi.max()/2 else "black",
                             fontsize=8)
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Count', fontsize=12, fontweight='bold')
    
    ax.set_title('Confusion Matrix - Multi-class Classification\n(VotingClassifier)', 
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '3_confusion_matrix_multiclass.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("OK Confusion Matrix (Multi-class) olusturuldu: 3_confusion_matrix_multiclass.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 4. SALDIRI TİPİ DAĞILIM GRAFİĞİ
# ============================================================================
print("\n[4/7] Saldiri Tipi Dagilim Grafigi olusturuluyor...")

try:
    attack_types = ['Normal', 'DoS', 'DDoS', 'PortScan', 'Web Attack', 
                    'BruteForce', 'Bot', 'Exploits', 'Fuzzers']
    counts = [45000, 12000, 8000, 6000, 5000, 4000, 3000, 2000, 1000]
    
    # Pie chart ve Bar chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Sol: Pie chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(attack_types)))
    wedges, texts, autotexts = ax1.pie(counts, labels=attack_types, autopct='%1.1f%%', 
                                        startangle=90, colors=colors)
    ax1.set_title('Attack Type Distribution\n(Pie Chart)', fontsize=16, fontweight='bold', pad=20)
    
    # Sağ: Bar chart
    bars = ax2.bar(attack_types, counts, color=colors, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Attack Type', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax2.set_title('Attack Type Distribution\n(Bar Chart)', fontsize=16, fontweight='bold', pad=20)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Bar üzerine değerleri yaz
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '4_attack_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("OK Saldiri Tipi Dagilim Grafigi olusturuldu: 4_attack_distribution.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 5. PERFORMANS METRİKLERİ GRAFİĞİ
# ============================================================================
print("\n[5/7] Performans Metrikleri Grafigi olusturuluyor...")

try:
    models = ['RandomForest\n(Binary)', 'VotingClassifier\n(Multi-class)']
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    
    # Veri
    rf_scores = [0.952, 0.941, 0.963, 0.952]
    vc_scores = [0.948, 0.935, 0.957, 0.946]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - width/2, rf_scores, width, label='RandomForest', 
                   color='#4472C4', edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, vc_scores, width, label='VotingClassifier', 
                   color='#ED7D31', edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Model Performance Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11)
    ax.legend(fontsize=11, loc='upper right')
    ax.set_ylim([0.90, 1.0])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Değerleri göster
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '5_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("OK Performans Metrikleri Grafigi olusturuldu: 5_performance_comparison.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 6. ROC CURVE
# ============================================================================
print("\n[6/7] ROC Curve oluşturuluyor...")

try:
    # Örnek ROC curve
    np.random.seed(42)
    fpr = np.linspace(0, 1, 100)
    tpr = 1 - np.exp(-5 * fpr)  # Örnek ROC eğrisi
    tpr = np.clip(tpr, 0, 1)
    roc_auc = np.trapz(tpr, fpr)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(fpr, tpr, color='darkorange', lw=3, 
            label=f'ROC curve (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
            label='Random Classifier (AUC = 0.500)')
    ax.fill_between(fpr, tpr, alpha=0.3, color='darkorange')
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold')
    ax.set_title('ROC Curve - Binary Classification\n(RandomForest)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '6_roc_curve.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("OK ROC Curve olusturuldu: 6_roc_curve.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 7. SİSTEM MİMARİSİ DİYAGRAMI
# ============================================================================
print("\n[7/7] Sistem Mimarisi Diyagrami olusturuluyor...")

try:
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Box koordinatları (x, y, width, height, label, color)
    boxes = [
        (1, 7, 2.5, 1, 'Data Source\nLayer', '#E7E6E6'),
        (1, 5, 2.5, 1, 'Feature\nEngineering', '#D9E1F2'),
        (4.5, 5, 2.5, 1, 'Rule Engine', '#FFE699'),
        (8, 5, 2.5, 1, 'ML Inference\n(RandomForest)', '#C5E0B4'),
        (11.5, 5, 2.5, 1, 'Multi-class\n(VotingClassifier)', '#B4C6E7'),
        (6.5, 2, 3, 1, 'Decision\nEngine', '#F4B084'),
        (6.5, 0, 3, 1, 'Dashboard\nOutput', '#8FAADC'),
    ]
    
    # Boxes çiz
    from matplotlib.patches import Rectangle
    for x, y, w, h, label, color in boxes:
        rect = Rectangle((x, y), w, h, linewidth=2.5, 
                        edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.text(x+w/2, y+h/2, label, ha='center', va='center', 
               fontsize=11, fontweight='bold', wrap=True)
    
    # Oklar (x, y, dx, dy)
    arrows = [
        (2.25, 6.5, 0, -0.5),      # Data Source -> Feature
        (4, 5.5, 0.5, 0),          # Feature -> Rule
        (7, 5.5, 1, 0),            # Rule -> ML
        (10.5, 5.5, 1, 0),         # ML -> Multi-class
        (12.75, 5, 0, -2.5),       # Multi-class -> Decision
        (8, 2, 0, -1.5),           # Decision -> Dashboard
    ]
    
    for x, y, dx, dy in arrows:
        ax.arrow(x, y, dx, dy, head_width=0.3, head_length=0.3, 
                fc='black', ec='black', linewidth=2.5)
    
    ax.set_xlim(0, 15)
    ax.set_ylim(-1, 9)
    ax.axis('off')
    ax.set_title('System Architecture', fontsize=20, fontweight='bold', pad=30)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '7_system_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("OK Sistem Mimarisi Diyagrami olusturuldu: 7_system_architecture.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# ÖZET
# ============================================================================
print("\n" + "=" * 70)
print("POSTER GORSELLERI BASARIYLA OLUSTURULDU!")
print("=" * 70)
print(f"\nCikti Klasoru: {OUTPUT_DIR.absolute()}")
print("\nOlusturulan Gorseller:")
print("1. Model Performans Tablosu")
print("2. Confusion Matrix (Binary)")
print("3. Confusion Matrix (Multi-class)")
print("4. Saldırı Tipi Dağılım Grafiği")
print("5. Performans Metrikleri Grafiği")
print("6. ROC Curve")
print("7. Sistem Mimarisi Diyagramı")
print("\nNOT: Gorseller ornek verilerle olusturulmustur.")
print("Gercek verilerle guncellemek icin scripti duzenleyin.")
print("=" * 70)
