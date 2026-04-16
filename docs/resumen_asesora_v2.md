# Resumen de Avance v2 — Reunión con Asesora

**Proyecto:** Q-Shield — Detección Multimodal de Quishing con Siamese Networks  
**Autor:** Nicolás Alejandro Llerena Silva  
**Asesora:** Aurea Soriano-Vargas  
**Fecha:** Abril 2026  
**Actualización respecto a la reunión anterior:** Se incorporó el feedback de Siamese Network + contrastive learning

---

## 1. Cambios desde la última reunión

### Lo que pediste:
1. Hacerlo multimodal
2. Siamese Network para aprender embeddings que diferencien QR benignos vs maliciosos
3. Aprendizaje contrastivo (auto-supervisión) para los embeddings
4. Reproducir los baselines de los papers de referencia primero
5. Agregar nuestro valor agregado

### Lo que hicimos:

| Tarea | Estado |
|-------|--------|
| Implementar Siamese Network con MobileNetV2 | Implementado y testeado (2.9M params) |
| Contrastive Loss (Chopra et al. 2005) | Implementado (margin=2.0) |
| Notebook de entrenamiento para Colab Pro+ | Listo, auto-extrae datos desde Drive |
| Reproducir baseline Trad et al. | AUC=0.813 con 25 features (vs 0.913 reportado con 4761 pixeles) |
| Entrenar en CIC dataset completo | Preparado — 1M+ QR images zipeados para Drive |
| Actualizar paper LaTeX | Sección de Siamese methodology agregada |
| Limpiar workspace local | Recuperados ~16 GB de espacio |

---

## 2. Arquitectura actual (post-feedback)

```
FASE 1: CONTRASTIVE PRETRAINING (Auto-supervisión)
  QR_anchor ──┐
              ├── MobileNetV2 (pesos compartidos) ──► embedding_a ──┐
  QR_pair ────┘                                       embedding_b ──┤── Contrastive Loss
                                                                     L = y·d² + (1-y)·max(0,m-d)²

FASE 2: CLASIFICACIÓN SUPERVISADA
  QR Image ──► Backbone pretrained ──► Embedding (128-d) ──► FC ──► Sigmoid ──► 0/1
```

### ¿Por qué Siamese?
1. **Aprende QUÉ diferencia un QR malicioso** — no solo clasifica, entiende la estructura
2. **Funciona con pocos datos** — ideal cuando expandamos al dataset peruano
3. **Los embeddings son transferibles** — entrenados en CIC, usables en otros datasets
4. **Nadie lo ha hecho para quishing** — contribución original clara para el paper

---

## 3. Resultados que ya tenemos (baselines)

### 3.1 Features estructurales + ML clásico (Trad dataset, n=9,987)

| Modelo | AUC | Precisión | Recall | F1 |
|--------|-----|-----------|--------|----|
| Random Forest | **0.813** | 0.794 | 0.659 | 0.720 |
| XGBoost | 0.810 | 0.785 | 0.664 | 0.720 |
| LightGBM | 0.808 | 0.771 | 0.670 | 0.717 |

**Contexto:** Trad et al. reportaron AUC=0.9133 usando 4,761 features (todos los pixeles raw). Nosotros logramos 0.813 con solo 25 features interpretables. La diferencia es el costo de la explicabilidad.

### 3.2 Siamese Network (en progreso)
- Modelo implementado y testeado localmente
- Notebook listo para correr en Colab Pro+ con GPU T4/A100
- **Resultados del Siamese se tendrán después de correr el entrenamiento** (~30 min en GPU)

### 3.3 Hallazgos estadísticos clave

| Feature | Cohen's d | Interpretación |
|---------|-----------|---------------|
| Transiciones horizontales | **-0.76** | Phishing QRs tienen menos alternancia H (bloques más concentrados) |
| Transiciones verticales | **+0.68** | Phishing QRs tienen más complejidad V (codewords más densos) |
| Densidad de datos | **+0.40** | Phishing QRs codifican más datos (URLs más largas) |
| Columna 44 (alineamiento) | p < 10⁻¹⁴⁹ | Hotspot espacial más discriminativo |

---

## 4. Datasets preparados para entrenamiento

| Dataset | Formato | Tamaño | Estado |
|---------|---------|--------|--------|
| Trad et al. | 9,987 matrices 69×69 | 9 MB (zip) | En Drive, listo |
| CIC QR Benignos | 429,976 PNGs | 241 MB (zip) | En Drive, listo |
| CIC QR Maliciosos | 575,762 PNGs | 319 MB (zip) | En Drive, listo |
| **Total** | **1,005,725 QR codes** | **569 MB** | **Todo en Drive** |

El notebook descomprime automáticamente en el SSD de Colab (más rápido que leer de Drive).

---

## 5. Timeline actualizado

```
Semana 1 (Abr 15-20)  ████████████████████  Data + Patterns + SOTA + Baselines   [COMPLETADO]
Semana 2 (Abr 16-22)  ████████████░░░░░░░░  Siamese Network + Entrenamiento      ← ESTAMOS AQUÍ
Semana 3 (Abr 23-29)  ░░░░░░░░░░░░░░░░░░░░  Dataset peruano + DistilBERT fusion
Semana 4 (Abr 30-May 6) ░░░░░░░░░░░░░░░░░░  XAI (Grad-CAM + SHAP) + Ablation
Semana 5-6 (May 7-25)  ░░░░░░░░░░░░░░░░░░░  Paper completo + revisión + envío
```

### Lo que sigue esta semana:
- [ ] Correr Siamese training en Colab Pro+ (30 min)
- [ ] Obtener AUC del Siamese en Trad (esperamos superar 0.90)
- [ ] Visualizar t-SNE de embeddings (figura para el paper)
- [ ] Si AUC > 0.91: superar a Trad et al. → resultado principal del paper

### Próxima semana:
- [ ] Dataset peruano sintético (SMS con Yape/Plin/BCP)
- [ ] DistilBERT para rama semántica
- [ ] Fusión tardía Siamese + DistilBERT

---

## 6. Preguntas para la asesora

1. **Sobre los embeddings:** ¿Prefieres que usemos Contrastive Loss (pares) o Triplet Loss (anchor/positive/negative)? Contrastive es más simple pero Triplet puede dar mejor separación. ¿Hay alguna preferencia por la literatura del área?

2. **Sobre el dataset peruano:** ¿Podemos generar los 100 SMS sintéticos internamente o necesitamos pasar por el comité de ética de UTEC? Los mensajes simulan phishing pero son completamente ficticios.

3. **Sobre la conferencia:** ¿Ya definimos si es IEEE Intercon o LA-CCI? Esto afecta el deadline exacto y el formato de las páginas.

4. **Sobre ablation study:** Para el paper necesitamos comparar: (a) solo features manuales, (b) solo Siamese, (c) Siamese + texto, (d) Siamese + texto + XAI. ¿Hay algún otro ablation que consideres importante?

5. **Sobre el valor agregado:** ¿Consideras que la Siamese Network sola es suficiente como contribución, o necesitamos también la parte multimodal (DistilBERT) para que el paper sea competitivo?

---

*Documento preparado por Nicolás Llerena — Abril 2026*
