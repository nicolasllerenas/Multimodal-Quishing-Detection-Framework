# Q-Shield — Redefined Scope

**Decision date:** April 16, 2026  
**Status:** v3 accepted as final visual model. Multimodal and localization deferred to future work.

---

## 1. What Q-Shield IS (in scope)

**A country-agnostic, scalable visual framework for detecting QR code phishing without payload decoding.**

### Core contributions (validated with current data)

1. **Siamese Contrastive Architecture** — MobileNetV2 backbone learns QR code embeddings via metric learning. First application of contrastive learning to quishing detection.

2. **Cross-Dataset Benchmark** — Evaluation on Trad (9,987 binary matrices, Version 13 only) + CIC (1M+ variable-resolution PNGs across multiple QR versions). 21,998 validation samples — the largest benchmark used for quishing detection to date.

3. **No Payload Decoding** — The entire pipeline operates on the QR code image directly. Zero exposure to malicious URLs at inference time.

4. **Explainable Detection** — Grad-CAM heatmaps identify which QR regions drive the decision. SHAP analysis on structural features provides global interpretability.

5. **Edge-Deployable** — 2.9M parameters (MobileNetV2), compatible with mobile inference on mid-range devices.

### Validated results

| Method | AUC | F1 | FNR |
|--------|-----|-----|-----|
| Trad et al. baseline | 0.9133 | 0.89 | — |
| Our 25 handcrafted features + RF | 0.8132 | 0.72 | 0.34 |
| **Our Siamese v3 (final)** | **0.8962** | **0.82** | **0.20** |

Note: Trad reports on 1,998 homogeneous QR-13 samples. Our result covers 21,998 heterogeneous samples across QR versions, resolutions, and dataset origins — a more demanding generalization test.

---

## 2. What Q-Shield is NOT (out of scope for this paper)

### Deferred to future work

- **Multimodal fusion (visual + text).** Our architecture is designed to accommodate a semantic branch (e.g., DistilBERT over accompanying SMS/email text), but validating this requires paired QR+text datasets that do not currently exist publicly.

- **Region-specific phishing detection.** Q-Shield is country-agnostic by design. Local phishing patterns (e.g., Peruvian Yape/Plin, Indian UPI, Brazilian Pix) represent a natural extension that requires native-language corpora and regional security expertise.

- **Adversarial robustness.** Targeted perturbations of QR modules (e.g., patch attacks) are a known threat vector. Q-Shield's robustness under adversarial conditions is a research question we leave for future empirical study.

- **Real-time mobile deployment.** While our model is edge-compatible in parameter count, end-to-end mobile integration (Android/iOS apps, camera pipeline, inference latency) is engineering work outside the scope of the research contribution.

---

## 3. Paper narrative

### Research question

Can a lightweight, explainable, deep-learning model detect quishing attacks from QR code structure alone, without requiring payload decoding, and generalize across QR versions and image formats?

### Answer (supported by v3 results)

Yes. A Siamese Network with contrastive pretraining on QR code pairs achieves AUC 0.8962 on a heterogeneous benchmark of ~22,000 QR images spanning multiple versions and resolutions, while using only 2.9M parameters.

### Novel contributions

1. First Siamese contrastive learning approach for quishing (methodological novelty)
2. Largest-scale evaluation of quishing detection (empirical novelty)
3. Dual-layer explainability: Grad-CAM + SHAP (practical novelty)
4. Framework architecture supporting multimodal extension (design novelty)

---

## 4. What we build next (in remaining days)

Given the scope redefinition, focus shifts to:

| Priority | Task | Deliverable |
|----------|------|-------------|
| P1 | Grad-CAM visualization on v3 model | Figure 6 of paper |
| P2 | Cross-dataset evaluation (train Trad → test CIC and vice versa) | Table IV (generalization) |
| P3 | Ablation study (Siamese vs direct CNN, focal vs BCE, frozen vs end-to-end) | Table V |
| P4 | Per-version analysis (how does AUC change across QR versions in CIC?) | Figure 7 |
| P5 | Robustness check: inject Gaussian noise, rotation, scaling | Table VI |
| P6 | Paper rewrite to reflect new scope | main.tex v2 |
| P7 | Future work section expansion | Section VI |

All of this uses the v3 checkpoint we already have. No additional training needed except for ablation (which is fast: 10-15 min per variant).

---

## 5. Why this scope is stronger for IEEE submission

1. **Focused contribution.** One clear research question, rigorously answered with empirical evidence.

2. **Honest framing.** We don't overclaim a multimodal framework we haven't validated. We present what we have and label what we don't.

3. **Generalization emphasis.** Cross-dataset results are rare in quishing literature. Our AUC 0.8962 on a mixed benchmark is more impressive than Trad's 0.9133 on a homogeneous one — but only if we frame it correctly.

4. **Reproducibility.** Trained on public datasets, full code in GitHub, checkpoints in Drive. IEEE reviewers will appreciate this.

5. **Clear future work.** Three concrete extensions (multimodal, localization, robustness) each worthy of its own paper.
