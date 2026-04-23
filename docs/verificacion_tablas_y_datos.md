# Verificacion de Tablas, Figuras, y Datos del Paper

**Fecha:** Abril 2026  
**Proposito:** Confirmar que todos los numeros en las tablas y figuras son correctos, trazables a los experimentos ejecutados, y que los datos de baselines son fieles a las fuentes originales.

---

## 1. Tablas del paper — Checklist

### Table I — SOTA Comparison

| Referencia | Fuente exacta | ¿Correcto? |
|-----------|---------------|------------|
| Trad & Chehab 2025 | arXiv:2505.03451, Table 3 (XGBoost on 29x29 pixel features) | Correct — reported AUC 0.9133 |
| Nejati et al. 2026 | CIC UNB Tech Report, Table 5 (RF on combined features) | OK — Acc>0.95 |
| Wahid et al. 2025 (QRIS) | IEEE ICIT 2025 proceedings | OK — F1 ~0.85 reportado |
| Wahsheh & Al-Zahrani 2021 | IEEE Access vol.9 | OK — URL-based |
| Sharevski et al. 2022 | EuroUSEC 2022 | OK — User study, no AUC |
| Khalifa & Shah 2025 | Comp & Security vol.148 | OK — MultiPhishNet |
| Weinz et al. 2025 | J. Cybersecurity vol.11(1) | OK — organizational study |
| Geisler & Pöhn 2024 | ACM CCS Workshops 2024 | OK — field study |
| Bekavac & Garbin 2024 | Info & Computer Security vol.32(4) | OK — design intervention |
| Wahid et al. 2026 (ALFA) | IEEE TrustCom 2026 | OK — robustness focus |

**Observaciones:**
- Los numeros que reportamos de Trad (0.9133) son los que ellos reportan en su Table 3 con XGBoost sobre 29x29 raw pixels
- Nejati et al. reportan mas del 0.95 pero eso es con URL features (no solo QR image), por lo que es una comparacion parcial
- Wahid 2025 y Wahid 2026 son del mismo grupo — citamos ambos correctamente

### Table III — Main Results (Our Implementation)

| Row | Metodo | AUC | Prec | Recall | F1 | FNR | Fuente del numero |
|-----|--------|-----|------|--------|-----|-----|---|
| 1 | RF + 25 features | 0.813 | 0.794 | 0.660 | 0.720 | 0.340 | notebook 02, run propio |
| 2 | XGBoost + 25 feat | 0.810 | 0.785 | 0.664 | 0.720 | 0.336 | notebook 02 |
| 3 | LightGBM + 25 feat | 0.808 | 0.771 | 0.670 | 0.717 | 0.330 | notebook 02 |
| 4 | Trad reported (1,998 eval samples) | 0.913 | — | — | 0.890 | — | arXiv 2505.03451 Table 3 |
| 5 | **Q-Shield Siamese** | **0.925** | **0.844** | **0.834** | **0.858** | **0.166** | notebook 07 + 08 A1 |

**TODOS los numeros de nuestra fila (5) vienen de ejecuciones reales reproducibles.**

### Table IV — Cross-Dataset

| Setup | AUC | Recall | F1 | FNR | Fuente |
|-------|-----|--------|-----|-----|--------|
| CV1: Train CIC → Test Trad | 0.7178 | 1.000 | 0.666 | 0.000 | notebook 08 CV1 |
| CV2: Train Trad → Test CIC | 0.5181 | 0.508 | 0.517 | 0.492 | notebook 08 CV2 |
| CV3: Combined (ours) | **0.9254** | **0.834** | **0.858** | **0.166** | notebook 08 CV3 / A1 |

**Observacion:** CV1 recall=1.000 es consecuencia matematica de FNR=0 (classifier predice todo positivo).

### Table V — Ablation

| Variant | AUC | Recall | F1 | FNR | Fuente |
|---------|-----|--------|-----|-----|--------|
| A1: Full Q-Shield | 0.9254 | 0.834 | 0.858 | 0.166 | notebook 08 A1 |
| A2: No Siamese pretrain | 0.8764 | 0.733 | 0.785 | 0.267 | notebook 08 A2 |
| A3: BCE (no focal) | 0.8771 | 0.729 | 0.786 | 0.271 | notebook 08 A3 |
| A4: No frozen start | 0.8810 | 0.770 | 0.801 | 0.230 | notebook 08 A4 |
| A5: Small head | 0.8752 | 0.771 | 0.794 | 0.229 | notebook 08 A5 |

### Table VI — Embedding Distance Statistics

| Pair type | Distance | Fuente |
|-----------|----------|--------|
| Benign-Benign | 0.501 | notebook 07 embedding analysis |
| Phish-Phish | 0.458 | notebook 07 |
| Benign-Phish | 0.928 | notebook 07 |
| Separation ratio | 1.94 | computado: 0.928 / ((0.501+0.458)/2) |

### Table VII — Gaps Benchmark (Our Value-Adds)

Todos los Yes/No son verificables por inspeccion directa de los papers de referencia. Numeros (0.913, 0.95, 0.925, 2K, 22K) son consistentes con los reportados.

### Table VIII — Threshold Calibration (Pendiente — se llena con notebook 09)

Cuando corras notebook 09, agregamos:
- Default (0.5): precision, recall, FNR, F1
- Max F1 threshold
- FNR ≤ 0.10 threshold
- FNR ≤ 0.05 threshold

---

## 2. Figuras del paper — Checklist

| Fig | Archivo | Contenido | Status |
|-----|---------|-----------|--------|
| 1 | `fig_pipeline_architecture.png` | Pipeline paso a paso (8 steps) | **Nueva, generada hoy** |
| 5 | `fig5_gradcam_samples.png` | Grad-CAM en 6 benign + 6 phishing | OK, generado notebook 07 |
| 6 | `fig6_gradcam_aggregate.png` | Mapas de atencion agregada por clase | OK, notebook 07 |
| 7 | `fig7_embedding_distances.png` | Histograma de distancias | OK, notebook 07 |
| 8 | `fig8_shap_embedding.png` | SHAP top-20 dims | OK, notebook 07 |

Pendiente de agregar cuando notebook 09 corra:
- `fig_gradcam_per_dataset.png` — validacion del patron izq/der por dataset
- `fig_threshold_calibration.png` — curvas FNR/FPR vs threshold

---

## 3. Formulas del paper — Checklist

### Equation 1 — Problem formulation
$f_\theta(x) = \sigma(g_\phi \circ h_\psi(x))$  
**OK.** Composicion estandar.

### Equation 2 — Contrastive Loss
$\mathcal{L}_{con}(e_1, e_2, y) = (1-y)\frac{d^2}{2} + y\frac{\max(0, m-d)^2}{2}$  
**OK.** Forma canonica de Chopra et al. 2005.

### Equation 3 — Focal Loss
$\mathcal{L}_{focal}(p, y) = -\alpha_y (1-p_y)^\gamma \log p_y$  
**OK.** Forma canonica de Lin et al. 2017 (α, γ params correctos).

### Grad-CAM (conceptual, no numerada)
Referencia a Selvaraju et al. 2017. No hay formula explicita en el paper (solo conceptual). Si quieres agregarla:
$L^c_{Grad-CAM} = \text{ReLU}\left(\sum_k \alpha^c_k A^k\right)$  
donde $\alpha^c_k = \frac{1}{Z} \sum_i \sum_j \frac{\partial y^c}{\partial A^k_{ij}}$

### SHAP (conceptual)
Referencia a Lundberg & Lee 2017.

---

## 4. Datos de baselines — Trazabilidad

### Trad et al. 2025 (arXiv:2505.03451)

Cita del abstract del paper original:
> "Our best model, XGBoost, achieves an AUC of 0.9106 with the full feature set and 0.9133 after removing non-informative pixels."

**Nosotros reportamos 0.913** — redondeado a 3 decimales. **Correcto.**

### CIC Trap4Phish 2025

Reporta multiple metodos sobre URL features y QR image features. Accuracies >0.95 son sobre URL features (diferentes a nuestras). Lo mencionamos correctamente como "URL-derived features, not QR images directly. Not directly comparable" en Table VII.

### Nuestros baselines handcrafted (0.813 AUC)

Estos son REPRODUCIBLES con notebook 02. Los numeros fueron capturados del output del notebook.

---

## 5. Consistency checks

**Numeros clave que deben aparecer identicos en todo el paper:**

| Numero | ¿Donde? | Consistente? |
|--------|---------|-------------|
| 0.925 | Abstract, Table III, Table V, Section IV | Yes |
| 0.8576 o 0.858 | Abstract, Table III, Table V, Section IV | Depende del redondeo — validar |
| 0.1662 o 0.166 | Abstract, Table III, Table V, Section IV | Depende del redondeo |
| 21,998 | Abstract, Section IV, Tables | Yes |
| 2.9M params | Abstract, Section IV, Section V | Yes |
| 1.94 separation ratio | Abstract, Section V XAI | Yes |
| m=1.5 margin | Methodology eq (2), ablation | Yes |

**Recomendacion:** consolidar a 3 decimales (ej: 0.925, 0.858, 0.166) en todo el paper. Yo ya lo hice en las ultimas ediciones.

---

## 6. Referencias bibliograficas — Checklist

Actualmente 18 entradas:
1. `mitnick2002artdeception` — NEW (book, social engineering foundations)
2. `hadnagy2018socialengineering` — NEW (book, SE framework)
3. `verizon2024dbir` — NEW (industry report)
4. `ibm2024cost` — NEW (industry report)
5. `elharrouss2024lossfunctions` — NEW (loss function survey)
6. `ganin2015dann` — (DANN for domain adaptation)
7. `lin2017focal` — Focal Loss
8. `selvaraju2017grad` — Grad-CAM
9. `chopra2005learning` — Contrastive Loss
10. `trad2025detecting` — Trad quishing
11. `sharevski2022phishing` — User study
12. `wahsheh2021secure` — URL-based
13. `geisler2024hooked` — Field study
14. `wahid2025qris` — Structural features
15. `khalifa2025multiphishnet` — MultiPhishNet
16. `weinz2025impact` — Organizational
17. `nejati2026cic` — CIC dataset
18. `wahid2026alfa` — Robustness
19. `bekavac2024qr` — Design
20. `lundberg2017unified` — SHAP
21. `sandler2018mobilenetv2` — MobileNetV2
22. `sanh2019distilbert` — DistilBERT (mentioned only in future work)

**22 referencias total.** Adecuado para conference paper IEEE.

---

## 7. Resumen de cambios aplicados hoy

1. **Pipeline figure** (Fig 1) generada y agregada al paper
2. **Parrafo de ingenieria social** agregado al Introduction (con citas Mitnick, Hadnagy, Verizon, IBM)
3. **Provenance-aware detection** agregado como future work
4. **Numeros consistentes** (0.8962 viejo → 0.925 actual en todo el paper)
5. **Verificacion** de todos los datos de baselines

---

## 8. Lo que queda por ejecutar (notebook 09 si da tiempo)

1. Per-dataset Grad-CAM validation (confirma patron izq/der no es artifact)
2. Threshold calibration → llena Table VIII
3. Inference time benchmarks → numeros concretos de latency
4. Per-size analysis en CIC

**Si corres notebook 09 antes del envio, el paper queda 100%. Si no, esta 95% con lo actual.**
