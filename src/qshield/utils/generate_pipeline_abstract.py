"""Graphical abstract for the Q-Shield multimodal architecture.

Reproducible matplotlib version. Two parallel processing branches
(visual + text) converging into a late-fusion head, training-loss
annotations underneath each component, and an XAI block on the side.
"""

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


REPO = Path(__file__).resolve().parents[3]
OUTPUT = REPO / 'figures' / 'fig_pipeline_abstract.png'


# Color palette: fill / edge per category
COLORS = {
    'input':     ('#CEE4F4', '#1E5A93'),
    'visual':    ('#FAD8C8', '#C44A2A'),
    'classifier':('#D4ECCC', '#3C7B3C'),
    'decode':    ('#F5E6A3', '#B89220'),
    'text':      ('#E0D2EE', '#6B4D9A'),
    'fusion':    ('#B8DDB1', '#2E7D32'),
    'output':    ('#C5E0DA', '#2C7C7B'),
    'training':  ('#FCDFB1', '#D08A2A'),
    'xai':       ('#E6D5EC', '#6E3D8C'),
}

INK = '#1A1A1A'


def box(ax, x, y, w, h, label_top, label_body, kind, *,
        fontsize_top=11, fontsize_body=10, weight_top='bold'):
    fill, edge = COLORS[kind]
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle='round,pad=0.02,rounding_size=0.05',
                          linewidth=1.3, edgecolor=edge, facecolor=fill,
                          mutation_aspect=1)
    ax.add_patch(rect)
    if label_top:
        ax.text(x + w / 2, y + h - 0.18, label_top,
                ha='center', va='top', fontsize=fontsize_top,
                fontweight=weight_top, color=INK)
    if label_body:
        ax.text(x + w / 2, y + h - 0.55, label_body,
                ha='center', va='top', fontsize=fontsize_body,
                color=INK, wrap=True, linespacing=1.25)


def arrow(ax, x1, y1, x2, y2, *, color='#3A3A3A', lw=1.3, style='-|>',
          mutation=14, alpha=1.0):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                        arrowstyle=style, mutation_scale=mutation,
                        linewidth=lw, color=color, alpha=alpha,
                        connectionstyle='arc3,rad=0.0')
    ax.add_patch(a)


def curved_arrow(ax, x1, y1, x2, y2, *, color='#3A3A3A', lw=1.3,
                 mutation=14, rad=0.2, alpha=1.0, style='-|>'):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                        arrowstyle=style, mutation_scale=mutation,
                        linewidth=lw, color=color, alpha=alpha,
                        connectionstyle=f'arc3,rad={rad}')
    ax.add_patch(a)


def training_annot(ax, x, y, w, h, title, body):
    """Smaller orange-tinted box anchored below a pipeline component."""
    fill, edge = COLORS['training']
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle='round,pad=0.015,rounding_size=0.04',
                          linewidth=1.0, edgecolor=edge, facecolor=fill,
                          mutation_aspect=1)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h - 0.13, title,
            ha='center', va='top', fontsize=9, fontweight='bold',
            color='#7A4F11', style='italic')
    ax.text(x + w / 2, y + h - 0.38, body,
            ha='center', va='top', fontsize=8.5,
            color=INK, linespacing=1.25)


# ------------------------------------------------------------
# Canvas — wide-format to fit a single IEEE figure* without forcing
# a page break.
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(16, 7.6))
ax.set_xlim(0, 16)
ax.set_ylim(0, 7.6)
ax.set_aspect('auto')
ax.axis('off')


# Title
ax.text(8, 7.20, 'Q-Shield: Multimodal Quishing Detection Pipeline',
        ha='center', va='center', fontsize=18, fontweight='bold',
        color='#0E1B2C')
ax.text(8, 6.78, 'visual Siamese branch + offline-decoded URL text branch + late fusion',
        ha='center', va='center', fontsize=11, color='#444444', style='italic')

# Faint horizontal divider under the title
ax.plot([0.5, 15.5], [6.50, 6.50], color='#CCCCCC', linewidth=0.6)

# Headline metrics strip
ax.text(8, 6.27,
        'AUC 0.9749   ·   F1 0.936   ·   recall 0.943   ·   '
        'FNR 0.057   ·   ECE 0.038   ·   n = 21,998 (Trad + CIC)',
        ha='center', va='center', fontsize=10.5, color='#0E1B2C',
        fontweight='bold')


# ------------------------------------------------------------
# Stage 1 — shared input column (left)
# ------------------------------------------------------------
box(ax, 0.4, 5.05, 1.7, 0.95, '1. Raw QR',
    'image\n(any version,\nany resolution)',
    'input', fontsize_top=10.5, fontsize_body=8)

box(ax, 0.4, 3.55, 1.7, 0.95, '2. Pre-process',
    'grayscale\n+ resize\n224×224',
    'input', fontsize_top=10.5, fontsize_body=8)

# Connector from raw → preprocess
arrow(ax, 1.25, 5.05, 1.25, 4.5, lw=1.2)


# ------------------------------------------------------------
# Stage 2 — VISUAL branch (upper row)
# ------------------------------------------------------------
box(ax, 2.6, 4.4, 2.6, 1.25, '3a. Visual backbone',
    'Siamese MobileNetV2\n(shared weights)',
    'visual', fontsize_top=10.5, fontsize_body=8.5)

box(ax, 5.5, 4.4, 1.95, 1.25, '4a. Embedding',
    '128-d\nL2-normalized',
    'visual', fontsize_top=10.5, fontsize_body=8.5)

box(ax, 7.75, 4.4, 2.5, 1.25, '5a. Classifier head',
    '128→512→128→32→1\n(BN+ReLU+Dropout)',
    'classifier', fontsize_top=10.5, fontsize_body=8.5)

# Visual logit label
ax.text(10.5, 5.0, '$\\ell_v$', ha='center', va='center',
        fontsize=13, fontweight='bold', color=COLORS['visual'][1])

# Arrows along visual branch
arrow(ax, 2.1, 4.0, 2.6, 5.0, lw=1.3, mutation=14)
arrow(ax, 5.2, 5.0, 5.5, 5.0)
arrow(ax, 7.45, 5.0, 7.75, 5.0)
arrow(ax, 10.25, 5.0, 11.0, 4.4, lw=1.5)


# ------------------------------------------------------------
# Stage 3 — TEXT branch (lower row)
# ------------------------------------------------------------
box(ax, 2.6, 2.55, 2.0, 1.25, '3b. pyzbar decode',
    'libzbar\n(offline, local)',
    'decode', fontsize_top=10.5, fontsize_body=8.5)

box(ax, 4.85, 2.55, 2.4, 1.25, '4b. URL string',
    'or  ⟨UNDECODABLE⟩\n+ binary flag $f$',
    'decode', fontsize_top=10.5, fontsize_body=8.5)

box(ax, 7.55, 2.55, 2.7, 1.25, '5b. URL classifier',
    'tokenizer +\nDistilBERT (66M)',
    'text', fontsize_top=10.5, fontsize_body=8.5)

# Text logit label
ax.text(10.5, 3.18, '$\\ell_t$', ha='center', va='center',
        fontsize=13, fontweight='bold', color=COLORS['text'][1])

# Arrows along text branch
arrow(ax, 2.1, 4.0, 2.6, 3.18, lw=1.3, mutation=14)
arrow(ax, 4.6, 3.18, 4.85, 3.18)
arrow(ax, 7.25, 3.18, 7.55, 3.18)
arrow(ax, 10.25, 3.18, 11.0, 3.7, lw=1.5)


# ------------------------------------------------------------
# Stage 4 — FUSION + OUTPUT
# ------------------------------------------------------------
box(ax, 11.0, 3.65, 2.5, 1.35, '6. Late-fusion',
    'MLP $[\\ell_v, \\ell_t, f]$\n$\\to 16 \\to 1$',
    'fusion', fontsize_top=10.5, fontsize_body=9)

box(ax, 13.85, 3.65, 1.85, 1.35, '7. $\\sigma(\\mathrm{logit})$',
    'final\n$P(\\mathrm{phishing})$',
    'output', fontsize_top=10.5, fontsize_body=9)

arrow(ax, 13.5, 4.32, 13.85, 4.32, lw=1.5)


# Undecodable flag arrow into fusion
ax.text(8.7, 2.30, 'undecodability flag $f$',
        ha='center', va='center', fontsize=8.5, color=COLORS['decode'][1],
        style='italic', fontweight='bold')
curved_arrow(ax, 6.05, 2.55, 11.0, 3.8, color=COLORS['decode'][1],
             lw=1.2, rad=-0.25, mutation=12, alpha=0.85)


# ------------------------------------------------------------
# Training annotations (compact row at bottom)
# ------------------------------------------------------------
training_annot(ax, 2.6, 1.05, 2.6, 0.85,
               'Phase 1 (visual)',
               'Contrastive,  $m=1.5$')
arrow(ax, 3.9, 1.90, 3.9, 4.4, color=COLORS['training'][1],
      lw=1.0, alpha=0.6, style='-|>')

training_annot(ax, 7.55, 1.05, 2.7, 0.85,
               'Phase 2 (visual head)',
               'Focal,  $\\gamma{=}2,\\,\\alpha{=}0.5$')
arrow(ax, 8.9, 1.90, 8.9, 4.4, color=COLORS['training'][1],
      lw=1.0, alpha=0.6, style='-|>')

training_annot(ax, 10.55, 1.05, 2.6, 0.85,
               'Text fine-tune',
               'Focal,  AdamW $2{\\times}10^{-5}$,  3 ep')
arrow(ax, 11.85, 1.90, 9.0, 2.55, color=COLORS['training'][1],
      lw=1.0, alpha=0.6, style='-|>')

training_annot(ax, 13.45, 1.05, 2.3, 0.85,
               'Fusion train',
               'Focal on cached logits')
arrow(ax, 14.45, 1.90, 12.25, 3.65, color=COLORS['training'][1],
      lw=1.0, alpha=0.6, style='-|>')


# ------------------------------------------------------------
# XAI panel (left, below the input column)
# ------------------------------------------------------------
box(ax, 0.4, 1.05, 1.9, 0.85, '8. Explainability',
    'Grad-CAM + SHAP',
    'xai', fontsize_top=10, fontsize_body=8)
curved_arrow(ax, 1.35, 1.90, 8.5, 4.4, color=COLORS['xai'][1],
             lw=1.0, alpha=0.5, rad=-0.18, mutation=11, style='-|>')


# ------------------------------------------------------------
# Legend (bottom)
# ------------------------------------------------------------
legend_y = 0.45
legend_entries = [
    ('Input / pre-processing', 'input'),
    ('Visual backbone',         'visual'),
    ('Classifier head',         'classifier'),
    ('Decode',                  'decode'),
    ('Text branch',             'text'),
    ('Late fusion',             'fusion'),
    ('Output',                  'output'),
    ('Training loss',           'training'),
    ('Explainability',          'xai'),
]
swatch_w = 0.28
swatch_h = 0.28
text_dx = 0.38
spacing = 1.62
start_x = 0.5

for i, (label, kind) in enumerate(legend_entries):
    cx = start_x + i * spacing
    fill, edge = COLORS[kind]
    rect = FancyBboxPatch((cx, legend_y), swatch_w, swatch_h,
                          boxstyle='round,pad=0.01,rounding_size=0.04',
                          linewidth=1.0, edgecolor=edge, facecolor=fill)
    ax.add_patch(rect)
    ax.text(cx + text_dx, legend_y + swatch_h / 2, label,
            ha='left', va='center', fontsize=8, color=INK)


# Footer caption
ax.text(8, 0.10,
        'Training: visual phases 1+2, URL fine-tune, fusion train. '
        'Inference: visual + text logits + undecodability flag → fusion → P(phishing). '
        'Step 8 (XAI) on demand.',
        ha='center', va='center', fontsize=8, style='italic',
        color='#555555')


plt.tight_layout()
plt.savefig(str(OUTPUT), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f'Saved: {OUTPUT}')
