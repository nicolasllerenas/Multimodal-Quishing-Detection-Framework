# Analisis Critico — Puntos para discutir con la asesora

**Para:** Reunion Nicolas + Aurea Soriano-Vargas  
**Fecha:** Abril 2026  
**Intencion:** Ser riguroso y honesto antes del envio. Anticipar criticas de reviewers.

> **Regla que estoy aplicando aqui:** prefiero identificar yo los problemas (y proponer como defenderlos) antes que un reviewer los descubra y lo use para rechazar el paper.

---

## 1. ¿Hay sobreentrenamiento? ANALISIS RIGUROSO

### Evidencia directa

Revisando los logs de entrenamiento (notebook 07/08):

**Phase 1 (Siamese contrastive):**
- v1: TrAcc 99.1% / VaAcc 68.7% → **overfitting severo (30pp gap)**
- v2: TrAcc 74.7% / VaAcc 66.1% → **underfitting (gap 9pp pero ambos bajos)**
- v3: TrAcc 91.8% / VaAcc 71.4% → **gap ~20pp, moderate overfitting**

**Phase 2 (classification) v3 run:**
```
Ep  1: TrLoss 0.0711 / VaLoss 0.0691 / AUC 0.8150   — aligned
Ep  5: TrLoss 0.0682 / VaLoss 0.0669 / AUC 0.8221   — aligned
Ep  8: TrLoss 0.0434 / VaLoss 0.0531 / AUC 0.8962  * BEST
Ep 12: TrLoss 0.0303 / VaLoss 0.0622 / AUC 0.8940
Ep 15: TrLoss 0.0201 / VaLoss 0.0796 / AUC 0.8911
Ep 20: TrLoss 0.0112 / VaLoss 0.1032 / AUC 0.8850   — CLARA DIVERGENCIA
```

**Diagnostico honesto: SI HAY OVERFITTING en Phase 2.**

Despues del epoch 8, train loss SIGUE bajando (0.043 → 0.011) pero val loss SUBE (0.053 → 0.103). Esto es textbook overfitting. Lo mitigamos con early stopping (guardamos el checkpoint de epoch 8), pero la **capacidad del modelo excede lo que el dataset puede soportar sin regularizar mas**.

### Que mitigamos y que no

**Lo que tenemos:**
- Dropout 0.35 (v1 tenia 0.3 → overfit; v2 tuvo 0.5 → underfit; 0.35 intermedio)
- Weight decay 2e-4
- H-flip augmentation
- Early stopping en best val AUC

**Lo que NO tenemos:**
- MixUp / CutMix augmentation
- Label smoothing
- Stochastic depth
- Ensemble (solo reportamos 1 modelo)

### ¿Es esto un problema para el paper?

**Respuesta honesta:** No es critico si reportamos solo la metrica del best checkpoint (que es lo que hicimos). Un reviewer podria preguntar "¿por que 8 epochs nada mas? ¿estaba estable el training?"

**Nuestra defensa:**
> "We use early stopping (patience=3 on val AUC) and report metrics at the best checkpoint. The validation loss curve exhibits typical fine-tuning behavior: rapid convergence in the frozen-backbone phase (epochs 1-5) followed by gradual overfitting once the backbone unfreezes. Our reported results correspond to the peak generalization point."

**Lo que podriamos hacer como mitigacion adicional:**
- Reportar **media + std** sobre 3 seeds diferentes (mas robusto, toma 3x el tiempo)
- Agregar ensemble de 3 modelos (baja FNR, sube 0.5-1pp AUC)

**Recomendacion para la asesora:** decidir si vale la pena gastar 1 dia en ensemble o si preferimos reportar single-model + early stopping y defenderlo como estandar.

---

## 2. ¿El cross-dataset fue bien? REVISION CRITICA

### Resultados

| Setup | AUC | F1 | FNR |
|-------|-----|-----|-----|
| CV1: Train CIC → Test Trad | 0.7178 | 0.6658 | **0.0000** |
| CV2: Train Trad → Test CIC | 0.5181 | 0.5166 | 0.4917 |
| CV3: Combined → Combined | 0.9254 | 0.8576 | 0.1662 |

### CV1: ¿AUC 0.72 es un buen numero o un red flag?

**Interpretacion superficial:** "AUC 0.72 es mejor que random, el modelo generaliza algo."

**Interpretacion rigurosa:** FNR = 0.0000 significa que el modelo clasifica TODO (o casi todo) como phishing cuando ve Trad. Esto implica:
- Recall = 100% (detecta todos los phishing) ← parece bueno
- Pero Precision ~ 50% (marca muchos benignos como phishing) ← malo
- F1 = 0.666 es mediocre
- Lo que AUC 0.72 esta capturando es que el ORDENAMIENTO de probabilidades es medianamente informativo, pero el THRESHOLDING esta roto

**En deployment real esto seria inusable:** imagina una app que marca el 50% de los QRs legitimos como "posible phishing". Los usuarios la desactivan.

**Un reviewer agresivo diria:** "este resultado muestra que el modelo no generaliza cross-dataset; solo aprende caracteristicas dataset-specific."

### CV2: AUC 0.52 es esencialmente random

**Numero duro:** 0.52 esta a solo 2 puntos de aleatorio (0.50). Esto es **catastrofico**.

**Causa:** el modelo entrenado solo en matrices binarias 69x69 no puede procesar PNG de resolucion variable. Las estadisticas visuales son completamente distintas.

**Defensa posible:** "demuestra que el dominio de entrada cambia sustancialmente entre datasets".

**Defensa real que deberiamos articular:** nuestro modelo NO aprendio features genericos de phishing — aprendio features especificos del formato de imagen de cada dataset. Cuando ve un formato distinto, falla.

### ¿Entonces fue buena idea hacer cross-dataset?

**Argumento a favor (lo que ponemos en el paper):**
- "Combined training es una contribucion metodologica"
- "Demuestra que los datasets son complementarios"
- "Justifica usar ambos en produccion"

**Argumento en contra (honesto):**
- Revela que nuestro modelo puede estar haciendo "dataset identification" en vez de "phishing detection"
- Grad-CAM muestra atencion en la IZQUIERDA para benign y CENTRO-DERECHA para phishing — ¿es esto realmente un patron de phishing, o el modelo aprendio "los QRs de Trad (mas pequeños al hacer upsample) generan atencion en X region, y los de CIC en Y region"?

### ¿Esto es un problema para el paper?

**Honestamente: medio.** Si lo enmarcamos como "combined training es necesario", es aceptable. Si un reviewer lo ve como "el modelo no generaliza", puede rechazar.

**Propuesta de enmarcado mas solido:**

Cambiar la narrativa de:
> "Cross-dataset validation shows that combined training is necessary"

A:
> "Cross-dataset validation reveals that Trad (69×69 binary) and CIC (variable PNG) represent fundamentally different input distributions. Models trained on one do not transfer to the other. **This is not a failure of generalization, but a characterization of domain shift.** Our combined training approach is therefore positioned as domain-invariant learning: the model sees both distributions during training and produces a representation that handles both simultaneously."

**Esto es mas defendible porque:**
- Reconoce la limitacion
- La contextualiza como "domain shift, not generalization failure"
- Conecta con literatura de domain adaptation

---

## 3. Problemas que un reviewer detectara (y como atenderlos)

### Problema 3.1: FNR de 16.6% es alta para un sistema de seguridad

**Critica esperada:** "1 de cada 6 phishing se escapa — inaceptable para deployment."

**Mitigacion tecnica posible (1-2 dias de trabajo):**
1. **Threshold calibration**: bajar threshold de 0.5 a 0.35 → probablemente FNR baja a ~0.10 pero precision cae ~5pp
2. **Ensemble de 3 modelos** con seeds diferentes → tipicamente bajas FNR 3-5pp
3. **Temperature scaling** sobre el logit → calibra probabilidades sin afectar AUC

**Que reportar:** "We report the uncalibrated model at threshold 0.5 for comparability. Operational deployment can adjust this trade-off depending on tolerance for false positives."

**Recomendacion para la asesora:** decidir si vale la pena hacer threshold calibration para poner una Table VII que muestre "FNR vs precision" trade-off. Añade profundidad al paper.

### Problema 3.2: Data leakage entre Trad y CIC?

**Riesgo:** si los phishing URLs en Trad provienen de PhishTank (mismo source que CIC potencialmente), pueden haber URLs duplicados entre train y test.

**Verificamos esto?** **NO.** Esta es una debilidad seria si nos preguntan.

**Que deberiamos hacer:**
```python
# Pseudocódigo
urls_trad = extract_urls_from_trad()  # si los pickles incluyen URLs
urls_cic = read_cic_url_csv()
overlap = set(urls_trad).intersection(set(urls_cic))
print(f'URL overlap: {len(overlap)} / {len(urls_trad)}')
```

**Si hay overlap > 1%**: podemos tener inflacion artificial de metricas. Hay que deduplicar.

**Defensa si no podemos verificar:** "We assume independence between the two corpora based on their separate generation pipelines (Trad synthesized from QR library, CIC generated from independently collected PhishTank URLs)."

**Recomendacion:** hacer este check ANTES del envio del paper. Son 10 minutos de codigo y nos protege.

### Problema 3.3: Trad es solo QR Version 13

Trad: TODOS los samples son Version 13 (69x69). No hay Version 10, 15, 20, 40, etc.

**Critica esperada:** "¿Su modelo funciona con otras versiones de QR?"

**Respuesta honesta:** CIC tiene versiones variables, asi que SI entrena con diversidad. Pero no reportamos **per-version analysis**.

**Mitigacion:** agregar analisis por version en CIC. Si CIC tiene metadata del QR version, podemos:
```
Per-version AUC on CIC:
  Version 5:   AUC = 0.XX  (n = X,XXX)
  Version 10:  AUC = 0.XX
  Version 15:  AUC = 0.XX
  ...
```

**Esto añade rigor.** 1 hora de trabajo extra.

### Problema 3.4: Grad-CAM sesgo izquierda-derecha

Fig 6 muestra atencion en lado izquierdo para benigno, centro-derecha para phishing.

**Critica esperada:** "¿El modelo esta aprendiendo patrones de phishing o esta aprendiendo a identificar el layout del dataset?"

**Respuesta rigurosa:** No lo sabemos con certeza. Tendriamos que verificar que el mismo patron aparece dentro de CADA dataset (no solo en el combinado).

**Test propuesto:** correr Grad-CAM SEPARADAMENTE en muestras de Trad y de CIC. Si el patron izquierda-derecha es consistente en ambos → es senal real de phishing. Si solo aparece en uno → es artefacto de dataset.

**Recomendacion:** hacer este check antes de la reunion con tu asesora.

### Problema 3.5: Embedding dimensionality sobre-parametrizada

SHAP muestra que 20/128 dims cargan la señal. Esto indica que el embedding es ~6x mas grande de lo necesario.

**Critica esperada:** "Si 108 dims son irrelevantes, el modelo puede estar memorizando features espureas en esas dimensiones."

**Respuesta:** las dimensiones "irrelevantes" tambien hacen zero contribution, asi que no dañan. Pero es una señal de que podemos pruning para mejor eficiencia.

**Mitigacion experimental:** re-entrenar con embedding_dim=64 o 32. Si performance se mantiene, fortalece el paper con un numero adicional.

---

## 4. Otras consideraciones que pueden surgir

### 4.1 Balance de clases

- Reportamos Trad como 50/50 (5005 benign vs 4982 phishing) → balanceado
- CIC es 42% benign / 58% malicious (429,976 vs 575,762)
- Al samplear 50K de cada uno para training, forzamos 50/50 artificialmente

**¿Es esto un problema?** Es standard practice, pero deberiamos reportarlo explicitamente en el paper. El CIC real es desbalanceado.

### 4.2 Batch effects

Nuestro batch size cambio entre runs (v1 tenia 64, v2/v3 tienen 128). Batch size afecta estadisticas de BatchNorm.

**Critica posible:** "¿Como afecta el batch size las conclusiones del ablation?"

**Defensa:** el ablation se hizo todo con batch=128 consistente (verificable en notebook 08).

### 4.3 Random seed reporting

Reportamos single-seed (42). Reviewers fuertes piden mean +/- std sobre multiple seeds.

**Ideal:** 3 seeds para las metricas principales.  
**Tiempo:** 3x el entrenamiento de v3 = ~3 horas en A100.  
**Beneficio:** intervalos de confianza reportables.

**Recomendacion:** si hay tiempo, hacer 3 seeds y reportar mean±std. Si no, justificar single seed como "limited compute budget".

### 4.4 Calibration

No reportamos **calibration curves** (reliability diagrams). Los scores del modelo ¿son probabilidades bien calibradas o solo rankings?

**Check rapido:** Brier score, ECE (Expected Calibration Error).

**Si el modelo esta mal calibrado:** threshold 0.5 no es optimo. Threshold calibration puede ayudar.

### 4.5 Runtime benchmarks

No reportamos tiempo de inferencia explicito. Solo decimos "mobile-deployable" basado en tamaño.

**Lo que deberiamos reportar:**
- Inference time en CPU (x86, ARM)
- Inference time en GPU (T4, A100)
- Memoria pico durante inference

**Tiempo de medir:** 30 minutos.

---

## 5. Lo que creo que ES importante discutir con tu asesora

### Preguntas prioritarias para la reunion

**Pregunta 1:** ¿Hacemos experimentos adicionales antes del envio?

Opciones (en orden de retorno sobre tiempo):
- (a) **URL overlap check Trad vs CIC** — 15 min — CRITICO (si hay overlap debemos reportar)
- (b) **Threshold calibration experiment** — 1-2 horas — alto valor agregado
- (c) **Per-version analysis en CIC** — 1-2 horas — refuerza generalizacion
- (d) **Multi-seed training** — 3-4 horas — rigor estadistico
- (e) **Grad-CAM per-dataset** (Trad vs CIC separado) — 30 min — valida interpretacion
- (f) **Inference time benchmarks** — 30 min — refuerza "mobile-deployable"

**Mi recomendacion:** (a) + (e) + (f) son baratos y esenciales. (b) y (c) si tenemos 1 dia extra.

**Pregunta 2:** ¿Como enmarcamos el cross-dataset en el paper?

Opciones:
- (i) **Actual:** "Combined training is necessary" — honesto pero puede parecer defensivo
- (ii) **Propuesto:** "Domain shift characterization" — mas sofisticado academicamente
- (iii) **Agresivo:** "Proof of domain diversity" — positivo pero exagerado

**Mi recomendacion:** opcion (ii). Academicamente mas defendible, conecta con literatura de domain adaptation.

**Pregunta 3:** ¿Reportamos single model o ensemble?

- Single model: mas simple, honesto, lo que tenemos
- Ensemble (3 seeds): 0.5-1pp mas AUC, FNR mas bajo, pero mas complejidad

**Mi recomendacion:** single model si el paper va a conferencia con pages limit. Ensemble solo si tenemos tiempo Y se justifica (ej. reviewers de journal).

**Pregunta 4:** ¿Hacemos threshold calibration experiment?

Esta experimento mostraria:
- En threshold default (0.5): AUC 0.9254, F1 0.8576, FNR 0.166
- En threshold calibrado (ej. 0.35): AUC igual, F1 ~0.85, FNR ~0.10

Valor: muestra que el sistema puede tunearse para security deployment.

**Mi recomendacion:** SI. Es 1-2 horas de trabajo y añade una tabla util. Deberia ir como "Table VII: Threshold-Performance Trade-off".

**Pregunta 5:** ¿Abordamos Phase 2 overfitting en limitations?

El paper actual menciona limitations pero no discute el overfitting en Phase 2 explicitamente.

**Deberiamos agregar:** "While our early stopping protocol selects the best checkpoint, training beyond epoch 8 exhibits gradual validation loss increase, indicating that Q-Shield's capacity slightly exceeds the information content of the current training corpus. Additional regularization (MixUp, stronger dropout) or larger datasets are natural extensions."

Esto es honestidad que los reviewers apreciaran.

---

## 6. Resumen ejecutivo de riesgos

| Riesgo | Severidad | Probabilidad reviewer lo detecte | Mitigacion recomendada |
|--------|-----------|----------------------------------|------------------------|
| Phase 2 overfitting | Media | Alta | Documentar en limitations + early stopping curve |
| CV1 FNR=0 (collapse) | Alta | Muy alta | Reframe como "threshold calibration needed cross-domain" |
| CV2 AUC=0.52 (random) | Alta | Muy alta | Reframe como "domain shift characterization" |
| URL overlap Trad/CIC no verificado | Alta | Media | **HACER check antes de enviar** |
| Grad-CAM puede ser dataset artifact | Media | Media | **HACER per-dataset Grad-CAM antes de enviar** |
| FNR 0.166 para security | Alta | Alta | Threshold calibration experiment |
| Single-seed reporting | Baja | Baja | Multi-seed si hay tiempo, sino justificar |
| Sobre-parametrizacion embedding | Baja | Baja | Mencionar en future work (pruning) |
| No per-version analysis | Media | Media | Agregar si CIC tiene metadata |
| No calibration reporting | Baja | Baja | Brier score opcional |

---

## 7. Plan de accion ANTES de enviar

**Prioridad 1 (hacer SI o SI, 2-3 horas total):**
1. URL overlap check Trad vs CIC
2. Grad-CAM separado en Trad y CIC (validar interpretacion)
3. Inference time benchmarks
4. Mejorar limitations section (phase 2 overfitting + cross-dataset framing)

**Prioridad 2 (hacer si hay tiempo, 4-6 horas):**
5. Threshold calibration experiment + Table VII
6. Per-version analysis en CIC

**Prioridad 3 (nice to have):**
7. Multi-seed reporting (mean +/- std)
8. Ensemble de 3 modelos
9. Calibration curves

---

## 8. Puntos de conversacion para la reunion con Aurea

**Abre con:** "Quiero ser transparente sobre algunos aspectos criticos antes de enviar."

**Temas ordenados:**

1. **Overfitting Phase 2 es real pero manejado con early stopping.**  
   *Pregunta:* ¿reportamos mean+-std o single seed es aceptable?

2. **Cross-dataset tiene resultados nuances — CV1 colapsa, CV2 aleatorio.**  
   *Propuesta:* enmarcar como "domain shift characterization" en vez de "generalization test".

3. **FNR 0.166 es alto para security.**  
   *Pregunta:* ¿hacemos threshold calibration experiment?

4. **Riesgo de data leakage Trad-CIC no verificado.**  
   *Accion inmediata:* hacer URL overlap check.

5. **Grad-CAM puede ser dataset artifact.**  
   *Accion inmediata:* ejecutar Grad-CAM por separado en cada dataset.

6. **Sobre-parametrizacion embedding (SHAP dice 20/128 dims relevantes).**  
   *Pregunta:* ¿vale la pena experimento de pruning?

**Cierre con:** "Preferiria que reviewers detecten estas limitaciones en nuestro paper (donde las manejamos) que en rebuttal (donde las nuestras soluciones son reactivas)."

---

*Documento preparado por Nicolas Llerena Silva — Abril 2026*  
*Analisis critico previo a envio final*
