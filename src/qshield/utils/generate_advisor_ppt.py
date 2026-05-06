"""Build the Q-Shield advisor presentation (.pptx).

Multimodal version: visual + DistilBERT URL + LogitFusion.
Editorial-style deck with section dividers and varied layouts.
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


REPO = Path(__file__).resolve().parents[3]
FIGURES = REPO / 'figures'
OUTPUT = REPO / 'Q-Shield_Presentacion_Asesora.pptx'


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
# SLIDE BUILDERS
# ============================================================
deck = []


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
         'An Explainable Multimodal Framework for',
         size=22, color=INK, font='Calibri')
    text(s, Inches(0.9), Inches(3.25), Inches(11.5), Inches(0.6),
         'Quishing Detection via Siamese Visual and Offline URL Analysis',
         size=22, color=INK, font='Calibri')
    line(s, Inches(0.9), Inches(4.45), Inches(5.5), Inches(4.45), DEEP, 1.5)
    text(s, Inches(0.9), Inches(4.6), Inches(11), Inches(0.4),
         'Author', size=10, bold=True, color=GREY, spacing=1.0)
    text(s, Inches(0.9), Inches(4.85), Inches(11), Inches(0.5),
         'Nicolás Alejandro Llerena Silva', size=20, bold=True, color=INK)
    text(s, Inches(0.9), Inches(5.55), Inches(11), Inches(0.4),
         'Advisor', size=10, bold=True, color=GREY, spacing=1.0)
    text(s, Inches(0.9), Inches(5.8), Inches(11), Inches(0.5),
         'Aurea Soriano-Vargas', size=20, bold=True, color=INK)
    text(s, Inches(0.9), Inches(6.7), Inches(11), Inches(0.3),
         'Advisor meeting · May 2026 · multimodal pivot',
         size=11, color=GREY, italic=True)
    deck.append((s, 'cover'))


def agenda():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    text(s, Inches(0.7), Inches(0.6), Inches(11.9), Inches(0.4),
         'AGENDA', size=11, bold=True, color=ACCENT)
    text(s, Inches(0.7), Inches(0.85), Inches(11.9), Inches(0.8),
         'Six parts, with the pivot in the middle',
         size=32, bold=True, color=DEEP)
    line(s, Inches(0.7), Inches(1.7), Inches(12.6), Inches(1.7), GREY_LT, 1.0)
    sections = [
        ('01', 'The problem',
         'Quishing as social engineering;\nthe four research gaps we close.'),
        ('02', 'The pivot',
         'Why we moved from visual-only to multimodal,\nand why the visual branch stays as graceful fallback.'),
        ('03', 'Architecture',
         'Visual Siamese branch + DistilBERT URL branch +\nlate-fusion MLP with explicit undecodable flag.'),
        ('04', 'Experiments',
         'Datasets, iterations,\nand the reconciliation that produced honest numbers.'),
        ('05', 'Results',
         'Headline AUC 0.9749, FNR 0.057,\nbranch comparison, ablation, cross-dataset.'),
        ('06', 'What\'s next',
         'Limitations, future work,\nsubmission plan to IEEE Intercon / LA-CCI.'),
    ]
    cols = 3; cw = Inches(4.0); ch = Inches(2.3); gap_x = Inches(0.15); gap_y = Inches(0.3)
    sx = Inches(0.7); sy = Inches(2.0)
    for i, (num, title, desc) in enumerate(sections):
        col = i % cols; row = i // cols
        x = sx + col * (cw + gap_x); y = sy + row * (ch + gap_y)
        rect(s, x, y, cw, ch, WHITE, line=GREY_LT)
        rect(s, x, y, cw, Inches(0.05), ACCENT)
        text(s, x + Inches(0.25), y + Inches(0.2), Inches(1.0), Inches(0.7),
             num, size=36, bold=True, color=ACCENT)
        text(s, x + Inches(0.25), y + Inches(0.95), cw - Inches(0.5), Inches(0.4),
             title, size=15, bold=True, color=DEEP)
        text(s, x + Inches(0.25), y + Inches(1.35), cw - Inches(0.5), Inches(0.85),
             desc, size=11, color=GREY_DK, spacing=1.3)
    deck.append((s, 'meta'))


def divider(num, label, sub):
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
    deck.append((s, 'divider'))


def big_problem():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'The problem', 'Quishing is a social-engineering attack')
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


def the_pivot():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Part 02', 'Why we pivoted to multimodal')
    text(s, Inches(0.7), Inches(1.8), Inches(12), Inches(0.5),
         'Three failures of the original visual-only framing',
         size=16, bold=True, color=ACCENT)
    pivots = [
        ('1. The "decoding paradox" does not hold up',
         'pyzbar is local, deterministic, no network, no DNS, no JS. It conflates reading a string '
         '(safe) with opening it (risky). An informed reviewer would knock this down on first read.'),
        ('2. The visual signal alone is structurally weak in heterogeneous QRs',
         'CIC Trap4Phish 2025 reports SSIM benign↔phishing ≈ 0.34 — visually almost identical. '
         'Their CNN over images reaches F1 0.88; their LLMs over the decoded URL reach F1 0.97-0.99.'),
        ('3. Combining both branches dominates either alone, by construction',
         'Bountakas (2023) and Khalifa (2025) already validated multimodal fusion in webpage phishing. '
         'The framing that survives review is the one that uses every signal available.'),
    ]
    y = Inches(2.4); h = Inches(1.45); gap = Inches(0.12)
    for head, body in pivots:
        rect(s, Inches(0.7), y, Inches(11.9), h, WHITE, line=GREY_LT)
        rect(s, Inches(0.7), y, Inches(0.15), h, RED)
        text(s, Inches(1.0), y + Inches(0.15), Inches(11.5), Inches(0.5),
             head, size=14, bold=True, color=DEEP)
        text(s, Inches(1.0), y + Inches(0.6), Inches(11.5), Inches(0.85),
             body, size=12, color=INK, spacing=1.4)
        y += h + gap
    text(s, Inches(0.7), Inches(7.0), Inches(12), Inches(0.4),
         'The visual branch is NOT discarded — it remains the operative signal whenever the QR cannot be decoded (4.3% of the corpus).',
         size=12, italic=True, color=GREEN, bold=True)
    deck.append((s, 'Part 02'))


def gaps():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Research gaps', 'Four open problems we close')
    rows = [
        ('NO INTEGRATED VISUAL+TEXT DETECTOR FOR QR',
         'Trad operates only pre-decode; CIC reports both branches in parallel but does not fuse them. We provide the first end-to-end fused detector with explicit undecodability handling.'),
        ('NO CROSS-DATASET EVALUATION',
         'Every prior study reports on one dataset; none measures transfer across independently collected QR corpora. We are the first to do this.'),
        ('LIMITED DUAL EXPLAINABILITY',
         'Prior work provides feature importance OR handcrafted interpretability, but not both pixel-level and latent-level explanations.'),
        ('NO OPERATIONAL CHARACTERIZATION',
         'Reported single threshold (p = 0.5) without quantifying recall/precision trade-offs for security tolerances. The fused model meets the ≤10% FNR target out of the box.'),
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
    deck.append((s, 'Part 02'))


def contributions():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Contributions', 'Five claims supported by the paper')
    items = [
        ('Multimodal fusion is the operative configuration',
         'Visual + DistilBERT-URL + late-fusion MLP. AUC 0.9749, F1 0.936, FNR 0.057 on n=21,998 — exceeds Trad 0.913 by +6.16 pp.'),
        ('11× larger heterogeneous benchmark',
         'Joint Trad + CIC validation set spans multiple QR versions, resolutions, and image formats.'),
        ('Explicit handling of undecodable QRs',
         'pyzbar fallback + UNDECODABLE flag in fusion input. Visual branch is the operative signal in this 4.3% of the corpus.'),
        ('Default-threshold security target met',
         'FNR 0.057 at p=0.5 — already below the conventional ≤10% tolerance, no calibration required.'),
        ('Dual-layer explainability, cross-validated',
         'Grad-CAM (spatial) + SHAP (feature). Per-dataset Pearson r = 0.43: signal is structural, not dataset-specific.'),
    ]
    y = Inches(1.85); h = Inches(0.95); gap = Inches(0.1)
    for head, body in items:
        rect(s, Inches(0.7), y, Inches(11.9), h, SAND)
        rect(s, Inches(0.7), y, Inches(0.15), h, ACCENT)
        text(s, Inches(1.0), y + Inches(0.12), Inches(11.5), Inches(0.4),
             head, size=15, bold=True, color=DEEP)
        text(s, Inches(1.0), y + Inches(0.5), Inches(11.5), Inches(0.45),
             body, size=12, color=INK, spacing=1.3)
        y += h + gap
    deck.append((s, 'Part 02'))


def related_work():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Related work', 'Where Q-Shield sits relative to prior approaches')
    headers = ['Study', 'Approach', 'Decodes?', 'Branches fused?', 'Cross-DS?', 'Best F1']
    rows = [
        ['Trad & Chehab (2025)', 'Pixel-level XGBoost', 'No', 'N/A (visual only)', 'No', '0.890'],
        ['Wahid et al. (2025)', 'Structural features', 'No', 'N/A', 'No', '—'],
        ['Khalifa et al. (2025)', 'Multimodal DL (URL+img)', 'Yes', 'Yes (webpages)', 'No', '—'],
        ['Nejati et al. (2026)', 'CNN + LLMs (parallel)', 'Yes', 'No', 'No', '0.97-0.99 (text)'],
        ['Q-Shield (this work)', 'Siamese visual + DistilBERT URL + fusion', 'Local only', 'Yes', 'Yes', '0.936'],
    ]
    add_table(s, Inches(0.7), Inches(1.85), Inches(11.9), Inches(3.0),
              [headers] + rows, font_size=12, highlight_rows=[5],
              col_align=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.CENTER,
                         PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.CENTER])
    text(s, Inches(0.7), Inches(5.1), Inches(11.9), Inches(0.5),
         'Why Q-Shield is novel',
         size=14, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.5), Inches(11.9), Inches(2.0), [
        'First end-to-end fused detector for QR phishing — Trad and Wahid are visual-only, Khalifa is webpages, CIC reports the two branches but does not fuse them',
        'First to handle the UNDECODABLE case explicitly via a binary flag in the fusion input',
        'First to evaluate cross-dataset transfer between independently collected QR corpora',
    ], size=12)
    deck.append((s, 'Part 02'))


def architecture_full():
    s = slide()
    rect(s, 0, 0, SW, SH, WHITE)
    text(s, Inches(0.7), Inches(0.4), Inches(12), Inches(0.4),
         'PART 03 · ARCHITECTURE', size=10, bold=True, color=ACCENT, spacing=1.0)
    text(s, Inches(0.7), Inches(0.65), Inches(12), Inches(0.6),
         'Q-Shield multimodal pipeline',
         size=22, bold=True, color=DEEP)
    img = FIGURES / 'fig_pipeline_abstract.png'
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.4), Inches(1.45),
                             width=Inches(12.55), height=Inches(5.6))
    deck.append((s, 'Part 03'))


def visual_branch():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Visual branch', 'Pre-decode signal — Siamese MobileNetV2 + classifier head')
    bullets(s, Inches(0.7), Inches(1.85), Inches(7.5), Inches(5.0), [
        'Backbone: MobileNetV2 (3.08M params, 12 MB FP32) — adapted to 1-channel grayscale, ImageNet init averaged across RGB',
        'Embedding: 1280 → 512 → 128, L2-normalized (unit hypersphere)',
        'Phase 1 (contrastive): margin m = 1.5, AdamW lr 2e-4, cosine warm restarts (T_0 = 15), up to 40 epochs with patience 8',
        'Phase 2 (focal): head 128→512→128→32→1, focal loss (γ = 2, α = 0.5), backbone frozen for 5 epochs then unfrozen',
        'Best epoch typically epoch 8; early stopping on val AUC, patience 3',
        'Operates pre-decode — only signal available when the QR cannot be decoded',
    ], size=12)
    rect(s, Inches(8.5), Inches(1.85), Inches(4.2), Inches(5.0), WHITE, line=GREY_LT)
    rect(s, Inches(8.5), Inches(1.85), Inches(0.1), Inches(5.0), ACCENT)
    text(s, Inches(8.7), Inches(1.95), Inches(4.0), Inches(0.4),
         'METRICS', size=11, bold=True, color=ACCENT)
    rows = [
        ('Single seed AUC', '0.8962'),
        ('+ TTA AUC', '0.9053'),
        ('+ 2-seed ensemble AUC', '0.9146'),
        ('Single-seed FNR', '0.202'),
        ('Inter/intra ratio', '1.94'),
    ]
    yy = Inches(2.45)
    for k, v in rows:
        text(s, Inches(8.7), yy, Inches(2.6), Inches(0.4),
             k, size=12, color=GREY_DK)
        text(s, Inches(11.3), yy, Inches(1.3), Inches(0.4),
             v, size=14, bold=True, color=DEEP, align=PP_ALIGN.RIGHT)
        yy += Inches(0.55)
    deck.append((s, 'Part 03'))


def text_branch():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Text branch', 'Post-decode signal — DistilBERT over offline-decoded URLs')
    bullets(s, Inches(0.7), Inches(1.85), Inches(7.5), Inches(5.0), [
        'Backbone: DistilBERT base uncased (66M params, 255 MB FP32). Trade-off latency vs accuracy: smaller than DeBERTa-v3 / ModernBERT, larger than BERT-Tiny',
        'Tokenizer: AutoTokenizer at max_length 96 — covers the full URL distribution observed across both corpora',
        'Decoding: pyzbar (libzbar) — local, deterministic, no network call, no payload execution. The "decoding paradox" conflates reading and opening',
        'UNDECODABLE token: when pyzbar fails (low contrast, missing quiet zone, damaged finder pattern), we emit a sentinel token. The encoder learns it as a separate representation — undecodability becomes a feature',
        'Fine-tuning: 3 epochs of focal loss (γ=2, α=0.5), AdamW lr 2e-5, weight decay 1e-2, linear warmup-then-decay schedule with 10% warmup',
        'Decode rate: Trad 100% (cascade decoder), CIC 95.7% — total 95.7% across the joint corpus',
    ], size=12)
    rect(s, Inches(8.5), Inches(1.85), Inches(4.2), Inches(5.0), WHITE, line=GREY_LT)
    rect(s, Inches(8.5), Inches(1.85), Inches(0.1), Inches(5.0), DEEP)
    text(s, Inches(8.7), Inches(1.95), Inches(4.0), Inches(0.4),
         'METRICS', size=11, bold=True, color=ACCENT)
    rows = [
        ('Text-only AUC', '0.9592'),
        ('Text-only F1', '0.927'),
        ('Text-only FNR', '0.069'),
        ('Brier', '0.066'),
        ('ECE', '0.045'),
    ]
    yy = Inches(2.45)
    for k, v in rows:
        text(s, Inches(8.7), yy, Inches(2.6), Inches(0.4),
             k, size=12, color=GREY_DK)
        text(s, Inches(11.3), yy, Inches(1.3), Inches(0.4),
             v, size=14, bold=True, color=DEEP, align=PP_ALIGN.RIGHT)
        yy += Inches(0.55)
    deck.append((s, 'Part 03'))


def fusion_branch():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Fusion', 'Late fusion over logits — 161 parameters')
    formula_card(s, Inches(0.7), Inches(1.85), Inches(11.9), Inches(1.2),
                 'p̂(x) = σ( MLP_{16}( [ ℓ_v(x),  ℓ_t(x),  flag_undecodable ] ) )',
                 label='Late-fusion architecture',
                 size=20)
    rect(s, Inches(0.7), Inches(3.4), Inches(5.85), Inches(3.4), WHITE, line=GREY_LT)
    rect(s, Inches(0.7), Inches(3.4), Inches(5.85), Inches(0.06), GREEN)
    text(s, Inches(0.95), Inches(3.55), Inches(5.4), Inches(0.4),
         'WHAT IT DOES', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.95), Inches(3.95), Inches(5.4), Inches(2.5), [
        'Combines visual logit and text logit with explicit awareness of decode failure',
        'Architecture: 3 → 16 → 1 = 161 parameters, ReLU + linear, no normalization',
        'Trained on cached logits with focal loss (γ=2, α=0.5), 20 epochs, AdamW lr 1e-3',
        'Converges in <1 minute on cached features',
    ], size=12)
    rect(s, Inches(6.75), Inches(3.4), Inches(5.85), Inches(3.4), WHITE, line=GREY_LT)
    rect(s, Inches(6.75), Inches(3.4), Inches(5.85), Inches(0.06), GREEN)
    text(s, Inches(7.0), Inches(3.55), Inches(5.4), Inches(0.4),
         'WHY IT WORKS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(7.0), Inches(3.95), Inches(5.4), Inches(2.5), [
        'When decode succeeds: text logit is dominant (text branch is the strongest single signal)',
        'When decode fails: flag → 1, fusion learns to trust visual logit more',
        'Calibration metrics improve 3× over visual alone (Brier 0.054 vs 0.146)',
        'Fusion AUC 0.9749 vs text-alone 0.9592 — visual contributes +1.57 pp',
    ], size=12)
    deck.append((s, 'Part 03'))


def formulation():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Theoretical framework', 'Problem formulation')
    text(s, Inches(0.7), Inches(1.85), Inches(12), Inches(0.5),
         'Goal · Classify a grayscale QR image x as benign or phishing.',
         size=15, color=INK, italic=True)
    formula_card(s, Inches(2.5), Inches(2.7), Inches(8.3), Inches(1.4),
                 'f_θ(x) = σ( g_φ ∘ h_ψ (x) )',
                 label='Equation (1) — composition of embedding and classifier',
                 size=26)
    text(s, Inches(0.7), Inches(4.5), Inches(12), Inches(0.4),
         'COMPONENTS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(4.9), Inches(12), Inches(2.0), [
        'h_ψ : ℝ^(H×W) → ℝ^d  ·  convolutional embedding (visual MobileNetV2 backbone)',
        'g_φ : ℝ^d → ℝ        ·  classification head producing a logit',
        'σ : ℝ → [0, 1]       ·  sigmoid nonlinearity',
        'For multimodal: a parallel text branch produces ℓ_t, and the fusion combines [ℓ_v, ℓ_t, flag] → final probability',
    ], size=14)
    deck.append((s, 'Part 04'))


def contrastive_loss():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Phase 1 visual', 'Contrastive Loss · Chopra, Hadsell, LeCun (2005)')
    formula_card(s, Inches(1.0), Inches(1.85), Inches(11.3), Inches(1.4),
                 'L_con(e₁, e₂, y) = (1−y) · d² / 2  +  y · max(0, m − d)² / 2',
                 label='Equation (2) — pairwise contrastive objective',
                 size=22)
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
    deck.append((s, 'Part 04'))


def focal_loss():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Phase 2 visual + fusion', 'Focal Loss · Lin, Goyal, Girshick, He, Dollár (2017)')
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
        'Replacing focal with BCE in visual head raises FNR 0.20 → 0.27 (+7 pp)',
        'Used in both Phase 2 visual and the fusion head',
    ], size=13)
    deck.append((s, 'Part 04'))


def datasets_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Datasets', 'Two complementary corpora · joint evaluation')
    headers = ['Property', 'Trad et al. (2025)', 'CIC Trap4Phish 2025']
    rows = [
        ['Total samples', '9,987', '1,005,738'],
        ['Used in this work', '9,987 (full)', '100,000 (50k+50k stratified)'],
        ['Format', 'Binary matrix', 'Grayscale PNG'],
        ['Native resolution', '69 × 69 (fixed)', '114 – 582 px'],
        ['QR version coverage', 'V13 only', 'V5 – V30'],
        ['Decode rate (Q-Shield)', '100%', '95.7%'],
    ]
    add_table(s, Inches(0.7), Inches(1.85), Inches(11.9), Inches(3.0),
              [headers] + rows, font_size=12)
    text(s, Inches(0.7), Inches(5.1), Inches(12), Inches(0.4),
         'VALIDATION PROTOCOL', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.5), Inches(12), Inches(1.5), [
        'All inputs normalized to 224 × 224 grayscale before the visual CNN',
        '80/20 train/validation split per dataset, stratified by class',
        'Combined val set: 21,998 samples — 11× larger than the largest prior evaluation',
        'Random seed 42 for splits and CIC sampling — reproducible across ensemble seeds',
    ], size=12)
    deck.append((s, 'Part 05'))


def iterations_recon():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Iteration history & reconciliation', 'Honest research diary')
    headers = ['Stage', 'AUC', 'F1', 'FNR', 'Note']
    rows = [
        ['v1: Trad-only, dropout 0.3', '0.886', '0.81', '0.21', 'Severe overfitting (30 pp gap)'],
        ['v2: + CIC, rotation aug, dropout 0.5', '0.868', '0.78', '0.27', 'Underfitting + rotation broke finder patterns'],
        ['v3: dropout 0.35, no rotation, m=1.5', '0.896', '0.82', '0.20', 'Below Trad SOTA by 1.71 pp'],
        ['v3 + TTA + 2-seed ensemble', '0.915', '0.835', '0.199', 'Visual-only ceiling — match Trad'],
        ['Multimodal pivot · fusion (visual + text)', '0.9749', '0.936', '0.057', 'Headline: +6.16 pp over Trad'],
    ]
    add_table(s, Inches(0.4), Inches(1.85), Inches(12.5), Inches(3.4),
              [headers] + rows, font_size=11, highlight_rows=[5])
    text(s, Inches(0.7), Inches(5.5), Inches(12), Inches(0.4),
         'RECONCILIATION DURING THE PIVOT', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.9), Inches(12), Inches(1.5), [
        'Original ablation reported A1 = AUC 0.9254 — but the confusion matrix mathematically gave F1 0.821 and FNR 0.20, not 0.858 / 0.166',
        'Re-evaluated on the full 21,998 set: real visual single-seed AUC = 0.8962. The 0.9254 came from a subset evaluation',
        'Honest baseline (0.8962) became the foundation for the multimodal pivot — every paper number is now traceable to a script in the repo',
    ], size=12)
    deck.append((s, 'Part 05'))


def hero_result():
    s = slide()
    rect(s, 0, 0, SW, SH, DEEP)
    rect(s, 0, Inches(2.4), SW, Inches(0.04), ACCENT)
    text(s, Inches(0.9), Inches(1.0), Inches(11.5), Inches(0.5),
         'HEADLINE RESULT · n = 21,998', size=12, bold=True, color=ACCENT, spacing=1.0)
    text(s, Inches(0.9), Inches(1.4), Inches(11.5), Inches(1.0),
         'Q-Shield multimodal fusion (visual + DistilBERT URL)',
         size=22, color=RGBColor(0xCF, 0xD8, 0xE5))
    text(s, Inches(0.9), Inches(2.6), Inches(11.5), Inches(2.0),
         'AUC  0.9749',
         size=128, bold=True, color=WHITE, font='Calibri')
    text(s, Inches(0.9), Inches(4.7), Inches(11.5), Inches(0.6),
         '+6.16 pp over Trad et al. (0.9133)  ·  on a benchmark 11× larger and visually heterogeneous',
         size=18, color=RGBColor(0xCF, 0xD8, 0xE5), italic=True)
    sx = Inches(0.9); my = Inches(5.7); cw = Inches(2.85); gap = Inches(0.15)
    stats = [('F1', '0.936'), ('Recall', '0.943'), ('FNR (default)', '0.057'),
             ('ECE', '0.038')]
    for i, (l, v) in enumerate(stats):
        x = sx + i * (cw + gap)
        rect(s, x, my, cw, Inches(1.1), RGBColor(0x2B, 0x4A, 0x70))
        text(s, x + Inches(0.2), my + Inches(0.15), cw - Inches(0.4), Inches(0.3),
             l.upper(), size=10, bold=True, color=ACCENT, spacing=1.0)
        text(s, x + Inches(0.2), my + Inches(0.45), cw - Inches(0.4), Inches(0.6),
             v, size=28, bold=True, color=WHITE)
    deck.append((s, 'Part 06'))


def branch_chart():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Branch comparison', 'Visual / text / fusion · grouped bar chart')
    img = FIGURES / 'fig_branch_comparison.png'
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.7), Inches(1.85),
                             width=Inches(11.9), height=Inches(4.4))
    text(s, Inches(0.7), Inches(6.4), Inches(12), Inches(0.4),
         'KEY OBSERVATIONS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(6.8), Inches(12), Inches(0.6), [
        'Text alone already beats visual on every metric — confirms the URL-signal strength reported by CIC',
        'Fusion beats text on every metric — visual contributes genuine signal, especially on calibration (1−ECE) and F1',
    ], size=11)
    deck.append((s, 'Part 06'))


def main_results_table():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Main results', 'Combined validation set · n = 21,998')
    headers = ['Method', 'AUC', 'Prec.', 'Recall', 'F1', 'FNR']
    rows = [
        ['Trad et al. (n=1,998, V13 only)', '0.913', '—', '—', '0.890', '—'],
        ['Q-Shield visual single seed', '0.8962', '0.844', '0.798', '0.821', '0.202'],
        ['Q-Shield visual ensemble + TTA', '0.9146', '0.872', '0.801', '0.835', '0.199'],
        ['Q-Shield text-only (DistilBERT)', '0.9592', '0.923', '0.931', '0.927', '0.069'],
        ['Q-Shield fusion (visual + text)', '0.9749', '0.928', '0.943', '0.936', '0.057'],
    ]
    add_table(s, Inches(0.5), Inches(1.85), Inches(12.4), Inches(3.4),
              [headers] + rows, font_size=12, highlight_rows=[5])
    text(s, Inches(0.7), Inches(5.5), Inches(12), Inches(0.4),
         'TAKEAWAYS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.9), Inches(12), Inches(1.5), [
        'Fusion exceeds Trad SOTA by +6.16 pp AUC on a benchmark 11× larger and visually heterogeneous',
        'Fusion exceeds visual ensemble by +6.03 pp AUC and reduces FNR by 14.2 pp',
        'Visual single-seed remains the operative signal whenever the QR cannot be decoded (4.3% of corpus)',
    ], size=12)
    deck.append((s, 'Part 06'))


def cm_roc_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Decision behavior', 'Confusion matrix and ROC · fusion configuration')
    img = FIGURES / 'fig_confusion_roc.png'
    if img.exists():
        s.shapes.add_picture(str(img), Inches(1.4), Inches(1.85),
                             width=Inches(10.6), height=Inches(4.4))
    text(s, Inches(0.7), Inches(6.4), Inches(12), Inches(0.4),
         'READING THE FIGURE', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(6.8), Inches(12), Inches(0.6), [
        'CM at p=0.5: TN 10,201 · FP 800 · FN 623 · TP 10,374 → AUC = 0.9749',
        'Default operating point already meets FNR ≤ 10% — calibration optional, not load-bearing',
    ], size=11)
    deck.append((s, 'Part 06'))


def ablation_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Ablation', 'Visual single-seed (panel a, no TTA) — isolates architectural decisions')
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
        'Siamese pretraining (A2) is the largest single architectural contributor: −2 pp AUC, +6.5 pp FNR when removed',
        'Focal loss (A3) barely changes AUC but lifts FNR by 7 pp — directly supports the security claim',
        'TTA + ensemble (panel b) lift the visual to 0.9146; the multimodal pivot adds another 6 pp on top',
    ], size=12)
    deck.append((s, 'Part 06'))


def cross_dataset_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Cross-dataset', 'Why combined training is methodologically required')
    headers = ['Setup', 'AUC', 'Recall', 'F1', 'FNR', 'Diagnosis']
    rows = [
        ['CV1 · Train CIC → Test Trad', '0.7178', '1.000', '0.666', '0.000', 'Classifier collapse'],
        ['CV2 · Train Trad → Test CIC', '0.5181', '0.508', '0.517', '0.492', 'Near-random'],
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
        'Implication: prior single-dataset AUCs (e.g., Trad 0.913 on V13 only) should be read as upper bounds',
    ], size=12)
    deck.append((s, 'Part 06'))


def threshold_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Threshold calibration', 'Now optional — fusion meets the target at default')
    headers = ['Operating point', 'Threshold', 'Precision', 'Recall', 'FNR', 'F1']
    rows = [
        ['Visual default', '0.500', '0.860', '0.818', '0.182', '0.839'],
        ['Visual maximize F1', '0.475', '0.837', '0.844', '0.156', '0.840'],
        ['Visual FNR ≤ 0.10 (security target)', '0.400', '0.752', '0.902', '0.098', '0.820'],
        ['Fusion default — already below target', '0.500', '0.928', '0.943', '0.057', '0.936'],
    ]
    add_table(s, Inches(0.5), Inches(1.85), Inches(12.4), Inches(2.6),
              [headers] + rows, font_size=12, highlight_rows=[4])
    text(s, Inches(0.7), Inches(4.7), Inches(12), Inches(0.4),
         'WHY THIS MATTERS', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.1), Inches(12), Inches(2.4), [
        'Before pivot: FNR target met only after threshold sliding (0.50 → 0.40) on the visual model',
        'After pivot: fusion meets ≤ 10% target at default threshold — calibration becomes a tool for the visual fallback regime, not a load-bearing claim',
        'Visual fallback still uses the calibrated threshold when the QR cannot be decoded',
    ], size=12)
    deck.append((s, 'Part 06'))


def gradcam_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Explainability', 'Grad-CAM · spatial attention over the QR matrix')
    img = FIGURES / 'fig_gradcam_samples.png'
    img2 = FIGURES / 'fig_gradcam_aggregate.png'
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
    deck.append((s, 'Part 07'))


def shap_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Explainability', 'SHAP and embedding space · latent-level interpretability')
    a = FIGURES / 'fig_shap_embedding.png'
    b = FIGURES / 'fig_embedding_distances.png'
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
    deck.append((s, 'Part 07'))


def perdataset_slide():
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
    deck.append((s, 'Part 07'))


def inference_cost_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Inference cost', 'Mobile-deployable · configurable trade-off')
    headers = ['Configuration', 'Params', 'Disk', 'CPU', 'GPU (T4)', 'AUC']
    rows = [
        ['Visual single seed, no TTA', '3.08 M', '12 MB', '24.9 ms', '6.0 ms', '0.896'],
        ['Visual single seed + TTA', '3.08 M', '12 MB', '49.8 ms', '12.0 ms', '0.905'],
        ['Visual ensemble + TTA', '6.16 M', '24 MB', '99.6 ms', '24.0 ms', '0.915'],
        ['Fusion (visual + DistilBERT)', '69.1 M', '267 MB', '~95 ms', '~13 ms', '0.975'],
    ]
    add_table(s, Inches(0.4), Inches(1.85), Inches(12.5), Inches(2.8),
              [headers] + rows, font_size=12, highlight_rows=[4])
    text(s, Inches(0.7), Inches(4.9), Inches(12), Inches(0.4),
         'DEPLOYMENT NOTES', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.3), Inches(12), Inches(2.0), [
        '< 100 ms CPU keeps the fusion within the perceptual budget for interactive mobile applications',
        'Fusion adds 0.06 AUC over visual ensemble for ~equivalent CPU cost (text branch is fast at seq 96)',
        'For latency-critical or low-power deployments, single-seed visual offers a 0.08 AUC concession with 4× compute reduction',
        'GPU throughput per single visual model on T4: 1,156 images/s (batch 32)',
    ], size=12)
    deck.append((s, 'Part 07'))


def limitations_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Limitations', 'Stated explicitly in Section VI.B of the paper')
    items = [
        ('Visual fallback FNR', 'Visual single-seed FNR is 0.20 at default. Only matters when the QR fails to decode (4.3% of corpus).'),
        ('Phase-2 visual overfitting', 'Validation loss diverges after epoch 8. Early stopping selects the best checkpoint.'),
        ('Unverified URL overlap', 'Trad does not redistribute URL strings. Overlap with CIC unverified.'),
        ('Resolution-dependent perf.', 'Visual AUC drops to 0.844 on QRs > 246 px — resize loses module detail.'),
        ('Probability calibration (visual)', 'Visual ECE 0.13 — fusion calibration is 3× better.'),
        ('Out-of-QR context not modeled', 'Email subject, sender metadata. Third branch is future work.'),
        ('Container-format stripping', 'PDF/SVG/DOCX containers normalized to PNG before visual CNN.'),
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
    deck.append((s, 'Part 08'))


def future_work_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Future work', 'Five extensions worth dedicated study')
    items = [
        ('Surrounding-context branch',
         'Third modality over the message context (email subject, SMS body, sender metadata). Most direct path to FNR < 5%.'),
        ('Localized deployment',
         'Region-specific phishing campaigns: Yape (Peru), UPI (India), Pix (Brazil). Local data + lightweight fine-tuning.'),
        ('Multi-scale training',
         'Resolution-adaptive backbone or multiple input scales. Closes the gap on large QRs without inference cost.'),
        ('Adversarial robustness',
         'Module-level adversarial perturbations + adversarial training and randomized smoothing.'),
        ('Provenance-aware detection',
         'Cryptographic signatures, merchant-ID validation, session tokens. See next slide for the Yape/BCP example.'),
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
    deck.append((s, 'Part 08'))


def provenance_slide():
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
         'Solved by Q-Shield. The visual + URL branches inspect the QR pattern and content, flagging suspicious instances regardless of origin.',
         size=12, color=INK, spacing=1.4)
    rect(s, Inches(6.75), Inches(2.3), Inches(5.85), Inches(2.4), WHITE, line=GREY_LT)
    rect(s, Inches(6.75), Inches(2.3), Inches(5.85), Inches(0.06), RED)
    text(s, Inches(7.0), Inches(2.45), Inches(5.4), Inches(0.5),
         'Q2 · Was it generated by the authorized source?', size=15, bold=True, color=DEEP)
    text(s, Inches(7.0), Inches(2.95), Inches(5.4), Inches(1.6),
         'NOT solved. A content-valid QR placed at point-of-sale by an attacker (overlay, MITM, UI replacement) passes both Q-Shield branches.',
         size=12, color=INK, spacing=1.4)
    text(s, Inches(0.7), Inches(5.0), Inches(12), Inches(0.4),
         'WHAT A PROVENANCE LAYER LOOKS LIKE', size=11, bold=True, color=ACCENT)
    bullets(s, Inches(0.7), Inches(5.4), Inches(12), Inches(2.0), [
        'Yape (Peru, by BCP) generates merchant QRs through an authenticated backend',
        'Cryptographic signatures embedded in the QR payload + merchant-ID validation against the issuer',
        'Session-bound tokens · geolocation or capture-device attestation',
        'Q-Shield + provenance = orthogonal complementary layers, not competitors',
    ], size=12)
    deck.append((s, 'Part 08'))


def submission_slide():
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
        'Recompile main.tex (3 passes) — verify all figures including the new fig_branch_comparison',
        'Optional · add bootstrap CI on AUC at end of Main Results to formalize the +6.16 pp claim',
        'Optional · expand SimCLR vs supervised contrastive distinction in the Phase 1 section',
        'Final visual check of PDF: confusion-matrix figure shows fusion CM, ablation table footnotes correct',
        'Verify authors list, ORCID, abstract length, IEEE PDF Express compliance',
    ], size=12)
    deck.append((s, 'Part 08'))


def summary_slide():
    s = slide()
    rect(s, 0, 0, SW, SH, PAPER)
    page_header(s, 'Summary', 'Q-Shield in one slide')
    bullets(s, Inches(0.7), Inches(1.85), Inches(12), Inches(5.0), [
        'First end-to-end multimodal QR phishing detector — visual Siamese + DistilBERT URL + late fusion with explicit undecodability flag',
        '21,998-sample heterogeneous benchmark (Trad + CIC), 11× larger than prior evaluations',
        'Fusion AUC 0.9749, F1 0.936, FNR 0.057 — exceeds Trad SOTA 0.9133 by +6.16 pp on a harder benchmark',
        'Default-threshold FNR already meets ≤ 10% security tolerance — calibration becomes optional',
        'Visual ensemble 0.9146 remains as graceful fallback when QRs cannot be decoded (4.3% of corpus)',
        'Calibration metrics improve 3× over visual alone (Brier 0.054, ECE 0.038)',
        'Dual XAI (Grad-CAM + SHAP), validated cross-dataset (r = 0.43) — non-trivial structural signal',
        '7 honest limitations · 5 concrete future-work directions',
    ], size=14)
    rect(s, Inches(0.7), Inches(6.55), Inches(11.9), Inches(0.55), DEEP)
    text(s, Inches(0.7), Inches(6.55), Inches(11.9), Inches(0.55),
         'Status · ready for advisor review and IEEE Intercon / LA-CCI submission',
         size=14, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    deck.append((s, 'Close'))


def thanks_slide():
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

divider('01', 'The problem',
        'Quishing as a distinctive cybersecurity threat,\nand which gaps in the literature we set out to close.')
big_problem()

divider('02', 'The pivot',
        'Why we moved from visual-only to multimodal,\nand why the visual branch stays as graceful fallback.')
the_pivot()
gaps()
contributions()
related_work()

divider('03', 'Architecture',
        'Visual Siamese branch + DistilBERT URL branch +\nlate-fusion MLP with explicit undecodability flag.')
architecture_full()
visual_branch()
text_branch()
fusion_branch()

divider('04', 'Theory',
        'Three formulas: problem formulation,\ncontrastive loss (Phase 1), focal loss (Phase 2 + fusion).')
formulation()
contrastive_loss()
focal_loss()

divider('05', 'Experiments',
        'Datasets, validation protocol, iterations,\nand the reconciliation that produced honest numbers.')
datasets_slide()
iterations_recon()

divider('06', 'Results',
        'Headline AUC 0.9749, branch comparison,\nablation, cross-dataset, threshold trade-off.')
hero_result()
branch_chart()
main_results_table()
cm_roc_slide()
ablation_slide()
cross_dataset_slide()
threshold_slide()

divider('07', 'Explainability & deployment',
        'Grad-CAM, SHAP, per-dataset validation,\nand inference-cost trade-offs.')
gradcam_slide()
shap_slide()
perdataset_slide()
inference_cost_slide()

divider('08', 'What\'s next',
        'Limitations, future work, and the submission plan.')
limitations_slide()
future_work_slide()
provenance_slide()
submission_slide()

summary_slide()
thanks_slide()


# Footers
total = len(deck)
for i, (s, kind) in enumerate(deck):
    if kind in ('cover', 'divider'):
        continue
    page_footer(s, i + 1, total, kind)


prs.save(str(OUTPUT))
print(f'Saved: {OUTPUT}')
print(f'Total slides: {total}')
