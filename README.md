# Q-Shield

Multimodal quishing detection framework. Two branches operating on the same QR sample at different stages of the detection pipeline:

- **Visual branch** — Siamese MobileNetV2 over the QR image. Operates pre-decode, so it works even when the payload cannot be decoded.
- **Text branch** — DistilBERT over the offline-decoded URL string. Decoding is local: pyzbar reads the QR matrix and returns a string; no network call, no fetch, no JS execution.
- **Fusion** — small MLP combining `[visual_logit, text_logit, undecodable_flag]` into the final phishing score.

Reference implementation for the paper *Q-Shield: An Explainable Multimodal Framework for Quishing Detection via Siamese Visual and Offline URL Analysis* (Llerena Silva and Soriano-Vargas, 2026).

## Results

Combined validation set of 21,998 QR samples drawn from Trad et al. (2025) and CIC Trap4Phish 2025 (Nejati et al., 2026).

### Multimodal (visual + URL) — headline

| Configuration | AUC | F1 | Recall | FNR | Brier | ECE |
|---|---|---|---|---|---|---|
| Visual only (single seed) | 0.8962 | 0.821 | 0.798 | 0.202 | 0.146 | 0.133 |
| Text only (DistilBERT on offline-decoded URL) | 0.9592 | 0.927 | 0.931 | 0.069 | 0.066 | 0.045 |
| **Fusion (logit MLP)** | **0.9749** | **0.936** | **0.943** | **0.057** | **0.054** | **0.038** |

The fused configuration exceeds Trad et al.'s reported AUC (0.9133, n=1,998) by **+6.16 pp** on a benchmark eleven times larger and visually heterogeneous. The default-threshold FNR of 0.057 is already below the conventional ≤ 10% security tolerance, so threshold calibration becomes optional rather than load-bearing. Calibration metrics improve roughly threefold versus the visual-only baseline.

### Visual branch only — fallback path

Reported separately because the visual branch is the operative signal whenever the QR payload cannot be decoded (low contrast, missing quiet zone, damaged finder pattern).

| Configuration | AUC | F1 | Recall | FNR | CPU (1 image) | Params |
|---|---|---|---|---|---|---|
| Single seed, no TTA | 0.8962 | 0.821 | 0.798 | 0.202 | 24.9 ms | 3.08 M |
| Single seed + TTA | 0.9053 | 0.825 | 0.799 | 0.201 | 49.8 ms | 3.08 M |
| **Ensemble + TTA** | **0.9146** | **0.835** | **0.801** | **0.199** | 99.6 ms | 6.16 M |
| Trad et al. (reported, n=1,998) | 0.9133 | 0.890 | — | — | — | — |

For deployments where every sample must clear the ≤ 10% FNR target even when the URL is undecodable, threshold calibration on the visual fallback (p = 0.50 → 0.40) brings its FNR from 0.202 to 0.098 at a modest precision cost.

## Method

**Phase 1 — Siamese contrastive pretraining (visual).** Shared MobileNetV2 backbone with a 128-d L2-normalized projection head, trained on class-balanced same-class / different-class pairs with contrastive loss (Chopra et al., 2005). Margin m = 1.5, AdamW with cosine warm restarts, 40 epochs with patience 8.

**Phase 2 — Supervised classification (visual).** Four-layer dense head (128 → 512 → 128 → 32 → 1) trained with focal loss (γ = 2, α = 0.5). Backbone frozen for the first 5 epochs, then end-to-end fine-tuning for 15 more. Early stopping on validation AUC.

**Text branch.** DistilBERT (66M params) fine-tuned on the offline-decoded URL strings with focal loss for 3 epochs, AdamW (lr 2e-5, wd 1e-2), linear warmup-then-decay schedule with 10% warmup. Decoding is performed once per dataset and cached to JSON; samples whose decode fails are encoded as a single `<UNDECODABLE>` sentinel token.

**Fusion.** 3-input MLP (`[visual_logit, text_logit, undecodable_flag]` → 16 → 1) trained with focal loss for 20 epochs on cached features. Both branches frozen.

**Inference.** Visual branch runs original + horizontal flip (TTA). Two-seed ensemble averages over seeds 42 and 7. Text branch runs once (no TTA). Fusion is applied on the cached logits. The four-pass visual configuration plus one text pass is the full multimodal cost.

Augmentation in the visual branch is horizontal flip with p = 0.5; rotation is intentionally excluded because QR finder patterns encode orientation.

## Datasets

| Corpus | Total samples | Used in this work | Format |
|---|---|---|---|
| Trad et al. | 9,987 | 9,987 (full) | Binary matrices 69×69 |
| CIC Trap4Phish 2025 | 1,005,738 | 100,000 (50k benign + 50k malicious, stratified) | Variable-resolution grayscale PNG |

All inputs are normalized to 224×224 grayscale before the CNN. Each corpus is split 80/20 train/validation; the joint validation set used throughout the paper is 21,998 samples. Random seed for splits is 42.

## Repository layout

```
Multimodal-Quishing-Detection-Framework/
|-- src/qshield/                       installable Python package (`pip install -e .`)
|   |-- data/
|   |   |-- trad.py                    Trad et al. pickle loader
|   |   |-- cic.py                     CIC Trap4Phish zip loader + sampling
|   |   |-- splits.py                  canonical 80/20 train/val (DATA_SEED=42)
|   |   |-- transforms.py              224x224 grayscale preprocessing
|   |   |-- pairs.py                   Phase-1 contrastive pair samplers
|   |   |-- classify.py                Phase-2 single-image dataset
|   |   |-- decode.py                  offline QR -> URL via pyzbar (cached)
|   |   `-- url_dataset.py             multimodal (image, url, label) dataset
|   |-- models/
|   |   |-- visual.py                  MobileNetV2 + Siamese + classifier head
|   |   |-- losses.py                  contrastive + focal
|   |   |-- text.py                    DistilBERT URL classifier
|   |   `-- fusion.py                  late-fusion MLPs (logit / embedding level)
|   |-- training/
|   |   |-- phase1.py                  Siamese contrastive loop
|   |   |-- phase2.py                  focal-loss classifier loop
|   |   |-- text_train.py              DistilBERT fine-tune loop
|   |   `-- fusion_train.py            cached-features fusion loop
|   |-- eval/
|   |   |-- metrics.py                 AUC, F1, FNR, FPR, ECE, Brier, CM
|   |   |-- tta.py                     horizontal-flip TTA
|   |   |-- ensemble.py                seed-ensemble averaging
|   |   `-- calibration.py             threshold sweep + FNR target
|   |-- xai/
|   |   `-- gradcam.py                 Grad-CAM hook
|   `-- utils/                         seeds, paths, paper figure scripts
|-- notebooks/
|   |-- 01..03                         EDA, baselines, SOTA
|   |-- 06_Siamese_Training_v3.ipynb   seed-42 visual training
|   |-- 07_XAI_GradCAM.ipynb           visual XAI
|   |-- 08_Ablation_CrossDataset.ipynb ablation + cross-dataset
|   |-- 09_Final_Audit.ipynb           calibration + per-resolution + latency
|   |-- 10_Multimodal_Fusion.ipynb     visual + text + fusion (NEW)
|   |-- train_v3_seed7.py              seed-7 visual training
|   `-- eval_*.py                      thin orchestrators using qshield.*
|-- paper/                             IEEE LaTeX + bibliography
|-- figures/                           figures used in the paper
|-- docs/                              design notes, advisor summaries
|-- pyproject.toml                     package metadata for `pip install -e .`
`-- data/                              empty placeholders; corpora live on Drive
```

## Running on Colab

The notebooks expect a single project folder on Google Drive containing the dataset zips and the trained checkpoints:

```python
BASE = '/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas'
```

The first cell of every notebook installs the package as editable from the project directory and pulls the Colab-specific dependencies:

```python
!apt-get -qq install libzbar0 > /dev/null   # only for notebook 10 (decoding)
!pip install -q -e $PROJECT
```

After install, every module is importable as `from qshield.<subpackage> import ...`. Checkpoints, the URL decode cache, and JSON evaluation outputs are written back to `BASE`.

Phase 1 takes about 90 min on Tesla T4; Phase 2 about 12 min; URL decoding for the full 80k-train + 22k-val split runs in roughly 15 min and is cached so repeated runs are instant.

## Reproducing the paper numbers

1. `06_Siamese_Training_v3.ipynb` — seed-42 Phase 1 backbone (`siamese_v3_phase1.pth`) and Phase 2 classifier (`classifier_v3_phase2.pth`).
2. `train_v3_seed7.py` — seed-7 ensemble member (`classifier_v3_seed7_phase2.pth`).
3. `07_XAI_GradCAM.ipynb` — Grad-CAM, SHAP, embedding-distance analysis.
4. `08_Ablation_CrossDataset.ipynb` — A1–A5 and CV1–CV3 (40% subsample for A2–A5).
5. `eval_v3_on_full_set.py` — single-seed baseline.
6. `eval_v3_tta.py` — single-seed with TTA.
7. `eval_ensemble_tta.py` — two-seed ensemble with TTA (visual headline result).
8. `09_Final_Audit.ipynb` — threshold calibration, per-resolution, latency.
9. `10_Multimodal_Fusion.ipynb` — decodes URLs, fine-tunes DistilBERT on URLs, trains the fusion MLP, reports visual / text / fusion comparison (writes `eval_multimodal.json`).

## Limitations

The paper (Section VI) discusses: default-threshold FNR above the 0.10 target, Phase-2 overfitting, unverified URL overlap between Trad and CIC, resolution-dependent performance on QRs above 246 px, imperfect probability calibration (ECE 0.13), missing surrounding-message context branch, discarded container-format metadata (PDF, SVG, DOCX), and unevaluated adversarial robustness.

## Planned extensions

- Surrounding-message context branch (email subject / SMS body / sender metadata) fused with the existing two branches.
- Multi-scale or resolution-adaptive visual backbone to close the gap on large QR images.
- Provenance-aware detection: cryptographic signatures and merchant-ID validation as a complementary layer for mobile-payment ecosystems such as Yape (BCP, Peru).
- Empirical evaluation under module-level adversarial perturbations.

## Citation

```
@inproceedings{llerena2026qshield,
  author    = {Llerena Silva, Nicol{\'a}s Alejandro and Soriano-Vargas, Aurea},
  title     = {{Q-Shield}: An Explainable Multimodal Framework for Quishing Detection via Siamese Visual and Offline URL Analysis},
  booktitle = {(submitted)},
  year      = {2026}
}
```

## Authors

Nicolás Alejandro Llerena Silva, UTEC, Lima, Peru. Advised by Aurea Soriano-Vargas, UTEC.

## Acknowledgments

Canadian Institute for Cybersecurity at UNB for the Trap4Phish 2025 corpus. F. Trad and A. Chehab for the QR dataset and baseline implementation. Compute support from the UTEC IEEE Computer Society Student Branch Chapter.

