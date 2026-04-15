"""
Poster Görselleri Oluşturma Scripti
Tüm görselleri otomatik olarak oluşturur
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Seaborn olmadan çalışabilir, matplotlib ile yapacağız
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("[UYARI] Seaborn bulunamadı, matplotlib ile devam ediliyor...")

# Türkçe karakter desteği
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# Çıktı klasörü
OUTPUT_DIR = Path("poster_visuals")
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("POSTER GÖRSELLERİ OLUŞTURULUYOR...")
print("=" * 70)

# ============================================================================
# 1. MODEL PERFORMANS TABLOSU
# ============================================================================
print("\n[1/8] Model Performans Tablosu oluşturuluyor...")

try:
    # Tablo verileri (pandas olmadan)
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
    print("✓ Tablo oluşturuldu: 1_performance_table.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 2. CONFUSION MATRIX (BINARY)
# ============================================================================
print("\n[2/8] Confusion Matrix (Binary) oluşturuluyor...")

try:
    # Örnek confusion matrix (gerçek verilerle değiştirilebilir)
    cm_binary = np.array([[8500, 200],   # TN, FP
                          [150, 9150]])  # FN, TP
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if HAS_SEABORN:
        sns.heatmap(cm_binary, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Normal', 'Attack'],
                    yticklabels=['Normal', 'Attack'],
                    cbar_kws={'label': 'Count'}, ax=ax)
    else:
        # Matplotlib ile heatmap
        im = ax.imshow(cm_binary, cmap='Blues', aspect='auto')
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Normal', 'Attack'])
        ax.set_yticklabels(['Normal', 'Attack'])
        
        # Değerleri yaz
        for i in range(2):
            for j in range(2):
                text = ax.text(j, i, str(cm_binary[i, j]),
                             ha="center", va="center", color="black", fontsize=14, fontweight='bold')
        
        plt.colorbar(im, ax=ax, label='Count')
    
    ax.set_title('Confusion Matrix - Binary Classification\n(RandomForest)', 
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    
    # Değerleri vurgula
    for i in range(2):
        for j in range(2):
            text = ax.texts[i * 2 + j]
            text.set_fontsize(14)
            text.set_fontweight('bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '2_confusion_matrix_binary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Confusion Matrix (Binary) oluşturuldu: 2_confusion_matrix_binary.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")

# ============================================================================
# 3. CONFUSION MATRIX (MULTI-CLASS)
# ============================================================================
print("\n[3/8] Confusion Matrix (Multi-class) oluşturuluyor...")

try:
    # Örnek confusion matrix (9 sınıf)
    classes = ['Normal', 'DoS', 'DDoS', 'PortScan', 'Web Attack', 
               'BruteForce', 'Bot', 'Exploits', 'Fuzzers']
    
    # Rastgele örnek matrix (gerçek verilerle değiştirilebilir)
    np.random.seed(42)
    cm_multi = np.random.randint(50, 500, size=(9, 9))
    # Diagonal'i daha yüksek yap (doğru tahminler)
    for i in range(9):
        cm_multi[i, i] = np.random.randint(800, 1200)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    if HAS_SEABORN:
        sns.heatmap(cm_multi, annot=True, fmt='d', cmap='Blues',
                    xticklabels=classes, yticklabels=classes,
                    cbar_kws={'label': 'Count'}, ax=ax)
    else:
        # Matplotlib ile heatmap
        im = ax.imshow(cm_multi, cmap='Blues', aspect='auto')
        ax.set_xticks(range(len(classes)))
        ax.set_yticks(range(len(classes)))
        ax.set_xticklabels(classes, rotation=45, ha='right')
        ax.set_yticklabels(classes)
        
        # Değerleri yaz (sadece büyük değerler)
        for i in range(len(classes)):
            for j in range(len(classes)):
                if cm_multi[i, j] > 50:  # Sadece önemli değerleri göster
                    text = ax.text(j, i, str(cm_multi[i, j]),
                                 ha="center", va="center", 
                                 color="white" if cm_multi[i, j] > cm_multi.max()/2 else "black",
                                 fontsize=8)
        
        plt.colorbar(im, ax=ax, label='Count')
    
    ax.set_title('Confusion Matrix - Multi-class Classification\n(VotingClassifier)', 
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '3_confusion_matrix_multiclass.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Confusion Matrix (Multi-class) oluşturuldu: 3_confusion_matrix_multiclass.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")

# ============================================================================
# 4. SALDIRI TİPİ DAĞILIM GRAFİĞİ
# ============================================================================
print("\n[4/8] Saldırı Tipi Dağılım Grafiği oluşturuluyor...")

try:
    attack_types = ['Normal', 'DoS', 'DDoS', 'PortScan', 'Web Attack', 
                    'BruteForce', 'Bot', 'Exploits', 'Fuzzers']
    counts = [45000, 12000, 8000, 6000, 5000, 4000, 3000, 2000, 1000]
    
    # Pie chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Sol: Pie chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(attack_types)))
    wedges, texts, autotexts = ax1.pie(counts, labels=attack_types, autopct='%1.1f%%', 
                                        startangle=90, colors=colors)
    ax1.set_title('Attack Type Distribution\n(Pie Chart)', fontsize=16, fontweight='bold', pad=20)
    
    # Sağ: Bar chart
    bars = ax2.bar(attack_types, counts, color=colors)
    ax2.set_xlabel('Attack Type', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax2.set_title('Attack Type Distribution\n(Bar Chart)', fontsize=16, fontweight='bold', pad=20)
    ax2.tick_params(axis='x', rotation=45)
    
    # Bar üzerine değerleri yaz
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '4_attack_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saldırı Tipi Dağılım Grafiği oluşturuldu: 4_attack_distribution.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")

# ============================================================================
# 5. PERFORMANS METRİKLERİ GRAFİĞİ
# ============================================================================
print("\n[5/8] Performans Metrikleri Grafiği oluşturuluyor...")

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
    print("✓ Performans Metrikleri Grafiği oluşturuldu: 5_performance_comparison.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")

# ============================================================================
# 6. ROC CURVE
# ============================================================================
print("\n[6/8] ROC Curve oluşturuluyor...")

try:
    # Örnek ROC curve (gerçek verilerle değiştirilebilir)
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
    print("✓ ROC Curve oluşturuldu: 6_roc_curve.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")

# ============================================================================
# 7. SİSTEM MİMARİSİ DİYAGRAMI
# ============================================================================
print("\n[7/8] Sistem Mimarisi Diyagramı oluşturuluyor...")

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
    for x, y, w, h, label, color in boxes:
        rect = plt.Rectangle((x, y), w, h, linewidth=2.5, 
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
    print("✓ Sistem Mimarisi Diyagramı oluşturuldu: 7_system_architecture.png")
    
except Exception as e:
    print(f"✗ Hata: {e}")

# ============================================================================
# 8. ÖZET BİLGİ
# ============================================================================
print("\n[8/8] Özet bilgi oluşturuluyor...")

try:
    summary_text = f"""
POSTER GÖRSELLERİ BAŞARIYLA OLUŞTURULDU!

Çıktı Klasörü: {OUTPUT_DIR.absolute()}

Oluşturulan Görseller:
1. Model Performans Tablosu
2. Confusion Matrix (Binary)
3. Confusion Matrix (Multi-class)
4. Saldırı Tipi Dağılım Grafiği
5. Performans Metrikleri Grafiği
6. ROC Curve
7. Sistem Mimarisi Diyagramı

NOT: Görseller örnek verilerle oluşturulmuştur.
Gerçek verilerle güncellemek için scripti düzenleyin.

Tüm görseller 300 DPI çözünürlükte PNG formatında kaydedilmiştir.
Poster tasarımına uygun şekilde kullanılabilir.
"""
    
    with open(OUTPUT_DIR / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(summary_text)
    
    print(summary_text)
    print("=" * 70)
    print("TÜM GÖRSELLER BAŞARIYLA OLUŞTURULDU!")
    print("=" * 70)
    
except Exception as e:
    print(f"✗ Hata: {e}")
