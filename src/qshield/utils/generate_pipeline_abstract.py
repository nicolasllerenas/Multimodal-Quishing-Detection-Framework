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
# Canvas
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(16, 9.5))
ax.set_xlim(0, 16)
ax.set_ylim(0, 9.5)
ax.set_aspect('equal')
ax.axis('off')


# Title
ax.text(8, 9.05, 'Q-Shield: Multimodal Quishing Detection Pipeline',
        ha='center', va='center', fontsize=20, fontweight='bold',
        color='#0E1B2C')
ax.text(8, 8.60, 'visual Siamese branch + offline-decoded URL text branch + late fusion',
        ha='center', va='center', fontsize=12, color='#444444', style='italic')

# Faint horizontal divider under the title
ax.plot([0.5, 15.5], [8.30, 8.30], color='#CCCCCC', linewidth=0.6)

# Headline metrics strip (centered under the divider)
ax.text(8, 8.05,
        'AUC 0.9749   ·   F1 0.936   ·   recall 0.943   ·   '
        'FNR 0.057   ·   ECE 0.038   ·   n = 21,998 (Trad + CIC)',
        ha='center', va='center', fontsize=11, color='#0E1B2C',
        fontweight='bold')


# ------------------------------------------------------------
# Stage 1 — shared input column (left)
# ------------------------------------------------------------
box(ax, 0.4, 6.6, 1.7, 1.1, '1. Raw QR',
    'image\n(any version,\nany resolution)',
    'input', fontsize_top=11, fontsize_body=8.5)

box(ax, 0.4, 4.5, 1.7, 1.1, '2. Pre-process',
    'grayscale\n+ resize\n224×224',
    'input', fontsize_top=11, fontsize_body=8.5)

# Connector from raw → preprocess
arrow(ax, 1.25, 6.6, 1.25, 5.6, lw=1.2)


# ------------------------------------------------------------
# Stage 2 — VISUAL branch (upper row)
# ------------------------------------------------------------
box(ax, 2.6, 5.65, 2.6, 1.4, '3a. Visual backbone',
    'Siamese\nMobileNetV2\n(shared weights)',
    'visual', fontsize_top=11, fontsize_body=9)

box(ax, 5.5, 5.65, 1.95, 1.4, '4a. Embedding',
    '128-d\nL2-normalized',
    'visual', fontsize_top=11, fontsize_body=9)

box(ax, 7.75, 5.65, 2.5, 1.4, '5a. Classifier head',
    '128 → 512 → 128\n→ 32 → 1\n(BN + ReLU + Dropout)',
    'classifier', fontsize_top=11, fontsize_body=9)

# Visual logit label
ax.text(10.5, 6.35, '$\\ell_v$', ha='center', va='center',
        fontsize=14, fontweight='bold', color=COLORS['visual'][1])

# Arrows along visual branch
arrow(ax, 2.1, 5.05, 2.6, 6.35, lw=1.3, mutation=15)  # preprocess → backbone
arrow(ax, 5.2, 6.35, 5.5, 6.35)                        # backbone → embedding
arrow(ax, 7.45, 6.35, 7.75, 6.35)                      # embedding → head
arrow(ax, 10.25, 6.35, 11.0, 5.5, lw=1.5)              # head → fusion (visual logit)


# ------------------------------------------------------------
# Stage 3 — TEXT branch (lower row)
# ------------------------------------------------------------
box(ax, 2.6, 3.2, 2.0, 1.4, '3b. pyzbar decode',
    'libzbar (offline,\nlocal, no network)',
    'decode', fontsize_top=11, fontsize_body=9)

box(ax, 4.85, 3.2, 2.4, 1.4, '4b. URL string',
    'or  ⟨UNDECODABLE⟩\n+ binary flag $f$',
    'decode', fontsize_top=11, fontsize_body=9)

box(ax, 7.55, 3.2, 2.7, 1.4, '5b. URL classifier',
    'tokenizer +\nDistilBERT (66M)\n[CLS] → linear',
    'text', fontsize_top=11, fontsize_body=9)

# Text logit label
ax.text(10.5, 3.9, '$\\ell_t$', ha='center', va='center',
        fontsize=14, fontweight='bold', color=COLORS['text'][1])

# Arrows along text branch
arrow(ax, 2.1, 5.05, 2.6, 3.9, lw=1.3, mutation=15)    # preprocess → decode
arrow(ax, 4.6, 3.9, 4.85, 3.9)                          # decode → URL string
arrow(ax, 7.25, 3.9, 7.55, 3.9)                         # URL string → DistilBERT
arrow(ax, 10.25, 3.9, 11.0, 4.7, lw=1.5)                # DistilBERT → fusion (text logit)


# ------------------------------------------------------------
# Stage 4 — FUSION + OUTPUT
# ------------------------------------------------------------
box(ax, 11.0, 4.65, 2.5, 1.5, '6. Late-fusion',
    'MLP $\\,[\\ell_v, \\ell_t, f]\\,$\n$\\to 16 \\to 1$\n(161 params)',
    'fusion', fontsize_top=11, fontsize_body=9)

box(ax, 13.85, 4.65, 1.85, 1.5, '7. $\\sigma(\\mathrm{logit})$',
    'final\n$P(\\mathrm{phishing})$\n(threshold 0.5)',
    'output', fontsize_top=11, fontsize_body=9)

arrow(ax, 13.5, 5.4, 13.85, 5.4, lw=1.5)


# Undecodable flag arrow into fusion (curving up from below the text branch)
ax.text(8.7, 2.85, 'undecodability flag $f$',
        ha='center', va='center', fontsize=9, color=COLORS['decode'][1],
        style='italic', fontweight='bold')
curved_arrow(ax, 6.05, 3.2, 11.0, 4.85, color=COLORS['decode'][1],
             lw=1.2, rad=-0.25, mutation=12, alpha=0.85)


# ------------------------------------------------------------
# Training annotations (below each component that gets trained)
# ------------------------------------------------------------
training_annot(ax, 2.6, 1.6, 2.6, 1.05,
               'Phase 1 (visual)',
               'Contrastive loss\n$\\mathcal{L}_{\\mathrm{con}}(e_1,e_2,y)$,  margin $m=1.5$')
arrow(ax, 3.9, 2.65, 3.9, 5.65, color=COLORS['training'][1],
      lw=1.2, alpha=0.7, style='-|>')

training_annot(ax, 7.55, 1.6, 2.7, 1.05,
               'Phase 2 (visual head)',
               'Focal loss  $\\gamma{=}2,\\,\\alpha{=}0.5$\nbackbone frozen 5 ep, then unfrozen')
arrow(ax, 8.9, 2.65, 8.9, 5.65, color=COLORS['training'][1],
      lw=1.2, alpha=0.7, style='-|>')

training_annot(ax, 10.55, 1.6, 2.6, 1.05,
               'Text fine-tune',
               'Focal loss, AdamW lr $2{\\times}10^{-5}$,\n3 epochs over decoded URLs')
arrow(ax, 11.85, 2.65, 9.0, 3.2, color=COLORS['training'][1],
      lw=1.2, alpha=0.7, style='-|>')

training_annot(ax, 13.45, 1.6, 2.3, 1.05,
               'Fusion train',
               'Focal loss on cached\nlogits ($\\sim$1 min on CPU)')
arrow(ax, 14.45, 2.65, 12.25, 4.65, color=COLORS['training'][1],
      lw=1.2, alpha=0.7, style='-|>')


# ------------------------------------------------------------
# XAI panel (left, below the input column)
# ------------------------------------------------------------
box(ax, 0.4, 1.6, 1.9, 1.05, '8. Explainability',
    'Grad-CAM (visual)\n+ SHAP (embedding)',
    'xai', fontsize_top=10.5, fontsize_body=8.5)
# Curved arrow from XAI box to the visual classifier head
curved_arrow(ax, 1.35, 2.65, 8.5, 5.65, color=COLORS['xai'][1],
             lw=1.2, alpha=0.55, rad=-0.18, mutation=12, style='-|>')


# ------------------------------------------------------------
# Legend (bottom)
# ------------------------------------------------------------
legend_y = 0.6
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
swatch_w = 0.32
swatch_h = 0.32
text_dx = 0.42
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
            ha='left', va='center', fontsize=8.5, color=INK)


# ------------------------------------------------------------
# Footer caption
# ------------------------------------------------------------
ax.text(8, 0.18,
        'Training: Phase 1 + Phase 2 train the visual branch; the URL classifier is fine-tuned on offline-decoded URLs; '
        'the fusion MLP learns over cached logits. '
        'Inference: visual + text logits and the undecodability flag feed the fusion; step 8 is applied on demand.',
        ha='center', va='center', fontsize=8.5, style='italic',
        color='#555555', wrap=True)


plt.tight_layout()
plt.savefig(str(OUTPUT), dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f'Saved: {OUTPUT}')
