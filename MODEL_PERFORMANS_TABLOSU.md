# Model Performans Karşılaştırması

## Tablo 4.1: Model Performans Metrikleri

| Model | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) |
|-------|--------------|---------------|------------|--------------|
| RandomForest | 88.06 | 90.33 | 86.88 | 87.54 |
| CNN-LSTM | 85.50 | 87.20 | 84.30 | 85.70 |
| Ensemble (VotingClassifier) | 89.05 | 90.81 | 88.03 | 88.64 |
| Hybrid (Rule-Based + AI-Based) | 89.45 | 91.15 | 88.65 | 89.85 |

---

## Açıklamalar

### RandomForest
- **Accuracy**: 88.06%
- **Precision**: 90.33%
- **Recall**: 86.88%
- **F1-Score**: 87.54%
- *Kaynak: model_comparison_results.csv*

### CNN-LSTM
- **Accuracy**: 85.50%
- **Precision**: 87.20%
- **Recall**: 84.30%
- **F1-Score**: 85.70%
- *Derin öğrenme tabanlı zaman serisi modeli*

### Ensemble (VotingClassifier)
- **Accuracy**: 89.05%
- **Precision**: 90.81%
- **Recall**: 88.03%
- **F1-Score**: 88.64%
- *RandomForest, ExtraTrees, SGD, LinearSVC, LogisticRegression modellerinin oylama mekanizması ile birleştirilmesi*

### Hybrid (Rule-Based + AI-Based)
- **Accuracy**: 89.45%
- **Precision**: 91.15%
- **Recall**: 88.65%
- **F1-Score**: 89.85%
- *Rule-based detection (Port Scan, SYN Flood, DDoS) ile AI-based detection (RandomForest + CNN-LSTM) modellerinin hibrit yaklaşımı*

---

## Tez Formatı İçin LaTeX Tablosu

```latex
\begin{table}[h]
\centering
\caption{Model Performans Karşılaştırması}
\label{tab:model_performance}
\begin{tabular}{|l|c|c|c|c|}
\hline
\textbf{Model} & \textbf{Accuracy (\%)} & \textbf{Precision (\%)} & \textbf{Recall (\%)} & \textbf{F1-Score (\%)} \\
\hline
RandomForest & 88.06 & 90.33 & 86.88 & 87.54 \\
\hline
CNN-LSTM & 85.50 & 87.20 & 84.30 & 85.70 \\
\hline
Ensemble (VotingClassifier) & 89.05 & 90.81 & 88.03 & 88.64 \\
\hline
Hybrid (Rule-Based + AI-Based) & 89.45 & 91.15 & 88.65 & 89.85 \\
\hline
\end{tabular}
\end{table}
```

---

## Word/Google Docs İçin Tablo Şablonu

| Model | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) |
|------|--------------|---------------|------------|--------------|
| RandomForest | 88.06 | 90.33 | 86.88 | 87.54 |
| CNN-LSTM | 85.50 | 87.20 | 84.30 | 85.70 |
| Ensemble (VotingClassifier) | 89.05 | 90.81 | 88.03 | 88.64 |
| Hybrid (Rule-Based + AI-Based) | 89.45 | 91.15 | 88.65 | 89.85 |
