"""All-in-one evaluation metrics. Returns a flat dict so we can json.dump it."""

import numpy as np
from sklearn.metrics import (
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def expected_calibration_error(probs, true, n_bins=15):
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(probs)
    for i in range(n_bins):
        mask = (probs >= edges[i]) & (probs < edges[i + 1] if i < n_bins - 1
                                      else probs <= edges[i + 1])
        if mask.sum() == 0:
            continue
        bin_acc = true[mask].mean()
        bin_conf = probs[mask].mean()
        ece += (mask.sum() / n) * abs(bin_acc - bin_conf)
    return float(ece)


def report(probs, true, threshold=0.5):
    probs = np.asarray(probs)
    true = np.asarray(true).astype(int)
    preds = (probs >= threshold).astype(int)
    cm = confusion_matrix(true, preds, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    out = {
        "n": int(len(true)),
        "threshold": float(threshold),
        "auc": float(roc_auc_score(true, probs)),
        "precision": float(precision_score(true, preds, zero_division=0)),
        "recall": float(recall_score(true, preds, zero_division=0)),
        "f1": float(f1_score(true, preds, zero_division=0)),
        "fnr": float(fn / max(fn + tp, 1)),
        "fpr": float(fp / max(fp + tn, 1)),
        "brier": float(brier_score_loss(true, probs)),
        "ece": expected_calibration_error(probs, true),
        "cm": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)},
    }
    return out


def pretty(report_dict, label=""):
    r = report_dict
    return (f"{label:<24}  AUC={r['auc']:.4f}  P={r['precision']:.4f}  "
            f"R={r['recall']:.4f}  F1={r['f1']:.4f}  "
            f"FNR={r['fnr']:.4f}  ECE={r['ece']:.3f}")
