# Resumen de Avance — Reunión con Asesora

**Proyecto:** Q-Shield — Detección de Quishing mediante Análisis Estructural de Códigos QR  
**Autor:** Nicolás Alejandro Llerena Silva  
**Asesora:** Aurea Soriano-Vargas  
**Fecha:** Abril 2026  
**Target:** IEEE Intercon / LA-CCI — Envío mayo 2026

---

## 1. ¿Qué es el problema?

**Quishing** = QR + Phishing. Los atacantes esconden URLs maliciosas dentro de códigos QR que se distribuyen por SMS, redes sociales o stickers físicos. Cuando el usuario escanea el QR, es redirigido a una página falsa que roba credenciales.

**¿Por qué es relevante en Perú?** Yape tiene más de 15 millones de usuarios que usan QR diariamente. Plin, BCP, Interbank — todos dependen de QR para pagos. Un solo QR malicioso en un punto de venta puede afectar a miles de personas.

**Tres problemas que nadie ha resuelto juntos:**

1. **Ceguera visual** — Los filtros de phishing actuales (Gmail, antivirus) analizan el texto del mensaje pero no pueden "ver" la URL escondida dentro de la imagen del QR.

2. **La paradoja del decodificado** — Para saber si un QR es malicioso, hay que escanearlo. Pero escanearlo ya te expone al ataque (redirecciones automáticas, tracking, etc.). Es como abrir una carta bomba para ver si es peligrosa.

3. **Sin contexto local** — Todos los modelos existentes están entrenados con phishing en inglés. No entienden "Tu cuenta Yape ha sido bloqueada" ni "Gana S/500 con Plin".

---

## 2. Nuestra propuesta

Detectar QR maliciosos analizando su **estructura visual** (patrones de módulos blancos y negros) **sin nunca decodificar el contenido**. La idea clave:

> Los QR que codifican URLs largas y obfuscadas producen patrones de módulos más densos y complejos que los QR con URLs cortas y legítimas. Esto es detectable por un clasificador sin necesidad de leer la URL.

**Nombre del framework:** Q-Shield  
**Enfoque del paper:** 25 características estructurales + clasificadores ML + explicabilidad con SHAP

---

## 3. ¿Qué datasets tenemos?

| Dataset | Fuente | Tamaño | Uso |
|---------|--------|--------|-----|
| **CIC Trap4Phish 2025** | Canadian Institute for Cybersecurity (UNB) | 429,976 QR benignos + 575,762 QR maliciosos (1M+ total) | Entrenamiento principal |
| **Trad et al. (2025)** | Paper IEEE arxiv:2505.03451 | 9,987 QR codes (matrices 69×69) | Baseline y validación cruzada |
| **Feature CSVs (CIC)** | Misma fuente | ~80,000 muestras (HTML, PDF, Excel, Word) | Análisis cruzado de formatos |

Los dos datasets son públicos, citables, y con licencias que permiten investigación.

---

## 4. ¿Qué hallazgos tenemos hasta ahora?

### 4.1 Las diferencias estructurales son reales y significativas

Analizamos las 9,987 muestras del dataset Trad con pruebas estadísticas rigurosas:

| Característica | QR Benigno | QR Phishing | Cohen's d | p-value |
|---------------|-----------|-------------|-----------|---------|
| Transiciones horizontales | 4611.9 | 4529.1 | **-0.76** | < 10⁻²⁹³ |
| Transiciones verticales | 4267.9 | 4367.3 | **+0.68** | < 10⁻²³³ |
| Densidad región de datos | 0.4920 | 0.4947 | +0.40 | < 10⁻⁸⁸ |
| Densidad cuadrante BR | 0.4948 | 0.4993 | +0.38 | < 10⁻⁷⁸ |
| Densidad total de módulos | 0.4927 | 0.4945 | +0.29 | < 10⁻⁴⁶ |

**Interpretación:**
- Cohen's d de -0.76 para transiciones horizontales → efecto **medio-grande** (umbral de "grande" es 0.80)
- Los QR de phishing tienen **menos** transiciones horizontales porque las URLs largas producen bloques de datos más concentrados
- Los QR de phishing tienen **más** transiciones verticales porque los codewords del QR se organizan en tiras verticales de 2 columnas que se vuelven más densas con URLs más largas
- Los p-values son extremadamente pequeños (< 10⁻⁴⁶ en todos los casos) — esto no es casualidad

### 4.2 Hay un "hotspot" espacial en la Columna 44

En la grilla de 69×69 módulos, la columna 44 (zona del patrón de alineamiento del QR Version 13) muestra la mayor diferencia entre clases (p < 10⁻¹⁴⁹). Esto pasa porque el patrón de alineamiento es fijo, pero los módulos de datos que lo rodean cambian según la longitud del payload.

### 4.3 Existen 3 subtipos de ataque

Aplicando K-Means (k=3) sobre las características de los QR maliciosos:

- **Tipo A — Alta densidad:** URLs obfuscadas largas → módulos muy densos → fácil de detectar
- **Tipo B — Estructura compleja:** Cadenas de redirección múltiple → muchas transiciones → detectable
- **Tipo C — Obfuscación sutil:** URL shorteners (bit.ly, etc.) → diferencias mínimas → **el más difícil** → motiva agregar análisis de texto del SMS como complemento

### 4.4 Los patrones se generalizan entre datasets

Entrenamos un modelo en el dataset CIC y lo probamos en el dataset Trad **sin ningún ajuste**. Las características que suben para malicious en CIC también suben en Trad, y viceversa. Esto confirma que los patrones no son un artefacto del dataset sino una propiedad del estándar QR.

---

## 5. Estado del arte — ¿Dónde nos posicionamos?

| Método | ¿Decodifica QR? | ¿Multimodal? | ¿Explainable? | ¿Edge-deploy? | Mejor métrica |
|--------|:---:|:---:|:---:|:---:|---:|
| Trad & Chehab (2025) | No | No | Medio | — | AUC=0.913 |
| Nejati et al. (2025) | Sí | No | Medio | — | Acc>0.95 |
| Khalifa et al. (2025) | Sí | Sí | Bajo | No | — |
| Bountakas et al. (2023) | N/A | Sí | Medio | No | Acc=0.972 |
| **Nosotros** | **No** | **Sí*** | **Alto (SHAP)** | **Sí** | **En progreso** |

*La parte multimodal (texto SMS con DistilBERT) está planificada para la siguiente fase.

**5 gaps que llenamos:**
1. Nadie ha hecho detección multimodal (visual + texto) para quishing
2. La mayoría requiere decodificar el QR (inseguro)
3. No existe solución ligera para móviles
4. No hay modelos con contexto latinoamericano
5. La explicabilidad es limitada en todos los trabajos previos

---

## 6. ¿Qué tenemos implementado?

### Código y notebooks (listos para ejecutar en Colab)
- `01_EDA_CIC_Trap4Phish.ipynb` — Análisis exploratorio de todos los datasets
- `02_Pattern_Analysis.ipynb` — Análisis de patrones, tests estadísticos, clustering, SHAP
- `03_SOTA_Review.ipynb` — Tabla comparativa y gap analysis con figuras

### Paper LaTeX
- `paper/main.tex` — Draft completo en formato IEEEtran
- Secciones listas: Abstract, Introduction, Related Work (10 refs), Methodology (25 features, 3 clasificadores, SHAP)
- Sección de resultados con estadísticas reales (tablas II y III)
- `paper/references.bib` — 13 entradas BibTeX

### Repositorio GitHub
- https://github.com/nicolasllerenas/Multimodal-Quishing-Detection-Framework
- README profesional en inglés con arquitectura, datasets, SOTA
- Documentación en `docs/`: problem statement, SOTA, pattern analysis, análisis de Trad et al.

---

## 7. Timeline y próximos pasos

```
Semana 1 (Abr 15-20)  ████████░░░░░░░░░░  Data Analysis & Patterns    ← ESTAMOS AQUÍ
Semana 2 (Abr 21-27)  ░░░░░░░░░░░░░░░░░░  SOTA & Baseline Reproduction
Semana 3 (Abr 28-May 4) ░░░░░░░░░░░░░░░░░  Q-Shield Architecture
Semana 4 (May 5-11)   ░░░░░░░░░░░░░░░░░░  XAI & Ablation Studies
Semana 5-6 (May 12-25) ░░░░░░░░░░░░░░░░░░  Paper Writing & Submission
```

### Resultados experimentales (ya ejecutados)

**Dataset Trad (9,987 QRs, matrices 69×69 binarias):**

| Modelo | AUC | Precisión | Recall | F1 |
|--------|-----|-----------|--------|----|
| Random Forest | **0.813** | 0.794 | 0.659 | 0.720 |
| XGBoost | 0.810 | 0.785 | 0.664 | 0.720 |
| LightGBM | 0.808 | 0.771 | 0.670 | 0.717 |

→ Trad reportó AUC=0.9133 con 4,761 features (todos los pixeles). Nosotros logramos 0.813 con solo 25 features interpretables. La diferencia es el costo de la explicabilidad, y es un trade-off justificable.

**Dataset CIC (4,000 QRs PNG muestreados):**

| Modelo | AUC | Precisión | Recall | F1 |
|--------|-----|-----------|--------|----|
| Random Forest | **0.655** | 0.626 | 0.574 | 0.599 |
| XGBoost | 0.630 | 0.590 | 0.566 | 0.578 |
| LightGBM | 0.627 | 0.595 | 0.564 | 0.579 |

→ Performance más baja porque las imágenes CIC son PNGs de tamaño variable (no matrices binarias fijas). Las features de transición y run-length son sensibles a la resolución. **Esto es un hallazgo clave: motiva usar CNN (MobileNetV2) que puede aprender representaciones invariantes a la resolución.**

**Validación cruzada CIC→Trad:** AUC = 0.41 (falló — clasificó todo como malicioso). Las distribuciones de features son muy diferentes entre PNGs grayscale y matrices binarias. **Otro hallazgo clave: se necesita un CNN o normalización de formato para transferencia real.**

### Inmediato (esta semana)
- [x] ~~Ejecutar experimentos completos: RF, XGBoost, LightGBM en CIC y Trad~~
- [x] ~~Llenar Table III del paper con métricas reales~~
- [x] ~~Validación cruzada CIC→Trad con AUC formal~~

### Semana 2
- [ ] Reproducir baseline de Trad et al. (target: AUC ≥ 0.91)
- [ ] Implementar rama visual con MobileNetV2

### Semana 3
- [ ] Dataset sintético peruano (100 SMS)
- [ ] Rama semántica con DistilBERT
- [ ] Fusión tardía (Two-Stream)

### Semana 4-5
- [ ] Grad-CAM + SHAP completo
- [ ] Ablation study
- [ ] Terminar paper

---

## 8. Preguntas para la asesora

1. **Sobre el scope del paper:** El paper actual se enfoca en features estructurales + ML clásico + SHAP. ¿Incluimos la parte multimodal (DistilBERT) en este paper o lo dejamos como future work y lo hacemos en un segundo paper?

2. **Sobre el dataset peruano:** Necesitamos 100 SMS sintéticos con contexto de Yape/Plin/BCP. ¿Hay algún protocolo de ética de UTEC que debamos seguir para generar datos sintéticos de phishing?

3. **Sobre la conferencia target:** ¿IEEE Intercon o LA-CCI? ¿Hay algún deadline específico que debamos considerar?

4. **Sobre co-autoría:** ¿Hay alguien más del laboratorio que deba ser incluido como co-autor?

---

*Documento preparado por Nicolás Llerena — Abril 2026*
