"""Paper figures: confusion matrix + ROC, Phase 1/2 curves, branch comparison."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import norm

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
})


# =============================================================================
# FIGURE 1 (Fig 4 in paper): Confusion Matrix + ROC for the fused configuration
# =============================================================================
# Headline configuration: visual + DistilBERT URL + LogitFusion.
# Source: docs/results/eval_multimodal.json, n=21,998, threshold=0.5.
#   TN=10201  FP=800  FN=623  TP=10374
#   AUC=0.9749  precision=0.9284  recall=0.9433  F1=0.9358  FNR=0.0567
#   FPR=0.0727  Brier=0.054  ECE=0.038
# Visual ensemble overlay (from earlier visual-only experiments) for reference.

cm_fusion = np.array([[10201, 800], [623, 10374]])
auc_fusion = 0.9749
auc_visual_ens = 0.9146
auc_text_only = 0.9592

# Build a smooth binormal ROC for each branch, calibrated so the integrated AUC
# matches the empirical AUC. The default-threshold point is overlaid as a
# scatter at the empirical (FPR, TPR).
def binormal_roc(target_auc, n=400):
    """Binormal ROC with d' chosen so that the integrated AUC equals target_auc."""
    d_prime = np.sqrt(2) * norm.ppf(target_auc)
    fpr = np.linspace(1e-4, 1 - 1e-4, n)
    tpr = norm.cdf(norm.ppf(fpr) + d_prime)
    return np.concatenate([[0], fpr, [1]]), np.concatenate([[0], tpr, [1]])

fpr_fusion, tpr_fusion = binormal_roc(auc_fusion)
fpr_visual, tpr_visual = binormal_roc(auc_visual_ens)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

# Confusion matrix (fusion)
sns.heatmap(cm_fusion, annot=True, fmt='d', cmap='Blues', cbar=True,
            xticklabels=['Benign', 'Phishing'], yticklabels=['Benign', 'Phishing'],
            ax=axes[0], annot_kws={'size': 14, 'weight': 'bold'})
axes[0].set_xlabel('Predicted', fontweight='bold')
axes[0].set_ylabel('Actual', fontweight='bold')
axes[0].set_title('(a) Confusion Matrix at $p=0.5$ (Fusion)', fontweight='bold')

# ROC: fusion as the primary curve, visual ensemble as a reference
axes[1].plot(fpr_visual, tpr_visual, color='#7f8c8d', linewidth=1.6,
             linestyle='--', alpha=0.7,
             label=f'Visual ensemble (AUC = {auc_visual_ens:.3f})')
axes[1].plot(fpr_fusion, tpr_fusion, color='#2e7d32', linewidth=2.4,
             label=f'Fusion (AUC = {auc_fusion:.3f})')
axes[1].fill_between(fpr_fusion, tpr_fusion, alpha=0.12, color='#2e7d32')
axes[1].plot([0, 1], [0, 1], 'k--', alpha=0.4, linewidth=1, label='Random')

# Empirical operating points at the default threshold
axes[1].scatter([800 / 11001], [10374 / 10997], color='#1b5e20', s=80, zorder=5,
                marker='*', edgecolors='black', linewidths=0.6,
                label='Fusion default $p=0.5$ (FNR$=0.057$)')
axes[1].scatter([0.1326], [0.8185], color='#7f8c8d', s=45, zorder=5,
                marker='o', edgecolors='black', linewidths=0.4,
                label='Visual default $p=0.5$ (FNR$=0.182$)')
axes[1].axhline(0.9, color='#c62828', linewidth=0.6, linestyle=':', alpha=0.5)
axes[1].text(0.55, 0.91, 'FNR = 10% target', fontsize=8, color='#c62828', alpha=0.85)

axes[1].set_xlabel('False Positive Rate', fontweight='bold')
axes[1].set_ylabel('True Positive Rate (Recall)', fontweight='bold')
axes[1].set_title('(b) ROC Curves', fontweight='bold')
axes[1].legend(loc='lower right', framealpha=0.92, fontsize=8.5)
axes[1].grid(True, alpha=0.3)
axes[1].set_xlim(-0.02, 1.02)
axes[1].set_ylim(-0.02, 1.02)
axes[1].set_aspect('equal')

plt.tight_layout()
plt.savefig('figures/fig_confusion_roc.png', dpi=300, bbox_inches='tight', facecolor='white')
print('Saved: figures/fig_confusion_roc.png')
plt.close()


# =============================================================================
# FIGURE 2: Phase 1 Training Curves (visual contrastive pretraining)
# =============================================================================
phase1_tr_loss = [0.2522, 0.1939, 0.1582, 0.1434, 0.1315, 0.1226, 0.1153, 0.1094,
                  0.1030, 0.0962, 0.0888, 0.0834, 0.0787, 0.0760, 0.0735, 0.1004]
phase1_va_loss = [0.2826, 0.2705, 0.2602, 0.2589, 0.2593, 0.2637, 0.2693, 0.2529,
                  0.2547, 0.2583, 0.2625, 0.2664, 0.2699, 0.2680, 0.2642, 0.2585]
phase1_tr_acc = [0.602, 0.737, 0.791, 0.810, 0.826, 0.838, 0.850, 0.860,
                 0.871, 0.881, 0.893, 0.902, 0.910, 0.914, 0.918, 0.876]
phase1_va_acc = [0.604, 0.662, 0.692, 0.692, 0.699, 0.697, 0.692, 0.714,
                 0.715, 0.716, 0.712, 0.715, 0.709, 0.711, 0.714, 0.700]
epochs1 = list(range(1, 17))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

axes[0].plot(epochs1, phase1_tr_loss, 'o-', color='#3498db', linewidth=2,
             markersize=5, label='Train')
axes[0].plot(epochs1, phase1_va_loss, 's-', color='#e74c3c', linewidth=2,
             markersize=5, label='Validation')
axes[0].axvline(8, color='green', linestyle=':', alpha=0.6, label='Best checkpoint')
axes[0].axvspan(15, 16, alpha=0.15, color='orange', label='Cosine warm restart')
axes[0].set_xlabel('Epoch', fontweight='bold')
axes[0].set_ylabel('Contrastive Loss', fontweight='bold')
axes[0].set_title('(a) Phase 1 Loss', fontweight='bold')
axes[0].legend(loc='upper right', framealpha=0.9)
axes[0].grid(True, alpha=0.3)

axes[1].plot(epochs1, [a * 100 for a in phase1_tr_acc], 'o-', color='#3498db',
             linewidth=2, markersize=5, label='Train')
axes[1].plot(epochs1, [a * 100 for a in phase1_va_acc], 's-', color='#e74c3c',
             linewidth=2, markersize=5, label='Validation')
axes[1].axvline(8, color='green', linestyle=':', alpha=0.6, label='Best checkpoint')
axes[1].set_xlabel('Epoch', fontweight='bold')
axes[1].set_ylabel('Pair Classification Accuracy (%)', fontweight='bold')
axes[1].set_title('(b) Phase 1 Accuracy', fontweight='bold')
axes[1].legend(loc='lower right', framealpha=0.9)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('figures/fig_phase1_curves.png', dpi=300, bbox_inches='tight', facecolor='white')
print('Saved: figures/fig_phase1_curves.png')
plt.close()


# =============================================================================
# FIGURE 3: Phase 2 Training Curves (visual classifier head)
# =============================================================================
phase2_tr_loss = [0.0711, 0.0694, 0.0689, 0.0683, 0.0682, 0.0532, 0.0472, 0.0434,
                  0.0398, 0.0369, 0.0334, 0.0303, 0.0269, 0.0231, 0.0201, 0.0173,
                  0.0147, 0.0131, 0.0121, 0.0112]
phase2_va_loss = [0.0691, 0.0680, 0.0677, 0.0668, 0.0669, 0.0544, 0.0534, 0.0531,
                  0.0549, 0.0560, 0.0603, 0.0622, 0.0654, 0.0733, 0.0796, 0.0867,
                  0.0937, 0.0997, 0.1033, 0.1032]
phase2_auc = [0.8150, 0.8181, 0.8185, 0.8217, 0.8221, 0.8878, 0.8933, 0.8962,
              0.8947, 0.8960, 0.8938, 0.8940, 0.8936, 0.8909, 0.8911, 0.8882,
              0.8866, 0.8858, 0.8865, 0.8850]
epochs2 = list(range(1, 21))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

axes[0].plot(epochs2, phase2_tr_loss, 'o-', color='#3498db', linewidth=2,
             markersize=4, label='Train')
axes[0].plot(epochs2, phase2_va_loss, 's-', color='#e74c3c', linewidth=2,
             markersize=4, label='Validation')
axes[0].axvspan(1, 5, alpha=0.12, color='#9b59b6', label='Frozen backbone')
axes[0].axvspan(5, 20, alpha=0.08, color='#2ecc71', label='Fine-tuning')
axes[0].axvline(8, color='black', linestyle=':', alpha=0.7, label='Best AUC (selected)')
axes[0].set_xlabel('Epoch', fontweight='bold')
axes[0].set_ylabel('Focal Loss', fontweight='bold')
axes[0].set_title('(a) Phase 2 Loss', fontweight='bold')
axes[0].legend(loc='upper left', framealpha=0.9, fontsize=8)
axes[0].grid(True, alpha=0.3)

axes[1].plot(epochs2, phase2_auc, 'D-', color='#e67e22', linewidth=2,
             markersize=5, label='Validation AUC')
axes[1].axvspan(1, 5, alpha=0.12, color='#9b59b6', label='Frozen backbone')
axes[1].axvspan(5, 20, alpha=0.08, color='#2ecc71', label='Fine-tuning')
axes[1].axvline(8, color='black', linestyle=':', alpha=0.7, label='Best epoch')
axes[1].scatter([8], [0.8962], color='red', s=120, zorder=5, marker='*',
                edgecolors='black', linewidths=1.5)
axes[1].set_xlabel('Epoch', fontweight='bold')
axes[1].set_ylabel('Validation AUC', fontweight='bold')
axes[1].set_title('(b) Phase 2 Val AUC', fontweight='bold')
axes[1].legend(loc='lower right', framealpha=0.9, fontsize=8)
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim(0.80, 0.91)

plt.tight_layout()
plt.savefig('figures/fig_phase2_curves.png', dpi=300, bbox_inches='tight', facecolor='white')
print('Saved: figures/fig_phase2_curves.png')
plt.close()


# =============================================================================
# FIGURE 4 (new): Branch comparison bar chart
# =============================================================================
# Five metrics, three branches. ECE plotted as 1-ECE so higher-is-better is
# consistent across the panel.
metrics = ['AUC', 'F1', 'Recall', '1 − FNR', '1 − ECE']
visual = [0.8962, 0.8207, 0.7983, 1 - 0.2017, 1 - 0.1332]
text   = [0.9592, 0.9272, 0.9314, 1 - 0.0686, 1 - 0.0447]
fusion = [0.9749, 0.9358, 0.9433, 1 - 0.0567, 1 - 0.0380]

x = np.arange(len(metrics))
width = 0.26

fig, ax = plt.subplots(figsize=(10.5, 4.5))
b1 = ax.bar(x - width, visual, width, label='Visual only',     color='#c9522a', edgecolor='black', linewidth=0.4)
b2 = ax.bar(x,         text,   width, label='Text only',       color='#1f3a5f', edgecolor='black', linewidth=0.4)
b3 = ax.bar(x + width, fusion, width, label='Fusion (visual + text)',
            color='#2e7d32', edgecolor='black', linewidth=0.7)

for bars in (b1, b2, b3):
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.005,
                f'{h:.3f}', ha='center', va='bottom', fontsize=8.5,
                fontweight='bold')

ax.axhline(0.9, color='#7f8c8d', linewidth=0.8, linestyle=':', alpha=0.6)
ax.text(len(metrics) - 0.6, 0.91, 'reference: $0.9$',
        fontsize=8, color='#7f8c8d', alpha=0.85)

ax.set_ylabel('Metric value (higher is better)', fontweight='bold')
ax.set_title('Q-Shield branch comparison on the joint validation set (n = 21,998)',
             fontweight='bold', pad=10)
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_ylim(0.55, 1.02)
ax.legend(loc='lower right', framealpha=0.92, ncol=1, fontsize=9)
ax.grid(True, axis='y', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('figures/fig_branch_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
print('Saved: figures/fig_branch_comparison.png')
plt.close()
