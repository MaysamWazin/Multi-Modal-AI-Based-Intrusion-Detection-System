"""
Academic Metrics Calculator
test.csv üzerinden Accuracy, Precision, Recall, F1 Score hesaplar.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

from ..core.intelligence_engine import IntelligenceEngine
from ..core.data_source import CSVDatasetSource, FlowData


class MetricsCalculator:
    """Akademik metrikleri hesaplayan sınıf"""
    
    def __init__(self, intelligence_engine: IntelligenceEngine):
        self.intelligence_engine = intelligence_engine
    
    def calculate_metrics(
        self,
        test_csv_path: str,
        label_col: str = "label",
        limit: Optional[int] = None
    ) -> Dict[str, float]:
        """
        test.csv üzerinden metrikleri hesapla
        
        Args:
            test_csv_path: Test CSV dosya yolu
            label_col: Label kolonu adı
            limit: İşlenecek maksimum satır sayısı (None = hepsi)
        
        Returns:
            Metrikler dictionary'si
        """
        print(f"[Metrics] Test CSV yükleniyor: {test_csv_path}")
        
        # CSV'yi yükle
        df = pd.read_csv(test_csv_path)
        
        if limit:
            df = df.head(limit)
        
        print(f"[Metrics] {len(df)} satır işlenecek")
        
        # Label kolonunu kontrol et
        if label_col not in df.columns:
            if "Label" in df.columns:
                label_col = "Label"
            else:
                raise ValueError(f"Label kolonu bulunamadı: {label_col}")
        
        # Veri kaynağı oluştur
        data_source = CSVDatasetSource(test_csv_path, label_col=label_col)
        
        # Tahminleri topla
        y_true = []
        y_pred = []
        y_pred_proba = []
        
        processed = 0
        for flow in data_source.get_flows():
            if limit and processed >= limit:
                break
            
            # Gerçek label
            true_label = flow.label if flow.label is not None else 0
            y_true.append(true_label)
            
            # Tahmin
            result = self.intelligence_engine.process_flow(flow)
            decision = result.get("decision", {})
            pred_label = decision.get("is_attack", 0)
            pred_proba = decision.get("confidence", 0.0)
            
            y_pred.append(pred_label)
            y_pred_proba.append(pred_proba)
            
            processed += 1
            
            if processed % 100 == 0:
                print(f"[Metrics] İşlenen: {processed}/{len(df)}")
        
        # Metrikleri hesapla
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Classification report
        report = classification_report(y_true, y_pred, output_dict=True)
        
        metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "confusion_matrix": cm.tolist(),
            "classification_report": report,
            "total_samples": len(y_true),
            "true_positives": int(cm[1][1]) if cm.shape == (2, 2) else 0,
            "true_negatives": int(cm[0][0]) if cm.shape == (2, 2) else 0,
            "false_positives": int(cm[0][1]) if cm.shape == (2, 2) else 0,
            "false_negatives": int(cm[1][0]) if cm.shape == (2, 2) else 0,
        }
        
        return metrics
    
    def print_metrics(self, metrics: Dict[str, float]):
        """Metrikleri konsola yazdır"""
        print("\n" + "=" * 60)
        print("ACADEMIC PERFORMANCE METRICS")
        print("=" * 60)
        print(f"Total Samples: {metrics.get('total_samples', 0)}")
        print(f"Accuracy:  {metrics.get('accuracy', 0):.4f}")
        print(f"Precision: {metrics.get('precision', 0):.4f}")
        print(f"Recall:   {metrics.get('recall', 0):.4f}")
        print(f"F1 Score: {metrics.get('f1_score', 0):.4f}")
        print()
        
        if "confusion_matrix" in metrics:
            print("Confusion Matrix:")
            cm = np.array(metrics["confusion_matrix"])
            print(cm)
            print()
        
        if "classification_report" in metrics:
            print("Classification Report:")
            report = metrics["classification_report"]
            if isinstance(report, dict):
                print(f"  Class 0 (Normal):")
                print(f"    Precision: {report.get('0', {}).get('precision', 0):.4f}")
                print(f"    Recall:    {report.get('0', {}).get('recall', 0):.4f}")
                print(f"    F1-Score:  {report.get('0', {}).get('f1-score', 0):.4f}")
                print(f"  Class 1 (Attack):")
                print(f"    Precision: {report.get('1', {}).get('precision', 0):.4f}")
                print(f"    Recall:    {report.get('1', {}).get('recall', 0):.4f}")
                print(f"    F1-Score:  {report.get('1', {}).get('f1-score', 0):.4f}")
        
        print("=" * 60)


def calculate_and_save_metrics(
    test_csv_path: str,
    intelligence_engine: IntelligenceEngine,
    output_path: str = "evaluation_metrics.json",
    limit: Optional[int] = None
):
    """Metrikleri hesapla ve kaydet"""
    import json
    
    calculator = MetricsCalculator(intelligence_engine)
    metrics = calculator.calculate_metrics(test_csv_path, limit=limit)
    
    # Konsola yazdır
    calculator.print_metrics(metrics)
    
    # Dosyaya kaydet
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    print(f"\n[✓] Metrikler kaydedildi: {output_path}")
    
    return metrics
