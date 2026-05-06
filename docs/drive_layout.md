# Drive layout — recommended organization

**Purpose:** the Drive folder is the data root for every Colab notebook in
this project. Right now it is flat, with v1/v2/v3 checkpoints, JSONs, figures,
zip archives and a misc `Untitled1.ipynb` mixed at the top level. This is
hard to skim during the advisor meeting and easy to break if a notebook
asks for a stale filename.

This document is the **canonical layout** the project's code expects. Every
script in `qshield/` and every notebook resolves paths via
`qshield.utils.paths.resolve_base()`, which defaults to
`/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas`. As long as the
top-level filenames match what the scripts expect, the subfolder organization
below is purely for human navigation and does not affect any code path.

---

## Target layout

```
Proyecto_Quishing_Detection_Nicolas/                  ← BASE
│
├── 01_datasets/                                      raw inputs
│   ├── QuishingDataset.zip                           Trad pickled QR matrices
│   ├── QR_benign_430K.zip                            CIC benign images
│   └── QR_malicious_576K.zip                         CIC malicious images
│
├── 02_checkpoints/                                   trained models
│   ├── visual/
│   │   ├── siamese_v3_phase1.pth                     Phase 1 backbone (seed 42)
│   │   ├── siamese_v3_seed7_phase1.pth               Phase 1 backbone (seed 7)
│   │   ├── classifier_v3_phase2.pth                  Phase 2 classifier (seed 42)  ← FINAL
│   │   └── classifier_v3_seed7_phase2.pth            Phase 2 classifier (seed 7)   ← FINAL
│   ├── text/
│   │   └── text_v1_distilbert.pth                    fine-tuned DistilBERT URL classifier
│   └── fusion/
│       └── fusion_v1_logit_mlp.pth                   late-fusion MLP (161 params)
│
├── 03_results/                                       canonical numeric outputs
│   ├── eval_v3_full_set.json                         single-seed visual baseline
│   ├── eval_v3_tta.json                              single-seed + TTA
│   ├── eval_ensemble_2seeds_tta.json                 visual ensemble + TTA
│   ├── eval_multimodal.json                          fusion (HEADLINE)
│   ├── final_audit_report.json                       calibration + per-resolution + latency
│   └── threshold_calibration.csv                     threshold sweep CSV
│
├── 04_figures/                                       canonical figure outputs
│   ├── fig_phase1_curves.png
│   ├── fig_phase2_curves.png
│   ├── fig_confusion_roc.png
│   ├── fig_branch_comparison.png
│   ├── fig_pipeline_abstract.png
│   ├── fig_gradcam_samples.png
│   ├── fig_gradcam_aggregate.png
│   ├── fig_gradcam_per_dataset.png
│   ├── fig_shap_embedding.png
│   ├── fig_embedding_distances.png
│   └── fig_threshold_calibration.png
│
├── 05_caches/                                        intermediate caches (rebuildable)
│   └── url_cache.json                                pyzbar decode cache (~108k entries)
│
├── Notebooks/                                        Colab copies of the notebooks
│   └── (already exists)
│
├── Papers/                                           reference PDFs
│   └── (already exists)
│
└── _archive/                                         superseded outputs (kept for trace)
    ├── classifier_phase2.pth                         v1 (visual-only initial attempt)
    ├── classifier_v2_phase2.pth                      v2 (over-regularized, dropped)
    ├── siamese_phase1.pth                            v1 backbone
    ├── siamese_v2_phase1.pth                         v2 backbone
    ├── experiment_results_v2.json                    v2 metrics
    ├── experiment_results_v3.json                    v3 visual-only metrics (pre-pivot)
    ├── ablation_results.csv                          older intermediate
    ├── ablation_crossdataset_results.csv             older intermediate
    ├── crossdataset_results.csv                      older intermediate
    ├── per_size_results.csv                          older intermediate
    ├── fig_v2_final.png                              v2 confusion matrix
    ├── fig_v3_final.png                              v3 visual-only confusion matrix
    ├── fig_tsne_embeddings.png                       v2 t-SNE
    ├── fig_final_results.png                         pre-pivot summary plot
    └── Untitled1.ipynb                               misc Colab scratch
```

---

## Why this matters

1. **The advisor can navigate without explanation.** A folder name like
   `02_checkpoints/visual/` says exactly what is inside, while
   `classifier_v3_phase2.pth` at the top level next to nine other `.pth`
   files at different stages of training does not.

2. **No code path changes.** The Q-Shield scripts only read a small number of
   filenames at the BASE root: the three dataset zips, the visual
   checkpoints (`classifier_v3_phase2.pth`, `classifier_v3_seed7_phase2.pth`,
   `siamese_v3_phase1.pth`, `siamese_v3_seed7_phase1.pth`), the text
   checkpoint (`text_v1_distilbert.pth`), the fusion checkpoint
   (`fusion_v1_logit_mlp.pth`), and the cache files (`url_cache.json`).
   The subfolders are for the human.

3. **Reproducibility.** Each `03_results/*.json` is the numeric output of a
   specific script in `qshield/`; if the advisor asks "where does the 0.9749
   come from", the answer is `03_results/eval_multimodal.json`, produced by
   `notebooks/10_Multimodal_Fusion.ipynb`.

---

## Migration checklist

Open Drive in a browser, then:

1. **Create six folders at the BASE root** (right-click → New folder):
   `01_datasets`, `02_checkpoints`, `03_results`, `04_figures`,
   `05_caches`, `_archive`.

2. **Inside `02_checkpoints/`** create three subfolders: `visual`, `text`,
   `fusion`.

3. **Move files** (drag, or right-click → Move to):
   - The three `.zip` files → `01_datasets/`.
   - All `siamese_*.pth` and `classifier_*.pth` (v3 and v3_seed7) →
     `02_checkpoints/visual/`.
   - `text_v1_distilbert.pth` → `02_checkpoints/text/`.
   - `fusion_v1_logit_mlp.pth` → `02_checkpoints/fusion/`.
   - All `eval_*.json`, `final_audit_report.json`,
     `threshold_calibration.csv` → `03_results/`.
   - All `fig_*.png` (current paper figures) → `04_figures/`.
   - `url_cache.json` → `05_caches/`.

4. **Move v1, v2 and superseded files to `_archive/`**:
   - `classifier_phase2.pth`, `classifier_v2_phase2.pth`,
     `siamese_phase1.pth`, `siamese_v2_phase1.pth`.
   - `experiment_results_v2.json`, `experiment_results_v3.json`.
   - `fig_v2_final.png`, `fig_v3_final.png`, `fig_tsne_embeddings.png`,
     `fig_final_results.png`.
   - `ablation_results.csv`, `ablation_crossdataset_results.csv`,
     `crossdataset_results.csv`, `per_size_results.csv`.
   - `Untitled1.ipynb`.

5. **Optional: update the BASE constant.** Right now every script expects
   to find the active checkpoints **at the BASE root**, not in
   `02_checkpoints/visual/`. If you move the active `classifier_v3_phase2.pth`
   into `02_checkpoints/visual/`, the eval scripts will break. Two ways to
   handle this:

   - **(a) Easy:** keep a *copy* (not a move) of the four active checkpoints at
     the BASE root. The neat folders are then a navigation aid; the code keeps
     reading from BASE. Drive copies are cheap. This is what I recommend.
   - **(b) Strict:** update the path constants in
     `qshield.utils.paths.DEFAULT_BASE` and the BASE-relative paths in the
     eval scripts to point inside `02_checkpoints/visual/`. More work, more
     fragile.

I recommend (a). Keep the active four `.pth` files at the BASE root **and** in
`02_checkpoints/visual/`. The advisor sees the organized structure; the code
sees the BASE root; nothing breaks.

---

## Files that should NOT live at the BASE root anymore

After the migration, the BASE root should contain only:

- The six top-level folders above.
- The four active checkpoint files (visual seed 42, visual seed 7,
  text DistilBERT, fusion MLP) — copies, see point 5(a).
- The three dataset zip files — Drive may keep them at the root if they
  were uploaded directly; you can move them to `01_datasets/` and update
  `qshield.data.cic.load` to look there if you really want the strictness.
  In practice they are large enough that I suggest leaving them at the
  root **and** linking from `01_datasets/` (Drive supports adding shortcuts).
- `url_cache.json` (active cache, copy from `05_caches/`).

Anything else at the BASE root means it slipped through; move it to
`_archive/` if it is no longer needed for an active script.
