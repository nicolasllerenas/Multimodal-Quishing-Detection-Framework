# State of the Art: Quishing and Phishing Detection

## 1. Comprehensive Literature Review

### 1.1 QR Code-Specific Detection

#### Trad & Chehab (2025) — "Detecting Quishing Attacks with ML Through QR Code Analysis"
- **Key contribution**: First framework to detect quishing by analyzing QR structure without payload extraction
- **Method**: Classical ML (XGBoost, LightGBM, RF, LR, Naive Bayes) on 69x69 binary pixel matrices
- **Dataset**: 9,987 QR codes (5,005 benign, 4,982 phishing)
- **Results**: Best AUC = 0.9133 (XGBoost with feature selection)
- **Insight**: Pixel patterns in QR codes correlate with phishing risk due to URL complexity driving module density
- **Limitation**: No deep learning, single modality, fixed QR version, small dataset

#### Nejati et al. (2025) — CIC_Trap4Phish_2025 Dataset
- **Key contribution**: Largest multi-format malicious attachment dataset including 1M+ QR code images
- **Method**: Feature extraction (41-49 features per format) + classical ML
- **Dataset**: 1,005,738 QR images + 80K document features (HTML, PDF, Excel, Word)
- **Results**: Accuracy > 0.95 per format with SHAP-based feature selection
- **Insight**: Cross-format feature comparison reveals format-specific attack patterns
- **Limitation**: Requires payload decoding for QR analysis; no DL; no text semantics

### 1.2 Multimodal Phishing Detection

#### Bountakas et al. (2023) — Multimodal Visual+Text Phishing Detection
- **Key contribution**: Fuses webpage screenshots (ResNet) with HTML content (BERT)
- **Method**: Early fusion of visual and textual features
- **Dataset**: Custom phishing websites with screenshots
- **Results**: Accuracy = 0.972
- **Insight**: Multimodal fusion outperforms unimodal approaches; visual and text signals are complementary
- **Limitation**: Webpage-focused (not QR); heavy architecture (ResNet + BERT); not edge-deployable

#### DB-CBIL Framework (2024) — Hybrid CNN+Transformer
- **Key contribution**: Validates hybrid CNN + sequence model architecture for cybersecurity
- **Method**: CNN for visual features + BiLSTM with attention for sequential features
- **Dataset**: Various cybersecurity datasets
- **Results**: F1 > 0.96
- **Insight**: Hybrid architectures capture both spatial and sequential patterns
- **Limitation**: Not QR-specific; computationally expensive; no edge deployment

### 1.3 URL and Text-Based Phishing Detection

#### Alnajim et al. (2023) — DL for Phishing URL Detection
- **Method**: CNN, LSTM, and CNN-LSTM on URL string features
- **Results**: Accuracy = 0.969
- **Limitation**: Requires URL extraction (decoding); no visual analysis

#### Jain & Gupta (2022) — NLP-Based Phishing Detection
- **Method**: BERT and RoBERTa on email/webpage content
- **Results**: F1 = 0.98
- **Limitation**: Text only; blind to QR images; monolingual (English)

### 1.4 Lightweight/Mobile ML

#### Sandler et al. (2018) — MobileNetV2
- **Key contribution**: Inverted residual blocks with linear bottlenecks
- **Parameters**: 3.4M (vs ResNet-50: 25.6M)
- **Relevance**: Enables visual branch on mobile devices

#### Sanh et al. (2019) — DistilBERT
- **Key contribution**: Knowledge distillation from BERT-base
- **Size**: 40% smaller, 60% faster, retains 97% of BERT's performance
- **Relevance**: Enables NLP branch on mobile/edge devices

## 2. Capability Gap Analysis

### Feature Comparison Matrix

| Capability | Trad (2025) | Nejati (2025) | DB-CBIL (2024) | Alnajim (2023) | Bountakas (2023) | **Q-Shield** |
|-----------|:-----------:|:------------:|:--------------:|:-------------:|:----------------:|:-----------:|
| No QR Decoding | Yes | No | N/A | No | N/A | **Yes** |
| Visual Analysis | Yes | Partial | Yes | No | Yes | **Yes** |
| Text Semantics | No | No | Partial | Yes | Yes | **Yes** |
| Multimodal Fusion | No | No | Yes | No | Yes | **Yes** |
| Edge Deployable | -- | -- | No | -- | No | **Yes** |
| Explainable (XAI) | Partial | Partial | Partial | No | Partial | **Yes** |
| Local Context | No | No | No | No | No | **Yes** |
| Deep Learning | No | No | Yes | Yes | Yes | **Yes** |

### Research Gaps Identified

**Gap 1: No multimodal quishing detection.**
All existing QR-focused methods (Trad, Nejati) are unimodal. Multimodal methods (Bountakas, DB-CBIL) target webpages, not QR codes. Q-Shield is the first to combine QR visual analysis with SMS semantic analysis.

**Gap 2: Payload decoding is a security risk.**
Methods that decode QR codes to analyze URLs (Nejati, Alnajim) expose the analysis system to the malicious redirect chain. Only Trad avoids decoding, but uses only classical ML. Q-Shield extends the no-decoding approach with deep learning.

**Gap 3: No lightweight solution for mobile deployment.**
Bountakas (ResNet + BERT) and DB-CBIL (CNN + BiLSTM) are too heavy for edge devices. Q-Shield specifically chooses MobileNetV2 + DistilBERT for mobile inference viability.

**Gap 4: No localization for Latin American markets.**
Every reviewed paper uses English-language datasets and global phishing patterns. Q-Shield incorporates Peruvian Spanish social engineering with local platform context (Yape, Plin).

**Gap 5: Insufficient explainability.**
Trad uses only basic feature importance. Q-Shield provides dual-modality explainability: Grad-CAM for the visual branch (which QR regions triggered the alert) and SHAP for the semantic branch (which words/phrases were suspicious).

## 3. Positioning Q-Shield in the Literature

```
                         Multimodal
                              |
                   Bountakas  |
                    (2023)    |
                              |  Q-Shield
                              |  (Ours)
        ──────────────────────┼──────────────────── Edge-Deployable
                              |
              DB-CBIL         |
              (2024)          |
                              |
                         Unimodal
                              |
            Trad (2025)       |
            Nejati (2025)     |
            Alnajim (2023)    |
            Jain (2022)       |
                              
                        NOT Edge-Deployable
```

Q-Shield uniquely occupies the **multimodal + edge-deployable** quadrant, which no existing method addresses.

## 4. Key References

```bibtex
@article{trad2025detecting,
  title={Detecting Quishing Attacks with ML Through QR Code Analysis},
  author={Trad, Fouad and Chehab, Ali},
  journal={arXiv:2505.03451},
  year={2025}
}

@dataset{nejati2025malicious,
  author={Nejati, Fatemeh and collaborators},
  title={CIC\_Trap4Phish\_2025},
  institution={CIC, University of New Brunswick},
  year={2025}
}

@inproceedings{sandler2018mobilenetv2,
  title={MobileNetV2: Inverted Residuals and Linear Bottlenecks},
  author={Sandler, Mark and Howard, Andrew and others},
  booktitle={CVPR},
  year={2018}
}

@article{sanh2019distilbert,
  title={DistilBERT, a distilled version of BERT},
  author={Sanh, Victor and Debut, Lysandre and others},
  journal={NeurIPS Workshop},
  year={2019}
}
```
