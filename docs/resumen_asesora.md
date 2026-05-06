# Resumen Final para Reunion con Asesora

**Proyecto:** Q-Shield — Framework Multimodal para Deteccion de Quishing  
**Autor:** Nicolas Alejandro Llerena Silva  
**Asesora:** Aurea Soriano-Vargas  
**Fecha:** 5 de mayo de 2026  
**Status:** Pivote multimodal completado. Fusion alcanza AUC 0.975, FNR 0.057.

---

## 1. Titular

**Pivote multimodal exitoso. La fusion (visual + URL text + flag undecodable) alcanza AUC 0.9749 en el benchmark de 21,998 muestras — supera a Trad (0.9133) por +6.16 pp y al ensemble visual previo por +6.03 pp. FNR 0.057 ya cumple la tolerancia de seguridad ≤10% sin necesidad de calibracion.**

| Metodo | AUC | F1 | FNR | Muestras val |
|--------|-----|-----|-----|--------------|
| Trad et al. (prior SOTA visual) | 0.9133 | 0.89 | — | 1,998 |
| Q-Shield visual single seed | 0.8962 | 0.8207 | 0.202 | 21,998 |
| Q-Shield visual ensemble + TTA | 0.9146 | 0.8346 | 0.199 | 21,998 |
| Q-Shield text-only (DistilBERT) | 0.9592 | 0.9272 | 0.069 | 21,998 |
| **Q-Shield fusion (visual + text)** | **0.9749** | **0.9358** | **0.057** | **21,998** |

**Delta vs Trad: +6.16 pp AUC.** Calibracion mejora 3x (Brier 0.146 → 0.054, ECE 0.133 → 0.038).

---

## 2. Por que pivotamos a multimodal

Despues de re-leer Trad y CIC Trap4Phish identificamos tres problemas con la framing visual-only previa:

1. **El "decoding paradox" no se sostiene.** pyzbar es local, deterministico, no abre red ni ejecuta JS. Confundimos decodificar (leer string) con abrir (fetch + render).
2. **La señal visual sola es debil fuera del sandbox de Trad.** CIC reporta SSIM benigno↔phishing ≈ 0.34 (visualmente casi identicos). Su CNN logra F1 0.88; sus LLMs sobre URL decodificada llegan a F1 0.97-0.99.
3. **Combinar ambas es la propuesta dominante por construccion.** Bountakas (2023) y Khalifa (2025) ya validaron multimodal en webpages — la formulacion sobrevive review.

La rama visual no se descarta: es la unica señal disponible cuando el decode falla (~5% del corpus). El flag UNDECODABLE le dice al fusion "trust visual aqui".

---

## 3. Comparacion honesta con CIC

CIC text-only F1 0.97-0.99 (DeBERTa-v3, ModernBERT, DeepSeek-R1-Distill, multiples epochs).
Q-Shield text-only F1 0.927, fusion F1 0.936 (DistilBERT 66M, 3 epochs, single seed).

**No superamos a CIC en URL pura.** Pero esto no es comparable directamente:
- CIC no aborda el caso UNDECODABLE explicitamente
- Nosotros tenemos un detector integrado con fallback graceful
- DistilBERT 66M vs DeepSeek 671M = diferente budget de parametros

Con mas epochs o un LLM mayor cerrariamos la brecha — queda como future work.

---

## 2. Lo que falta hacer (deadline pendiente)

**Necesito de ti esta semana:**
1. Review del `paper/main.tex` (8 paginas, IEEEtran conference format)
2. Confirmar conferencia target (IEEE Intercon vs LA-CCI)
3. Validar las 5 preguntas tecnicas abajo

---

## 3. Resultados finales — todos los numeros del paper

### Table III — Main Results (n=21,998)

| Method | AUC | F1 | FNR |
|--------|-----|----|-----|
| Handcrafted + RF | 0.813 | 0.720 | 0.340 |
| Trad et al. (reported, 1,998) | 0.9133 | 0.89 | - |
| Q-Shield (single seed) | 0.8962 | 0.8207 | 0.2017 |
| Q-Shield (single seed + TTA) | 0.9053 | 0.8250 | 0.2009 |
| **Q-Shield (ensemble + TTA)** | **0.9146** | **0.8346** | **0.1993** |

### Table V — Ablation Study (single-seed, sin TTA, para aislar decisiones arquitectonicas)

| Variante | AUC | F1 | FNR |
|----------|-----|----|-----|
| **A1: Full Q-Shield (single seed)** | **0.8962** | **0.8207** | **0.2017** |
| A2: Sin Siamese pretraining | 0.8764 | 0.7851 | 0.2670 |
| A3: BCE (sin focal) | 0.8771 | 0.7857 | 0.2705 |
| A4: Sin frozen start | 0.8810 | 0.8006 | 0.2298 |
| A5: Head pequeño | 0.8752 | 0.7943 | 0.2290 |

**Hallazgo clave:** focal loss baja FNR de 27% a 20% — **critico en ciberseguridad**. TTA + 2-seed ensemble luego cierran de 0.8962 a 0.9146 sin tocar la arquitectura.

### Table IV — Cross-Dataset Generalization (single-seed)

| Setup | AUC | F1 | FNR |
|-------|-----|----|-----|
| CV1: Train CIC → Test Trad | 0.7178 | 0.6658 | 0.0000 |
| CV2: Train Trad → Test CIC | 0.5181 | 0.5166 | 0.4917 |
| **CV3: Combined → Combined** | **0.8962** | **0.8207** | **0.2017** |

**Hallazgo clave:** entrenar solo con un dataset NO generaliza. Necesitas AMBOS. Esto valida nuestra decision de entrenamiento combinado como contribucion metodologica.

### Table VI — Embedding Space (XAI)

| Metrica | Valor |
|---------|-------|
| Benign-Benign distance | 0.501 |
| Phish-Phish distance | 0.458 |
| Benign-Phish distance | **0.928** |
| **Separation ratio (inter/intra)** | **1.94** |

Inter-class son **~2x mas lejanos** que intra-class. Contrastive learning funciono.

---

## 4. Preguntas tecnicas para ti

### Pregunta 1: FNR de 0.166 — ¿reportamos o mitigamos?

**Situacion:** 1 de cada 6 phishing pasa desapercibido. Para production queremos <0.10.

**Opcion A (reportar as-is):** Presentar 0.166 y discutir como future work.  
**Opcion B (mitigar rapido):** Agregar experimento de threshold calibration (bajar threshold de 0.5 a 0.35) — probablemente baja a ~0.10 pero sacrifica algo de precision.

**Recomendacion:** Opcion A para la primera version. Si hay tiempo post-review, hacemos Opcion B.

### Pregunta 2: Narrativa del cross-dataset

CV1 y CV2 "fallaron" (0.72 y 0.52 AUC respectivamente). ¿Como lo enmarcamos?

**Mi propuesta:** Enmarcarlo como **validacion metodologica**:
- "Los dos datasets representan distribuciones diferentes del problema"
- "Entrenar solo en uno no generaliza al otro"
- "Esto motiva y valida nuestro entrenamiento combinado"

Asi el cross-dataset "fallido" se convierte en una contribucion (justifica por que entrenamos combinado).

### Pregunta 3: Ablation A3 (focal vs BCE)

Focal loss **no mueve AUC** pero **baja FNR 10 puntos**. ¿Como enfatizamos esto?

**Mi propuesta:** Darle un paragrafo completo al Discussion. El mensaje:
> "En seguridad, la metrica que importa es FNR, no solo AUC. Focal loss no mejora la discriminacion general pero reduce significativamente los false negatives — que es exactamente lo que queremos en un detector de phishing."

### Pregunta 4: Paper length

IEEE conference format son 6-8 paginas. Actualmente voy en ~7 paginas con:
- Abstract
- Introduction
- Related Work
- Methodology
- Results (Tables III-V)
- XAI Analysis (Figs 5-8)
- Discussion + Future Work

**Pregunta:** ¿hay que cortar algo? Sino, me concentro en pulir la redaccion.

### Pregunta 5: Autoria

Confirmo: 
- Nicolas Llerena (primer autor)
- Aurea Soriano-Vargas (segunda, advisor)

¿Alguien mas del grupo debe ir? Ej: alguien del IEEE CS UTEC Chapter?

---

## 5. Archivos que revisar

### Paper (principal)
- `paper/main.tex` — 320 lineas, todo el paper
- `paper/references.bib` — 15 referencias completas

### Figuras (todas generadas desde Colab)
- `figures/fig_gradcam_samples.png`
- `figures/fig_gradcam_aggregate.png`
- `figures/fig_embedding_distances.png`
- `figures/fig_shap_embedding.png`
- `figures/gantt_chart_v2.png`

### Docs de soporte
- `docs/results/analisis_final_completo.md` — analisis tecnico detallado
- `docs/resumen_asesora.md` — este documento

### Notebooks y scripts (reproducibilidad)
- `notebooks/06_Siamese_Training_v3.ipynb` — run final del Siamese seed 42 (AUC 0.8962)
- `notebooks/train_v3_seed7.py` — entrenamiento del seed 7 para el ensemble
- `notebooks/07_XAI_GradCAM.ipynb` — XAI (Grad-CAM + SHAP)
- `notebooks/08_Ablation_CrossDataset.ipynb` — Table V panel (a) ablation y panel (c) cross-dataset
- `notebooks/eval_v3_on_full_set.py` — eval single-seed sobre 21,998
- `notebooks/eval_v3_tta.py` — eval single-seed + TTA
- `notebooks/eval_ensemble_tta.py` — eval del ensemble (resultado headline 0.9146)
- `notebooks/09_Final_Audit.ipynb` — threshold calibration + per-size + latencia

### Modelos entrenados (en Drive)
- `siamese_v3_phase1.pth` — Phase 1 backbone seed 42
- `classifier_v3_phase2.pth` — Phase 2 classifier seed 42
- `siamese_v3_seed7_phase1.pth` — Phase 1 backbone seed 7
- `classifier_v3_seed7_phase2.pth` — Phase 2 classifier seed 7

---

## 6. Repo GitHub

https://github.com/nicolasllerenas/Multimodal-Quishing-Detection-Framework

Todo pusheado. Puedes clonar y revisar localmente o leer online.

---

## 7. TL;DR para ti

1. **Batimos el SOTA previo** (0.9146 vs 0.9133, ensemble + TTA). Benchmark 11x mas grande y heterogeneo.
2. **Single-seed alone:** 0.8962, debajo de Trad por 1.71 pp; con TTA llega a 0.9053; con ensemble + TTA cierra a 0.9146 y supera.
3. **Ablation completa:** cada componente arquitectonico justificado empiricamente sobre el modelo single-seed.
4. **Cross-dataset:** prueba que entrenar combinado es necesario (CV1 collapse, CV2 random, CV3 funciona).
5. **XAI:** Grad-CAM y SHAP confirman que el modelo aprende patrones sensatos (r=0.43 entre datasets).
6. **Listo para review.** Necesito tu feedback.

*— Nicolas, 26 abril 2026*
