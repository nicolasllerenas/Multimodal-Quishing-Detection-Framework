# Q-Shield: Multimodal Quishing Detection Framework

> **A lightweight, explainable, multimodal framework for detecting QR code phishing (quishing) attacks without payload decoding, designed for mobile deployment in emerging economies.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![IEEE](https://img.shields.io/badge/Target-IEEE%20Conference-blue.svg)]()

## Abstract

The proliferation of QR codes in mobile payment ecosystems has introduced **quishing** (QR phishing) as a critical cybersecurity threat, particularly in el against quishing because they (a) assume malicious content is in the message body rather than embedded in a QR code (**visual blindness**), (b) require decoding the QR payload, which exposes users to the malicious content itself, and (c) do not understand localized social engineering patterns in Latin American markets.

**Q-Shield** addresses these gaps through a **hybrid two-stream architecture** that fuses:
- **Visual Branch** (MobileNetV2): Extracts structural anomalies from QR code images *without decoding* the payload
- **Semantic Branch** (DistilBERT Multilingual): Analyzes the accompanying SMS/message text for social engineering patterns (urgency, authority, reward) with support for Peruvian Spanish context (Yape, Plin, BCP)

The framework is designed for **edge deployment** on mobile devices, with full **explainability** via SHAP and Grad-CAM.

## Problem Statement

### The Quishing Threat Landscape

QR code adoption has surged globally, with Latin American fintech platforms like **Yape** (Peru, 15M+ users), **Plin**, and traditional banks increasingly relying on QR-based transactions. This creates a fertile attack surface:

1. **Visual Blindness**: Traditional phishing detectors analyze email/SMS text but cannot "see" the malicious URL hidden inside a QR code image
2. **Decoding Danger**: Scanning a malicious QR code to extract its URL for analysis defeats the purpose — the user is already exposed to the redirect chain
3. **Localization Gap**: Existing models are trained on English-language phishing campaigns and miss social engineering cues in Peruvian Spanish ("Tu cuenta Yape ha sido bloqueada", "Gana S/500 con Plin")
4. **Resource Constraints**: Heavy models (ResNet + BERT) are impractical for mobile deployment in markets where mid-range Android devices dominate

### Key Insight

> Malicious QR codes encoding longer/obfuscated URLs produce **measurably different structural patterns** — higher module density, more complex transition patterns, and asymmetric data regions — that can be detected by a CNN *without ever decoding the payload*.

This insight, first demonstrated by Trad & Chehab (2025) using classical ML, is extended by Q-Shield through deep learning and multimodal fusion.

## Architecture

Q-Shield uses a **two-phase training strategy** combining self-supervised contrastive learning with supervised multimodal classification.

### Phase 1: Siamese Pretraining (Contrastive Learning)

```
    QR_anchor ──────┐
                    ├── MobileNetV2 (shared weights) ──> emb_a ─┐
    QR_pair ────────┘                                    emb_b ─┤
                                                                ├─ Contrastive Loss
                        "Learn what makes QR codes               │  L = y*d^2 + (1-y)*max(0, m-d)^2
                         similar or different"                   └──────────────────────────
```

The Siamese backbone learns a **128-dimensional embedding space** where benign QR codes cluster together and malicious QR codes form a separate cluster, based purely on structural patterns.

### Phase 2: Multimodal Fine-Tuning (Supervised Classification)

```
    QR Image ──> Siamese MobileNetV2 ──> QR Embedding (128-d) ─┐
                 (pretrained Phase 1)                            ├── Concat ──> FC ──> Sigmoid
    SMS Text ──> DistilBERT Multilingual ──> Text Emb (768-d) ──┘         |
                                                                    XAI Layer:
                                                                    Grad-CAM + SHAP
```

### Why This Architecture?

| Decision | Justification | Reference |
|----------|--------------|-----------|
| Siamese Network | Learns *what differs* between benign/malicious QR structure; works with limited data | Chopra et al. (2005) |
| MobileNetV2 backbone | 3.4M params vs 25.6M — deployable on mobile | Sandler et al. (2018) |
| Contrastive pretraining | Learns resolution-invariant embeddings; solves cross-dataset transfer | Chen et al. (2020) |
| DistilBERT (not BERT) | 40% smaller, 60% faster, 97% of BERT performance | Sanh et al. (2019) |
| Late Fusion | Visual and semantic features are orthogonal signals | Bountakas et al. (2023) |
| No QR Decoding | Zero-risk scanning — payload never executed | Trad & Chehab (2025) |
| Grad-CAM + SHAP | Full interpretability for both modalities | Selvaraju et al. (2017) |

## Datasets

### Primary: CIC_Trap4Phish_2025 (Canadian Institute for Cybersecurity)

| Component | Samples | Format | Purpose |
|-----------|---------|--------|---------|
| QR Benign | 429,976 | PNG images | Visual branch training |
| QR Malicious | 575,762 | PNG images | Visual branch training |
| HTML Features | 19,997 | CSV (41 features) | Cross-format baseline |
| PDF Features | 19,296 | CSV (41 features) | Cross-format baseline |
| Excel Features | 20,000 | CSV (49 features) | Cross-format baseline |
| Word Features | 20,000 | CSV (43 features) | Cross-format baseline |

**Citation:** Nejati, N. et al. "A Comprehensive Multi-Format Malicious Attachment Dataset for Email Threat Detection." CIC, University of New Brunswick, 2025.

### Secondary: Trad et al. QR Dataset

| Property | Value |
|----------|-------|
| Samples | 9,987 QR codes |
| Format | Binary matrices (69x69), int16 |
| Class Balance | 5,005 benign / 4,982 phishing (50.1% / 49.9%) |
| QR Version | 13 (69 modules per side) |
| Encoding | Binary (0=white, 1=black module) |

**Key findings from our analysis:** See [docs/trad_et_al_analysis.md](docs/trad_et_al_analysis.md)

**Citation:** Trad, F. and Chehab, A. "Detecting Quishing Attacks with Machine Learning Techniques Through QR Code Analysis." arXiv:2505.03451, 2025.

### Tertiary: Peruvian SMS Synthetic Dataset (In Development)

- 100 base messages (50 phishing, 50 legitimate) with Peruvian context
- Data augmentation to expand training set
- Social engineering categories: Urgency, Authority, Reward, Scarcity
- Platforms: Yape, Plin, BCP, Interbank, BBVA

## State of the Art

| Method | Input | Model | Decodes QR? | Multimodal? | Edge? | Best Metric |
|--------|-------|-------|-------------|-------------|-------|-------------|
| Trad & Chehab (2025) | QR pixels | XGBoost | No | No | -- | AUC=0.913 |
| Nejati et al. (2025) | Doc features | RF, XGBoost | Yes | No | -- | Acc>0.95 |
| DB-CBIL (2024) | Visual+Meta | CNN+BiLSTM | N/A | Yes | No | F1>0.96 |
| Alnajim et al. (2023) | URL text | CNN-LSTM | Yes | No | -- | Acc=0.969 |
| Bountakas et al. (2023) | Screenshot+HTML | ResNet+BERT | N/A | Yes | No | Acc=0.972 |
| **Q-Shield (Ours)** | **QR image + SMS** | **MobileNetV2 + DistilBERT** | **No** | **Yes** | **Yes** | **TBD** |

### Research Gaps Addressed

1. **No multimodal quishing detection exists** — prior work uses either vision OR text, never both for QR phishing
2. **Payload decoding is assumed** — most methods require scanning the QR, exposing users to the attack
3. **No edge-deployable solution** — existing multimodal approaches use heavy architectures
4. **No Latin American context** — all existing work assumes English/global phishing patterns
5. **Limited explainability** — most methods are black-box classifiers

## Evaluation Metrics

| Metric | Why It Matters |
|--------|---------------|
| Accuracy | Overall correctness |
| Precision | Of predicted phishing, how many are truly phishing |
| Recall | Of actual phishing, how many are detected |
| F1-Score | Harmonic mean of precision and recall |
| AUC-ROC | Discrimination ability across all thresholds |
| **False Negative Rate** | **Missed attacks = user exposed to phishing (critical)** |

## Repository Structure

```
Multimodal-Quishing-Detection-Framework/
├── README.md
├── docs/
│   ├── problem_statement.md
│   ├── state_of_the_art.md
│   ├── pattern_analysis.md
│   └── trad_et_al_analysis.md
├── notebooks/
│   ├── 01_EDA_CIC_Trap4Phish.ipynb
│   ├── 02_Pattern_Analysis.ipynb
│   └── 03_SOTA_Review.ipynb
├── src/
│   ├── models/
│   ├── data/
│   └── utils/
├── data/
│   ├── raw/
│   └── processed/
├── figures/
└── paper/
```

## Getting Started

### Prerequisites

```bash
pip install torch torchvision transformers
pip install numpy pandas scikit-learn matplotlib seaborn
pip install shap grad-cam Pillow tqdm
```

### Quick Start (Google Colab)

```python
from google.colab import drive
drive.mount('/content/drive')
# Then run: notebooks/01_EDA_CIC_Trap4Phish.ipynb
```

## References

1. Trad, F. and Chehab, A. (2025). "Detecting Quishing Attacks with Machine Learning Techniques Through QR Code Analysis." *arXiv:2505.03451*.
2. Nejati, N. et al. (2025). "A Comprehensive Multi-Format Malicious Attachment Dataset for Email Threat Detection." *CIC, University of New Brunswick*.
3. Sandler, M. et al. (2018). "MobileNetV2: Inverted Residuals and Linear Bottlenecks." *CVPR 2018*.
4. Sanh, V. et al. (2019). "DistilBERT, a distilled version of BERT." *NeurIPS Workshop*.
5. Selvaraju, R. et al. (2017). "Grad-CAM: Visual Explanations from Deep Networks." *ICCV 2017*.

## Authors

- **Nicolas Alejandro Llerena Silva** — UTEC, Lima, Peru (Principal Investigator)
- **Aurea Soriano-Vargas** — UTEC (Advisor)

## License

This project is licensed under the MIT License.

## Acknowledgments

- Canadian Institute for Cybersecurity (CIC) at UNB for the CIC_Trap4Phish_2025 dataset
- Fouad Trad and Ali Chehab for the QuishingDataset and baseline methodology
- IEEE Computer Society, UTEC Chapter
