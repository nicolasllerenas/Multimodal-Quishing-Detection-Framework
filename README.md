# Q-Shield

Siamese network for detecting QR-code phishing (quishing) directly from images, without decoding the payload.

Reference implementation for the paper *Q-Shield: An Explainable Siamese Network for Scalable Quishing Detection Without Payload Decoding* (Llerena Silva and Soriano-Vargas, 2026).

## Results

Combined validation set of 21,998 QR samples drawn from Trad et al. (2025) and CIC Trap4Phish 2025 (Nejati et al., 2026). The full configuration is a two-seed ensemble with horizontal-flip test-time augmentation; a single-seed variant is reported alongside as a low-latency alternative.

| Configuration | AUC | F1 | Recall | FNR | CPU (1 image) | Params |
|---|---|---|---|---|---|---|
| Single seed, no TTA | 0.8962 | 0.821 | 0.798 | 0.202 | 24.9 ms | 3.08 M |
| Single seed + TTA | 0.9053 | 0.825 | 0.799 | 0.201 | 49.8 ms | 3.08 M |
| **Ensemble + TTA** | **0.9146** | **0.835** | **0.801** | **0.199** | 99.6 ms | 6.16 M |
| Trad et al. (reported, n=1,998) | 0.9133 | 0.890 | — | — | — | — |

The ensemble exceeds Trad et al.'s reported AUC by +0.13 pp on a benchmark eleven times larger and visually heterogeneous. GPU inference on a Tesla T4 is 6.0 ms per forward pass with batched throughput of 1,156 images/s.

Threshold calibration on the single-seed model reduces FNR from 0.202 to 0.098 by sliding the decision threshold from 0.50 to 0.40, satisfying the conventional ≤ 10% security tolerance. The same calibration applies to the ensemble configuration.

## Method

Two-phase training plus two inference-time refinements.

**Phase 1 — Siamese contrastive pretraining.** A shared MobileNetV2 backbone with a 128-d L2-normalized projection head, trained on class-balanced same-class / different-class pairs with contrastive loss (Chopra et al., 2005). Margin m = 1.5, AdamW with cosine warm restarts, 40 epochs with patience 8.

**Phase 2 — Supervised classification.** A four-layer dense head (128 → 512 → 128 → 32 → 1) trained with focal loss (γ = 2, α = 0.5). The backbone is frozen for the first five epochs and fine-tuned end-to-end for the next fifteen. Early stopping on validation AUC.

**Inference.** Each image is evaluated together with its horizontal flip (TTA). Probabilities from two models trained with different seeds (42 and 7) are then averaged. The full configuration runs four forward passes per scan; the single-seed variant runs one.

Augmentation in both training phases is horizontal flip with p = 0.5. Rotation is intentionally excluded: QR finder patterns encode orientation, so rotating a QR changes its semantics and would inject label noise.

## Datasets

| Corpus | Total samples | Used in this work | Format |
|---|---|---|---|
| Trad et al. | 9,987 | 9,987 (full) | Binary matrices 69×69 |
| CIC Trap4Phish 2025 | 1,005,738 | 100,000 (50k benign + 50k malicious, stratified) | Variable-resolution grayscale PNG |

All inputs are normalized to 224×224 grayscale before the CNN. Each corpus is split 80/20 train/validation; the joint validation set used throughout the paper is 21,998 samples. Random seed for splits is 42.

## Repository layout

```
Multimodal-Quishing-Detection-Framework/
|-- notebooks/
|   |-- 01_EDA_CIC_Trap4Phish.ipynb      Exploratory analysis of CIC
|   |-- 02_Pattern_Analysis.ipynb        Handcrafted feature baselines
|   |-- 03_SOTA_Review.ipynb             Literature review tables
|   |-- 06_Siamese_Training_v3.ipynb     Seed-42 training (Phase 1 + Phase 2)
|   |-- 07_XAI_GradCAM.ipynb             Grad-CAM, SHAP, embedding-distance analysis
|   |-- 08_Ablation_CrossDataset.ipynb   Ablation A1-A5 and CV1-CV3
|   |-- 09_Final_Audit.ipynb             Threshold calibration, per-resolution, latency
|   |-- train_v3_seed7.py                Seed-7 training for ensemble
|   |-- eval_v3_on_full_set.py           Single-seed eval on the 21,998 set
|   |-- eval_v3_tta.py                   Single-seed eval with TTA
|   `-- eval_ensemble_tta.py             Two-seed ensemble eval with TTA (headline result)
|-- src/
|   |-- models/siamese_qr.py             Backbone, Siamese wrapper, losses, datasets, classifier
|   `-- utils/generate_paper_figures.py  Figures 4, phase 1 curves, phase 2 curves
|-- figures/                             Generated figures used in the paper
|-- paper/                               IEEE conference draft (LaTeX) and bibliography
|-- docs/                                Design notes, advisor summaries, result snapshots
|   `-- results/                         Per-experiment JSON outputs (audit, ensemble TTA)
`-- data/                                Empty placeholders; data lives on Google Drive
```

## Running the notebooks

All notebooks are written for Google Colab with Google Drive mounted. They expect a single project folder on the user's Drive containing the Trad pickled dataset and the CIC zip archives:

```python
BASE = '/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas'
```

Checkpoints, figures, and CSVs are written back to the same folder. Local execution is possible but has been tested only on the inference path.

Dependencies (installed via pip in each notebook):

```
torch >= 2.0
torchvision
scikit-learn
shap
matplotlib
seaborn
pandas
tqdm
Pillow
```

Training was performed on Tesla T4 (mixed precision, batch 64 for Phase 1, batch 128 for Phase 2). Phase 1 takes about 90 minutes; Phase 2 takes about 12 minutes.

## Reproducing the paper numbers

1. `06_Siamese_Training_v3.ipynb` — produces the seed-42 Phase 1 backbone (`siamese_v3_phase1.pth`) and Phase 2 classifier (`classifier_v3_phase2.pth`).
2. `train_v3_seed7.py` — produces the seed-7 ensemble member (`classifier_v3_seed7_phase2.pth`). Same hyperparameters and data splits as the seed-42 run; only the weight initialization and pair-sampling stochasticity differ.
3. `07_XAI_GradCAM.ipynb` — Grad-CAM, SHAP, and embedding-distance analysis (Table VI, Figures 5–8).
4. `08_Ablation_CrossDataset.ipynb` — ablation A1–A5 and cross-dataset CV1–CV3 (Table V panels (a) and (c)). A2–A5 use a 40 % subsample of the training set for compute reasons; the paper reports this in the table footnote.
5. `eval_v3_on_full_set.py` — single-seed baseline (Table III row 1, Table V row A1).
6. `eval_v3_tta.py` — single-seed with TTA (Table III row 2, Table V row B1).
7. `eval_ensemble_tta.py` — two-seed ensemble with TTA (Table III row 3, Table V row B2, Figure 4).
8. `09_Final_Audit.ipynb` — threshold calibration (Table VII), per-resolution stratification (Table IX), and CPU/GPU latency benchmarks.

## Limitations

The paper (Section VI) discusses seven limitations: default-threshold FNR above the 0.10 target, mild overfitting in Phase 2, unverified URL overlap between Trad and CIC, resolution-dependent performance on QRs above 246 px, imperfect probability calibration (ECE 0.13), the unimodal scope (no text branch), the discarded container-format metadata (PDF, SVG, DOCX), and unevaluated adversarial robustness.

## Planned extensions

- Multimodal fusion with a text branch (DistilBERT or equivalent) on paired QR + message data.
- Multi-scale or resolution-adaptive backbone to close the gap on large QR images.
- Provenance-aware detection: cryptographic signatures and merchant-ID validation as a complementary layer for mobile-payment ecosystems such as Yape (BCP, Peru).
- Empirical evaluation under module-level adversarial perturbations.

## Citation

```
@inproceedings{llerena2026qshield,
  author    = {Llerena Silva, Nicol{\'a}s Alejandro and Soriano-Vargas, Aurea},
  title     = {{Q-Shield}: An Explainable Siamese Network for Scalable Quishing Detection Without Payload Decoding},
  booktitle = {(submitted)},
  year      = {2026}
}
```

## Authors

Nicolás Alejandro Llerena Silva, UTEC, Lima, Peru. Advised by Aurea Soriano-Vargas, UTEC.

## Acknowledgments

Canadian Institute for Cybersecurity at UNB for the Trap4Phish 2025 corpus. F. Trad and A. Chehab for the QR dataset and baseline implementation. Compute support from the UTEC IEEE Computer Society Student Branch Chapter.

