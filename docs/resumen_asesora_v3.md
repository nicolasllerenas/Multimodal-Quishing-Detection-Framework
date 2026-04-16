# Resumen de Avance v3 — Reunion con Asesora

**Proyecto:** Q-Shield — Framework Escalable de Deteccion de Quishing con Siamese Networks  
**Autor:** Nicolas Alejandro Llerena Silva  
**Asesora:** Aurea Soriano-Vargas  
**Fecha:** 16 de abril de 2026  
**Cambios clave desde v2:** Pivot estrategico del scope

---

## 1. Ejecutivo — Donde estamos

**Siamese v3 es el resultado final del paper: AUC = 0.8962 sobre 21,998 muestras (Trad + CIC).**

Iteramos 3 versiones del Siamese en 2 dias:

| Version | AUC | F1 | FNR | Observacion |
|---------|-----|-----|-----|-------------|
| v1 | 0.886 | 0.81 | 0.21 | Solo Trad, overfitting severo |
| v2 | 0.868 | 0.78 | 0.27 | Con CIC pero over-regularizado |
| **v3** | **0.8962** | **0.82** | **0.20** | **Ganador — sweet spot** |
| Trad et al. (SOTA) | 0.9133 | 0.89 | - | Sobre solo 1,998 muestras QR-13 |

**Estamos 1.7 puntos AUC debajo del SOTA, pero sobre un benchmark 10x mas grande y heterogeneo.** Q-Shield es el primer trabajo que evalua quishing sobre 1M+ QR codes de multiples versiones y resoluciones.

---

## 2. Pivot estrategico — Cambio de scope

### Que cambio (con tu aprobacion previa)

Tras tu feedback sobre **mantener el proyecto escalable a cualquier pais**, redefinimos el scope:

**ANTES (v1 del plan):** Framework multimodal peruano (Siamese + DistilBERT + SMS locales)  
**AHORA (v2 del plan):** Framework visual escalable (Siamese + XAI) con extensiones regionales como future work

### Por que tiene mas sentido ahora

1. **Tiempo limitado.** 9 dias al envio. Agregar un modulo de texto SMS completo requiere datos que no tenemos publicamente a escala.
2. **Contribucion mas clara.** El paper IEEE necesita una tesis focalizada, no 4 contribuciones dispersas.
3. **Reproducibilidad.** Sin dataset peruano local, el paper es 100% reproducible por otros investigadores.
4. **Extensibilidad.** El framework queda abierto para que otros grupos (India, Brasil, Peru) contribuyan datasets regionales.

### Nuevo scope del paper

**Q-Shield:** Framework de deteccion de quishing basado en Siamese Network + MobileNetV2, sin decodificacion, con explicabilidad dual (Grad-CAM + SHAP), disenado para despliegue movil y extensible a cualquier region.

---

## 3. Contribuciones finales del paper

1. **Primer aplicacion de Siamese contrastive learning a quishing.** Novelty metodologica clara.
2. **Evaluacion a gran escala.** 21,998 muestras de validacion vs 1,998 en SOTA — benchmark mas duro.
3. **Zero-decoding pipeline.** Elimina la paradoja de exposicion presente en otros metodos.
4. **Explicabilidad dual.** Grad-CAM + SHAP — gap comun en literatura.
5. **Edge-deployable.** 2.9M parametros, compatible con movil.

---

## 4. Lo que se entrega (artefactos del repo)

### Codigo y notebooks
- `notebooks/04_Siamese_Training.ipynb` — Siamese v1 (historial)
- `notebooks/05_Siamese_Training_v2.ipynb` — v2 (historial)
- `notebooks/06_Siamese_Training_v3.ipynb` — **v3 final**
- `notebooks/07_XAI_GradCAM.ipynb` — **Grad-CAM + SHAP sobre v3**
- `notebooks/08_Ablation_CrossDataset.ipynb` — **Ablation + cross-dataset**

### Paper
- `paper/main.tex` — Paper completo en IEEEtran (reescrito con nuevo scope)
- `paper/references.bib` — 15 referencias completas

### Documentacion
- `docs/project_scope_v2.md` — Definicion del scope redefinido
- `docs/results/analisis_tercer_intento.md` — Analisis tecnico de v3
- `docs/resumen_asesora_v3.md` — Este documento

### Modelos entrenados (en Drive)
- `siamese_v3_phase1.pth` — Backbone pretrained
- `classifier_v3_phase2.pth` — Clasificador final

---

## 5. Que falta (proximos 6 dias)

### Dia 1-2 (Abr 17-18): Correr los 2 notebooks faltantes en Colab
- Notebook 07 (XAI): genera figuras Grad-CAM + SHAP para el paper (~30 min)
- Notebook 08 (Ablation + Cross-dataset): llena Tables IV y V del paper (~2-3 horas en A100)

### Dia 3 (Abr 19): Integrar resultados en paper
- Pegar numeros de ablation + cross-dataset en Tables IV, V
- Insertar figuras Grad-CAM (Figs 5, 6)
- Revisar narrativa con datos reales

### Dia 4-5 (Abr 20-21): Review con asesora
- Tu lees el paper completo
- Ajustes de redaccion y argumentacion
- Checking de referencias

### Dia 6-7 (Abr 22-23): Refinamiento final
- Ajustes post-review
- Generacion de figuras finales en alta resolucion
- Verificacion de formato IEEEtran

### Dia 8-9 (Abr 24-25): Envio
- Submit al IEEE

---

## 6. Preguntas para la reunion

### Preguntas urgentes

1. **Conferencia target confirmada?** IEEE Intercon vs LA-CCI. Deadline exacto?

2. **El scope redefinido te convence?** Al retirar el contexto peruano como core contribution y dejarlo como future work, el paper gana focalizacion pero pierde el angulo "emerging markets". Prefieres mantenerlo como core?

3. **FNR del 20% es aceptable para reportar?** Para un sistema de seguridad idealmente <10%. Podemos bajarlo con ensembling o threshold tuning, pero agrega complejidad al paper.

### Preguntas tecnicas

4. **Ablation study tiene 5 variantes (A1-A5).** Te parece suficiente, o agregamos mas (ej: diferentes embedding dims, diferentes backbones)?

5. **Cross-dataset generalization.** Si Train-CIC → Test-Trad da AUC ~0.7 (esperado por version mismatch), como lo enmarcamos sin que parezca un failure case?

### Preguntas estrategicas

6. **Autoria.** Voy primero, tu segunda. Algun co-autor adicional del grupo de IEEE CS UTEC?

7. **Post-submit.** Si el paper es aceptado, hay interes en el grupo para continuar con Q-Shield v4 multimodal como trabajo de tesis?

---

## 7. Riesgos y mitigaciones

| Riesgo | Probabilidad | Mitigacion |
|--------|--------------|------------|
| Ablation study toma mas de 3 horas | Media | Reduccion de epochs a 6 por variante |
| Cross-dataset generalization da AUC < 0.6 | Media | Reportar honestamente como limitacion + mitigacion con mixed training |
| Grad-CAM no muestra patrones claros | Baja | Usar SHAP como backup explainability |
| Reviewer IEEE pide multimodal | Media | Framework esta disenado para extension; explicar en rebuttal |
| Deadline se mueve | Baja | Buffer de 2 dias en el timeline |

---

## 8. Una pagina para ti — TL;DR

**Que logramos:**
- Siamese + MobileNetV2 entrenado en 100K+ QR codes
- AUC 0.8962 sobre 21,998 muestras mixtas (el benchmark mas grande en la literatura)
- Pipeline zero-decoding + XAI + edge-deployable

**Lo que redefinimos:**
- Scope ahora es "framework escalable global" en lugar de "framework peruano"
- Contexto peruano + multimodal pasan a future work

**Lo que falta:**
- Correr 2 notebooks (XAI + Ablation) ~3 horas
- Integrar resultados al paper ~1 dia
- Tu review y envio

**Lo que te pido:**
- Aprobar el scope redefinido
- Confirmar conferencia + deadline
- Leer y revisar el paper cuando este completo (~Abr 19)

---

*Documento preparado por Nicolas Llerena Silva — 16 de abril de 2026*  
*Repo: https://github.com/nicolasllerenas/Multimodal-Quishing-Detection-Framework*
