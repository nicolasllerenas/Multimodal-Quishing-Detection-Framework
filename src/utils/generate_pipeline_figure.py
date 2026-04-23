"""
Generate Q-Shield pipeline architecture figure for the paper.
Creates a step-by-step visual diagram of the detection workflow.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(figsize=(14, 9))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# Colors
C_INPUT = '#3498db'
C_BACKBONE = '#e74c3c'
C_LOSS = '#f39c12'
C_HEAD = '#2ecc71'
C_XAI = '#9b59b6'
C_OUTPUT = '#1abc9c'

def box(ax, x, y, w, h, text, color, fontsize=10, fontweight='normal', text_color='white'):
    b = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.1',
                        facecolor=color, edgecolor='black', linewidth=1.5)
    ax.add_patch(b)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight, color=text_color,
            wrap=True)

def arrow(ax, x1, y1, x2, y2, color='black', lw=2):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                         arrowstyle='->', mutation_scale=20,
                         linewidth=lw, color=color)
    ax.add_patch(a)

def step_label(ax, x, y, num, text):
    circle = plt.Circle((x, y), 0.25, color='black', zorder=10)
    ax.add_patch(circle)
    ax.text(x, y, str(num), ha='center', va='center',
            fontsize=10, fontweight='bold', color='white', zorder=11)
    ax.text(x + 0.4, y, text, ha='left', va='center',
            fontsize=9, fontweight='bold', color='black')

# Title
ax.text(7, 9.5, 'Q-Shield Detection Pipeline',
        ha='center', va='center', fontsize=16, fontweight='bold')
ax.text(7, 9.1, '(Zero-decoding inference + dual explainability)',
        ha='center', va='center', fontsize=10, style='italic', color='#555')

# ===== STEP 1: Input =====
step_label(ax, 0.5, 8.2, 1, 'QR image input')
box(ax, 1, 7.4, 2.5, 0.9, 'QR code image\n(any QR version,\nany resolution)',
    C_INPUT, fontsize=9)

# ===== STEP 2: Preprocessing =====
step_label(ax, 0.5, 6.5, 2, 'Preprocessing')
box(ax, 1, 5.7, 2.5, 0.9, 'Grayscale convert\nResize to 224x224',
    '#5dade2', fontsize=9)

# ===== STEP 3: Siamese backbone =====
step_label(ax, 5, 8.2, 3, 'Feature extraction via Siamese backbone (pretrained)')
# Twin backbone boxes showing shared weights
box(ax, 4.5, 6.5, 2.3, 1.2, 'MobileNetV2\n(shared weights)',
    C_BACKBONE, fontsize=9, fontweight='bold')
box(ax, 7, 6.5, 2.3, 1.2, 'MobileNetV2\n(shared weights)',
    C_BACKBONE, fontsize=9, fontweight='bold')
# Indicate sharing
ax.plot([5.65, 8.15], [6.4, 6.4], color='black', linewidth=1.5, linestyle=':')
ax.text(6.9, 6.3, 'shared $\\psi$', ha='center', va='top', fontsize=8, style='italic')

# Connect step 2 to step 3
arrow(ax, 3.5, 6.2, 4.5, 7.1)

# ===== STEP 4: Embedding =====
step_label(ax, 0.5, 4.8, 4, 'L2-normalized embedding (128-d)')
box(ax, 5.3, 4.3, 3, 1, 'embedding e $\\in$ $\\mathbb{R}^{128}$\n||e||$_2$ = 1',
    '#c0392b', fontsize=9)
arrow(ax, 5.65, 6.5, 6.5, 5.3)
arrow(ax, 8.15, 6.5, 7.3, 5.3)

# ===== STEP 5: Phase 1 loss (training only) =====
# Left branch: contrastive loss
box(ax, 10.5, 6.5, 3, 1.2,
    'Phase 1 (training only):\nContrastive Loss\n$\\mathcal{L}_{con}(e_1, e_2, y)$',
    C_LOSS, fontsize=8)
arrow(ax, 9.3, 7.1, 10.5, 7.1, color='#888')
ax.text(10.4, 7.3, 'pair of QRs', ha='center', fontsize=7, style='italic', color='#555')

# ===== STEP 6: Classifier head =====
step_label(ax, 0.5, 3.3, 5, 'Phase 2 classifier head')
box(ax, 5.3, 2.8, 3, 1,
    'Linear 128->512->128->32->1\n+BN +ReLU +Dropout',
    C_HEAD, fontsize=9)
arrow(ax, 6.8, 4.3, 6.8, 3.8)

# ===== STEP 7: Focal loss (training) =====
box(ax, 10.5, 2.9, 3, 1,
    'Phase 2 (training):\nFocal Loss\n$\\mathcal{L}_{focal}(p, y)$',
    C_LOSS, fontsize=8)
arrow(ax, 8.3, 3.3, 10.5, 3.3, color='#888')

# ===== STEP 8: Output =====
step_label(ax, 0.5, 1.8, 6, 'Output probability')
box(ax, 5.3, 1.3, 3, 0.9,
    '$\\sigma$(logit) = P(phishing)\n[0, 1]',
    C_OUTPUT, fontsize=10, fontweight='bold')
arrow(ax, 6.8, 2.8, 6.8, 2.2)

# ===== STEP 9: XAI =====
step_label(ax, 10, 1.8, 7, 'Explainability')
box(ax, 9.5, 1.3, 1.8, 0.9, 'Grad-CAM\n(spatial)', C_XAI, fontsize=8)
box(ax, 11.5, 1.3, 1.8, 0.9, 'SHAP\n(feature)', C_XAI, fontsize=8)
arrow(ax, 8.3, 1.75, 9.5, 1.75)

# ===== STEP 10: Threshold decision =====
step_label(ax, 0.5, 0.3, 8, 'Calibrated threshold for deployment (see Table VII)')

# Legend
legend_y = 0.1
legend_items = [
    (C_INPUT, 'Input/Preprocess'),
    (C_BACKBONE, 'Backbone'),
    (C_HEAD, 'Classifier'),
    (C_LOSS, 'Training loss'),
    (C_XAI, 'XAI'),
    (C_OUTPUT, 'Output'),
]
x_start = 1.5
for color, label in legend_items:
    ax.scatter(x_start, legend_y, s=150, c=color, edgecolors='black', zorder=5)
    ax.text(x_start + 0.2, legend_y, label, va='center', fontsize=8)
    x_start += 1.9

# Note about training vs inference
ax.text(7, -0.35,
        'Training: steps 1-6 + both loss boxes. Inference: steps 1-6 + step 9 only (loss boxes inactive).',
        ha='center', fontsize=8, style='italic', color='#666')

plt.tight_layout()
plt.savefig('figures/fig_pipeline_architecture.png',
            dpi=250, bbox_inches='tight', facecolor='white')
print('Pipeline figure saved: figures/fig_pipeline_architecture.png')
