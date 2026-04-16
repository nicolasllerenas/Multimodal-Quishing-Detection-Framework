# Resumen de Avance v2 — Reunión con Asesora

**Proyecto:** Q-Shield — Detección Multimodal de Quishing con Siamese Networks  
**Autor:** Nicolás Alejandro Llerena Silva  
**Asesora:** Aurea Soriano-Vargas  
**Fecha:** 16 de abril de 2026  
**Hardware:** Colab Pro+ con NVIDIA A100 40GB

---

## 1. Resumen ejecutivo

Entrené el primer Siamese Network siguiendo tu recomendación de contrastive learning. Los resultados son **prometedores pero aún no superan el SOTA**:

| Método | AUC | Nuestro comentario |
|--------|-----|-------------------|
| Trad et al. (SOTA actual) | 0.913 | Raw pixels + XGBoost (4,761 features) |
| Features manuales + RF (baseline nuestro) | 0.813 | 25 features interpretables |
| **Siamese v1 (primer intento)** | **0.886** | MobileNetV2 + Contrastive Loss |
| Siamese v2 (siguiente experimento) | Target ≥ 0.92 | Con mejoras identificadas |

**Status honesto:** Superamos nuestro baseline por +9% pero quedamos 2.7 puntos debajo de Trad. Identifiqué exactamente qué faltó y tengo el plan v2 ya implementado.

---

## 2. Lo que sí funcionó (hallazgos positivos)

### La dirección arquitectónica es correcta
- El Siamese Network converge y genera embeddings separables
- t-SNE muestra dos clusters parcialmente diferenciados (benignos a la derecha, phishing a la izquierda)
- El modelo tiene solo 2.9M parámetros — deployable en móvil

### Resultados Phase 2 (clasificación final)
- AUC = 0.886
- Precision 0.80, Recall 0.79, F1 = 0.81
- 828 TN, 173 FP, 209 FN, 788 TP
- Ejecución estable, reproducible

---

## 3. Lo que falló (diagnóstico honesto)

### Problema 1 — Overfitting severo (causa raíz: falta de datos)
```
Epoch 1:  TrAcc 59%, VaAcc 60%    (alineados)
Epoch 10: TrAcc 97%, VaAcc 70%    (brecha de 27pp)
Epoch 30: TrAcc 99%, VaAcc 69%    (no mejora desde ep 5)
```
El modelo memoriza pares de entrenamiento. Solo tenía 7,989 muestras de train y 2.9M parámetros.

### Problema 2 — No usó el dataset CIC (bug del notebook)
Tenía 1M+ QR images del CIC en Drive listos para usar, pero el notebook no los cargó correctamente. El script detectó `HAS_CIC=False` y entrenó solo con Trad (9,987 muestras).

### Problema 3 — Pares de entrenamiento muy fáciles
Genero pares random 50/50 same-class vs different-class. El modelo resuelve los fáciles rápido y no aprende las distinciones sutiles (Type C attacks: URL shorteners con diferencias visuales mínimas).

---

## 4. Plan v2 — Ya implementado, listo para correr

### Mejoras concretas en el código

| Cambio | v1 | v2 | Justificación |
|--------|-----|-----|-------|
| Dataset | Solo Trad (9,987) | Trad + CIC 100K | +10x datos → menos overfitting |
| Pares por epoch | 30,000 | 60,000 | Más cobertura del espacio |
| Epochs | 30 fijos | Max 25 + early stop | Se estancaba en ep 10 |
| Dropout | 0.3 | 0.5 | Más regularización |
| Weight decay | 1e-4 | 5e-4 | Más regularización |
| Learning rate | 1e-4 plano | 3e-4 + warmup + cosine | Convergencia más rápida |
| Batch size | 64 | 128 | A100 tiene VRAM de sobra |
| Margin | 2.0 | 1.0 | Mejor gradiente |
| Data augmentation | Ninguna | Flips + rotación | QRs son invariantes |
| Gradient clipping | No | max_norm=1.0 | Estabilidad |

### Target v2
- AUC ≥ 0.92 (superar a Trad et al.)
- FNR < 15% (reducir falsos negativos de 21% a <15%)
- F1 ≥ 0.88
- Tiempo de entrenamiento: ~45 min en A100

---

## 5. Decisiones que necesito consultarte

### Decisión 1 — ¿Incluimos Triplet Loss como alternativa?

La literatura sugiere que Triplet Loss produce separaciones más definidas que Contrastive Loss. ¿Agregamos un ablation Triplet vs Contrastive en el paper?

- **Pro:** Más rigor experimental, fortalece la contribución
- **Con:** +1 semana de experimentos

### Decisión 2 — Hard Negative Mining online o offline?

Hay dos formas de implementarlo:
- **Online (dentro del batch):** Rápido pero requiere batches grandes
- **Offline (pre-compute embeddings):** Más preciso pero re-indexar cada epoch

Recomiendo online (A100 soporta batch=256 tranquilo). ¿Opiniones?

### Decisión 3 — ¿Reportamos v1 como "ablation" en el paper?

Tres opciones para el paper:
1. Solo reportar v2 (el bueno)
2. Reportar v1 y v2 como progresión metodológica (más honesto)
3. Reportar v2 y mencionar v1 en supplementary material

Yo voto por la opción 2 — muestra que iteramos de manera sistemática.

### Decisión 4 — Dataset peruano SMS: ¿cuándo?

Tengo planificado:
- Semana 3 (23-29 abril): Generar 100 SMS con Yape/Plin/BCP context
- Semana 3-4: DistilBERT multilingual para procesarlos
- Semana 4: Fusión tardía Siamese + DistilBERT

¿Necesitamos aprobación ética de UTEC para generar datos sintéticos de phishing?

### Decisión 5 — Conferencia target

IEEE Intercon vs LA-CCI — ¿ya hay un deadline definido? El paper actual tiene 8 páginas en IEEEtran conference format.

---

## 6. Próxima semana — Lo que haré

1. **Hoy/mañana:** Correr Siamese v2 con CIC completo (45 min en A100)
2. **Miércoles:** Validar resultados, generar figuras finales
3. **Jueves-Viernes:** Escribir sección de "Results" con números reales de v2
4. **Fin de semana:** Avanzar con dataset SMS peruano

**Meta para la próxima reunión:** Traerte el paper con Results completos y la decisión de si vamos multimodal (DistilBERT) o cerramos el paper con solo el Siamese.

---

## 7. Figuras disponibles para el paper

- `fig_phase1_curves.png` — Curvas de entrenamiento Phase 1
- `fig_tsne_embeddings.png` — Espacio de embeddings (t-SNE)
- `fig_final_results.png` — Confusion matrix + ROC curve
- `gantt_chart_v2.png` — Timeline del proyecto

---

## 8. Repositorio

Todo está pusheado: https://github.com/nicolasllerenas/Multimodal-Quishing-Detection-Framework

Commits recientes:
- `fix: CUDA property compatibility`
- `feat: v1 results analysis + v2 training notebook`
- `feat: updated Siamese notebook, Gantt v2, advisor summary v2`

---

*Documento preparado por Nicolás Llerena Silva — Abril 2026*
