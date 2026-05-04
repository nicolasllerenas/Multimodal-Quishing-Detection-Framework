# Q-Shield — handoff for the other Claude session

**Audience:** the Claude session running on Nicolás's other computer.
**Author:** Claude (Opus 4.7) on the first computer, after a long multimodal pivot session with Nicolás on 2026-05-02.
**Status when this was written:** all the changes described below exist on disk on the first computer but **were not committed** at write time. See §11 before assuming GitHub has any of this.

This document is the canonical brief on what the project is, why we just changed direction, what is in the repo now, and what is still left to do. Read it end to end before touching anything.

---

## 1. TL;DR

- Project: **Q-Shield**, a quishing (QR phishing) detector. Author Nicolás Llerena Silva (UTEC), advisor Aurea Soriano-Vargas. Paper targets a 2026 IEEE conference.
- We just **pivoted** the framing from *visual-only, no-decoding* to **multimodal: visual branch + offline-decoded URL text branch + late fusion**. Reasons in §3.
- Repo was reorganized into an installable Python package `qshield` under `src/qshield/`. 32 modules. Notebooks are now thin orchestrators.
- **Notebook `10_Multimodal_Fusion.ipynb`** is the new headline experiment. It compares visual / text / fusion on the existing 21,998-sample joint validation set and writes `eval_multimodal.json` to Drive.
- The previously-failing Colab error was **`ModuleNotFoundError: No module named 'qshield'`**. Root cause: the Drive folder is the *data* root, not the *source* root. Fixed in the rewritten setup cell of notebook 10 (clones the GitHub repo into `/content/qshield_repo` instead of `pip install -e $DRIVE_PATH`). Details in §8.
- Paper LaTeX (`paper/main.tex`) is already updated — new title, new abstract, new methodology subsections (`sec:textbranch`, `sec:fusion`), and a results table `tab:multimodal` with `$\dagger$` placeholders that you fill from `eval_multimodal.json` once notebook 10 finishes.

---

## 2. Project context

| Field | Value |
|---|---|
| Working directory (computer 1) | `/Users/nllerenas/UTEC/research/Multimodal-Quishing-Detection-Framework` |
| GitHub remote | `https://github.com/nicolasllerenas/Multimodal-Quishing-Detection-Framework.git` |
| Current branch | `main` |
| Drive folder used in Colab | `/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas` |
| Drive role | **data + checkpoints + figures only**, not source. Source lives in the GitHub repo. |
| Visual checkpoints already on Drive | `classifier_v3_phase2.pth` (seed 42), `classifier_v3_seed7_phase2.pth`, `siamese_v3_phase1.pth`, `siamese_v3_seed7_phase1.pth` |
| Reference papers (in `2505.03451v2.pdf` and `2602.09015v3.pdf` at repo root) | Trad et al. 2025 and CIC Trap4Phish 2025 — see §4 |

---

## 3. The strategic decision

The original paper claimed *no payload decoding* as a security advantage, mirroring Trad et al. 2025. After re-reading both reference papers we identified three problems with that framing that a reviewer would attack on first read:

1. **The "decoding paradox" is overstated.** Decoding a QR code with a library like `pyzbar` is a deterministic, local, offline operation that returns a string. It does *not* fetch the URL, resolve DNS, or execute JavaScript. The exposure risk is at the *browser-fetch* step, not at the decode step. Framing decoding itself as the threat conflates two different things.

2. **The visual-only signal is weak outside the Trad sandbox.** Trad fixed QR version 13, error correction `low`, box size 1, no logos, no color. CIC Trap4Phish 2025 reports on heterogeneous QRs:
   - SSIM between benign and malicious classes ≈ **0.34–0.35** (visually almost identical)
   - Silhouette score ≈ **0.002**
   - Their CNN over images gets **F1 0.8828**
   - Their LLMs over the *decoded URL* get **F1 0.97–0.99**
   The paper says verbatim: *"image-based methods face challenges because QR encoding creates identical visual patterns... LLMs outperformed the CNN because they used text-based semantic analysis"*. Our own numbers reproduce this gap — single-seed visual on the joint set is F1 ≈ 0.821.

3. **Combining both is the demonstrably-best proposal.** The two pre-existing visual-only and URL-only literatures together imply that fusion will dominate either alone, and Bountakas (2023) and Khalifa (2025) already validate this on webpages. Multimodal is the framing that survives review.

So we kept the visual Siamese branch (it is the only available signal when decoding fails — low contrast, missing quiet zone, damaged finder pattern — which is itself a phishing-relevant condition) and **added an offline URL text branch and a small late-fusion head**.

The paper's framing now says: **two intervention layers. Pre-decode visual layer. Post-decode URL layer. Fused into one decision.** No more *no-decoding* claim as a security argument.

---

## 4. Reference papers, in one paragraph each

**Trad and Chehab, 2025 — `2505.03451v2.pdf`.** Generates 9,987 QR codes (5,005 benign / 4,982 phishing) from PhishStorm URLs using the Python `qrcode` library at fixed version 13, EC `low`, 69×69 binary matrices. Trains classical ML (LR, DT, RF, GNB, XGBoost, LightGBM) over flattened 4,761-pixel vectors. XGBoost reaches AUC 0.9106; with feature selection (drop low-importance pixels) AUC 0.9133. Argues *no decoding* is a security feature. Methodologically clean but the uniform rendering setting hides the generalization problem.

**Nejati et al., CIC Trap4Phish, 2026 — `2602.09015v3.pdf`.** Multi-format malicious-attachment dataset spanning Word, Excel, PDF, HTML, and QR (430k benign + 576k malicious QRs). For QR specifically they evaluate two approaches in parallel: (a) a basic CNN over the QR image — F1 0.8828; (b) lightweight LLMs (BERT-Tiny, DeBERTa-v3, ModernBERT, DeepSeek-R1-Distill) over the *decoded URL string* — F1 0.97–0.99. The two branches are reported side-by-side, **not fused**. SSIM and t-SNE analyses show that benign and malicious QRs are visually nearly indistinguishable.

The Q-Shield multimodal pivot is, in one sentence, *combining Trad's visual contribution with CIC's URL contribution into a single fused detector that neither paper produced*.

---

## 5. Repository layout (after the refactor)

```
Multimodal-Quishing-Detection-Framework/
├── pyproject.toml                              installable package metadata
├── src/qshield/                                <- the package, importable as `qshield`
│   ├── __init__.py
│   ├── data/
│   │   ├── trad.py                             pickle loader for Trad's 69×69 matrices
│   │   ├── cic.py                              zip extractor + 50k stratified sample
│   │   ├── splits.py                           canonical 80/20 (DATA_SEED=42)
│   │   ├── transforms.py                       array_to_tensor / png_to_tensor
│   │   ├── pairs.py                            Phase-1 contrastive pair samplers
│   │   ├── classify.py                         single-image dataset, returns global ID
│   │   ├── decode.py                           offline pyzbar decode + JSON cache
│   │   └── url_dataset.py                      multimodal (image, url, label) dataset
│   ├── models/
│   │   ├── visual.py                           MobileNetV2 backbone + Siamese + classifier
│   │   ├── losses.py                           ContrastiveLoss + FocalLoss
│   │   ├── text.py                             URLClassifier (DistilBERT default)
│   │   └── fusion.py                           LogitFusion + EmbeddingFusion
│   ├── training/
│   │   ├── phase1.py                           Siamese contrastive loop
│   │   ├── phase2.py                           focal-loss classifier loop
│   │   ├── text_train.py                       DistilBERT fine-tune loop
│   │   └── fusion_train.py                     fusion-head loop on cached logits
│   ├── eval/
│   │   ├── metrics.py                          AUC, F1, FNR, FPR, ECE, Brier, CM
│   │   ├── tta.py                              horizontal-flip TTA
│   │   ├── ensemble.py                         seed averaging
│   │   └── calibration.py                      threshold sweep + FNR target
│   ├── xai/
│   │   └── gradcam.py                          Grad-CAM hook on MobileNetV2's last block
│   └── utils/
│       ├── paths.py                            BASE/WORK resolution
│       ├── seeds.py                            set_all_seeds(seed)
│       ├── generate_paper_figures.py           kept from before
│       └── generate_advisor_ppt.py             kept from before
├── notebooks/
│   ├── 01_EDA_CIC_Trap4Phish.ipynb             EDA, unchanged
│   ├── 02_Pattern_Analysis.ipynb               handcrafted-feature baselines, unchanged
│   ├── 03_SOTA_Review.ipynb                    related-work tables, unchanged
│   ├── 06_Siamese_Training_v3.ipynb            seed-42 visual training, unchanged
│   ├── 07_XAI_GradCAM.ipynb                    visual XAI, unchanged
│   ├── 08_Ablation_CrossDataset.ipynb          ablation + cross-dataset, unchanged
│   ├── 09_Final_Audit.ipynb                    calibration / per-resolution / latency, unchanged
│   ├── 10_Multimodal_Fusion.ipynb              <- NEW. Visual + Text + Fusion.
│   ├── eval_v3_on_full_set.py                  rewritten as thin orchestrator
│   ├── eval_v3_tta.py                          rewritten as thin orchestrator
│   ├── eval_ensemble_tta.py                    rewritten as thin orchestrator
│   └── train_v3_seed7.py                       rewritten as thin orchestrator
├── paper/
│   ├── main.tex                                already updated for the multimodal framing
│   └── references.bib                          unchanged
├── figures/                                    unchanged
├── docs/                                       includes this handoff
├── data/                                       still empty (data lives on Drive)
├── 2505.03451v2.pdf                            Trad reference paper
└── 2602.09015v3.pdf                            CIC Trap4Phish reference paper
```

The four scripts under `notebooks/` (the `.py` files) are now thin orchestrators that import from `qshield.*` instead of redefining `MobileNetV2Embedding` / `QRClassifier` / `ClassifyDataset` inline. Net diff at the time of writing was **−2,312 lines** despite adding the multimodal extension, because the duplicated class definitions are now in `qshield/`.

---

## 6. The multimodal pipeline, in one diagram

```
  QR sample (image bytes)
       │
       ├─ PRE-DECODE STAGE ────────────────────────────────────┐
       │                                                       │
       │  qshield.data.transforms.png_to_tensor / array_to_tensor
       │  -> [1, 224, 224] grayscale tensor                    │
       │  -> qshield.models.visual.QRClassifier                │
       │  -> visual logit  ℓ_v                                 │
       │                                                       │
       ├─ DECODE STAGE (local, no network) ────────────────────┤
       │                                                       │
       │  qshield.data.decode.decode_image (pyzbar)            │
       │  -> URL string  OR  '<UNDECODABLE>'  + flag f         │
       │                                                       │
       ├─ POST-DECODE STAGE ───────────────────────────────────┤
       │                                                       │
       │  qshield.models.text.URLTokenizer + URLClassifier     │
       │  -> text logit  ℓ_t                                   │
       │                                                       │
       └─ FUSION ──────────────────────────────────────────────┘
                            │
                            ▼
                qshield.models.fusion.LogitFusion
                MLP([ℓ_v, ℓ_t, f]) -> 16 -> 1
                            │
                            ▼
                final phishing probability
```

LogitFusion is the default. EmbeddingFusion (concatenates the 128-d visual embedding and the 768-d text pooled output) exists in `qshield/models/fusion.py` as an ablation row.

---

## 7. Colab recipe (the canonical one)

The Drive folder `Proyecto_Quishing_Detection_Nicolas` holds **only data + checkpoints + JSON outputs + figures**. It does NOT contain the Python source. The package `qshield` lives in the GitHub repo, and we clone it fresh each Colab session.

The setup cell of notebook 10 is now:

```python
import os, sys
IN_COLAB = 'google.colab' in sys.modules

BASE = '/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas'
REPO = '/content/qshield_repo'
REPO_GIT = 'https://github.com/nicolasllerenas/Multimodal-Quishing-Detection-Framework.git'
WORK = '/content/qshield_work' if IN_COLAB else os.path.join(BASE, 'data', 'work')

if IN_COLAB:
    from google.colab import drive
    drive.mount('/content/drive')
    if not os.path.exists(REPO):
        !git clone -q $REPO_GIT $REPO
    else:
        !cd $REPO && git pull -q
    !apt-get -qq install libzbar0
    !pip install -q transformers pyzbar

# Source: prefer the GitHub clone. Fall back to a Drive copy if the package
# was not pushed yet.
candidates = [
    os.path.join(REPO, 'src'),
    os.path.join(BASE, 'qshield_src'),
]
src_dir = next((p for p in candidates if os.path.isdir(os.path.join(p, 'qshield'))), None)
if src_dir is None:
    raise RuntimeError('qshield not found. Push to GitHub or copy src/qshield to Drive.')
sys.path.insert(0, src_dir)
os.makedirs(WORK, exist_ok=True)
```

Two reasons this is the right pattern:

- **`pip install -e <Drive path>` fails** because the Drive folder has no `pyproject.toml` (and even if you copy one in, Drive's FUSE filesystem is unreliable for editable installs).
- **`sys.path.insert(0, BASE/src)` also fails** because `BASE` is the data root, not the source root.

The fallback path lets a stuck user copy `src/qshield` to `BASE/qshield_src/qshield/` on Drive when they cannot push, e.g. while travelling or on the wrong computer.

---

## 8. Diagnostic playbook for the Colab error you may have seen

The error reported on 2026-05-02 was:

```
ERROR: file:///content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found.
ModuleNotFoundError: No module named 'qshield'
```

Both lines come from the same cause: the old setup cell did `pip install -e $PROJECT` against the Drive folder, which is a *data* folder. The fix is shipped in §7 above.

If you see a different error after applying the new setup cell, walk this list in order:

1. **`fatal: Authentication failed`** when cloning — the repo is public, no auth needed, but corporate proxies sometimes require credentials. Fall back to copying `src/qshield` to Drive at `BASE/qshield_src/qshield/`.
2. **`No such file or directory: '/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas/QR_benign_430K.zip'`** — the Drive mount worked but the user pointed at the wrong folder. The shared folder may be mounted under "Compartido conmigo" / "Shared with me" rather than under MyDrive. Tell the user to open the folder in Drive UI, click the three dots, choose *Add shortcut to My Drive*. Then `BASE` resolves correctly.
3. **`ImportError: cannot import name 'X' from 'qshield.…'`** — the user's clone is stale. `cd $REPO && git pull` and rerun the setup cell.
4. **`libzbar.so.0: cannot open shared object file`** — `apt-get install libzbar0` did not run. Check that the previous `!apt-get` cell finished without error; in a fresh Colab session it sometimes needs `sudo apt-get update` first.
5. **`CUDA out of memory`** in the text-branch fine-tune (cell 11) — drop `train_loader_t` batch size from 64 to 32, or switch `TEXT_MODEL = 'bert-tiny'`.
6. **The decode cell (cell 7) appears hung** — it's not, decoding ~102k QRs takes around 15 minutes on T4. After the first run the cache is on Drive (`url_cache.json`) and re-running is instant.
7. **`Drive already mounted`** with the cell raising — that's a warning, not an error. The mount is reused. If the assert fails it means the Drive folder really doesn't exist at that path.

---

## 9. Open tasks (in priority order)

Once notebook 10 finishes successfully:

1. **Fill `tab:multimodal` in `paper/main.tex`** with the numbers from `eval_multimodal.json`. The placeholders are `$\dagger$`. Copy AUC, Precision, Recall, F1, FNR for each of `visual_only`, `text_only`, `fusion`.
2. **Run the visual ensemble member with multimodal too.** Re-run notebook 10 with `VISUAL_CKPT = 'classifier_v3_seed7_phase2.pth'` and report whether seed-7 + text branch fusion outperforms seed-42 + text branch fusion. If yes, mention it in the paper as an ensemble + multimodal ablation row.
3. **Threshold-sweep the fused model.** Use `qshield.eval.calibration.find_threshold_for_fnr(fused_probs, labels, target_fnr=0.10)` to locate the operating point that meets the ≤10% FNR target on the multimodal model, and add it to the paper's `tab:threshold`.
4. **Update `06_Siamese_Training_v3.ipynb`** to also use the `qshield` package (right now only the four `.py` scripts under `notebooks/` were refactored). The notebook still has the model defined inline. Refactoring it is mechanical but tedious.
5. **Write the SHAP-on-text-branch counterpart** of the visual SHAP analysis. The visual SHAP is over the 128-d embedding; the text SHAP would be over input tokens. `qshield/xai/` is the place to drop it.
6. **Adversarial robustness study** is still listed in §VI of the paper as future work. Optional for this submission.
7. **Surrounding-message context branch** (the *third* modality) is also future work. Out of scope for the current paper.

---

## 10. Working with Nicolás — preferences and style

These are saved in our memory store and are worth knowing before you propose anything.

- **Spanish in conversation**, English in code/comments and the paper.
- **Asks for critical feedback, not diplomatic softening.** When something in the paper or code is weak, say so directly and propose the fix.
- **Demands "demonstrable without doubt"** claims. We dropped the *no-decoding* framing precisely because it would not survive review against CIC. Apply the same standard to anything new you add.
- **Notebooks must stay readable for the advisor**, who is not a Python person. The `qshield` package + thin notebook orchestrators is the agreed pattern. Do not move logic back into notebooks.
- **Working in Colab on T4**. Phase 1 is ~90 min, Phase 2 ~12 min, URL decoding ~15 min. Budget your suggestions accordingly.
- **Code style: terse, no defensive bloat.** Match what's already in `src/qshield/`. No type hints, minimal docstrings (only when WHY is non-obvious), no AI-style symmetric structure.

---

## 11. Cross-computer state (READ THIS FIRST)

At the time this document was committed, **the local repo on computer 1 had a large set of uncommitted changes** that produced the package, the new notebook, the paper edits, and this handoff. Specifically, `git status --short` reported:

```
 M README.md
 M notebooks/eval_ensemble_tta.py
 M notebooks/eval_v3_on_full_set.py
 M notebooks/eval_v3_tta.py
 M notebooks/train_v3_seed7.py
 M paper/main.tex
 D src/__init__.py
 D src/data/__init__.py
 D src/models/__init__.py
 D src/models/siamese_qr.py
 D src/utils/__init__.py
 D src/utils/generate_advisor_ppt.py
 D src/utils/generate_paper_figures.py
?? 2505.03451v2.pdf
?? 2602.09015v3.pdf
?? notebooks/10_Multimodal_Fusion.ipynb
?? pyproject.toml
?? src/qshield/
?? docs/HANDOFF.md
```

If you, the other chat, are reading this **after** Nicolás has committed and pushed, the GitHub clone in §7 will work and you can ignore this section. If you are reading it **before**, then:

- The GitHub remote is on commit `2027e1f guion` and does not yet contain any of the multimodal work.
- Tell Nicolás to commit and push from computer 1, or copy `src/qshield/` plus `pyproject.toml` and `notebooks/10_Multimodal_Fusion.ipynb` onto Drive at `BASE/qshield_src/` so the fallback path in the setup cell picks it up.

When you do commit, the suggested commit message is:

```
Multimodal extension: qshield package + visual/text/fusion notebook

- src/qshield/ package (32 modules) with data, models, training,
  eval, xai, utils subpackages. Replaces the inline definitions
  previously duplicated across notebooks and eval scripts.
- pyproject.toml for `pip install -e .` (local dev only; Colab
  imports via sys.path against a fresh GitHub clone).
- notebooks/10_Multimodal_Fusion.ipynb: end-to-end multimodal
  experiment producing eval_multimodal.json on Drive.
- paper/main.tex: re-titled, abstract rewritten, methodology
  subsections sec:textbranch and sec:fusion added, results table
  tab:multimodal with placeholders to fill from notebook 10.
- README.md and docs/HANDOFF.md updated for the new pipeline.
- eval_v3_on_full_set.py / eval_v3_tta.py / eval_ensemble_tta.py /
  train_v3_seed7.py rewritten as thin orchestrators using qshield.
```

---

## 12. One-paragraph summary you can paste back to Nicolás

> "Project pivoted to multimodal: visual Siamese branch (already trained, on Drive) plus an offline-decoded URL text branch (DistilBERT) plus a tiny late-fusion MLP. New `qshield` package under `src/qshield/`, new notebook `10_Multimodal_Fusion.ipynb`, paper rewritten with the new framing. The Colab error you saw was caused by the old setup trying to `pip install -e` the Drive folder; fixed it to clone the GitHub repo into `/content/qshield_repo` and add that to `sys.path`. Step 0: commit and push the local changes from computer 1, otherwise the clone won't have the package. After that, run notebook 10 end-to-end and copy the numbers from `eval_multimodal.json` into Table III of the paper."
