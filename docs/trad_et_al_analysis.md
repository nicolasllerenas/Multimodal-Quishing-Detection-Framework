# Deep Analysis: Trad et al. (2025) — QR Code Quishing Detection

> **Reference:** Trad, F. and Chehab, A. "Detecting Quishing Attacks with Machine Learning Techniques Through QR Code Analysis." arXiv:2505.03451, 2025.  
> **Repository:** [github.com/fouadtrad/Detecting-Quishing-Attacks](https://github.com/fouadtrad/Detecting-Quishing-Attacks-with-Machine-Learning-Techniques-Through-QR-Code-Analysis)

## 1. Overview

This paper introduces the **first framework** for quishing detection that analyzes QR code structure and pixel patterns **without extracting the embedded content**. This is the closest prior work to Q-Shield and serves as our primary baseline.

### Core Contribution
- Generated a dataset of 9,987 phishing and benign QR codes
- Trained classical ML models (XGBoost, LightGBM, RF, LR, Naive Bayes) on pixel-level features
- Best model (XGBoost) achieves **AUC = 0.9106**, improved to **0.9133** after feature selection
- Demonstrated that QR code *structure alone* correlates with phishing risk

## 2. Dataset Analysis

### 2.1 Structure

| Property | Value |
|----------|-------|
| Total samples | 9,987 |
| Benign | 5,005 (50.1%) |
| Phishing | 4,982 (49.9%) |
| Format | NumPy arrays (int16) |
| Dimensions | 69 x 69 per QR code |
| Pixel values | Binary (0 = white module, 1 = black module) |
| QR Version | 13 (confirmed: 4*13 + 17 = 69 modules) |
| Storage | Two pickle files (~9 MB compressed) |
| License | Creative Commons Attribution 4.0 |

### 2.2 QR Version 13 Capacity

QR Version 13 with a 69x69 module grid can encode:
- Up to **428 numeric characters** (Error correction level L)
- Up to **259 alphanumeric characters** (L)
- Up to **177 bytes** of raw data (L)
- This is sufficient for most URL-based payloads

### 2.3 Important Observation: Fixed Version

All 9,987 QR codes in this dataset are **Version 13 (69x69)**. This means:
- The dataset controls for QR version as a confounding variable
- All differences between classes are due to **data content** affecting the module pattern
- In the real world, malicious QR codes may use different versions — the CIC dataset (which contains variable-size PNGs) addresses this

## 3. Our Statistical Analysis of the Dataset

We performed rigorous statistical analysis beyond what the original paper reported.

### 3.1 Feature-Level Comparison (Welch's t-test)

| Feature | Benign Mean | Phishing Mean | Cohen's d | p-value | Significance |
|---------|------------|---------------|-----------|---------|-------------|
| H-transitions/row | 4611.9 | 4529.1 | **-0.76** | 9.1e-293 | *** (MEDIUM-LARGE) |
| V-transitions/col | 4267.9 | 4367.3 | **+0.68** | 4.2e-233 | *** (MEDIUM) |
| Data region density | 0.4920 | 0.4947 | +0.40 | 2.3e-88 | *** |
| BR quadrant density | 0.4948 | 0.4993 | +0.38 | 9.0e-78 | *** |
| Module density | 0.4927 | 0.4945 | +0.29 | 3.9e-46 | *** |

**Key insight:** Horizontal and vertical transition frequencies are the most discriminative features, with medium-to-large effect sizes. Phishing QR codes show **fewer horizontal transitions** (d=-0.76) but **more vertical transitions** (d=+0.68), suggesting a characteristic encoding pattern for longer URLs.

### 3.2 Spatial Analysis

**Column 44 is the most discriminative spatial position:**
- Benign mean density: 0.5936
- Phishing mean density: 0.5713
- t-statistic: 26.52, p < 10^-149

Column 44 corresponds to the **alignment pattern region** in QR Version 13. The alignment pattern itself is fixed, but the surrounding data modules differ systematically between classes, likely because longer phishing URLs push more data into regions that interact with alignment patterns.

### 3.3 Quadrant Analysis

The bottom-right quadrant (data-heavy region, no finder patterns) shows the clearest class separation:
- QR codes have 3 finder patterns in TL, TR, BL corners (fixed structure)
- BR corner contains only data modules
- Phishing QR codes have **higher density** in the BR quadrant (0.4993 vs 0.4948)
- This is consistent with longer payloads filling more data modules

### 3.4 Average QR Fingerprint

Computing the pixel-wise average of benign and phishing QR codes reveals:
- The **finder patterns** (3 corners) appear identical across classes (expected — these are fixed structures)
- The **data region** (center and BR) shows systematic differences
- Maximum pixel difference: 0.49 (nearly half a module flip between classes on average)
- This "average difference map" visually confirms what statistical tests show numerically

## 4. Methodology Assessment

### 4.1 What Trad et al. Did Well
- **No payload decoding**: The fundamental insight is correct and validated
- **Multiple ML models**: Comprehensive comparison of 6 classical ML approaches
- **Feature selection**: Identified non-informative pixels and removed them (improving AUC from 0.9106 to 0.9133)
- **Balanced dataset**: Near-perfect 50/50 class balance eliminates class imbalance bias

### 4.2 Limitations We Address with Q-Shield

| Limitation in Trad et al. | How Q-Shield Addresses It |
|---------------------------|--------------------------|
| Classical ML only (no deep learning) | MobileNetV2 learns spatial features automatically |
| Single modality (vision only) | Two-stream: vision + text semantics |
| Fixed QR version (69x69 only) | CIC dataset has variable-size QR images |
| No text context analysis | DistilBERT analyzes accompanying messages |
| Basic feature importance only | SHAP + Grad-CAM for full XAI |
| No edge deployment consideration | MobileNet designed for mobile inference |
| No localization | Peruvian SMS dataset for LatAm context |
| Small dataset (9,987) | CIC provides 1M+ QR images |

### 4.3 Results We Should Reproduce

To validate our pipeline, we should reproduce these results from the paper:

| Model | AUC (Reported) | Our Target |
|-------|---------------|------------|
| XGBoost | 0.9133 | >= 0.91 |
| LightGBM | 0.9090 | >= 0.90 |
| Random Forest | 0.8955 | >= 0.89 |
| Logistic Regression | 0.8826 | >= 0.88 |

## 5. Data Reuse Strategy for Q-Shield

### What We Take From This Dataset
1. **Baseline benchmark**: Reproduce Trad's results to validate our feature extractor
2. **Validation set**: Use as an independent test set for models trained on CIC
3. **Feature engineering inspiration**: Transition frequency and quadrant asymmetry as key features
4. **Architecture motivation**: The AUC of 0.91 with classical ML suggests that CNN (which learns spatial features automatically) should improve significantly

### What We Do NOT Take
1. **The model architecture** — we use deep learning, not classical ML
2. **The fixed-version assumption** — our CIC dataset has variable QR sizes
3. **The single-modality approach** — we add text analysis
4. **The lack of explainability** — we add Grad-CAM + SHAP

## 6. Citation

```bibtex
@article{trad2025detecting,
  title={Detecting Quishing Attacks with Machine Learning Techniques Through QR Code Analysis},
  author={Trad, Fouad and Chehab, Ali},
  journal={arXiv preprint arXiv:2505.03451},
  year={2025}
}
```
