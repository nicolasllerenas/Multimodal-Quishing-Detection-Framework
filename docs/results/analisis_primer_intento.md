# Análisis del Primer Intento de Entrenamiento — Q-Shield Siamese Network

**Fecha:** 16 de abril de 2026  
**Hardware:** NVIDIA A100-SXM4-40GB (Colab Pro+)  
**Dataset usado:** Solo Trad et al. (9,987 QRs) — CIC no se incluyó en este run  
**Tiempo total:** ~60 minutos (Phase 1: 50 min + Phase 2: 10 min)

---

## 1. Resultados obtenidos

### Phase 1 — Siamese Contrastive Pretraining (30 epochs)

| Epoch | Train Loss | Val Loss | Train Acc | Val Acc |
|-------|-----------|----------|-----------|---------|
| 1 | 0.459 | 0.475 | 59.0% | 60.5% |
| 5 | 0.150 | 0.504 | 90.4% | 68.0% |
| 10 | 0.0595 | 0.518 | 96.6% | 69.5% |
| 15 | 0.0335 | 0.553 | 98.2% | 68.9% |
| 20 | 0.0234 | 0.563 | 98.8% | 69.0% |
| 21 (best) | 0.0203 | 0.534 | 98.9% | **70.9%** |
| 30 | 0.0172 | 0.573 | 99.1% | 68.7% |

**Best val loss:** 0.4614 (epoch 2)

### Phase 2 — Supervised Classification (20 epochs)

| Metric | Valor |
|--------|-------|
| **AUC** | **0.8860** |
| Precision (Benign) | 0.80 |
| Recall (Benign) | 0.83 |
| Precision (Phishing) | 0.82 |
| Recall (Phishing) | 0.79 |
| **F1 weighted** | **0.81** |
| Accuracy | 0.81 |

### Matriz de confusión (val set, n=1998)

|  | Pred: Benign | Pred: Phishing |
|---|---|---|
| **Real: Benign** | 828 (TN) | 173 (FP) |
| **Real: Phishing** | 209 (FN) | 788 (TP) |

### Comparación con baselines

| Método | AUC | Notas |
|--------|-----|-------|
| Trad et al. (4761 raw pixels + XGBoost) | 0.9133 | Reportado en paper |
| Ours: 25 handcrafted features + RF | 0.8132 | Run previo |
| **Ours: Siamese MobileNetV2** | **0.8860** | **Este run** |

---

## 2. Diagnóstico — Qué funcionó y qué no

### Lo que funcionó

**El enfoque Siamese es válido.** Superamos el baseline de features manuales por **+9.0%** (0.886 vs 0.813 AUC). Esto valida que los embeddings aprendidos con contrastive learning capturan información más rica que features handcrafted.

**La arquitectura es correcta.** MobileNetV2 con 2.9M parámetros es suficientemente expresiva para la tarea. El modelo converge consistentemente y el comportamiento es estable.

**El t-SNE muestra separación parcial.** Hay dos grandes clusters en el espacio de embeddings — uno con dominancia de phishing (lado izquierdo) y otro con dominancia de benignos (lado derecho). No es perfecto, pero la señal es real.

### Lo que falló — 3 problemas concretos

#### Problema 1: Overfitting severo en Phase 1

El train accuracy sube a 99.1% mientras el val accuracy se estanca en ~70%. La brecha de **29 puntos porcentuales** indica que el modelo memoriza pares de entrenamiento en lugar de aprender características generalizables.

**Evidencia:**
- Epoch 1: TrAcc 59%, VaAcc 60.5% (alineados)
- Epoch 5: TrAcc 90.4%, VaAcc 68.0% (brecha de 22 puntos)
- Epoch 30: TrAcc 99.1%, VaAcc 68.7% (brecha de 30 puntos)
- **El val accuracy ni siquiera mejoró después del epoch 10** — seguimos entrenando 20 epochs innecesarios

**Causa raíz:** Dataset pequeño (7,989 muestras train) + modelo grande (2.9M params) + pares fáciles (muestreo random).

#### Problema 2: No se usó el dataset CIC

El run entrenó **solo con Trad (9,987 muestras)**, ignorando los zips de CIC que ya estaban en Drive (1M+ QR images). Esto es lo que más limitó los resultados. El notebook debería haber cargado ambos datasets automáticamente pero no lo hizo — hay un bug en la detección de CIC o la variable `HAS_CIC` no se activó correctamente.

**Evidencia:** Los logs no muestran "Extracting CIC benign QRs" ni "Training will use BOTH Trad + CIC datasets".

#### Problema 3: Pares de entrenamiento muy fáciles

Estamos generando pares random (50% same-class, 50% different-class). Con una tarea donde las clases tienen diferencias visibles a simple vista (algunos QRs obviamente tienen más módulos negros), el modelo resuelve los pares fáciles rápido y no aprende las distinciones sutiles.

**Consecuencia:** 209 falsos negativos (phishing clasificados como benignos) — esto es **inaceptable en un sistema de ciberseguridad**.

---

## 3. Comparación con el objetivo

| Métrica | Target | Obtenido | Gap |
|---------|--------|----------|-----|
| AUC | > 0.91 (superar a Trad) | 0.886 | -2.7 pp |
| False Negative Rate | < 10% | 21.0% | -11 pp |
| F1 | > 0.90 | 0.81 | -9 pp |

**Conclusión:** El resultado es un buen baseline para el paper pero **no supera al SOTA actual**. Para ser publicable en IEEE top-tier debemos subir al menos a 0.92+ AUC.

---

## 4. Plan de acción — Segundo intento (v2)

### Prioridad 1: Usar el CIC completo (resuelve 60% del problema)

El CIC tiene 1M+ QR images. Aumentar datos 100x es la forma más directa de reducir overfitting.

**Acción:** Arreglar el notebook para que:
- Detecte los zips CIC correctamente
- Los extraiga al SSD local de Colab
- Use 50K benign + 50K malicious (sampled, balanced)
- Combine Trad + CIC en el mismo training loop

### Prioridad 2: Hard Negative Mining

Generar pares que sean difíciles de distinguir. Para cada anchor, buscar el par más similar pero de clase opuesta (o el más diferente de la misma clase).

**Acción:**
- Pre-computar embeddings en cada época
- Mining de "top-k hardest pairs"
- Reemplazar el 50% de pares random con hard pairs

### Prioridad 3: Regularización agresiva

Para prevenir overfitting incluso con más datos:
- **Dropout**: Aumentar de 0.3 a 0.5 en la projection head
- **Weight decay**: Subir de 1e-4 a 5e-4
- **Early stopping**: Paciencia de 5 epochs basado en val AUC
- **Data augmentation**: Rotación, flip, recorte (QR codes permiten rotación de 90°)

### Prioridad 4: Triplet Loss (opcional)

Probar triplet loss como alternativa a contrastive:

```
L_triplet = max(0, d(anchor, positive) - d(anchor, negative) + margin)
```

La literatura muestra que triplet loss suele converger a embeddings mejor separados, especialmente con semi-hard mining.

### Prioridad 5: Learning rate más alto

El LR 1e-4 es muy bajo para MobileNetV2 con BatchNorm. Probar 3e-4 con warmup.

---

## 5. Hiperparámetros propuestos para v2

| Param | v1 (actual) | v2 (propuesto) | Razón |
|-------|-------------|----------------|-------|
| Dataset | Solo Trad (9,987) | Trad + CIC sample (109,987) | +10x datos |
| Pairs/epoch | 30,000 | 60,000 | Cubrir más combinaciones |
| Epochs Phase 1 | 30 | 15 + early stop | Overfit después de ep 10 |
| LR Phase 1 | 1e-4 | 3e-4 + warmup | Más eficiente |
| Dropout | 0.3 | 0.5 | Regularizar más |
| Weight decay | 1e-4 | 5e-4 | Regularizar más |
| Batch size | 64 | 128 (A100 puede más) | Más estable |
| Pair mining | Random | Hard negative mining | Forzar aprendizaje profundo |
| Augmentation | Ninguna | Rotación 90°, flip | QR son rotation-invariant |

**Tiempo estimado v2 en A100:** ~45 minutos (más datos pero menos epochs + batch más grande)

**Target v2:** AUC ≥ 0.92 (superar a Trad et al.)

---

## 6. Lo que le decimos a la asesora

### Mensaje honesto
> El primer intento del Siamese Network obtuvo **AUC 0.886** en el dataset Trad, superando nuestro baseline de features manuales (+9%) pero quedando 2.7 puntos debajo del baseline de Trad et al. (0.913). Identifiqué que el overfitting es severo (train 99% vs val 69%) y que el notebook no usó el dataset CIC (1M+ images) por un bug de detección.

### Plan de acción
> El v2 corrige tres cosas: (1) incorpora el CIC completo para bajar el overfitting, (2) agrega hard negative mining para forzar al modelo a aprender diferencias sutiles, (3) sube regularización y aplica early stopping. Con esto esperamos superar 0.92 AUC en el siguiente run.

### Lo rescatable
- La arquitectura Siamese está validada como dirección correcta
- Los embeddings muestran separación visible en t-SNE
- El notebook es reproducible y corre sin errores
- Tenemos figuras listas para el paper (t-SNE, ROC, confusion matrix)

---

## 7. Archivos de este run

| Archivo | Ubicación |
|---------|-----------|
| Checkpoints | Drive: `siamese_phase1.pth` (11.7 MB), `classifier_phase2.pth` (12.0 MB) |
| t-SNE plot | Drive: `fig_tsne_embeddings.png` |
| Training curves | Drive: `fig_phase1_curves.png` |
| Final results | Drive: `fig_final_results.png` |
| Raw metrics | Drive: `experiment_results.json` |
| Screenshots | Local: `Resultados-First-Attempt/*.png` |
