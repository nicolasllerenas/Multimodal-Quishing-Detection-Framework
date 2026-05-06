# Q-Shield

Multimodal quishing (QR code phishing) detector. Two parallel branches over the
same QR sample at different stages of the detection pipeline:

- **Visual branch** — Siamese MobileNetV2 over the QR image (pre-decode).
  Operates without decoding, so it remains the only signal available when the
  payload cannot be recovered.
- **Text branch** — DistilBERT over the offline-decoded URL string (post-decode).
  Decoding uses pyzbar locally: it produces a string from the QR matrix; no
  network call, no DNS resolution, no JavaScript.
- **Late fusion** — small MLP that combines `[visual_logit, text_logit, undecodable_flag]`
  into the final phishing probability.

Reference implementation for the paper *Q-Shield: An Explainable Multimodal
Framework for Quishing Detection via Siamese Visual and Offline URL Analysis*
(Llerena Silva and Soriano-Vargas, 2026). Targeted at IEEE Intercon / LA-CCI 2026.

---

## Headline result

| Configuration | AUC | F1 | Recall | FNR | Brier | ECE |
|---|---|---|---|---|---|---|
| Visual only (single seed) | 0.8962 | 0.821 | 0.798 | 0.202 | 0.146 | 0.133 |
| Visual ensemble + TTA | 0.9146 | 0.835 | 0.801 | 0.199 | — | — |
| Text only (DistilBERT) | 0.9592 | 0.927 | 0.931 | 0.069 | 0.066 | 0.045 |
| **Fusion (visual + URL)** | **0.9749** | **0.936** | **0.943** | **0.057** | **0.054** | **0.038** |
| Trad et al. (reported, n = 1,998) | 0.9133 | 0.890 | — | — | — | — |

Joint validation set: **n = 21,998** (Trad + CIC, 80/20 split, seed 42).

Fusion exceeds the prior visual-only SOTA by **+6.16 pp AUC** on a benchmark
eleven times larger and visually heterogeneous. The default-threshold FNR of
**0.057** already meets the conventional ≤ 10 % security tolerance, so
threshold calibration becomes optional.

---

## What to look at first (advisor meeting starting points)

| If you want to see... | Open this |
|---|---|
| The story end to end | `docs/resumen_ejecutivo_general.md` (24 sections, ~30 min) |
| Just the results | `docs/results/eval_multimodal.json` and Table V of `paper/main.tex` |
| The architecture diagram | `figures/fig_pipeline_abstract.png` |
| The branch-by-branch numbers | `figures/fig_branch_comparison.png` |
| The confusion matrix | `figures/fig_confusion_roc.png` |
| The IEEE paper draft | `paper/main.tex` (compiles to ~14 pages) |
| The slide deck | `Q-Shield_Presentacion_Asesora.pptx` (41 slides) |
| The slide-by-slide script | `docs/presentacion_guion.md` (Spanish, with Q&A) |
| Why we pivoted to multimodal | `docs/HANDOFF.md` § 3 |
| Anticipated reviewer critiques | `docs/resumen_ejecutivo_general.md` § 22 |

---

## Method

**Phase 1 — Siamese contrastive pretraining (visual).** Shared MobileNetV2
backbone with a 128-d L2-normalized projection head, trained on class-balanced
same-class / different-class pairs with contrastive loss (Chopra et al., 2005).
Margin m = 1.5, AdamW with cosine warm restarts, 40 epochs with patience 8.

**Phase 2 — Supervised classification (visual).** Four-layer dense head
(128 → 512 → 128 → 32 → 1) trained with focal loss (γ = 2, α = 0.5). Backbone
frozen for the first 5 epochs, then end-to-end fine-tuning for 15 more.

**Text branch.** DistilBERT (66 M params) fine-tuned on the offline-decoded URL
strings with focal loss for 3 epochs, AdamW lr 2e-5. Decoding is performed once
per dataset and cached to JSON; samples whose decode fails are encoded as a
single `<UNDECODABLE>` sentinel token.

**Fusion.** 3-input MLP (`[visual_logit, text_logit, undecodable_flag] → 16 → 1`)
trained with focal loss for 20 epochs on cached features. Both branches frozen.

---

## Repository layout

```
Multimodal-Quishing-Detection-Framework/
├── paper/                              IEEE LaTeX draft + bibliography
├── figures/                            All paper figures (flat directory)
├── notebooks/
│   ├── 01..03                          EDA, handcrafted baselines, SOTA review
│   ├── 06_Siamese_Training_v3.ipynb    seed-42 visual training
│   ├── 07_XAI_GradCAM.ipynb            visual XAI
│   ├── 08_Ablation_CrossDataset.ipynb  ablation A1-A5 + cross-dataset CV1-CV3
│   ├── 09_Final_Audit.ipynb            calibration, per-resolution, latency
│   ├── 10_Multimodal_Fusion.ipynb      visual + text + fusion (HEADLINE)
│   ├── train_v3_seed7.py               seed-7 visual training (ensemble member)
│   └── eval_*.py                       single-seed / TTA / ensemble eval scripts
├── src/qshield/                        installable Python package
│   ├── data/                           Trad / CIC loaders, splits, decode, datasets
│   ├── models/                         visual, text, fusion, losses
│   ├── training/                       phase1, phase2, text, fusion training loops
│   ├── eval/                           metrics, TTA, ensemble, calibration
│   ├── xai/                            Grad-CAM hook
│   └── utils/                          paths, seeds, paper-figure scripts, PPT generator
├── docs/                               advisor-facing notes and analysis
│   ├── results/                        per-experiment JSON outputs (audit, ensemble, multimodal)
│   ├── HANDOFF.md                      pivot rationale (visual-only → multimodal)
│   ├── presentacion_guion.md           slide-by-slide script (Spanish)
│   ├── resumen_asesora.md              short briefing for the advisor
│   └── resumen_ejecutivo_general.md    long form (~30 min read)
├── pyproject.toml                      package metadata for `pip install -e .`
├── 2505.03451v2.pdf                    Trad et al. reference paper
├── 2602.09015v3.pdf                    CIC Trap4Phish reference paper
└── Q-Shield_Presentacion_Asesora.pptx  41-slide advisor deck
```

The four scripts under `notebooks/` are thin orchestrators — they import
everything they need from `qshield.*`. The package is installable with
`pip install -e .` for local development.

---

## Datasets

| Corpus | Total | Used in this work | Format | Native resolution |
|---|---|---|---|---|
| Trad et al. (2025) | 9,987 | 9,987 (full) | Binary matrices | 69 × 69 (V13 only) |
| CIC Trap4Phish 2025 | 1,005,738 | 100,000 (50k + 50k stratified) | Grayscale PNG | 114 – 582 px (V5 – V30) |

All inputs are normalized to 224 × 224 grayscale before the visual CNN.
80 / 20 train / validation split per corpus, stratified by class. Random
seed 42 throughout. Decode rate over the joint validation set: Trad 100 %,
CIC 95.7 %.

---

## Running on Colab

The notebooks expect a single Drive folder containing the dataset zips and
the trained checkpoints. By convention this folder is

```python
BASE = '/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas'
```

Recommended internal layout (see `docs/resumen_asesora.md` for the exact
file list):

```
Proyecto_Quishing_Detection_Nicolas/
├── 01_datasets/         QuishingDataset.zip, QR_benign_430K.zip, QR_malicious_576K.zip
├── 02_checkpoints/
│   ├── visual/          siamese_v3_phase1.pth, classifier_v3_phase2.pth (+ seed 7)
│   ├── text/            text_v1_distilbert.pth
│   └── fusion/          fusion_v1_logit_mlp.pth
├── 03_results/          eval_*.json, threshold_calibration.csv, final_audit_report.json
├── 04_figures/          (generated outputs of figures the notebooks produce)
├── 05_caches/           url_cache.json
├── Notebooks/           Colab copies of the notebooks (linked from this repo)
└── Papers/              reference PDFs
```

The first cell of every notebook clones a fresh copy of the GitHub repo into
`/content/qshield_repo` and adds it to `sys.path`, then mounts Drive as the
data root. URL decoding for the full corpus runs in roughly 15 minutes the
first time and is cached afterwards; Phase 1 visual training is ~ 90 minutes
on Tesla T4; the multimodal fusion notebook end-to-end is ~ 45 minutes
including DistilBERT fine-tuning.

---

## Reproducing the paper numbers

| Number | Script |
|---|---|
| Visual single seed (0.8962) | `notebooks/eval_v3_on_full_set.py` |
| Visual + TTA (0.9053) | `notebooks/eval_v3_tta.py` |
| Visual ensemble + TTA (0.9146) | `notebooks/eval_ensemble_tta.py` |
| Text only (0.9592) | `notebooks/10_Multimodal_Fusion.ipynb` cells 11-14 |
| **Fusion (0.9749)** | `notebooks/10_Multimodal_Fusion.ipynb` cells 15-17 |

Each script writes its output to a JSON in the Drive folder; the canonical
copies are in `docs/results/` for traceability.

---

## Limitations (from the paper)

The paper (Section VI.B) lists seven limitations explicitly:

1. Visual-fallback FNR is 0.20 at the default threshold — only matters when
   the QR fails to decode (4.3 % of the joint corpus).
2. Mild Phase-2 overfitting in the visual branch after epoch 8 — early
   stopping selects the best checkpoint.
3. URL overlap between Trad and CIC has not been verified empirically (Trad
   does not redistribute URL strings).
4. Visual accuracy degrades on QRs above 246 px per side because of the
   fixed 224 × 224 resize.
5. Visual branch has imperfect probability calibration (ECE 0.13); the
   fusion fixes this (ECE 0.038).
6. The framework does not yet include a third branch over the surrounding
   message context (email subject, sender metadata).
7. Adversarial robustness has not been evaluated.

---

## Planned extensions

- **Surrounding-context branch** as a third modality fused with visual + URL.
- **Provenance-aware detection** (cryptographic signatures + merchant-ID
  validation), particularly for mobile-payment ecosystems such as Yape (BCP,
  Peru). Q-Shield answers *"is the content malicious"*; a provenance layer
  would answer *"was this QR generated by the authorized source"*.
- **Multi-scale or resolution-adaptive backbone** to close the gap on large QRs.
- **Adversarial robustness** (module-level perturbations + adversarial training).
- **Localized deployment** (Yape, UPI, Pix) with lightweight regional fine-tuning.

---

## Citation

```
@inproceedings{llerena2026qshield,
  author    = {Llerena Silva, Nicol{\'a}s Alejandro and Soriano-Vargas, Aurea},
  title     = {{Q-Shield}: An Explainable Multimodal Framework for Quishing
               Detection via Siamese Visual and Offline URL Analysis},
  booktitle = {(submitted)},
  year      = {2026}
}
```

---

## Authors

Nicolás Alejandro Llerena Silva, UTEC, Lima, Peru.
Advised by Aurea Soriano-Vargas, UTEC.

## Acknowledgments

Canadian Institute for Cybersecurity at UNB for releasing the Trap4Phish 2025
corpus. F. Trad and A. Chehab for releasing their QR dataset and baseline
implementation.

## License

MIT.
