# Pattern Analysis: What Makes a QR Code Malicious?

## 1. Executive Summary

Our analysis of 1M+ QR code images (CIC_Trap4Phish_2025) and 9,987 QR arrays (Trad et al.) reveals that malicious QR codes exhibit **statistically significant structural differences** from benign ones. These differences arise because phishing URLs are typically longer and more complex than legitimate URLs, which forces the QR encoder to use denser module patterns.

**Key finding:** Structural features alone achieve AUC > 0.91 using classical ML (Trad et al.), confirming that a CNN like MobileNetV2 can learn to distinguish malicious QR codes without ever decoding the payload.

## 2. Feature Engineering: 25 Structural Features

We extract features from QR code images organized into 5 groups:

### Group A: Geometric Properties
| Feature | Description |
|---------|-------------|
| `width` | Image width in pixels |
| `height` | Image height in pixels |
| `total_pixels` | Total pixel count (w * h) |
| `aspect_ratio` | Width / height ratio |

### Group B: Module Density
| Feature | Description | Rationale |
|---------|-------------|-----------|
| `black_ratio` | Fraction of black (data) modules | Longer URLs require more black modules |
| `q_tl`, `q_tr`, `q_bl` | Quadrant densities (finder corners) | Should be similar across classes (fixed patterns) |
| `q_br` | Bottom-right quadrant density | **Data-heavy region** — most discriminative |
| `quad_std` | Standard deviation across quadrants | Measures asymmetry |
| `quad_range` | Max - min quadrant density | Measures spread |
| `finder_vs_data` | Average finder corners - data corner | Higher = more data in BR quadrant |

### Group C: Complexity Metrics
| Feature | Description | Rationale |
|---------|-------------|-----------|
| `h_transitions` | Horizontal black/white transitions per row | **Best discriminator** (d = -0.76) |
| `v_transitions` | Vertical transitions per column | Second-best (d = +0.68) |
| `total_transitions` | Normalized total transitions | Overall complexity proxy |
| `entropy` | Shannon entropy of pixel values | Information density |
| `edge_density` | Average gradient magnitude | Visual complexity |

### Group D: Spatial Distribution
| Feature | Description | Rationale |
|---------|-------------|-----------|
| `row_std` | Std of per-row black ratios | Row-level uniformity |
| `col_std` | Std of per-column black ratios | Column-level uniformity |
| `center_density` | Density of center region | Data concentration |
| `border_density` | Density of border region | Fixed pattern + timing |
| `center_border_diff` | Center - border density | Data distribution pattern |

### Group E: Run-Length Texture
| Feature | Description | Rationale |
|---------|-------------|-----------|
| `avg_run_length` | Mean consecutive same-color pixels | Proxy for QR module size |
| `run_length_std` | Std of run lengths | Texture regularity |

## 3. Statistical Findings

### 3.1 Trad et al. Dataset (69x69 Binary Arrays)

| Feature | Benign Mean | Phishing Mean | Cohen's d | p-value |
|---------|------------|---------------|-----------|---------|
| H-transitions/row | 4611.9 | 4529.1 | **-0.76** | 9.1e-293 |
| V-transitions/col | 4267.9 | 4367.3 | **+0.68** | 4.2e-233 |
| Data region density | 0.4920 | 0.4947 | +0.40 | 2.3e-88 |
| BR quadrant density | 0.4948 | 0.4993 | +0.38 | 9.0e-78 |
| Module density | 0.4927 | 0.4945 | +0.29 | 3.9e-46 |

**Interpretation of effect sizes (Cohen's d):**
- |d| >= 0.8: Large effect
- |d| >= 0.5: Medium effect
- |d| >= 0.2: Small effect

H-transitions (d = -0.76) approaches the large-effect threshold. This means phishing QR codes have **fewer horizontal transitions** — consistent with longer URLs producing more concentrated data blocks rather than alternating patterns.

### 3.2 Spatial Hotspot: Column 44

Column 44 in the 69x69 grid (corresponding to the alignment pattern region in QR Version 13) shows the most significant class difference:
- Benign: 0.5936 mean density
- Phishing: 0.5713 mean density
- p-value: 5.68e-149

This is because the alignment pattern is a fixed structure, but the data modules surrounding it change based on payload complexity.

### 3.3 CIC Dataset (Variable-Size PNG Images)

The CIC dataset provides a more realistic scenario with variable QR sizes. Key findings (from sampled analysis):

- **Module density** remains a strong discriminator across QR versions
- **Edge density** (gradient-based) provides additional signal not available in binary arrays
- **Run-length statistics** capture texture differences between QR versions
- **Image dimensions** correlate with QR version, which correlates with payload complexity

## 4. Attack Taxonomy

K-Means clustering (k=3) on malicious QR features reveals three attack subtypes:

### Type A: High-Density Attacks
- **Characteristics**: Dense module patterns, high black ratio
- **Likely payload**: Long obfuscated URLs with tracking parameters
- **Detection**: Straightforward — module density and entropy are high

### Type B: Complex Structure Attacks
- **Characteristics**: High transition frequency, complex spatial patterns
- **Likely payload**: URLs with multiple redirect chains
- **Detection**: Moderate — transition features are discriminative

### Type C: Obfuscated Attacks
- **Characteristics**: Subtle visual differences, URL shorteners
- **Likely payload**: Short URLs that redirect to malicious content
- **Detection**: Hardest — structural differences are minimal, highlighting the need for the semantic branch (SMS text analysis) to complement visual detection

## 5. Cross-Dataset Validation

We verified that patterns discovered in CIC generalize to Trad et al.:

| Feature | Direction in CIC | Direction in Trad | Consistent? |
|---------|-----------------|------------------|-------------|
| Module density | Higher in malicious | Higher in malicious | Yes |
| H-transitions | Lower in malicious | Lower in malicious | Yes |
| V-transitions | Higher in malicious | Higher in malicious | Yes |
| Data region density | Higher in malicious | Higher in malicious | Yes |

**A Random Forest model trained on CIC and tested on Trad maintains discriminative power**, confirming that structural QR patterns are generalizable.

## 6. URL Metadata Patterns

Analysis of URL metadata from the CIC dataset (429K benign + 575K malicious URLs):

| URL Feature | Benign Mean | Malicious Mean | Significant? |
|-------------|------------|----------------|-------------|
| URL length | varies | **longer** | Yes |
| Number of dots | lower | higher | Yes |
| Has IP address | rare | more common | Yes |
| Suspicious TLD | rare | more common | Yes |
| Digit ratio | lower | higher | Yes |
| URL entropy | lower | higher | Yes |

**These URL patterns directly explain the QR structural differences**: longer, more complex URLs require more QR modules, producing denser, more complex patterns that our visual branch can detect.

## 7. Implications for Q-Shield

1. **MobileNetV2 is justified**: The spatial patterns (quadrant asymmetry, transition gradients) are exactly what CNNs excel at learning
2. **Late fusion is appropriate**: Visual features (structural complexity) and text features (social engineering cues) capture orthogonal signals
3. **Type C attacks need the semantic branch**: When QR structure alone is insufficient (URL shorteners), the SMS text provides the complementary signal
4. **25 handcrafted features serve as interpretable baseline**, while the CNN can discover additional non-obvious spatial patterns
