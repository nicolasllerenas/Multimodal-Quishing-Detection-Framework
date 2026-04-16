# Análisis del Segundo Intento — v2 Regressió (pero aprendimos algo clave)

**Fecha:** 16 de abril de 2026, 15:35  
**Hardware:** NVIDIA A100 40GB  
**Dataset usado:** Trad (7,989 train) + CIC (80,000 train) = **87,989 samples**  
**Tiempo:** ~80 minutos total (Phase 1: 80 min, Phase 2: ~7 min)

---

## 1. Números finales

### Phase 1 — Contrastive Pretraining (25 epochs)

| Epoch | TrLoss | VaLoss | TrAcc | VaAcc | LR |
|-------|--------|--------|-------|-------|-----|
| 1 | 0.1294 | 0.1852 | 50.1% | 50.1% | 0.000200 |
| 10 | 0.1127 | 0.1587 | 59.6% | 57.4% | 0.000231 |
| 15 | 0.1041 | 0.1342 | 65.4% | 59.5% | 0.000129 |
| 20 | 0.0889 | 0.1195 | 72.8% | **66.2%** | 0.000037 |
| 22 (best) | 0.0859 | **0.1191** | 73.9% | **66.0%** | 0.000014 |
| 25 | 0.0834 | 0.1195 | 74.7% | 66.1% | 0.000000 |

**Best val loss:** 0.1191 (epoch 22)

### Phase 2 — Supervised Classification (15 epochs)

| Epoch | TrLoss | VaLoss | AUC | F1 | Prec | Rec |
|-------|--------|--------|-----|-----|------|-----|
| 1 | 0.5067 | 0.4839 | 0.8425 | 0.7605 | 0.8216 | 0.7078 |
| 5 | 0.4503 | 0.4633 | 0.8576 | 0.7718 | 0.8229 | 0.7267 |
| 10 | 0.4210 | 0.4520 | 0.8643 | 0.7739 | 0.8379 | 0.7190 |
| 13 | 0.4122 | 0.4465 | **0.8673** | 0.7773 | 0.8401 | 0.7232 |
| 15 | 0.4101 | 0.4482 | 0.8678 | 0.7789 | 0.8399 | 0.7262 |

**Best AUC:** 0.8678

### Resultados finales (validation, n=21,998)

| Clase | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| Benign | 0.76 | 0.86 | 0.81 | 11,001 |
| Phishing | 0.84 | 0.73 | 0.78 | 10,997 |
| **Weighted avg** | **0.80** | **0.79** | **0.79** | 21,998 |

### Matriz de confusión

|  | Pred: Benign | Pred: Phishing |
|---|---|---|
| **Real: Benign** | 9,479 (TN) | 1,522 (FP) |
| **Real: Phishing** | **3,011 (FN)** | 7,986 (TP) |

**False Negative Rate = 27.4%** ← peor que v1 (21%)

---

## 2. Comparación v1 vs v2

| Dimensión | v1 | v2 | Veredicto |
|-----------|-----|-----|-----------|
| AUC | **0.886** | 0.868 | v1 gana |
| F1 | **0.81** | 0.78 | v1 gana |
| Train-Val gap | 30 pp (malo) | **9 pp (bueno)** | v2 gana |
| Train dataset | 9,987 | **87,989** | v2 gana |
| FN rate | 21% | **27%** | v1 gana |
| Embedding quality (t-SNE) | Borroso | **Clara estructura** | v2 gana |
| Tiempo | ~60 min | ~80 min | v1 gana |

**Conclusión:** v2 es una mala *clasificación* pero un mejor *aprendizaje*.

---

## 3. Diagnóstico profundo — ¿Qué pasó?

### Causa raíz 1: OVER-regularization → UNDERFITTING

v1 memoriza (overfitting). v2 no aprende lo suficiente (underfitting). Con Dropout 0.5 + WD 5e-4 + augmentation agresiva + margin bajo, el modelo es demasiado conservador.

**Evidencia:**
- v1 TrAcc final: 99.1%
- v2 TrAcc final: **74.7%** ← el modelo no pudo memorizar ni con 88K muestras
- Si el modelo no puede aprender el training set, no podrá clasificar bien

### Causa raíz 2: LR decay prematuro

El cosine schedule llevó el LR a 0.000000 en epoch 25. Pero el val loss SEGUÍA BAJANDO:

```
Ep 22: VaLoss 0.1191 (LR 0.000014)
Ep 25: VaLoss 0.1195 (LR 0.000000) ← fin del training pero no convergencia
```

**El modelo se quedó a medio entrenar.** Si hubiéramos dado 10 epochs más con LR más alto, probablemente seguiríamos ganando performance.

### Causa raíz 3: Rotación como augmentation fue un error

Los QR codes tienen **orientación semántica**:
- Finder patterns en esquinas TL, TR, BL (NO BR)
- Timing pattern en filas/columnas específicas
- Alignment pattern en posiciones dependientes de la versión

Al rotar aleatoriamente 180°, confundimos al modelo sobre dónde están los patrones estructurales. Un QR rotado 180° ya no tiene los finder patterns en las esquinas "correctas" que el CNN esperaba.

### Causa raíz 4: Classifier head débil para dataset más grande

v1 clasificaba 1,998 muestras de val. v2 clasifica 21,998 — **11x más**. La head del clasificador (256→64→1) es la misma pero ahora tiene que generalizar sobre distribución más heterogénea (CIC tiene QR de tamaños variables).

---

## 4. Lo bueno que sí logramos (no tirar)

### 4.1 Los embeddings mejoraron dramáticamente

**t-SNE v1:** dos manchas borrosas con mucho overlap  
**t-SNE v2:** phishing forma brazos estructurados a la izquierda, benignos compactos a la derecha

Esto significa que la backbone MobileNetV2 v2 capturó mejor la estructura de los QR. El problema es que el head no está explotando esa información.

### 4.2 El modelo generaliza mejor

Gap Train-Val de 9pp es saludable. Un modelo que aprenda un 5-10pp más en train con este nivel de gap sería ideal.

### 4.3 La validación con CIC ya es significativa

v1 validaba sobre 1,998 muestras de Trad. v2 valida sobre 21,998 (11x) incluyendo variabilidad de CIC. **Los números v2 son mucho más confiables estadísticamente**, aunque sean más bajos.

---

## 5. Plan v3 — Ataque quirúrgico

### Hipótesis principal
El modelo v2 aprendió bien pero no aprendió **lo suficiente**. Necesitamos:
1. Menos regularización (pero no tanto como v1)
2. Más training
3. Mejor head en Phase 2

### Cambios específicos v3

| Hyperparámetro | v1 | v2 | **v3** | Razón |
|----------------|-----|-----|--------|-------|
| Dropout backbone | 0.3 | 0.5 | **0.35** | zona intermedia |
| Weight decay | 1e-4 | 5e-4 | **2e-4** | menos restrictivo |
| Margin contrastive | 2.0 | 1.0 | **1.5** | zona intermedia |
| LR Phase 1 | 1e-4 | 3e-4 | **2e-4** con restart | permite seguir entrenando |
| Epochs Phase 1 | 30 | 25 | **40** con restart scheduler | más tiempo |
| LR schedule | cosine | cosine+warmup | **cosine con WARM RESTART** cada 15 ep | evita plateaus |
| Augmentation | ninguna | H/V flip + rotación | **solo H-flip** | preservar orientación |
| Hard negative mining | No | No | **SÍ** (online, top-50%) | pares difíciles |
| Focal loss Phase 2 | No | No | **SÍ** (γ=2) | penalizar FN |
| Classifier head | 256→64→1 | 256→64→1 | **512→128→32→1** | más capacidad |
| Batch Phase 2 | 32 | 128 | **256** | más estable |
| Frozen backbone start | No | No | **SÍ (5 epochs)** | estabilizar head |

### Expectativa v3

Basado en el análisis:
- Embeddings ya son buenos (t-SNE v2 lo muestra)
- Solo falta extraer mejor la señal en el head
- Focal loss debería reducir FNR del 27% a ~15%
- Con head más grande + frozen start, AUC debería subir a 0.89-0.92

**Target v3:** AUC ≥ 0.91, FNR ≤ 15%

---

## 6. Alternativa: pivotar a multimodal

Si v3 también falla (< 0.89), **detenemos la iteración unimodal y pasamos a multimodal**. El paper gana más con:
- Siamese (0.87-0.89) + DistilBERT SMS + Fusion = AUC esperado 0.92+
- La contribución novel es el FRAMEWORK MULTIMODAL, no batir a Trad en solo-visual

El riesgo de seguir iterando el Siamese solo es perder 1-2 semanas sin avance material.

---

## 7. Decisión recomendada

**Corre v3 HOY (30 min)** → analizar → decidir:
- Si v3 AUC ≥ 0.91: reportar como resultado principal, luego multimodal como extension
- Si v3 AUC 0.87-0.90: reportar y pasar a multimodal (fusionar texto mejorará)
- Si v3 AUC < 0.87: algo raro está pasando, revisar bugs

**No perder más de 1 semana en unimodal.** Multimodal es la tesis central del paper.

---

## 8. Archivos de este run

| Archivo | Dónde |
|---------|-------|
| Screenshots | `Resultados-Second-Attempt/*.png` |
| Análisis | `Resultados-Second-Attempt/analisis_segundo_intento.md` (este archivo) |
| Checkpoints | Drive: `siamese_v2_phase1.pth`, `classifier_v2_phase2.pth` |
| JSON métricas | Drive: `experiment_results_v2.json` |

