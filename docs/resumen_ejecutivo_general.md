# Q-Shield — Resumen Ejecutivo Integral

**Para:** Validacion del proyecto completo (teoria + practica + formulas)
**Autor:** Nicolas Alejandro Llerena Silva
**Fecha:** Mayo 2026
**Lectura estimada:** 25-30 minutos
**Status:** Pivote multimodal completado. Fusion alcanza AUC 0.9749 en el benchmark de 21,998 muestras.

---

# INDICE

- PARTE I: Teoria del problema y de la solucion (secciones 1-7)
- PARTE II: Formulas del paper explicadas linea por linea (secciones 8-13)
- PARTE III: Practica — experimentos y numeros (secciones 14-19)
- PARTE IV: Validacion y justificacion (secciones 20-22)
- PARTE V: Cheat sheet para defender el paper (seccion 23)

---

# PARTE I — TEORIA

## 1. ¿Que es el problema?

**Quishing** (QR + Phishing) es un ataque donde un atacante genera un codigo QR que, al ser escaneado, redirige al usuario a una pagina fraudulenta que roba credenciales o instala malware.

**Por que es grave ahora:**

- Los codigos QR se usan masivamente en pagos moviles, menus, tickets, etc.
- Los usuarios confian ciegamente en que los QRs son legitimos
- Las herramientas anti-phishing tradicionales no procesan la URL contenida en una imagen QR a menos que la imagen sea decodificada primero

## 2. ¿Por que es dificil detectarlo?

Tres problemas reales:

**1. Ceguera del filtro estandar.** Un filtro de email lee texto plano. La URL maliciosa esta dentro de la imagen del QR — un filtro que no decodifica el QR no la ve.

**2. La señal visual sola es debil fuera del sandbox.** Trad et al. 2025 reportan AUC 0.913 sobre QRs version 13 fija, EC `low`, sin logos — un escenario de laboratorio. CIC Trap4Phish 2025 reporta SSIM benigno↔phishing ≈ 0.34: visualmente casi indistinguibles. El CNN de CIC sobre imagenes alcanza solo F1 0.88 en QRs heterogeneos. Conclusion: el patron pixel-level es informativo pero no suficiente cuando los QRs varian en version, resolucion y formato.

**3. La señal de URL es fuerte pero requiere decodificar.** CIC reporta F1 0.97-0.99 con LLMs sobre la URL decodificada. Decodificar con `pyzbar` es local — lee el patron de modulos y devuelve un string, sin red, sin DNS, sin JS. La "paradoja del decodificado" que algunos trabajos invocan confunde dos pasos distintos: leer el contenido (seguro) y abrirlo (riesgoso).

## 3. ¿Que propone Q-Shield?

**Idea central:** combinar las dos señales, no elegir una. La defensa contra quishing tiene dos puntos de intervencion naturales — pre-decodificacion (solo imagen) y post-decodificacion (URL como string) — y un detector que opera en uno solo descarta la evidencia del otro.

**Diseño:**

1. **Rama visual** — MobileNetV2 Siamese sobre la imagen QR. Opera pre-decode. Es la unica señal disponible cuando el QR no se puede decodificar (bajo contraste, quiet zone faltante, finder patterns dañados).
2. **Rama de texto** — DistilBERT sobre la URL decodificada offline. Opera post-decode. Captura la señal lexica que CIC mostro que es la mas fuerte.
3. **Fusion** — un MLP pequeño que combina `[logit_visual, logit_texto, flag_undecodable]` → probabilidad final. El flag explicito le permite a la cabeza aprender que cuando el decode falla, debe confiar mas en el visual.

**Resultado headline:** AUC 0.9749, F1 0.936, FNR 0.057 sobre 21,998 muestras (Trad + CIC). Supera a Trad por +6.16 pp y al ensemble visual previo por +6.03 pp. El FNR ya cumple la tolerancia de seguridad ≤10% sin necesidad de threshold calibration.

## 4. ¿Como funciona a alto nivel?

**Tres etapas, dos fases de entrenamiento, un modelo de inferencia:**

1. **Phase 1 (visual contrastive pretraining):** mostramos al MobileNetV2 pares de QRs y le decimos "misma clase" o "clases distintas". Aprende un espacio de embedding 128-d donde los QRs benignos quedan cerca entre si, los phishing quedan cerca entre si, y benigno-phishing se separan.
2. **Phase 2 (visual classifier head):** sobre el backbone preentrenado, entrenamos una cabeza densa con focal loss para clasificacion binaria. Esto produce el clasificador visual del paper anterior.
3. **Text branch fine-tuning:** DistilBERT (66M params) se ajusta sobre las URLs decodificadas con focal loss durante 3 epochs. Aprende patrones lexicos de phishing.
4. **Fusion training:** sobre features ya cacheadas (logits del visual, logits del text, flag undecodable), entrenamos un MLP de 161 parametros (3→16→1). Esto solo aprende la calibracion relativa entre las dos ramas.

En inferencia: cada QR pasa por las dos ramas (visual y text decoder + DistilBERT), los logits van a la fusion, y sale la probabilidad final.

## 5. ¿Por que pivotamos? La motivacion del giro multimodal

La version inicial del paper era visual-only y usaba "no decoding" como argumento de seguridad. Despues de releer Trad y CIC identificamos tres problemas que un reviewer atacaria de inmediato:

1. **El "decoding paradox" no se sostiene.** pyzbar es local y deterministico. Confunde leer (string) con abrir (fetch + render). Un reviewer informado lo derriba.
2. **La señal visual sola es estructuralmente debil.** CIC lo demuestra empiricamente con SSIM 0.34 y CNN F1 0.88 en QRs heterogeneos.
3. **Combinar ambas dominaba a cualquiera sola, por construccion.** Bountakas 2023 y Khalifa 2025 ya lo validaron en webpages.

El pivote es honesto: la rama visual NO se descarta — es el fallback graceful cuando el decode falla (~5% del corpus). El flag UNDECODABLE le dice al fusion "trust visual aqui". El sistema degrada limpiamente al modo visual-solo en el peor caso.

## 6. ¿Por que el modelo es explicable?

Tres tecnicas XAI cubriendo niveles distintos:

- **Grad-CAM** sobre la rama visual: mapa de calor que muestra donde miro el modelo. Verifica que atiende zonas de datos y no finder patterns. Validado per-dataset (r=0.43 entre los mapas de Trad y CIC) — la señal visual es estructural, no dataset-specific.
- **SHAP** sobre el embedding de 128-d: mide que dimensiones contribuyen mas. Encontramos que las top-20 dominan; las 108 restantes son ruido — el embedding esta sobre-parametrizado y se podria podar a 32-d sin perdida.
- **Calibracion probabilistica** del fusion: Brier 0.054, ECE 0.038. El fusion es un buen ranker Y un buen estimador de probabilidades. La rama visual sola tiene Brier 0.146 y ECE 0.133 — mucho peor.

## 7. ¿Como nos comparamos con CIC?

**CIC reporta text-only F1 0.97-0.99** con LLMs dedicados (BERT-Tiny, DeBERTa-v3, ModernBERT, DeepSeek-R1-Distill). Es el numero mas alto en URL-only.

**Q-Shield text-only F1 0.927** con DistilBERT 66M, 3 epochs. Esta debajo de CIC porque:

- DistilBERT es mas chico que DeBERTa-v3 o ModernBERT
- Usamos solo 3 epochs vs el setup mas largo de CIC
- Ellos prepararon el dataset desde cero con etiquetas limpias, nosotros usamos la decodificacion offline directa

**Q-Shield fusion F1 0.936**, AUC 0.9749. Estamos **debajo de CIC en URL pura** pero **arriba en deteccion integrada** porque:

- CIC text-only no aborda el caso UNDECODABLE — silencio sobre que pasa con QRs no decodificables
- Nuestro fusion + flag explicito tiene fallback graceful
- Combinar visual + text es lo que CIC NO hace — ellos reportan las dos ramas en paralelo, no fusionadas

Conclusion honesta: con un LLM mas grande y mas epochs cerrariamos la brecha en text-only. La contribucion de Q-Shield no es ganarle a CIC en URL pura — es ofrecer un detector multimodal end-to-end con manejo explicito del caso degradado.

---

# PARTE II — FORMULAS DEL PAPER EXPLICADAS LINEA POR LINEA

Esta seccion cubre cada formula del paper con su justificacion. Si un reviewer pregunta "¿por que usan X?", aqui tienes la respuesta.

## 8. Formulacion del problema

**Formula (eq. 1 del paper):**

```
f_θ(x) = σ( g_φ ∘ h_ψ (x) )
```

**Que dice:**

- `x ∈ ℝ^(H×W)` es la imagen QR en grayscale
- `h_ψ` es la funcion de embedding (el backbone): mapea la imagen a un vector en `ℝ^d` con `d=128`
- `g_φ` es la cabeza clasificadora: mapea el embedding a un logit (numero real)
- `σ` es la sigmoide: aplasta el logit a `[0,1]` (probabilidad)

**Por que dos componentes:** `h_ψ` se entrena en Phase 1 con contrastive loss para producir representaciones discriminativas. `g_φ` se entrena en Phase 2 con focal loss para tomar decisiones binarias. La separacion permite reutilizar `h_ψ` para tareas auxiliares (XAI, recuperacion, etc.).

**Para multimodal:** la rama de texto produce su propio logit `ℓ_t`, y el fusion combina `[ℓ_v, ℓ_t, flag]` → logit final → sigmoide.

## 9. Contrastive Loss (Chopra et al. 2005)

**Formula (eq. 2 del paper):**

```
L_con(e1, e2, y) = (1-y) · d²/2  +  y · max(0, m - d)² / 2
```

donde `d = ‖e1 - e2‖₂` (distancia Euclidiana entre los dos embeddings).

**Que dice:**

- Si `y=0` (mismo clase): minimiza `d²/2` → empuja los embeddings a estar cerca.
- Si `y=1` (clases distintas): minimiza `max(0, m-d)²/2` → si la distancia ya supera `m`, no penaliza; si no, empuja a separar hasta llegar a `m`.

**Por que el margen `m=1.5`:** grid search sobre `{0.5, 1.0, 1.5, 2.0, 2.5}`. Margenes menores produjeron underfitting (clases no se separan lo suficiente). Margenes mayores no mejoraron el AUC final.

**Resultado en el espacio aprendido:** ratio inter/intra-clase de **1.94**. Los pares benigno-phishing estan al doble de distancia que los pares de la misma clase. El contrastive learning hizo lo que tenia que hacer.

## 10. Focal Loss (Lin et al. 2017) — Phase 2 visual

**Formula (eq. 3 del paper):**

```
L_focal(p, y) = -α_y · (1 - p_y)^γ · log(p_y)
```

**Que dice:**

- `p_y` es la probabilidad predicha de la clase verdadera
- `α_y = 0.5` para ambas clases (estan balanceadas despues del muestreo)
- `γ = 2` es el exponente de focusing

**Por que `(1-p_y)^γ`:** este factor reduce el peso de los ejemplos faciles (`p_y` cercano a 1) y aumenta el de los dificiles (`p_y` chico). El modelo se concentra en los samples que actualmente clasifica mal.

**Por que es critica en seguridad:** un FN expone al usuario al ataque; un FP solo dispara una advertencia. La asimetria de costo es exactamente lo que focal loss optimiza. Empiricamente, reemplazar focal por BCE estandar mantiene el AUC pero sube el FNR de 0.20 a 0.27 (visual). Es decir: `(1-p_y)^γ` traduce a una reduccion de 7 pp en FNR.

## 11. Fusion: combinacion lineal aprendida sobre logits

**Arquitectura:** MLP de 3 → 16 → 1 (161 parametros). Recibe `[ℓ_v, ℓ_t, f]` donde `f ∈ {0,1}` es el flag undecodable.

**Por que tan chiquita:** el rol del fusion es solo aprender la calibracion relativa entre dos logits que ya capturan las features. No tiene que aprender features visuales o textuales — esas ya estan en los logits. Con 161 parametros y 80,000 ejemplos de entrenamiento, el ratio params/samples es muy favorable y no hay riesgo de overfitting.

**Por que entrenar sobre features cacheadas:** en lugar de pasar imagenes y texto por las ramas en cada batch, precomputamos los logits una vez sobre todo el corpus. La fusion entrena en <1 minuto sobre features cacheadas, contra varios minutos por epoch si pasaramos los inputs originales.

## 12. Normalizacion L2 de embeddings

**Formula:**

```
e_norm = e / ‖e‖₂
```

**Por que se hace:** despues de la proyeccion lineal en el backbone, el embedding tendria magnitud arbitraria. Normalizar a la hipersfera unidad asegura que la distancia Euclidiana refleje solo la direccion (que es lo que codifica la similitud semantica). Sin esto, la contrastive loss se "engaña" empujando magnitudes en lugar de direcciones.

## 13. Grad-CAM (Selvaraju et al. 2017)

**Formula (conceptual):**

```
α^c_k = (1/Z) · Σ_{i,j} ∂y^c / ∂A^k_{ij}
L^c_GradCAM = ReLU( Σ_k α^c_k · A^k )
```

**Que dice:** `A^k` es el k-esimo feature map de la ultima capa convolucional. `α^c_k` es el peso de ese feature map para la clase `c`. La activacion final es la combinacion ponderada (con ReLU para enfatizar lo positivo).

**Por que la ultima capa conv:** es donde la informacion espacial todavia existe pero el modelo ya integro semantica de alto nivel. Antes de la capa final esta puramente espacial; despues del global pooling se pierde la posicion.

**Que vimos en Q-Shield:** el modelo atiende zonas de datos (no finder patterns), y los mapas agregados por clase muestran asimetria izquierda-derecha. La correlacion de los mapas-diferencia entre datasets es r=0.43 — la señal estructural es real, no dataset-specific.

---

# PARTE III — PRACTICA: EXPERIMENTOS Y NUMEROS

## 14. Datasets

**Trad et al. 2025:** 9,987 matrices binarias 69x69 (50% benigno / 50% phishing). QR version 13, EC `low`. URLs benignas de Alexa top-1M; maliciosas de PhishTank.

**CIC Trap4Phish 2025:** ~1M QRs PNG variados (resoluciones 114-582 px, versiones 5-30). Submuestreamos 50,000 por clase para tractabilidad.

**Splits:** 80/20 train/val con seed 42, estratificado por clase. Set de validacion combinado: **21,998 muestras** (1,998 Trad + 20,000 CIC). Esto es 11x mas grande que la evaluacion mas grande previa.

**Decodificacion offline (para la rama de texto):** pyzbar sobre cada imagen. Implementamos un cascade para Trad (multiple polaridades, paddings, escalas) que da 100% de exito sobre matrices binarias 69x69. CIC tiene 4.3% de tasa de fallo total. El URL-cache se guarda en JSON en Drive y es idempotente.

## 15. Resultado headline (Table III del paper)

| Configuracion | AUC | Prec | Recall | F1 | FNR | Brier | ECE |
|---|---|---|---|---|---|---|---|
| Trad et al. (reportado, n=1,998) | 0.9133 | — | — | 0.890 | — | — | — |
| Q-Shield visual single seed | 0.8962 | 0.844 | 0.798 | 0.821 | 0.202 | 0.146 | 0.133 |
| Q-Shield visual ensemble + TTA | 0.9146 | 0.872 | 0.801 | 0.835 | 0.199 | — | — |
| Q-Shield text-only (DistilBERT) | 0.9592 | 0.923 | 0.931 | 0.927 | 0.069 | 0.066 | 0.045 |
| **Q-Shield fusion (visual+text)** | **0.9749** | **0.928** | **0.943** | **0.936** | **0.057** | **0.054** | **0.038** |

**Como se mide AUC:** Area Under the ROC Curve. AUC 1.0 = perfecto, AUC 0.5 = aleatorio, AUC 0.9749 = excelente.

**Como se mide F1:** `F1 = 2·(precision·recall)/(precision+recall)`. Combina precision y recall en un solo numero.

**Como se mide FNR:** `FNR = FN/(FN+TP) = 1 - recall`. FNR 0.057 = de cada 100 phishing reales, 5.7 se escapan. Cumple la tolerancia conservadora ≤10%.

**Comparacion con Trad:** **+6.16 pp AUC** sobre un benchmark **11x mas grande** y heterogeneo.

## 16. Ablation Study — visual single-seed (Table V panel a)

Quitamos de a una cada decision arquitectonica del visual:

| Variante | AUC | Δ AUC | FNR | Δ FNR |
|----------|-----|-------|-----|-------|
| A1: Full Q-Shield (single seed) | 0.8962 | baseline | 0.2017 | baseline |
| A2: Sin Siamese pretraining | 0.8764 | -0.020 | 0.2670 | +6.5 pp |
| A3: BCE (sin focal) | 0.8771 | -0.019 | 0.2705 | +6.9 pp |
| A4: Sin frozen start | 0.8810 | -0.015 | 0.2298 | +2.8 pp |
| A5: Head pequeño | 0.8752 | -0.021 | 0.2290 | +2.7 pp |

**Refinamientos en inferencia (Table V panel b — cumulativos sobre visual):**

| Variante | AUC | Δ AUC vs single seed |
|----------|-----|---------------------|
| B0: Single seed | 0.8962 | baseline |
| B1: + TTA (h-flip avg) | 0.9053 | +0.009 |
| B2: + 2-seed ensemble | 0.9146 | +0.018 |

**La fusion multimodal (no parte del ablation visual) suma +0.060 sobre B2.** Es por mucho la palanca de mayor impacto del proyecto.

## 17. Cross-Dataset Generalization (Table V panel c — single seed)

| Setup | AUC | F1 | FNR |
|-------|-----|-----|-----|
| CV1: Train CIC → Test Trad | 0.7178 | 0.6658 | 0.0000 |
| CV2: Train Trad → Test CIC | 0.5181 | 0.5166 | 0.4917 |
| CV3: Train Combined → Test Combined | 0.8962 | 0.8207 | 0.2017 |

**Interpretacion:**

- **CV1 (AUC 0.72, FNR 0):** El modelo entrenado solo en CIC se colapsa cuando ve Trad: predice todo como phishing.
- **CV2 (AUC 0.52):** Modelo entrenado en Trad (69x69 binarios) no procesa PNGs de variable resolucion → practicamente random.
- **CV3 (AUC 0.8962):** Combinado funciona porque el modelo ve ambas distribuciones.

**Insight metodologico:** ningun dataset solo es suficiente. El entrenamiento combinado no es conveniencia, es requisito. Citamos a Ganin & Lempitsky 2015 (DANN) en el paper.

## 18. XAI findings

**Grad-CAM:**

- Finder patterns (esquinas): atencion baja → modelo los ignora correctamente.
- Zonas de datos: atencion alta → modelo aprende donde mirar.
- Agregado: benignos atienden a la izquierda, phishing al centro-derecha (URLs phishing son mas largas, empujan codewords hacia la derecha).

**Per-dataset Grad-CAM:** correlacion r=0.43 entre los mapas-diferencia de Trad y CIC. Patron parcialmente compartido (no es solo del dataset) y parcialmente especifico (la resolucion afecta el detalle).

**SHAP:** top-20 dimensiones del embedding 128-d concentran la mayoria de la señal. Las 108 restantes contribuyen poco. El embedding esta sobre-parametrizado y se podria podar a 32-64 dim sin perder rendimiento.

**Embedding distances:**
- Benigno-Benigno: 0.501
- Phishing-Phishing: 0.458 (phishing mas compacto que benigno)
- Benigno-Phishing: 0.928
- **Separation ratio inter/intra: 1.94**

**Calibracion del fusion:** Brier 0.054, ECE 0.038. Mejora 3x sobre el visual solo (Brier 0.146, ECE 0.133). El fusion no es solo mejor ranker, es mejor estimador probabilistico — relevante para deployments que necesitan probabilidades calibradas.

## 19. Per-resolution analysis del visual (Table VIII)

| Bucket | Tamaño (px) | n | AUC | F1 | FNR |
|--------|-------------|---|-----|-----|-----|
| Small | 114-198 | 1,561 | 0.940 | 0.885 | 0.132 |
| Medium-small | 222 | 1,446 | 0.928 | 0.860 | 0.214 |
| Large | 246-582 | 993 | 0.844 | 0.739 | 0.311 |

**Observacion:** AUC cae monotonicamente con el tamaño. QRs grandes pierden detalle de modulo cuando se redimensionan a 224x224. Multi-scale training es future work explicito.

---

# PARTE IV — VALIDACION Y JUSTIFICACION

## 20. ¿Como validamos cada claim del paper?

**Claim 1: "Pivote multimodal supera al SOTA visual"**
- Evidencia: Table V multimodal. Fusion AUC 0.9749 vs Trad 0.9133 = +6.16 pp.
- Reproducible: notebook 10.

**Claim 2: "El fusion gana al text alone"**
- Evidencia: AUC 0.9749 (fusion) vs 0.9592 (text). +1.57 pp AUC.
- Reproducible: notebook 10. La fusion explota el caso UNDECODABLE.

**Claim 3: "FNR 0.057 cumple tolerancia ≤10% sin calibracion"**
- Evidencia: eval_multimodal.json. FNR 0.0567 a threshold 0.5.
- Implicacion: threshold calibration deja de ser load-bearing claim.

**Claim 4: "Calibracion 3x mejor que visual"**
- Evidencia: Brier 0.054 (fusion) vs 0.146 (visual), ECE 0.038 vs 0.133.

**Claim 5: "Visual branch es fallback graceful"**
- Evidencia: Trad decode rate 100%, CIC 95.7%. El visual sigue activo en el ~4.3% de casos UNDECODABLE.

**Claim 6: "Cross-dataset analysis valida el entrenamiento combinado"**
- Evidencia: Table V panel c (CV1, CV2, CV3). Single-corpus se colapsa.

**Claim 7: "Modelo explicable a dos niveles"**
- Evidencia: Fig 5-8 (Grad-CAM + SHAP).

**Claim 8: "Mobile-deployable"**
- Evidencia: visual single 3.08M params (12 MB), fusion 69M params (267 MB con DistilBERT). CPU latency ~25ms (visual solo) o ~95ms (fusion).

## 21. Hiperparametros — por que los elegimos

| Hyperparam | Valor | Por que |
|-----------|-------|---------|
| Embedding dim (visual) | 128 | Standard en metric learning. SHAP confirma sobre-parametrizacion → poda futura posible. |
| Margin (contrastive) | 1.5 | Grid search {0.5, 1.0, 1.5, 2.0, 2.5}. Menores underfit. |
| Dropout (visual) | 0.35 | Grid search {0.3, 0.4, 0.5}. v1 (0.3) overfit, v2 (0.5) underfit. |
| Weight decay | 2e-4 | Standard para ImageNet fine-tuning. |
| LR Phase 1 | 2e-4 | AdamW con cosine warm restarts. |
| LR Phase 2 (frozen) | 5e-4 | Mas alto porque solo entrena la cabeza. |
| LR Phase 2 (unfrozen) | 1e-4 | Menor para no destruir embeddings preentrenados. |
| Epochs Phase 1 | 40 max + early stop 8 | Warm restarts cada 15 permiten escapar plateaus. |
| Epochs Phase 2 | 20 (5 frozen + 15 unfrozen) | Tipico para fine-tuning. |
| Frozen epochs | 5 | Ablation A4 justifica empiricamente. |
| Focal α | 0.5 | Clases balanceadas → α=0.5. |
| Focal γ | 2.0 | Standard (Lin et al. 2017). |
| Batch size visual | 128 (A100) / 64 (T4) | Memory vs estabilidad estadistica. |
| Data augmentation | Solo H-flip | QR tienen orientacion semantica → no rotar. |
| Text model | DistilBERT 66M | Trade-off latencia/accuracy. ModernBERT como alternativa. |
| Text max_length | 96 tokens | Cubre la distribucion de URLs en ambos corpus. |
| Text epochs | 3 | Suficiente para convergencia con focal loss. |
| Text LR | 2e-5 | Standard para fine-tune de transformers. |
| Fusion hidden | 16 | 3→16→1 = 161 params. Suficiente para calibrar 2 logits. |
| Fusion LR | 1e-3 | Mayor porque la fusion es mas chica. |
| Fusion epochs | 20 | Convergencia en <1 min sobre features cacheadas. |

## 22. Defensa contra criticas comunes

**Critica 1: "¿Por que no SimCLR?"**

Lo que hacemos en Phase 1 visual es **supervised contrastive** (Chopra 2005 / Khosla 2020 SupCon), no self-supervised. Usamos las etiquetas para formar pares. SimCLR seria self-supervised y queda como future work.

**Critica 2: "+6 pp es estadisticamente significativo?"**

Trad reporta sobre n=1,998 → IC 95% ≈ ±0.012. Nosotros sobre n=21,998 → IC 95% ≈ ±0.004. La diferencia 6 pp esta muy lejos de los IC superpuestos: es estadisticamente robusta.

**Critica 3: "Decodificar no es lo que ataca el QR?"**

Decodificar con pyzbar es local, deterministico, sin red. Confunde leer (string) con abrir (fetch + render). El paper lo aclara explicitamente.

**Critica 4: "La FNR 0.057 sigue siendo demasiado alta?"**

Cumple la tolerancia conservadora ≤10% en seguridad. Para deployments con tolerancias mas estrictas, sliding del threshold a 0.4 baja el FNR del visual fallback a 0.098. Future work: cost-sensitive fine-tuning.

**Critica 5: "Text branch domina, ¿el visual aporta algo?"**

Si: AUC 0.9749 (fusion) vs 0.9592 (text). +1.57 pp. La fusion explota el caso UNDECODABLE (4.3% del corpus) donde solo el visual esta disponible.

**Critica 6: "¿Por que no ResNet o ViT?"**

Mobile deployability. ResNet-50 son 25M params, ViTs igual o mas. Visual de Q-Shield son 3M params. Para escanear QRs en moviles, eso importa.

**Critica 7: "¿Por que combinar Trad y CIC?"**

Cross-dataset analysis (Table V panel c) muestra que individualmente NO generalizan. Combined training es requisito metodologico, no conveniencia.

**Critica 8: "Quedan limitaciones?"**

Si — siete reportadas en Section VI.B: FNR del fallback visual, overfitting Phase 2 visual, URL overlap no verificado, accuracy en QRs grandes, calibracion del visual, scope unimodal del contexto que rodea (email subject, sender), container-format, robustez adversarial.

---

# PARTE V — CHEAT SHEET PARA DEFENDER EL PAPER

## 23. Respuestas rapidas a preguntas esperadas

**"¿Cual es la contribucion principal?"**

> Primer framework multimodal end-to-end para quishing que fusiona la rama visual Siamese con la rama URL DistilBERT, con manejo explicito del caso UNDECODABLE. Supera el SOTA visual (Trad 0.9133) en +6.16 pp AUC en un benchmark 11x mas grande, y alcanza FNR 0.057 al threshold default — cumple la tolerancia de seguridad sin calibracion.

**"¿Por que multimodal y no visual-only?"**

> Tres razones. La señal visual sola es estructuralmente debil en QRs heterogeneos (CIC SSIM 0.34, F1 0.88). La señal URL es fuerte pero requiere decodificar — y la decodificacion offline con pyzbar no carga el riesgo del browser-fetch. Combinar ambas con un fusion calibrado domina por construccion (Bountakas 2023, Khalifa 2025) y nos da ademas un fallback graceful para QRs no decodificables.

**"¿Como manejan el caso UNDECODABLE?"**

> Flag binario explicito en el input del fusion. La cabeza aprende automaticamente "cuando flag=1, ignora text logit y usa visual logit". El 4.3% del corpus que no decodifica es atendido por el visual sin perdida cualitativa — el ablation muestra que el fusion gana +1.57 pp sobre text-only precisamente porque cubre ese caso.

**"¿Por que Siamese contrastive en la rama visual?"**

> Siamese aprende un espacio metrico (distancias) en lugar de una frontera de decision directa. Generaliza mejor con datos limitados. Ablation A2 confirma: sin pretraining contrastivo el AUC visual cae 2 pp y el FNR sube 6.5 pp.

**"¿Por que Contrastive Loss y no Triplet?"**

> Contrastive es mas simple, converge mas rapido. Nuestro separation ratio 1.94 demuestra que es suficiente para esta tarea. Triplet es future work si necesitamos separacion mas agresiva.

**"¿Por que MobileNetV2 y no ResNet?"**

> Edge deployability. ResNet-50 son 25.6M params; MobileNetV2 son 3.08M (10x menos). Diferencia de AUC marginal en esta tarea, pero la diferencia de footprint es decisiva para mobile.

**"¿Por que DistilBERT y no ModernBERT o DeepSeek?"**

> Trade-off latencia/accuracy. DistilBERT es 66M params, ModernBERT 150M+, DeepSeek-R1-Distill 671M+. CIC reporta DeepSeek con F1 0.99 vs DistilBERT 0.96. Para mobile vale la pena el trade-off. Future work: probar ModernBERT como rama text mas grande.

**"¿La FNR de 0.057 es aceptable para production?"**

> Si — cumple la tolerancia conservadora ≤10% que se usa convencionalmente en deteccion de phishing. Para SLAs mas estrictos, threshold sliding a 0.4 baja el FNR del visual fallback a 0.098. La fusion en si esta ya por debajo del target.

**"¿Como justifican el training combinado?"**

> Cross-dataset analysis (Table V panel c). CIC-only → Trad: AUC 0.72 con classifier collapse. Trad-only → CIC: AUC 0.52, practicamente random. Combinado: AUC 0.8962 visual / 0.9749 fusion. Single-corpus no funciona; combinar es requisito metodologico.

**"¿Que pasa si el attacker conoce Q-Shield?"**

> Adversarial robustness es limitacion explicita en el paper. Future work: adversarial training + randomized smoothing. Mitigacion arquitectonica: la dual-branch hace mas dificil un attack que requiere fooling visual + URL simultaneamente.

**"¿Como se compara con CIC Trap4Phish?"**

> CIC text-only F1 0.97-0.99 con LLMs grandes (DeBERTa, ModernBERT, DeepSeek). Q-Shield text-only F1 0.927, fusion F1 0.936. No superamos a CIC en URL pura pero ofrecemos un detector multimodal con manejo explicito del caso UNDECODABLE — algo que CIC no aborda. Con un LLM mas grande cerrariamos la brecha en text-only.

**"Si el text branch es lo que mas pesa, ¿por que mantienen el visual?"**

> Tres razones. Una: cuando el QR no decodifica, el visual es la unica señal. Dos: el flag UNDECODABLE en el fusion explota esto explicitamente — quitarlo + text-only daria peor performance en ese subset. Tres: el visual aporta interpretabilidad espacial (Grad-CAM) que el text branch no tiene.

---

## 24. Un parrafo de defensa final (si te preguntan "¿En 30 segundos que hicieron?")

> "Desarrollamos Q-Shield, un framework multimodal de deteccion de quishing que fusiona una rama visual Siamese sobre la imagen del QR con una rama transformer (DistilBERT) sobre la URL decodificada offline. La fusion es un MLP pequeño que toma los dos logits mas un flag de undecodable y produce la probabilidad final. Evaluamos sobre 21,998 muestras combinadas de Trad et al. y CIC Trap4Phish 2025 — 11 veces mas grande que la evaluacion mas grande previa. La configuracion fusion alcanza AUC 0.9749, F1 0.936 y FNR 0.057, superando el SOTA visual previo (Trad 0.9133) por +6.16 puntos y cumpliendo la tolerancia de seguridad ≤10% al threshold default sin necesidad de calibracion. La rama visual sola alcanza AUC 0.8962 y permanece como fallback graceful cuando el QR no se puede decodificar. Confirmamos cross-dataset que single-corpus no generaliza — el entrenamiento combinado es requisito metodologico. La explicabilidad es dual: Grad-CAM espacial (validado per-dataset con r=0.43) y SHAP sobre el embedding 128-d. La calibracion del fusion (Brier 0.054, ECE 0.038) es 3x mejor que el visual solo. El framework es mobile-deployable: visual ~25ms en CPU, fusion completa ~100ms — dentro del budget perceptivo movil. Limitaciones explicitas en seven puntos; provenance-aware detection y multi-scale training como direcciones de future work."

---

*Documento preparado por Nicolas Llerena Silva — Mayo 2026*
*Validacion integral del proyecto Q-Shield — pivote multimodal*
