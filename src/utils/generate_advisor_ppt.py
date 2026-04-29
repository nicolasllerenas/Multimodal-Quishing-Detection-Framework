"""Build the Q-Shield advisor presentation (.pptx).

Editorial-style deck. Sections are introduced by full-bleed dividers,
each content slide picks the layout that fits its message
(hero numbers, asymmetric splits, full-bleed images, narrative arcs).
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


REPO = Path(__file__).resolve().parents[2]
FIGURES = REPO / 'figures'
OUTPUT = REPO / 'Q-Shield_Presentacion_Asesora_v2.pptx'


INK = RGBColor(0x14, 0x1B, 0x29)
DEEP = RGBColor(0x1F, 0x3A, 0x5F)
ACCENT = RGBColor(0xC9, 0x52, 0x2A)
TEAL = RGBColor(0x2A, 0x7C, 0x7C)
GOLD = RGBColor(0xC8, 0x95, 0x1C)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
RED = RGBColor(0xC6, 0x28, 0x28)
PAPER = RGBColor(0xFA, 0xF7, 0xF1)
SAND = RGBColor(0xF1, 0xEC, 0xDF)
GREY_DK = RGBColor(0x55, 0x55, 0x55)
GREY = RGBColor(0x88, 0x88, 0x88)
GREY_LT = RGBColor(0xCC, 0xCC, 0xCC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW = prs.slide_width
SH = prs.slide_height


def slide():
    return prs.slides.add_slide(prs.slide_layouts[6])


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def no_line(shape):
    shape.line.fill.background()


def rect(s, x, y, w, h, color, line=None):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    fill(sh, color)
    if line is None:
        no_line(sh)
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    return sh


def line(s, x1, y1, x2, y2, color, weight=1.0):
    ln = s.shapes.add_connector(1, x1, y1, x2, y2)
    ln.line.color.rgb = color
    ln.line.width = Pt(weight)
    return ln


def text(s, x, y, w, h, content, *, size=18, bold=False, italic=False,
         color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         font='Calibri', spacing=1.15):
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    lines = content.split('\n')
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = ln
        r.font.name = font
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
    return tb


def bullets(s, x, y, w, h, items, *, size=15, color=INK, marker='—'):
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = 1.25
        p.space_after = Pt(6)
        r = p.add_run()
        r.text = f'{marker}  {item}'
        r.font.name = 'Calibri'
        r.font.size = Pt(size)
        r.font.color.rgb = color
    return tb


def page_header(s, eyebrow, headline):
    """Editorial page header: thin eyebrow + thick headline + hairline."""
    text(s, Inches(0.7), Inches(0.45), Inches(11.9), Inches(0.3),
         eyebrow.upper(), size=10, bold=True, color=ACCENT, font='Calibri')
    text(s, Inches(0.7), Inches(0.7), Inches(11.9), Inches(0.7),
         headline, size=28, bold=True, color=DEEP, font='Calibri')
    line(s, Inches(0.7), Inches(1.45), Inches(12.6), Inches(1.45), GREY_LT, 1.0)


def page_footer(s, n, total, section_label=None):
    line(s, Inches(0.7), SH - Inches(0.55), Inches(12.6), SH - Inches(0.55), GREY_LT, 0.6)
    text(s, Inches(0.7), SH - Inches(0.45), Inches(7), Inches(0.3),
         section_label or 'Q-Shield · Llerena Silva & Soriano-Vargas · UTEC 2026',
         size=9, color=GREY)
    text(s, SW - Inches(2.0), SH - Inches(0.45), Inches(1.3), Inches(0.3),
         f'{n:02d} / {total:02d}', size=9, color=GREY, align=PP_ALIGN.RIGHT)


def code_block(s, x, y, w, h, code, size=10):
    rect(s, x, y, w, h, RGBColor(0x14, 0x1B, 0x29))
    rect(s, x, y, Inches(0.08), h, ACCENT)
    tb = s.shapes.add_textbox(x + Inches(0.2), y + Inches(0.12),
                              w - Inches(0.3), h - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, ln in enumerate(code.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.1
        r = p.add_run()
        r.text = ln
        r.font.name = 'Consolas'
        r.font.size = Pt(size)
        r.font.color.rgb = RGBColor(0xE8, 0xE8, 0xEC)


def formula_card(s, x, y, w, h, formula, label=None, size=24):
    rect(s, x, y, w, h, PAPER, line=GREY_LT)
    rect(s, x, y, w, Inches(0.05), DEEP)
    if label:
        text(s, x, y + Inches(0.18), w, Inches(0.3),
             label, size=11, color=ACCENT, align=PP_ALIGN.CENTER, bold=True)
        formula_y = y + Inches(0.55)
    else:
        formula_y = y + Inches(0.2)
    text(s, x, formula_y, w, h - (formula_y - y) - Inches(0.2),
         formula, size=size, italic=True, color=DEEP,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
         font='Cambria Math')


def add_table(s, x, y, w, h, data, *, header_fill=DEEP, font_size=12,
              first_col_bold=True, highlight_rows=None,
              col_align=None):
    rows = len(data)
    cols = len(data[0])
    tbl = s.shapes.add_table(rows, cols, x, y, w, h).table
    for j, val in enumerate(data[0]):
        cell = tbl.cell(0, j)
        cell.fill.solid(); cell.fill.fore_color.rgb = header_fill
        cell.text_frame.text = ''
        cell.margin_left = cell.margin_right = Inches(0.08)
        cell.margin_top = cell.margin_bottom = Inches(0.04)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = str(val)
        r.font.name = 'Calibri'
        r.font.size = Pt(font_size)
        r.font.bold = True
        r.font.color.rgb = WHITE
    for i in range(1, rows):
        is_h = highlight_rows and i in highlight_rows
        for j, val in enumerate(data[i]):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                RGBColor(0xFF, 0xF1, 0xC4) if is_h
                else (SAND if i % 2 == 0 else WHITE))
            cell.text_frame.text = ''
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            p = cell.text_frame.paragraphs[0]
            if col_align:
                p.alignment = col_align[j] if j < len(col_align) else PP_ALIGN.LEFT
            else:
                p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            r = p.add_run()
            r.text = str(val)
            r.font.name = 'Calibri'
            r.font.size = Pt(font_size)
            r.font.color.rgb = INK
            r.font.bold = (j == 0 and first_col_bold) or is_h
    return tbl


# ============================================================
# SLIDE BUILDERS — each returns the slide it built
# ============================================================
deck = []
sections_for_index = []


def cover():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    rect(s, 0, 0, Inches(0.4), SH, DEEP)
    rect(s, 0, Inches(2.6), SW, Inches(0.06), ACCENT)
    text(s, Inches(0.9), Inches(0.95), Inches(8), Inches(0.4),
         'UTEC · DEPARTMENT OF COMPUTER SCIENCE · 2026',
         size=11, bold=True, color=ACCENT, spacing=1.0)
    text(s, Inches(0.9), Inches(1.4), Inches(11.5), Inches(1.5),
         'Q-Shield', size=84, bold=True, color=DEEP, font='Calibri')
    text(s, Inches(0.9), Inches(2.85), Inches(11.5), Inches(0.6),
         'An Explainable Siamese Network for',
         size=24, color=INK, font='Calibri')
    text(s, Inches(0.9), Inches(3.25), Inches(11.5), Inches(0.6),
         'Scalable Quishing Detection Without Payload Decoding',
         size=24, color=INK, font='Calibri')
    line(s, Inches(0.9), Inches(4.45), Inches(5.5), Inches(4.45), DEEP, 1.5)
    text(s, Inches(0.9), Inches(4.6), Inches(11), Inches(0.4),
         'Author', size=10, bold=True, color=GREY, spacing=1.0)
    text(s, Inches(0.9), Inches(4.85), Inches(11), Inches(0.5),
         'Nicolás Alejandro Llerena Silva',
         size=20, bold=True, color=INK)
    text(s, Inches(0.9), Inches(5.55), Inches(11), Inches(0.4),
         'Advisor', size=10, bold=True, color=GREY, spacing=1.0)
    text(s, Inches(0.9), Inches(5.8), Inches(11), Inches(0.5),
         'Aurea Soriano-Vargas',
         size=20, bold=True, color=INK)
    text(s, Inches(0.9), Inches(6.7), Inches(11), Inches(0.3),
         'Advisor meeting · April 2026',
         size=11, color=GREY, italic=True)
    deck.append((s, 'cover'))


def agenda():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    text(s, Inches(0.7), Inches(0.6), Inches(11.9), Inches(0.4),
         'AGENDA', size=11, bold=True, color=ACCENT)
    text(s, Inches(0.7), Inches(0.85), Inches(11.9), Inches(0.8),
         'How this meeting is organized',
         size=32, bold=True, color=DEEP)
    line(s, Inches(0.7), Inches(1.7), Inches(12.6), Inches(1.7), GREY_LT, 1.0)

    sections = [
        ('01', 'Problem & motivation',
         'Quishing as social engineering;\nthe four research gaps we close.'),
        ('02', 'Methodology',
         'Architecture, formulas, code:\nSiamese contrastive + focal loss + frozen→unfrozen schedule.'),
        ('03', 'Experiments',
         'Datasets, iterations v1→v3,\nand the reconciliation that led us to TTA + ensemble.'),
        ('04', 'Results',
         'Main numbers, ablation, cross-dataset,\nthreshold calibration, inference cost.'),
        ('05', 'Explainability',
         'Grad-CAM + SHAP\nvalidated per dataset (r = 0.43).'),
        ('06', 'What\'s next',
         'Limitations, future work,\nsubmission plan.'),
    ]
    cols = 3
    cw = Inches(4.0)
    ch = Inches(2.3)
    gap_x = Inches(0.15)
    gap_y = Inches(0.3)
    sx = Inches(0.7)
    sy = Inches(2.0)
    for i, (num, title, desc) in enumerate(sections):
        col = i % cols; row = i // cols
        x = sx + col * (cw + gap_x)
        y = sy + row * (ch + gap_y)
        rect(s, x, y, cw, ch, WHITE, line=GREY_LT)
        rect(s, x, y, cw, Inches(0.05), ACCENT)
        text(s, x + Inches(0.25), y + Inches(0.2), Inches(1.0), Inches(0.7),
             num, size=36, bold=True, color=ACCENT)
        text(s, x + Inches(0.25), y + Inches(0.95), cw - Inches(0.5), Inches(0.4),
             title, size=15, bold=True, color=DEEP)
        text(s, x + Inches(0.25), y + Inches(1.35), cw - Inches(0.5), Inches(0.85),
             desc, size=11, color=GREY_DK, spacing=1.3)
    deck.append((s, 'meta'))


def section_divider(num, label, sub):
    s = slide()
    rect(s, 0, 0, SW, SH, DEEP)
    rect(s, 0, Inches(3.5), SW, Inches(0.05), ACCENT)
    text(s, Inches(0.9), Inches(2.4), Inches(11), Inches(0.6),
         f'PART {num}', size=14, bold=True, color=ACCENT, spacing=1.0)
    text(s, Inches(0.9), Inches(2.85), Inches(11), Inches(1.0),
         label, size=44, bold=True, color=WHITE, font='Calibri')
    text(s, Inches(0.9), Inches(3.7), Inches(11), Inches(2.5),
         sub, size=18, color=RGBColor(0xCF, 0xD8, 0xE5),
         italic=True, spacing=1.4)
    sections_for_index.append((num, label))
    deck.append((s, 'divider'))


def big_problem():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'The problem', 'Quishing is a social-engineering attack')
    # Left: narrative
    text(s, Inches(0.7), Inches(1.8), Inches(7.0), Inches(0.5),
         'A learned trust the attacker weaponizes',
         size=18, bold=True, color=DEEP)
    text(s, Inches(0.7), Inches(2.4), Inches(7.0), Inches(3.7),
         'QR codes are opaque to the human eye, activated with a single gesture, '
         'and presented in contexts that implicitly mark them as legitimate '
         '— restaurant menus, parking meters, invoice PDFs, transit ads.\n\n'
         'Mitnick and Hadnagy describe this exact pattern: the attacker\'s goal '
         'is to induce an impulsive, low-scrutiny action. QR codes are almost '
         'a perfect medium for it.',
         size=14, color=INK, spacing=1.5)
    # Right: three big stats stacked
    sx = Inches(8.4); w = Inches(4.5)
    cards = [
        ('LEADING', 'initial-access vector', 'Verizon DBIR 2024'),
        ('MILLIONS', 'USD avg / phishing breach', 'IBM Cost Report 2024'),
        ('PARITY', 'with classic phishing rate', 'Weinz / Geisler 2024–2025'),
    ]
    cy = Inches(1.8)
    for big, sub, src in cards:
        rect(s, sx, cy, w, Inches(1.55), WHITE, line=GREY_LT)
        rect(s, sx, cy, Inches(0.08), Inches(1.55), ACCENT)
        text(s, sx + Inches(0.25), cy + Inches(0.1), w - Inches(0.4), Inches(0.6),
             big, size=26, bold=True, color=DEEP)
        text(s, sx + Inches(0.25), cy + Inches(0.7), w - Inches(0.4), Inches(0.45),
             sub, size=13, color=INK)
        text(s, sx + Inches(0.25), cy + Inches(1.15), w - Inches(0.4), Inches(0.35),
             src, size=10, italic=True, color=GREY)
        cy += Inches(1.7)
    deck.append((s, 'Part 01'))


def gaps():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Research gaps', 'Four problems open in the literature')
    rows = [
        ('PAYLOAD-DECODING DEPENDENCY',
         'High-performing detectors decode the QR before classifying — they inherit the exposure paradox they were meant to prevent.'),
        ('NO CROSS-DATASET EVALUATION',
         'Every prior study reports on one dataset; none measures transfer across independently collected QR corpora.'),
        ('LIMITED DUAL EXPLAINABILITY',
         'Prior work provides feature importance OR handcrafted interpretability, but not both pixel-level and latent-level explanations.'),
        ('NO OPERATIONAL CHARACTERIZATION',
         'Reported single threshold (p = 0.5) without quantifying recall/precision trade-offs for security tolerances.'),
    ]
    y = Inches(1.85); h = Inches(1.15); gap = Inches(0.15)
    for i, (head, body) in enumerate(rows):
        rect(s, Inches(0.7), y, Inches(11.9), h, WHITE, line=GREY_LT)
        rect(s, Inches(0.7), y, Inches(0.6), h, DEEP)
        text(s, Inches(0.78), y + Inches(0.3), Inches(0.5), Inches(0.6),
             f'{i+1:02d}', size=24, bold=True, color=WHITE)
        text(s, Inches(1.45), y + Inches(0.18), Inches(11.0), Inches(0.4),
             head, size=12, bold=True, color=ACCENT, spacing=1.0)
        text(s, Inches(1.45), y + Inches(0.5), Inches(11.0), Inches(0.65),
             body, size=13, color=INK, spacing=1.3)
        y += h + gap
    deck.append((s, 'Part 01'))


def contributions():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Contributions', 'Five claims supported by the paper')
    items = [
        ('Siamese contrastive architecture',
         'First Siamese-with-contrastive-loss application to QR phishing. Inter-/intra-class distance ratio = 1.94.'),
        ('Cross-dataset benchmark',
         '21,998 heterogeneous samples (Trad + CIC). 11× larger than the largest prior evaluation.'),
        ('Zero-decoding pipeline',
         'Payload never decoded. No exposure paradox; works for non-URL payloads (Wi-Fi, payment, contact).'),
        ('Calibrated operating points',
         'AUC 0.9146 / F1 0.835. Threshold sweep reaches FNR ≤ 0.10 without retraining.'),
        ('Dual-layer explainability',
         'Grad-CAM + SHAP, validated per-dataset (r = 0.43): non-trivial structural signal.'),
    ]
    y = Inches(1.85); h = Inches(0.95); gap = Inches(0.1)
    for i, (head, body) in enumerate(items):
        rect(s, Inches(0.7), y, Inches(11.9), h, SAND)
        rect(s, Inches(0.7), y, Inches(0.15), h, ACCENT)
        text(s, Inches(1.0), y + Inches(0.12), Inches(11.5), Inches(0.4),
             head, size=15, bold=True, color=DEEP)
        text(s, Inches(1.0), y + Inches(0.5), Inches(11.5), Inches(0.45),
             body, size=12, color=INK, spacing=1.3)
        y += h + gap
    deck.append((s, 'Part 01'))


def related():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Related work', 'Where Q-Shield sits relative to prior approaches')
    headers = ['Study', 'Approach', 'Decodes?', 'Deep?', 'Cross-DS', 'AUC']
    rows = [
        ['Wahsheh et al. (2021)', 'URL-based ML', 'Yes', 'No', 'No', '—'],
        ['Sharevski et al. (2022)', 'User study', '—', 'N/A', 'No', '—'],
        ['Trad & Chehab (2025)', 'Pixel-level XGBoost', 'No', 'No', 'No', '0.913'],
        ['Wahid et al. (2025)', 'Structural features', 'No', 'No', 'No', '—'],
        ['Khalifa et al. (2025)', 'Multimodal DL (URL+img)', 'Yes', 'Yes', 'No', '—'],
        ['Nejati et al. (2026)', 'CNN + URL hybrid', 'Yes', 'Yes', 'No', '> 0.95*'],
        ['Q-Shield (this work)', 'Siamese CNN + ensemble', 'No', 'Yes', 'Yes', '0.915'],
    ]
    add_table(s, Inches(0.7), Inches(1.85), Inches(11.9), Inches(3.6),
              [headers] + rows, font_size=12, highlight_rows=[7],
              col_align=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.CENTER,
                         PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.CENTER])
    text(s, Inches(0.7), Inches(5.7), Inches(11.9), Inches(0.4),
         '* Reported on URL-derived features after decoding the QR — not directly comparable to image-only systems.',
         size=10, color=GREY, italic=True)
    text(s, Inches(0.7), Inches(6.3), Inches(11.9), Inches(0.5),
         'Q-Shield is the first to combine zero-decoding, deep metric learning,',
         size=14, color=INK)
    text(s, Inches(0.7), Inches(6.65), Inches(11.9), Inches(0.5),
         'cross-dataset benchmarking, and dual-layer explainability.',
         size=14, bold=True, color=DEEP)
    deck.append((s, 'Part 01'))


def architecture_full():
    s = slide()
    rect(s, 0, 0, SW, SH, WHITE)
    text(s, Inches(0.7), Inches(0.4), Inches(12), Inches(0.4),
         'PART 02 · METHODOLOGY', size=10, bold=True, color=ACCENT, spacing=1.0)
    text(s, Inches(0.7), Inches(0.65), Inches(12), Inches(0.6),
         'The Q-Shield pipeline at a glance',
         size=22, bold=True, color=DEEP)
    img = FIGURES / 'fig_pipeline_abstract.png'
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.4), Inches(1.45),
                             width=Inches(12.55), height=Inches(5.6))
    deck.append((s, 'Part 02'))


def formulation():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Theoretical framework', 'Problem formulation')
    text(s, Inches(0.7), Inches(1.85), Inches(12), Inches(0.5),
         'Goal · Classify a grayscale QR image x without decoding its payload.',
         size=15, color=INK, italic=True)
    formula_card(s, Inches(2.0), Inches(2.7), Inches(9.3), Inches(1.4),
                 'f_θ(x) = σ( g_φ ∘ h_ψ (x) )',
                 label='Equation (1) — composition of embedding and classifier',
                 size=26)
    text(s, Inches(0.7), Inches(4.5), Inches(12), Inches(0.4),
         'COMPONENTS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(4.9), Inches(12), Inches(2.0), [
        'h_ψ : ℝ^(H×W) → ℝ^d  ·  convolutional embedding (MobileNetV2 backbone)',
        'g_φ : ℝ^d → ℝ        ·  classification head producing a logit',
        'σ : ℝ → [0, 1]       ·  sigmoid nonlinearity',
        'd = 128, L2-normalized — places all embeddings on the unit hypersphere',
    ], size=14)
    deck.append((s, 'Part 02'))


def contrastive():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Phase 1', 'Contrastive Loss · Chopra, Hadsell, LeCun (2005)')
    formula_card(s, Inches(1.0), Inches(1.85), Inches(11.3), Inches(1.4),
                 'L_con(e₁, e₂, y) = (1−y) · d² / 2  +  y · max(0, m − d)² / 2',
                 label='Equation (2) — pairwise contrastive objective',
                 size=22)
    # Two columns: where + intuition
    rect(s, Inches(0.7), Inches(3.5), Inches(5.85), Inches(3.4), WHITE, line=GREY_LT)
    text(s, Inches(0.95), Inches(3.65), Inches(5.4), Inches(0.4),
         'WHERE', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.95), Inches(4.05), Inches(5.4), Inches(2.7), [
        'd = ‖e₁ − e₂‖₂ (euclidean distance)',
        'y = 0 same class · y = 1 different class',
        'm = 1.5 — margin (grid-searched)',
    ], size=13)
    rect(s, Inches(6.75), Inches(3.5), Inches(5.85), Inches(3.4), WHITE, line=GREY_LT)
    text(s, Inches(7.0), Inches(3.65), Inches(5.4), Inches(0.4),
         'INTUITION', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(7.0), Inches(4.05), Inches(5.4), Inches(2.7), [
        'Same-class pairs ⇒ d² / 2 pulls embeddings together',
        'Different-class pairs ⇒ max(0, m − d)² / 2 pushes apart until d ≥ m',
        'Result: inter/intra ratio = 1.94 in our embedding space',
    ], size=13)
    deck.append((s, 'Part 02'))


def focal():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Phase 2', 'Focal Loss · Lin, Goyal, Girshick, He, Dollár (2017)')
    formula_card(s, Inches(2.0), Inches(1.85), Inches(9.3), Inches(1.4),
                 'L_focal(p, y) = − α_y · (1 − p_y)^γ · log p_y',
                 label='Equation (3) — focuses gradient on hard examples',
                 size=24)
    rect(s, Inches(0.7), Inches(3.5), Inches(5.85), Inches(3.4), WHITE, line=GREY_LT)
    text(s, Inches(0.95), Inches(3.65), Inches(5.4), Inches(0.4),
         'PARAMETERS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.95), Inches(4.05), Inches(5.4), Inches(2.7), [
        'p_y — predicted probability of true class',
        'α = 0.5 — balanced class weight after sampling',
        'γ = 2 — down-weights easy examples',
    ], size=13)
    rect(s, Inches(6.75), Inches(3.5), Inches(5.85), Inches(3.4), WHITE, line=GREY_LT)
    text(s, Inches(7.0), Inches(3.65), Inches(5.4), Inches(0.4),
         'WHY IT MATTERS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(7.0), Inches(4.05), Inches(5.4), Inches(2.7), [
        'Asymmetric cost — a missed phishing exposes the user',
        'Replacing focal with BCE raises FNR 0.20 → 0.27 (+7 pp)',
        'Same AUC ranking, much better coverage of malicious QRs',
    ], size=13)
    deck.append((s, 'Part 02'))


def code_backbone():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Implementation', 'Backbone — src/models/siamese_qr.py')
    code = '''class MobileNetV2Embedding(nn.Module):
    def __init__(self, embedding_dim=128, pretrained=True):
        super().__init__()
        mn = models.mobilenet_v2(
            weights=models.MobileNet_V2_Weights.DEFAULT)
        original_conv = mn.features[0][0]
        self.features = mn.features
        self.features[0][0] = nn.Conv2d(1, 32, 3, stride=2,
                                        padding=1, bias=False)
        with torch.no_grad():
            self.features[0][0].weight = nn.Parameter(
                original_conv.weight.mean(dim=1, keepdim=True))
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.projection = nn.Sequential(
            nn.Linear(1280, 512), nn.BatchNorm1d(512),
            nn.ReLU(inplace=True), nn.Dropout(0.3),
            nn.Linear(512, embedding_dim))

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x).flatten(1)
        x = self.projection(x)
        return F.normalize(x, p=2, dim=1)'''
    code_block(s, Inches(0.7), Inches(1.8), Inches(8.0), Inches(5.3), code, size=10)
    notes = [
        ('First conv: 3 → 1 channels',
         'for grayscale QR input.'),
        ('Init = mean of pretrained RGB weights',
         'preserves the ImageNet prior.'),
        ('Projection 1280 → 512 → 128',
         'with BatchNorm and Dropout 0.3.'),
        ('L2 normalization',
         'embeddings on the unit hypersphere.'),
        ('3.08 M params · 12 MB FP32',
         'per model.'),
    ]
    y = Inches(1.85)
    for h, b in notes:
        rect(s, Inches(8.95), y, Inches(3.7), Inches(0.95), WHITE, line=GREY_LT)
        rect(s, Inches(8.95), y, Inches(0.08), Inches(0.95), ACCENT)
        text(s, Inches(9.2), y + Inches(0.1), Inches(3.4), Inches(0.4),
             h, size=11, bold=True, color=DEEP)
        text(s, Inches(9.2), y + Inches(0.42), Inches(3.4), Inches(0.5),
             b, size=10, color=GREY_DK, spacing=1.2)
        y += Inches(1.05)
    deck.append((s, 'Part 02'))


def code_phase1():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Implementation', 'Phase 1 training loop · contrastive pretraining')
    code = '''model = SiameseQRNet(emb_dim=128, dropout=0.35).to(device)
criterion = ContrastiveLoss(margin=1.5)
optimizer = optim.AdamW(model.parameters(), lr=2e-4,
                        weight_decay=2e-4)
scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
    optimizer, T_0=15, T_mult=1, eta_min=1e-6)

for ep in range(1, EPOCHS1 + 1):
    model.train()
    for x1, x2, y in train_loader:
        x1, x2, y = x1.to(device), x2.to(device), y.to(device)
        optimizer.zero_grad()
        e1, e2 = model(x1, x2)
        loss = criterion(e1, e2, y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
    scheduler.step()
    if val_loss < best_val_loss:
        best_state = copy.deepcopy(model.state_dict())'''
    code_block(s, Inches(0.7), Inches(1.8), Inches(8.0), Inches(5.3), code, size=10)
    bullets(s, Inches(8.95), Inches(1.85), Inches(3.7), Inches(5.0), [
        '60,000 pairs / epoch (Trad + CIC, balanced)',
        'Up to 40 epochs · early stop patience 8',
        'Cosine annealing with warm restarts every 15 epochs',
        'Augmentation: H-flip only — rotation excluded (finder patterns encode orientation)',
        'Gradient clipping at 1.0',
    ], size=11)
    deck.append((s, 'Part 02'))


def code_phase2():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Implementation', 'Phase 2 — frozen-then-unfrozen schedule')
    code = '''classifier = QRClassifier(model.backbone, embedding_dim=128).to(device)
focal = FocalLoss(alpha=0.5, gamma=2.0)

# Phase 2a: frozen backbone, train head only (5 epochs)
classifier.set_backbone_grad(False)
opt = optim.AdamW([p for p in classifier.parameters() if p.requires_grad],
                  lr=5e-4, weight_decay=1e-4)

for ep in range(1, EPOCHS2 + 1):
    if ep == FROZEN_EP + 1:
        # Phase 2b: unfreeze, fine-tune end-to-end
        classifier.set_backbone_grad(True)
        opt = optim.AdamW(classifier.parameters(), lr=1e-4, weight_decay=2e-4)
        sch = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=15, eta_min=1e-6)

    classifier.train()
    for imgs, lbls in tr_loader:
        opt.zero_grad()
        loss = focal(classifier(imgs), lbls)
        loss.backward()
        opt.step()
    if ep > FROZEN_EP: sch.step()'''
    code_block(s, Inches(0.7), Inches(1.8), Inches(8.0), Inches(5.5), code, size=10)
    bullets(s, Inches(8.95), Inches(1.85), Inches(3.7), Inches(5.0), [
        'First 5 epochs: head only — stabilizes the random head before disturbing the backbone',
        'Last 15 epochs: end-to-end fine-tuning',
        'Empirical gain vs no-frozen-start: +0.015 AUC (Ablation A4)',
        'Best epoch typically epoch 8 — early stop on val AUC, patience 3',
    ], size=11)
    deck.append((s, 'Part 02'))


def datasets():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Datasets', 'Two complementary corpora · Trad and CIC Trap4Phish')
    headers = ['Property', 'Trad et al. (2025)', 'CIC Trap4Phish 2025']
    rows = [
        ['Total samples', '9,987', '1,005,738'],
        ['Used in this work', '9,987 (full)', '100,000 (50k+50k stratified)'],
        ['Format', 'Binary matrix', 'Grayscale PNG'],
        ['Native resolution', '69 × 69 (fixed)', '114 – 582 px'],
        ['QR version coverage', 'V13 only', 'V5 – V30'],
        ['Benign source', 'Alexa top-1M', 'Majestic Million'],
        ['Phishing source', 'PhishTank', 'PhishTank (independent crawl)'],
    ]
    add_table(s, Inches(0.7), Inches(1.85), Inches(11.9), Inches(3.5),
              [headers] + rows, font_size=12)
    text(s, Inches(0.7), Inches(5.55), Inches(12), Inches(0.4),
         'VALIDATION PROTOCOL', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.95), Inches(12), Inches(1.2), [
        'All inputs normalized to 224 × 224 grayscale before the CNN',
        '80/20 train/validation split per dataset · combined val set: 21,998 samples',
        'Random seed 42 for splits and CIC sampling — reproducible across ensemble seeds',
    ], size=12)
    deck.append((s, 'Part 03'))


def iterations():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Iteration history', 'A research diary, written in honest numbers')
    headers = ['Version', 'AUC', 'F1', 'FNR', 'Diagnosis']
    rows = [
        ['v1 — Trad-only, 64-d emb, dropout 0.3', '0.886', '0.81', '0.21',
         'Severe overfitting (30 pp gap)'],
        ['v2 — + CIC, dropout 0.5, m=1.0, rotation aug', '0.868', '0.78', '0.27',
         'Underfitting + rotation broke QR semantics'],
        ['v3 — single seed, full eval', '0.896', '0.82', '0.20',
         'Clean, but 1.71 pp below Trad SOTA'],
        ['v3 + TTA (h-flip averaging)', '0.905', '0.83', '0.20',
         '+0.91 pp at zero training cost'],
        ['v3 + TTA + 2-seed ensemble', '0.915', '0.835', '0.199',
         'Genuine SOTA-beating (+0.13 pp vs 0.913)'],
    ]
    add_table(s, Inches(0.5), Inches(1.85), Inches(12.4), Inches(3.4),
              [headers] + rows, font_size=11, highlight_rows=[5])
    text(s, Inches(0.7), Inches(5.5), Inches(12), Inches(0.4),
         'LESSONS DISTILLED INTO v3', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.9), Inches(12), Inches(1.5), [
        'Margin 1.5 wins · dropout 0.35 sweet spot · no rotation augmentation',
        'Cosine warm restarts every 15 epochs · frozen-start in Phase 2',
        'Ensembling and TTA applied at inference, not architectural rewrites',
    ], size=12)
    deck.append((s, 'Part 03'))


def reconciliation():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'A small detour', 'How we audited a number that did not match the data')
    # Three "what we found" blocks
    blocks = [
        ('Reported initially', '0.9254',
         'on the n = 21,998 set — but the confusion matrix in Fig 4 mathematically gives F1 = 0.821 and FNR = 0.20, not 0.858 / 0.166.', RED),
        ('Verified empirically', '0.8962',
         'when the same checkpoint is evaluated on the full 21,998 set. The 0.9254 came from an ablation on a subset.', GOLD),
        ('After TTA + ensemble', '0.9146',
         'on the same set, with two simple inference-time refinements that require no architectural change.', GREEN),
    ]
    sx = Inches(0.7); cw = Inches(4.0); ch = Inches(3.7); gap = Inches(0.1)
    for i, (label, num, body, c) in enumerate(blocks):
        x = sx + i * (cw + gap)
        rect(s, x, Inches(1.85), cw, ch, WHITE, line=GREY_LT)
        rect(s, x, Inches(1.85), cw, Inches(0.08), c)
        text(s, x + Inches(0.25), Inches(2.05), cw - Inches(0.5), Inches(0.4),
             label.upper(), size=11, bold=True, color=ACCENT)
        text(s, x + Inches(0.25), Inches(2.45), cw - Inches(0.5), Inches(1.3),
             num, size=64, bold=True, color=c)
        text(s, x + Inches(0.25), Inches(4.0), cw - Inches(0.5), Inches(1.6),
             body, size=12, color=INK, spacing=1.4)
    text(s, Inches(0.7), Inches(5.85), Inches(12), Inches(0.5),
         'TAKEAWAY', size=11, bold=True, color=ACCENT)
    text(s, Inches(0.7), Inches(6.2), Inches(12), Inches(0.7),
         'The reconciliation became part of the methodology — every paper number is now '
         'traceable to a script in the public repo.',
         size=14, color=INK, italic=True, spacing=1.3)
    deck.append((s, 'Part 04'))


def hero_result():
    s = slide()
    rect(s, 0, 0, SW, SH, DEEP)
    rect(s, 0, Inches(2.4), SW, Inches(0.04), ACCENT)
    text(s, Inches(0.9), Inches(1.0), Inches(11.5), Inches(0.5),
         'HEADLINE RESULT · n = 21,998', size=12, bold=True, color=ACCENT, spacing=1.0)
    text(s, Inches(0.9), Inches(1.4), Inches(11.5), Inches(1.0),
         'Q-Shield (ensemble + TTA)',
         size=24, color=RGBColor(0xCF, 0xD8, 0xE5))
    text(s, Inches(0.9), Inches(2.6), Inches(11.5), Inches(2.0),
         'AUC  0.9146',
         size=128, bold=True, color=WHITE, font='Calibri')
    text(s, Inches(0.9), Inches(4.7), Inches(11.5), Inches(0.6),
         '+0.13 pp over Trad et al. (0.9133)  ·  on a benchmark 11× larger and visually heterogeneous',
         size=18, color=RGBColor(0xCF, 0xD8, 0xE5), italic=True)
    # Mini-stats
    sx = Inches(0.9); my = Inches(5.7); cw = Inches(2.85); gap = Inches(0.15)
    stats = [('F1', '0.835'), ('Recall', '0.801'), ('FNR (default)', '0.199'),
             ('Params per model', '3.08 M')]
    for i, (l, v) in enumerate(stats):
        x = sx + i * (cw + gap)
        rect(s, x, my, cw, Inches(1.1), RGBColor(0x2B, 0x4A, 0x70))
        text(s, x + Inches(0.2), my + Inches(0.15), cw - Inches(0.4), Inches(0.3),
             l.upper(), size=10, bold=True, color=ACCENT, spacing=1.0)
        text(s, x + Inches(0.2), my + Inches(0.45), cw - Inches(0.4), Inches(0.6),
             v, size=28, bold=True, color=WHITE)
    deck.append((s, 'Part 04'))


def inference_improvements():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Inference-time refinements', 'TTA + 2-seed ensemble · no architectural change')
    rect(s, Inches(0.7), Inches(1.85), Inches(5.85), Inches(2.7), WHITE, line=GREY_LT)
    rect(s, Inches(0.7), Inches(1.85), Inches(0.1), Inches(2.7), GOLD)
    text(s, Inches(0.95), Inches(1.95), Inches(5.4), Inches(0.4),
         'TEST-TIME AUGMENTATION (TTA)', size=11, bold=True, color=ACCENT)
    text(s, Inches(0.95), Inches(2.35), Inches(5.4), Inches(0.6),
         'Average σ over original and h-flip',
         size=15, bold=True, color=DEEP)
    text(s, Inches(0.95), Inches(2.85), Inches(5.4), Inches(1.6),
         'p̂(x) = ½ ( σ(g·h(x)) + σ(g·h(x̃)) )\n\n'
         '2× forward passes per QR.\nGain: +0.91 pp AUC.',
         size=12, color=INK, spacing=1.4)
    rect(s, Inches(6.75), Inches(1.85), Inches(5.85), Inches(2.7), WHITE, line=GREY_LT)
    rect(s, Inches(6.75), Inches(1.85), Inches(0.1), Inches(2.7), GOLD)
    text(s, Inches(7.0), Inches(1.95), Inches(5.4), Inches(0.4),
         'TWO-SEED ENSEMBLE', size=11, bold=True, color=ACCENT)
    text(s, Inches(7.0), Inches(2.35), Inches(5.4), Inches(0.6),
         'Two pipelines, identical splits, different seeds',
         size=15, bold=True, color=DEEP)
    text(s, Inches(7.0), Inches(2.85), Inches(5.4), Inches(1.6),
         'Diversity from optimization stochasticity\n(weight init + pair sampling).\n\n'
         '4 forwards/QR total. Gain: +0.93 pp.',
         size=12, color=INK, spacing=1.4)
    headers = ['Configuration', 'AUC', 'Δ vs single-seed', 'Δ vs Trad (0.9133)']
    rows = [
        ['Single seed (B0)', '0.8962', 'baseline', '−1.71 pp'],
        ['+ TTA (B1)', '0.9053', '+0.91 pp', '−0.80 pp'],
        ['+ 2-seed ensemble (B2)', '0.9146', '+1.84 pp', '+0.13 pp'],
    ]
    add_table(s, Inches(0.7), Inches(4.85), Inches(11.9), Inches(2.0),
              [headers] + rows, font_size=12, highlight_rows=[3])
    deck.append((s, 'Part 04'))


def main_table():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Main results', 'Combined validation set · n = 21,998')
    headers = ['Method', 'AUC', 'Prec.', 'Recall', 'F1', 'FNR']
    rows = [
        ['25 feat + Random Forest', '0.813', '0.794', '0.660', '0.720', '0.340'],
        ['25 feat + XGBoost', '0.810', '0.785', '0.664', '0.720', '0.336'],
        ['25 feat + LightGBM', '0.808', '0.771', '0.670', '0.717', '0.330'],
        ['Trad et al. (n=1,998, V13 only)', '0.913', '—', '—', '0.890', '—'],
        ['Q-Shield (single seed, no TTA)', '0.8962', '0.844', '0.798', '0.821', '0.202'],
        ['Q-Shield (single seed + TTA)', '0.9053', '0.853', '0.799', '0.825', '0.201'],
        ['Q-Shield (ensemble + TTA)', '0.9146', '0.872', '0.801', '0.835', '0.199'],
    ]
    add_table(s, Inches(0.5), Inches(1.85), Inches(12.4), Inches(4.0),
              [headers] + rows, font_size=12, highlight_rows=[7])
    text(s, Inches(0.7), Inches(6.1), Inches(12), Inches(0.4),
         'TAKEAWAYS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(6.5), Inches(12), Inches(1.0), [
        'Ensemble + TTA exceeds Trad SOTA on a benchmark 11× larger and visually heterogeneous',
        'Single-seed variant offers a 4× cheaper inference path with only 1.84 pp AUC concession',
    ], size=12)
    deck.append((s, 'Part 04'))


def cm_roc():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Decision behavior', 'Confusion matrix and ROC curve · ensemble configuration')
    img = FIGURES / 'fig_confusion_roc.png'
    if img.exists():
        s.shapes.add_picture(str(img), Inches(1.4), Inches(1.85),
                             width=Inches(10.6), height=Inches(4.4))
    text(s, Inches(0.7), Inches(6.4), Inches(12), Inches(0.4),
         'READING THE FIGURE', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(6.8), Inches(12), Inches(0.6), [
        'CM at p=0.5: TN 9,703 · FP 1,298 · FN 2,192 · TP 8,805 → AUC = 0.9146',
        'Calibrated point (p=0.4) crosses the FNR ≤ 10% security tolerance',
    ], size=11)
    deck.append((s, 'Part 04'))


def ablation():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Ablation', 'Each architectural decision matters · single-seed, no TTA')
    headers = ['Variant', 'AUC', 'F1', 'FNR', 'Δ AUC']
    rows = [
        ['A1 · Full Q-Shield (single seed)', '0.8962', '0.821', '0.202', '—'],
        ['A2 · No Siamese pretraining', '0.8764', '0.785', '0.267', '−0.020'],
        ['A3 · BCE loss (no focal)', '0.8771', '0.786', '0.271', '−0.019'],
        ['A4 · No frozen start', '0.8810', '0.801', '0.230', '−0.015'],
        ['A5 · Small head (256→64→1)', '0.8752', '0.794', '0.229', '−0.021'],
    ]
    add_table(s, Inches(0.5), Inches(1.85), Inches(12.4), Inches(3.0),
              [headers] + rows, font_size=12)
    text(s, Inches(0.7), Inches(5.1), Inches(12), Inches(0.4),
         'INTERPRETATION', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.5), Inches(12), Inches(2.0), [
        'Siamese pretraining (A2) is the largest single contributor: −2 pp AUC, +6.5 pp FNR when removed',
        'Focal loss (A3) barely changes AUC but lifts FNR by 7 pp — directly supports the security claim',
        'Frozen start (A4) and large head (A5) add +0.015 to +0.021 AUC each — small but consistent',
        'Combined with TTA + ensemble (panel B in Table V), the system reaches AUC 0.9146',
    ], size=12)
    deck.append((s, 'Part 04'))


def cross_dataset():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Cross-dataset generalization', 'Why combined training is methodologically required')
    headers = ['Setup', 'AUC', 'Recall', 'F1', 'FNR', 'Diagnosis']
    rows = [
        ['CV1 · Train CIC → Test Trad', '0.7178', '1.000', '0.666', '0.000', 'Classifier collapse (everything → phishing)'],
        ['CV2 · Train Trad → Test CIC', '0.5181', '0.508', '0.517', '0.492', 'Near-random — Trad-only fails on PNGs'],
        ['CV3 · Combined (single seed)', '0.8962', '0.798', '0.821', '0.202', 'Operative regime'],
    ]
    add_table(s, Inches(0.5), Inches(1.85), Inches(12.4), Inches(2.6),
              [headers] + rows, font_size=11, highlight_rows=[3])
    text(s, Inches(0.7), Inches(4.7), Inches(12), Inches(0.4),
         'INTERPRETATION', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.1), Inches(12), Inches(2.4), [
        'The two corpora differ at the pixel level beyond what augmentation can bridge',
        'Single-corpus training does NOT generalize. Combining is not a convenience — it is required',
        'Position this as domain-invariant learning (Ganin & Lempitsky, 2015)',
        'Implication: prior single-dataset AUCs (e.g., 0.913 on V13 only) should be read as upper bounds',
    ], size=12)
    deck.append((s, 'Part 04'))


def threshold():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Threshold calibration', 'Operating points for security tolerance')
    headers = ['Operating point', 'Threshold', 'Precision', 'Recall', 'FNR', 'F1']
    rows = [
        ['Default', '0.500', '0.860', '0.818', '0.182', '0.839'],
        ['Maximize F1', '0.475', '0.837', '0.844', '0.156', '0.840'],
        ['FNR ≤ 0.10 (security target)', '0.400', '0.752', '0.902', '0.098', '0.820'],
        ['FNR ≤ 0.05 (aggressive)', '0.300', '0.607', '0.961', '0.039', '0.744'],
    ]
    add_table(s, Inches(0.5), Inches(1.85), Inches(12.4), Inches(2.6),
              [headers] + rows, font_size=12, highlight_rows=[3])
    text(s, Inches(0.7), Inches(4.7), Inches(12), Inches(0.4),
         'WHY THIS MATTERS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.1), Inches(12), Inches(2.4), [
        'AUC alone is threshold-independent — operators need a decision rule',
        '0.50 → 0.40 lowers FNR from 18% to 9.8% at modest precision cost',
        'Crosses the conventional ≤ 10% security tolerance without retraining',
        'Brier 0.138 · ECE 0.129 → ranker, not probability estimator',
    ], size=12)
    deck.append((s, 'Part 04'))


def xai_gradcam():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Explainability', 'Grad-CAM · spatial attention over the QR matrix')
    img = FIGURES / 'xai' / 'fig5_gradcam_samples.png'
    img2 = FIGURES / 'xai' / 'fig6_gradcam_aggregate.png'
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.5), Inches(1.85),
                             width=Inches(7.2), height=Inches(5.4))
    if img2.exists():
        s.shapes.add_picture(str(img2), Inches(7.9), Inches(1.85),
                             width=Inches(5.0), height=Inches(2.2))
    text(s, Inches(7.9), Inches(4.2), Inches(5.0), Inches(0.4),
         'WHAT WE SEE', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(7.9), Inches(4.6), Inches(5.0), Inches(2.6), [
        'Finder patterns (3 corners) consistently dark — model ignores them',
        'Attention concentrates on data-region modules — payload-encoded part',
        'Aggregated: benign attention to the left, phishing to the center-right',
        'Plausible cause: longer phishing URLs push more codewords to the right',
    ], size=11)
    deck.append((s, 'Part 05'))


def xai_shap():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Explainability', 'SHAP and embedding space · latent-level interpretability')
    a = FIGURES / 'xai' / 'fig8_shap_embedding.png'
    b = FIGURES / 'xai' / 'fig7_embedding_distances.png'
    if a.exists():
        s.shapes.add_picture(str(a), Inches(0.5), Inches(1.85),
                             width=Inches(6.1), height=Inches(3.2))
    if b.exists():
        s.shapes.add_picture(str(b), Inches(6.8), Inches(1.85),
                             width=Inches(6.1), height=Inches(3.2))
    text(s, Inches(0.5), Inches(5.2), Inches(6.1), Inches(0.4),
         'SHAP — TOP 20 OF 128 DIMS', size=10, bold=True, color=ACCENT)
    bullets(s, Inches(0.5), Inches(5.55), Inches(6.1), Inches(2.0), [
        'Top dim |SHAP| ≈ 0.016, decaying smoothly to 0.005 at position 20',
        'Remaining 108 dims contribute negligibly — embedding over-parameterized',
        'Pruning to 32–64 dims would likely preserve performance',
    ], size=11)
    text(s, Inches(6.8), Inches(5.2), Inches(6.1), Inches(0.4),
         'PAIRWISE DISTANCES', size=10, bold=True, color=ACCENT)
    bullets(s, Inches(6.8), Inches(5.55), Inches(6.1), Inches(2.0), [
        'Benign-Benign 0.501 · Phish-Phish 0.458 · Benign-Phish 0.928',
        'Inter/intra ratio = 1.94 — contrastive training works as intended',
        'Phishing cluster TIGHTER than benign — URLs share structural regularities',
    ], size=11)
    deck.append((s, 'Part 05'))


def xai_perdataset():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Explainability', 'Per-dataset Grad-CAM · ruling out artifacts')
    img = FIGURES / 'audit' / 'fig_gradcam_per_dataset.png'
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.5), Inches(1.85),
                             width=Inches(8.2), height=Inches(5.4))
    text(s, Inches(8.9), Inches(1.85), Inches(4.0), Inches(0.4),
         'THE CONCERN', size=11, bold=True, color=ACCENT)
    text(s, Inches(8.9), Inches(2.25), Inches(4.0), Inches(1.6),
         'Could the L/R asymmetry be an artifact of mixing 69×69 binary Trad samples with antialiased CIC PNGs?',
         size=12, color=INK, italic=True, spacing=1.3)
    text(s, Inches(8.9), Inches(4.0), Inches(4.0), Inches(0.4),
         'THE TEST', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(8.9), Inches(4.4), Inches(4.0), Inches(3.0), [
        'Recompute class-averaged Grad-CAM SEPARATELY on Trad and CIC',
        'Pixel-wise correlation r = 0.43',
        'Right-side positive region in BOTH datasets',
        '→ real structural signal',
    ], size=11)
    deck.append((s, 'Part 05'))


def inference_cost():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Inference cost', 'Mobile-deployable and configurable')
    headers = ['Configuration', 'Params', 'Disk', 'CPU', 'GPU (T4)', 'AUC']
    rows = [
        ['Single seed, no TTA', '3.08 M', '12 MB', '24.9 ms', '6.0 ms', '0.896'],
        ['Single seed + TTA', '3.08 M', '12 MB', '49.8 ms', '12.0 ms', '0.905'],
        ['Ensemble + TTA (full)', '6.16 M', '24 MB', '99.6 ms', '24.0 ms', '0.915'],
    ]
    add_table(s, Inches(0.5), Inches(1.85), Inches(12.4), Inches(2.4),
              [headers] + rows, font_size=12, highlight_rows=[3])
    text(s, Inches(0.7), Inches(4.5), Inches(12), Inches(0.4),
         'DEPLOYMENT NOTES', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(4.9), Inches(12), Inches(2.4), [
        '< 100 ms CPU keeps the full ensemble within the perceptual budget for interactive mobile',
        'Single-model variant trades 1.84 pp AUC for a 4× compute reduction',
        'GPU throughput per single model on T4: 1,156 images/s (batch 32)',
        'Bundled weights ~24 MB — fits typical mobile-app size budgets',
    ], size=12)
    deck.append((s, 'Part 05'))


def limitations():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Limitations', 'Stated explicitly in Section VI.B of the paper')
    items = [
        ('Default-threshold FNR', '0.199 — above the 0.10 target. Mitigated by threshold calibration.'),
        ('Phase-2 overfitting', 'Validation loss diverges after epoch 8. Early stopping selects the best.'),
        ('Unverified URL overlap', 'Trad does not redistribute URL strings. Overlap with CIC unverified.'),
        ('Resolution-dependent perf.', 'AUC drops to 0.844 on QRs > 246 px — resize loses module detail.'),
        ('Probability calibration', 'ECE 0.129 — good ranker, imperfect probability estimator.'),
        ('Unimodal scope', 'No accompanying-text branch; paired QR+text data not public at scale.'),
        ('Container-format stripping', 'PDF/SVG/DOCX containers normalized to PNG before CNN.'),
        ('No adversarial evaluation', 'Module-level perturbations not yet tested.'),
    ]
    y = Inches(1.85); h = Inches(0.6); gap = Inches(0.07)
    for head, body in items:
        rect(s, Inches(0.7), y, Inches(11.9), h, WHITE, line=GREY_LT)
        rect(s, Inches(0.7), y, Inches(0.1), h, RED)
        text(s, Inches(0.95), y + Inches(0.1), Inches(3.7), Inches(0.45),
             head, size=12, bold=True, color=DEEP)
        text(s, Inches(4.7), y + Inches(0.1), Inches(7.85), Inches(0.5),
             body, size=11, color=INK, spacing=1.2)
        y += h + gap
    deck.append((s, 'Part 06'))


def future_work():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Future work', 'Five extensions worth dedicated study')
    items = [
        ('Multimodal fusion',
         'Add a text branch (DistilBERT or compact LM) on accompanying email/SMS context. Most direct path to FNR < 10%.'),
        ('Multi-scale training',
         'Resolution-adaptive backbone or multiple input scales. Closes the gap on large QRs without inference cost.'),
        ('Provenance-aware detection',
         'Cryptographic signatures, merchant-ID validation, session tokens. See next slide for the Yape/BCP example.'),
        ('Adversarial robustness',
         'Module-level adversarial perturbations + adversarial training and randomized smoothing.'),
        ('Localized deployment',
         'Region-specific phishing campaigns: Yape (Peru), UPI (India), Pix (Brazil). Local data + lightweight fine-tuning.'),
    ]
    y = Inches(1.85); h = Inches(1.0); gap = Inches(0.08)
    for head, body in items:
        rect(s, Inches(0.7), y, Inches(11.9), h, WHITE, line=GREY_LT)
        rect(s, Inches(0.7), y, Inches(0.1), h, GREEN)
        text(s, Inches(0.95), y + Inches(0.12), Inches(11.8), Inches(0.4),
             head, size=14, bold=True, color=DEEP)
        text(s, Inches(0.95), y + Inches(0.5), Inches(11.8), Inches(0.5),
             body, size=11, color=INK, spacing=1.3)
        y += h + gap
    deck.append((s, 'Part 06'))


def provenance():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Future work · deep dive', 'Provenance-aware detection · Yape and BCP, Peru')
    text(s, Inches(0.7), Inches(1.85), Inches(12), Inches(0.4),
         'TWO QUESTIONS · TWO LAYERS', size=11, bold=True, color=ACCENT)
    rect(s, Inches(0.7), Inches(2.3), Inches(5.85), Inches(2.4), WHITE, line=GREY_LT)
    rect(s, Inches(0.7), Inches(2.3), Inches(5.85), Inches(0.06), GREEN)
    text(s, Inches(0.95), Inches(2.45), Inches(5.4), Inches(0.5),
         'Q1 · Is the content malicious?', size=15, bold=True, color=DEEP)
    text(s, Inches(0.95), Inches(2.95), Inches(5.4), Inches(1.6),
         'Solved by Q-Shield. The visual classifier inspects the QR pattern and flags content-suspicious codes regardless of origin.',
         size=12, color=INK, spacing=1.4)
    rect(s, Inches(6.75), Inches(2.3), Inches(5.85), Inches(2.4), WHITE, line=GREY_LT)
    rect(s, Inches(6.75), Inches(2.3), Inches(5.85), Inches(0.06), RED)
    text(s, Inches(7.0), Inches(2.45), Inches(5.4), Inches(0.5),
         'Q2 · Was it generated by the authorized source?', size=15, bold=True, color=DEEP)
    text(s, Inches(7.0), Inches(2.95), Inches(5.4), Inches(1.6),
         'NOT solved by Q-Shield. A content-valid QR placed at point-of-sale by an attacker (overlay, MITM, UI replacement) passes the visual filter.',
         size=12, color=INK, spacing=1.4)
    text(s, Inches(0.7), Inches(5.0), Inches(12), Inches(0.4),
         'WHAT A PROVENANCE LAYER LOOKS LIKE', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.4), Inches(12), Inches(2.0), [
        'Yape (Peru, by BCP) generates merchant QRs through an authenticated backend',
        'Cryptographic signatures embedded in the QR payload + merchant-ID validation against the issuer',
        'Session-bound tokens · geolocation or capture-device attestation',
        'Visual + provenance = orthogonal complementary layers, not competitors',
    ], size=12)
    deck.append((s, 'Part 06'))


def submission():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Submission plan', 'Where to send Q-Shield')
    headers = ['Venue', 'Fit', 'Notes']
    rows = [
        ['IEEE Intercon', 'Strong', 'Latin-American audience aligns with Yape/BCP framing'],
        ['IEEE LA-CCI', 'Strong', 'Latin-American Computational Intelligence; XAI + security focus'],
        ['IEEE TrustCom', 'Stretch', 'Trust + security venue; broader cybersecurity context'],
    ]
    add_table(s, Inches(0.5), Inches(1.85), Inches(12.4), Inches(2.0),
              [headers] + rows, font_size=12, highlight_rows=[1, 2])
    text(s, Inches(0.7), Inches(4.0), Inches(12), Inches(0.4),
         'PRE-SUBMISSION CHECKLIST · ~1 HOUR', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(4.4), Inches(12), Inches(2.7), [
        'Recompile main.tex (3 passes) — verify zero ?? remain',
        'Optional · add SimCLR/SupCon distinction + Khosla 2020 reference',
        'Optional · add bootstrap CI on AUC at end of Main Results',
        'Final visual check of PDF: figures, tables, page breaks',
        'Verify authors list, ORCID, abstract length, IEEE PDF Express compliance',
    ], size=12)
    deck.append((s, 'Part 06'))


def summary():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Summary', 'Q-Shield in one slide')
    bullets(s, Inches(0.7), Inches(1.85), Inches(12), Inches(5.0), [
        'First Siamese contrastive framework for QR-image quishing — zero-decoding',
        '21,998-sample heterogeneous benchmark (Trad + CIC), 11× larger than prior evaluations',
        'AUC 0.9146 (ensemble + TTA) > Trad 0.9133 — genuine improvement on a harder benchmark',
        'Single-seed variant 0.8962 with 4× lower inference cost — explicit accuracy/latency trade-off',
        'Threshold calibration · FNR 0.098 at p = 0.40 — meets security tolerance without retraining',
        'Dual XAI (Grad-CAM + SHAP), validated cross-dataset (r = 0.43) — non-trivial structural signal',
        '3.08 M parameters per model, 12 MB on disk, 25 ms CPU per scan — mobile-deployable',
        '7 honest limitations · 5 concrete future-work directions',
    ], size=14)
    rect(s, Inches(0.7), Inches(6.55), Inches(11.9), Inches(0.55), DEEP)
    text(s, Inches(0.7), Inches(6.55), Inches(11.9), Inches(0.55),
         'Status · ready for advisor review and IEEE Intercon / LA-CCI submission',
         size=14, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    deck.append((s, 'Close'))


def thanks():
    s = slide()
    rect(s, 0, 0, SW, SH, DEEP)
    rect(s, 0, Inches(3.5), SW, Inches(0.05), ACCENT)
    text(s, Inches(0.9), Inches(2.6), SW - Inches(1.8), Inches(1.5),
         'Thank you.',
         size=84, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    text(s, Inches(0.9), Inches(4.2), SW - Inches(1.8), Inches(0.5),
         'Questions, feedback, and design directions are welcome.',
         size=18, color=RGBColor(0xCF, 0xD8, 0xE5),
         italic=True, align=PP_ALIGN.CENTER)
    text(s, Inches(0.9), Inches(5.6), SW - Inches(1.8), Inches(0.4),
         'Nicolás Alejandro Llerena Silva  ·  UTEC',
         size=14, color=WHITE, align=PP_ALIGN.CENTER)
    text(s, Inches(0.9), Inches(6.0), SW - Inches(1.8), Inches(0.4),
         'Advisor · Aurea Soriano-Vargas',
         size=14, color=RGBColor(0xCF, 0xD8, 0xE5), align=PP_ALIGN.CENTER)
    deck.append((s, 'cover'))


# ============================================================
# Build deck in order
# ============================================================
cover()
agenda()

section_divider('01', 'The problem',
                'Why quishing is a distinctive cybersecurity threat,\nand which gaps in the literature we set out to close.')
big_problem()
gaps()
contributions()
related()

section_divider('02', 'Methodology',
                'Architecture, formulas, and code.\nTwo-phase training plus inference-time refinements.')
architecture_full()
formulation()
contrastive()
focal()
code_backbone()
code_phase1()
code_phase2()

section_divider('03', 'Experimental setup',
                'Datasets, validation protocol,\nand the iteration history that led to v3.')
datasets()
iterations()

section_divider('04', 'Results',
                'From the reconciliation that detected an inflated number\nto the ensemble that genuinely beats prior SOTA.')
reconciliation()
hero_result()
inference_improvements()
main_table()
cm_roc()
ablation()
cross_dataset()
threshold()

section_divider('05', 'Explainability & deployment',
                'Grad-CAM, SHAP, per-dataset validation,\nand inference-cost trade-offs.')
xai_gradcam()
xai_shap()
xai_perdataset()
inference_cost()

section_divider('06', 'What\'s next',
                'Limitations, future work, and the submission plan.')
limitations()
future_work()
provenance()
submission()

summary()
thanks()


# ============================================================
# Footers (skip cover, dividers, thanks)
# ============================================================
total = len(deck)
for i, (s, kind) in enumerate(deck):
    if kind in ('cover', 'divider'):
        continue
    page_footer(s, i + 1, total, kind)


prs.save(str(OUTPUT))
print(f'Saved: {OUTPUT}')
print(f'Total slides: {total}')
