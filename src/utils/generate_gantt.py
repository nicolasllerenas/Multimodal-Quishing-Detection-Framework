"""
Q-Shield Project — Gantt Chart Generator
IEEE Paper: Multimodal Quishing Detection Framework
Author: Nicolas Alejandro Llerena Silva (UTEC)
Generated: 2026-04-15
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import numpy as np

# ============================================================
# PROJECT PHASES — Critical Path for IEEE Submission
# ============================================================
# Deadline: May 25, 2026 (with buffer before conference submission)

phases = [
    # (Phase ID, Name, Start, End, Category, Status, Milestone?)
    # --- WEEK 1: April 15-20 — Data Analysis & Foundations ---
    ("P1", "Project Planning & Gantt", "2026-04-15", "2026-04-15", "planning", "done", False),
    ("P2a", "EDA: CIC Feature CSVs\n(HTML/PDF/Excel/Word)", "2026-04-15", "2026-04-17", "data", "done", False),
    ("P2b", "EDA: QR Structural Analysis\n(CIC 1M+ images)", "2026-04-16", "2026-04-19", "data", "active", False),
    ("P2c", "EDA: Trad et al. Dataset\n(9,987 QR arrays)", "2026-04-16", "2026-04-18", "data", "active", False),
    ("P2d", "Pattern Report:\nAttack Taxonomy", "2026-04-19", "2026-04-20", "data", "pending", False),
    ("M1", "MILESTONE: Patterns Identified", "2026-04-20", "2026-04-20", "milestone", "pending", True),

    # --- WEEK 2: April 21-27 — SOTA + Baseline ---
    ("P3", "Literature Review &\nSOTA Comparison Table", "2026-04-17", "2026-04-23", "paper", "pending", False),
    ("P4a", "Baseline: Feature Engineering\n(reproduce Trad features)", "2026-04-20", "2026-04-22", "model", "pending", False),
    ("P4b", "Baseline: XGBoost/LightGBM\nTraining & Evaluation", "2026-04-22", "2026-04-25", "model", "pending", False),
    ("M2", "MILESTONE: Baseline AUC > 0.90", "2026-04-25", "2026-04-25", "milestone", "pending", True),

    # --- WEEK 3: April 28 - May 4 — Q-Shield Architecture ---
    ("P5a", "Visual Branch:\nMobileNetV2 on QR images", "2026-04-25", "2026-04-30", "model", "pending", False),
    ("P6", "Peruvian SMS Dataset\n(100 samples + augmentation)", "2026-04-25", "2026-04-28", "data", "pending", False),
    ("P5b", "Semantic Branch:\nDistilBERT on SMS text", "2026-04-28", "2026-05-02", "model", "pending", False),
    ("P5c", "Late Fusion:\nTwo-Stream Integration", "2026-05-02", "2026-05-05", "model", "pending", False),
    ("M3", "MILESTONE: Q-Shield v1.0 Trained", "2026-05-05", "2026-05-05", "milestone", "pending", True),

    # --- WEEK 4: May 5-11 — XAI + Ablation ---
    ("P7a", "Grad-CAM: Visual Branch\nAttention Maps", "2026-05-05", "2026-05-08", "xai", "pending", False),
    ("P7b", "SHAP: Feature Importance\nAcross Both Branches", "2026-05-06", "2026-05-09", "xai", "pending", False),
    ("P7c", "Ablation Study:\nVisual-only vs Semantic-only vs Fused", "2026-05-08", "2026-05-11", "model", "pending", False),
    ("M4", "MILESTONE: All Experiments Done", "2026-05-11", "2026-05-11", "milestone", "pending", True),

    # --- WEEK 5-6: May 12-25 — Paper Writing ---
    ("P8a", "Paper: Sections I-III\n(Intro, Related Work, Method)", "2026-05-05", "2026-05-14", "paper", "pending", False),
    ("P8b", "Paper: Sections IV-V\n(Experiments, Results)", "2026-05-11", "2026-05-17", "paper", "pending", False),
    ("P8c", "Paper: Section VI + Abstract\n(Discussion, Conclusion)", "2026-05-17", "2026-05-20", "paper", "pending", False),
    ("P8d", "Figures, Tables &\nFormatting (IEEEtran)", "2026-05-14", "2026-05-20", "paper", "pending", False),
    ("P8e", "Advisor Review &\nRevisions", "2026-05-20", "2026-05-23", "paper", "pending", False),
    ("M5", "DEADLINE: Paper Submission", "2026-05-25", "2026-05-25", "milestone", "pending", True),
]

# ============================================================
# VISUALIZATION
# ============================================================

# Color scheme
COLORS = {
    "planning": "#95a5a6",
    "data":     "#3498db",
    "model":    "#e74c3c",
    "xai":      "#9b59b6",
    "paper":    "#2ecc71",
    "milestone": "#f39c12",
}

STATUS_ALPHA = {
    "done":    1.0,
    "active":  0.85,
    "pending": 0.5,
}

fig, ax = plt.subplots(figsize=(22, 14))

# Parse dates
y_labels = []
y_positions = []

for i, (pid, name, start_str, end_str, cat, status, is_milestone) in enumerate(reversed(phases)):
    y = i
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")
    duration = max((end - start).days, 0.5)  # min half-day for milestones

    color = COLORS[cat]
    alpha = STATUS_ALPHA[status]

    if is_milestone:
        # Diamond marker for milestones
        mid = start + timedelta(days=duration/2)
        ax.plot(mid, y, marker='D', markersize=16, color=color,
                markeredgecolor='black', markeredgewidth=1.5, zorder=5)
        ax.annotate(f"  {name}", (mid, y), fontsize=8, fontweight='bold',
                    va='center', color='#2c3e50')
    else:
        # Gantt bar
        bar = ax.barh(y, duration, left=start, height=0.6,
                      color=color, alpha=alpha, edgecolor='black', linewidth=0.8)

        # Status hatching
        if status == "done":
            ax.barh(y, duration, left=start, height=0.6,
                    color='none', edgecolor='black', linewidth=0.8,
                    hatch='///')

    y_labels.append(f"[{pid}] {name}")
    y_positions.append(y)

# Axes formatting
ax.set_yticks(y_positions)
ax.set_yticklabels(y_labels, fontsize=9, fontfamily='monospace')
ax.set_xlabel('Timeline', fontsize=12, fontweight='bold')

# Date formatting
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax.xaxis.set_minor_locator(mdates.DayLocator())
plt.xticks(rotation=45, ha='right')

# Grid
ax.grid(axis='x', alpha=0.3, which='major')
ax.grid(axis='x', alpha=0.1, which='minor')

# Today line
today = datetime(2026, 4, 15)
ax.axvline(today, color='red', linewidth=2, linestyle='--', alpha=0.8, zorder=10)
ax.annotate('TODAY\n(Apr 15)', xy=(today, len(phases)-1), fontsize=9,
            fontweight='bold', color='red', ha='center',
            xytext=(today, len(phases)+0.5))

# Deadline line
deadline = datetime(2026, 5, 25)
ax.axvline(deadline, color='#e74c3c', linewidth=3, linestyle='-', alpha=0.9, zorder=10)
ax.annotate('DEADLINE\n(May 25)', xy=(deadline, len(phases)-1), fontsize=9,
            fontweight='bold', color='#e74c3c', ha='center',
            xytext=(deadline, len(phases)+0.5))

# Week labels at top
for week_num, week_start in enumerate([
    datetime(2026, 4, 15), datetime(2026, 4, 21), datetime(2026, 4, 28),
    datetime(2026, 5, 5), datetime(2026, 5, 12), datetime(2026, 5, 19)
], 1):
    week_themes = {
        1: "Data Analysis\n& Patterns",
        2: "SOTA &\nBaseline",
        3: "Q-Shield\nArchitecture",
        4: "XAI &\nAblation",
        5: "Paper\nWriting",
        6: "Review &\nSubmit",
    }
    mid = week_start + timedelta(days=3)
    ax.annotate(f"Week {week_num}\n{week_themes[week_num]}",
                xy=(mid, len(phases) + 1.5), fontsize=8, ha='center',
                fontweight='bold', color='#2c3e50',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          edgecolor='gray', alpha=0.8))

# Legend
legend_elements = [
    mpatches.Patch(facecolor=COLORS["data"], alpha=0.7, label='Data & EDA', edgecolor='black'),
    mpatches.Patch(facecolor=COLORS["model"], alpha=0.7, label='Model Development', edgecolor='black'),
    mpatches.Patch(facecolor=COLORS["xai"], alpha=0.7, label='XAI / Explainability', edgecolor='black'),
    mpatches.Patch(facecolor=COLORS["paper"], alpha=0.7, label='Paper Writing', edgecolor='black'),
    mpatches.Patch(facecolor=COLORS["planning"], alpha=0.7, label='Planning', edgecolor='black'),
    plt.Line2D([0], [0], marker='D', color='w', markerfacecolor=COLORS["milestone"],
               markersize=10, markeredgecolor='black', label='Milestone'),
    mpatches.Patch(facecolor='white', hatch='///', edgecolor='black', label='Completed'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=9,
          framealpha=0.9, edgecolor='black')

# Title
ax.set_title('Q-Shield: IEEE Paper Development — Gantt Chart\n'
             'Multimodal Quishing Detection Framework\n'
             'Nicolas A. Llerena Silva — UTEC, 2026',
             fontsize=14, fontweight='bold', pad=40)

# Set x limits with padding
ax.set_xlim(datetime(2026, 4, 13), datetime(2026, 5, 28))

plt.tight_layout()
plt.savefig('QShield_Gantt_Chart.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Gantt chart saved: QShield_Gantt_Chart.png")
plt.show()
