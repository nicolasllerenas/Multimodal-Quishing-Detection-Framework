# Guion de presentación — Q-Shield

**Audiencia:** Aurea Soriano-Vargas (asesora)
**Duración objetivo:** 25–30 min + Q&A
**Slides:** 39 (en `Q-Shield_Presentacion_Asesora_v2.pptx`)
**Idioma:** español

---

## Antes de empezar

- Abre el `.pptx` en presentación, y en otra pestaña ten el **paper PDF** y el **GitHub** por si la asesora pide ver código.
- Postura: voz pausada, mira más a la asesora que a la pantalla.
- Si te interrumpe con una pregunta, **respóndela en el momento** y vuelve al hilo. No te apresures por terminar.
- Tu mejor herramienta es la honestidad metodológica. La slide 20 (la reconciliación) es el corazón emocional de la presentación.

---

## Slide 1 — Portada *(~30 s)*

> "Buenas tardes profesora. Voy a presentarle Q-Shield, el trabajo que hemos venido desarrollando estos meses. El título completo es 'An Explainable Siamese Network for Scalable Quishing Detection Without Payload Decoding'. La idea central es detectar phishing en códigos QR sin necesidad de decodificarlos."

*Arranque calmado. No leas el subtítulo entero, solo la idea.*

---

## Slide 2 — Agenda *(~45 s)*

> "La presentación está organizada en seis partes. Primero, el problema y por qué es importante. Segundo, la metodología — arquitectura, fórmulas, código. Tercero, el setup experimental: datasets e iteraciones. Cuarto, los resultados, que voy a contar como una narrativa: cómo detectamos un número inconsistente, cómo lo reconciliamos honestamente, y cómo terminamos superando al SOTA. Quinto, explicabilidad y deployment. Y al final, limitaciones, future work y plan de submission."

---

## Slide 3 — Part 01: The Problem *(~15 s)*

> "Empecemos por el problema."

*Slide divisora. Brevísima.*

---

## Slide 4 — Quishing es ingeniería social *(~90 s)*

> "El quishing — combinación de QR y phishing — es esencialmente un ataque de ingeniería social, no técnico. Mitnick y Hadnagy describen exactamente este patrón: el atacante busca inducir una acción impulsiva, de baja escrutinio. Los QR codes son casi un medio perfecto: son opacos al ojo humano, se activan con un solo gesto, y se presentan en contextos que implícitamente los marcan como legítimos — menús de restaurante, parquímetros, facturas en PDF.
>
> Los datos respaldan la urgencia. El reporte de Verizon DBIR 2024 identifica al phishing como vector líder de acceso inicial. IBM reporta costos en millones por incidente. Y trabajos recientes muestran que el quishing tiene la misma tasa de éxito que el phishing tradicional, con menos defensas existentes."

*Aquí muestras la motivación. No vendas el modelo todavía — vende el problema.*

---

## Slide 5 — Cuatro research gaps *(~90 s)*

> "Cuando revisamos la literatura encontramos cuatro huecos concretos. Primero: dependencia de decodificación. Los detectores que funcionan bien necesitan abrir el QR antes de clasificarlo, lo cual contradice el propósito de protegernos del payload. Segundo: ningún trabajo previo evalúa cross-dataset; cada paper reporta sobre su propio corpus. Tercero: la explicabilidad existente es parcial — o pixel o feature, pero no ambas. Y cuarto: ningún paper caracteriza puntos de operación; todos reportan threshold 0.5 sin pensar en deployment."

*El cuarto gap (operational characterization) es el más original. Léelo con énfasis.*

---

## Slide 6 — Cinco contribuciones *(~75 s)*

> "De ahí salen las cinco contribuciones de Q-Shield. Primera: somos la primera aplicación de Siamese Network con contrastive learning a quishing — separación inter sobre intra clase de 1.94. Segunda: el benchmark cross-dataset de 21,998 muestras, 11 veces más grande que cualquier evaluación previa. Tercera: zero-decoding por construcción. Cuarta: threshold calibration explícita para FNR menor o igual a 0.10. Y quinta: explicabilidad dual — Grad-CAM y SHAP — validada per-dataset."

*Si te preguntan cuál es la contribución más fuerte: el cross-dataset benchmarking. Eso es lo que hace al paper único.*

---

## Slide 7 — Related work *(~60 s)*

> "En esta tabla situamos Q-Shield contra los trabajos previos. Note dos cosas: somos los únicos en la columna 'Cross-dataset', y los únicos en combinar zero-decoding, deep learning, evaluación cross-dataset y dual XAI. Trad et al. 2025 es el competidor directo más relevante — también opera sobre la imagen sin decodificar, con XGBoost sobre pixels crudos. Reportan 0.913 AUC sobre 1,998 muestras de una sola versión de QR."

*El asterisco junto al 0.95 de Nejati: menciónalo. "El 0.95 de CIC es sobre URLs ya decodificadas, no comparable directamente."*

---

## Slide 8 — Part 02: Methodology *(~15 s)*

> "Pasemos a la metodología."

---

## Slide 9 — Arquitectura completa *(~120 s)*

> "Esta es la arquitectura completa del pipeline. De izquierda a derecha tenemos seis pasos en la cadena principal: la imagen QR cruda entra en cualquier resolución, se preprocesa a 224 por 224 grayscale, pasa por un backbone Siamese basado en MobileNetV2 con pesos compartidos. El backbone produce un embedding de 128 dimensiones L2-normalizado, que alimenta una cabeza clasificadora densa, y sale una probabilidad sigmoide.
>
> Las dos cajas naranjas debajo son las pérdidas de entrenamiento. Phase 1: contrastive loss sobre pares de imágenes con margen 1.5. Phase 2: focal loss con gamma igual a 2 y alpha 0.5.
>
> En la fila de abajo están las dos mejoras de inferencia: averaging por horizontal-flip — TTA — y promediado entre dos modelos entrenados con seeds distintos. Y al final, la capa de explicabilidad: Grad-CAM y SHAP."

*Esta es la slide más importante de la presentación. Tómate tu tiempo. Si la asesora pregunta acá, tienes la base para responder cualquier cosa de las próximas 10 slides.*

---

## Slide 10 — Problem formulation *(~45 s)*

> "Formalmente, queremos aprender un clasificador f que mapee una imagen QR a una probabilidad, sin decodificar el contenido. Lo factorizamos en dos componentes: h-psi es la función de embedding (el backbone), g-phi es la cabeza clasificadora, y sigma es la sigmoide. Entrenamos h-psi y g-phi en dos fases distintas — esa es la decisión metodológica clave."

---

## Slide 11 — Contrastive Loss *(~75 s)*

> "Phase 1 usa la contrastive loss canónica de Chopra, Hadsell y LeCun de 2005. Para pares de la misma clase, y igual a cero, queremos minimizar la distancia al cuadrado. Para pares de clases distintas, y igual a uno, queremos que la distancia sea al menos el margen m, que en nuestro caso es 1.5. Si la distancia ya supera el margen, no hay penalización. La intuición: misma clase se atrae, clases distintas se repelen hasta el margen.
>
> El margen 1.5 lo elegimos por grid search sobre 0.5, 1.0, 1.5, 2.0 y 2.5. Margenes menores produjeron underfitting; mayores no agregaron beneficio."

---

## Slide 12 — Focal Loss *(~75 s)*

> "Phase 2 usa focal loss, de Lin et al. 2017. La idea es modular la entropía cruzada con un factor de uno menos p elevado a gamma, que reduce el peso de los ejemplos fáciles y aumenta el de los difíciles. Usamos gamma igual a 2 — el estándar — y alpha 0.5 porque las clases están balanceadas después del muestreo.
>
> En seguridad esto importa mucho. Un falso negativo expone al usuario al ataque; un falso positivo solo dispara una advertencia. Esa asimetría de costo es exactamente lo que focal loss optimiza. En nuestro ablation, reemplazar focal con BCE estándar mantiene el AUC pero sube el FNR de 0.20 a 0.27."

---

## Slide 13 — Código: Backbone *(~75 s)*

> "Esta es la implementación del backbone, en el archivo siamese_qr.py del repositorio. Tres adaptaciones clave. Primero, la primera convolución la cambiamos de tres canales a uno para input grayscale. Segundo, los pesos los inicializamos como la media de los pesos RGB del modelo pre-entrenado en ImageNet — eso preserva el prior. Y tercero, después del global pooling tenemos una proyección de 1280 a 512 a 128, con BatchNorm y Dropout 0.3, terminando en normalización L2 para que todos los embeddings vivan en la hiperesfera unitaria. Total: 3.08 millones de parámetros, 12 megabytes en disco."

*Si la asesora pide ver el código real, abres el repo en otra ventana — es exactamente este snippet.*

---

## Slide 14 — Código: Phase 1 *(~60 s)*

> "El loop de Phase 1. Optimizer AdamW con learning rate dos por diez a la menos cuatro y weight decay del mismo valor. Scheduler cosine con warm restarts cada 15 epochs — eso ayuda a escapar plateaus. Hasta 40 epochs con early stopping de paciencia 8. Por cada batch hacemos forward sobre los dos inputs del par, calculamos la contrastive loss, y aplicamos clipping de gradientes a 1.0 para estabilidad. Augmentation solamente flip horizontal — la rotación la quitamos a propósito porque los finder patterns del QR codifican orientación."

---

## Slide 15 — Código: Phase 2 *(~75 s)*

> "Phase 2 tiene una mecánica de dos sub-fases. Las primeras 5 epochs entrenamos solo la cabeza clasificadora — el backbone está congelado. Eso le da estabilidad a una cabeza inicializada al azar antes de tocar el backbone pre-entrenado. En la epoch 6 descongelamos todo y hacemos fine-tuning end-to-end por 15 epochs más, con un learning rate más bajo. La best epoch típicamente es la 8.
>
> El ablation A4 confirma que sin este frozen-start perdemos 1.5 puntos de AUC."

---

## Slide 16 — Part 03: Experimental Setup *(~15 s)*

> "Pasemos a la parte experimental."

---

## Slide 17 — Datasets *(~75 s)*

> "Trabajamos con dos corpus complementarios. Trad et al. tiene 9,987 matrices binarias de 69 por 69, todas de QR versión 13 — un dataset limpio y homogéneo. CIC Trap4Phish 2025 es de la Universidad de New Brunswick: más de un millón de QRs en formato PNG, resoluciones variables de 114 a 582 píxeles, y versiones de QR de 5 a 30. De CIC tomamos un sample estratificado de 100 mil — 50 mil por clase — por capacidad de cómputo.
>
> Todo lo normalizamos a 224 por 224 grayscale antes del CNN. Splits 80/20 con seed 42, y el set de validación combinado tiene 21,998 muestras."

---

## Slide 18 — Iteration history *(~120 s)*

> "Aquí está el diario de investigación, sin filtro. v1 fue el primer intento entrenado solo con Trad y embedding de 64 dimensiones. AUC 0.886, pero con un gap brutal de 30 puntos entre train y validation — overfitting severo. v2 fue la sobrecorrección: agregamos CIC, subimos dropout a 0.5, bajamos margen a 1.0, y agregamos rotación como augmentation. Resultado: 0.868 — peor que v1, porque la rotación rompe los finder patterns y el dropout tan alto subentrena.
>
> v3 fue el equilibrio. Margen 1.5, dropout 0.35, sin rotación. Single seed sobre el set completo: 0.896. Honestamente, eso está debajo de Trad por 1.71 puntos.
>
> Las dos últimas filas son las mejoras de inferencia: TTA suma 0.91 puntos. Ensemble de dos seeds suma otros 0.93. Resultado final: 0.9146 — supera a Trad por 0.13 puntos."

*Esta slide es donde se nota que esto fue un proceso real. La asesora va a apreciar la honestidad.*

---

## Slide 19 — Part 04: Results *(~15 s)*

> "Y ahora los resultados."

---

## Slide 20 — La reconciliación *(~150 s — slide crítica)*

> "Aquí está el momento más importante del proyecto, profesora, y se lo quiero contar tal cual fue.
>
> Inicialmente reportamos 0.9254 como AUC en la ablation A1 — el número en rojo. Cuando hicimos la auditoría completa, detectamos que la confusion matrix de la Figura 4 — TN 9,382, FP 1,619, FN 2,220, TP 8,777 — matemáticamente da F1 igual a 0.821 y FNR 0.20, no los 0.858 y 0.166 que reportábamos.
>
> Volvimos a evaluar el mismo checkpoint sobre el set completo de 21,998 muestras. El número real fue 0.8962 — el dorado. El 0.9254 venía de evaluar A1 sobre un subset, no sobre el set completo. Eran dos números silenciosamente distintos.
>
> Esa fue la base honesta. Aplicamos TTA y ensemble de dos seeds y llegamos al 0.9146 — el verde — que sí supera a Trad. Toda la auditoría quedó documentada con scripts en el repositorio. Cada número del paper es trazable a una corrida específica."

*Pausa después de esta slide. Esta es la diapositiva por la cual la asesora va a respetar más el trabajo. Si interrumpe con preguntas, déjala.*

---

## Slide 21 — Hero result *(~30 s)*

> "El resultado titular: AUC 0.9146 con la configuración de ensemble más TTA, sobre las 21,998 muestras del set heterogéneo combinado. F1 de 0.835, recall 0.801, FNR 0.199. Por encima de Trad por 0.13 puntos, en un benchmark 11 veces más grande."

*Pausa. Que el número se asiente.*

---

## Slide 22 — Inference improvements *(~75 s)*

> "Las dos mejoras de inferencia. TTA — Test-Time Augmentation — promedia la salida sobre la imagen original y su flip horizontal. Cuesta dos forwards por QR. Gana 0.91 puntos de AUC.
>
> Ensemble: dos modelos con seeds distintos pero los mismos splits de datos. La diversidad viene puramente de la estocasticidad del optimizador. Cuesta cuatro forwards por QR. Gana otros 0.93 puntos sobre TTA solo.
>
> En total: 1.84 puntos sumados, sin tocar la arquitectura."

---

## Slide 23 — Main results table *(~75 s)*

> "Tabla principal. Los baselines handcrafted están todos clavados en 0.81 — los features son el cuello de botella, no el clasificador. Trad reporta 0.913 sobre 1,998 muestras. Nuestras tres configuraciones: single seed 0.896, single seed más TTA 0.905, y ensemble más TTA 0.915. La precision sube notablemente con el ensemble — de 0.844 a 0.872."

---

## Slide 24 — Confusion matrix + ROC *(~60 s)*

> "Esta es la Figura 4 del paper. La matriz a la izquierda: 9,703 verdaderos negativos, 1,298 falsos positivos, 2,192 falsos negativos, 8,805 verdaderos positivos. La curva ROC a la derecha muestra el AUC 0.915. Los dos puntos marcados: el negro es el threshold default 0.5; el verde es el threshold calibrado a 0.4 que cumple FNR menor o igual a 10%."

---

## Slide 25 — Ablation *(~90 s)*

> "El ablation isola cada decisión. Sin Siamese pretraining, A2: pierde 2 puntos de AUC, sube el FNR 6.5 puntos. Sin focal loss, A3: pequeño cambio en AUC pero el FNR se dispara 7 puntos — exactamente lo que predice la teoría. Sin frozen start, A4, y con cabeza pequeña, A5: cada uno cuesta entre 1.5 y 2 puntos de AUC.
>
> Lo importante es que todas las decisiones tienen evidencia empírica. Y todas operan sobre el modelo single-seed sin TTA, para aislar la contribución arquitectónica."

---

## Slide 26 — Cross-dataset *(~90 s)*

> "Cross-dataset analysis. Si entrenamos solo con CIC y testeamos en Trad — CV1 — el AUC cae a 0.72 pero el clasificador colapsa hacia la clase positiva: predice todo como phishing, FNR cero, recall cien por ciento. Si entrenamos solo con Trad y testeamos en CIC — CV2 — caemos a 0.52, prácticamente aleatorio.
>
> CV3, con ambos datasets combinados, es la única configuración viable. Esto valida que el entrenamiento combinado no es conveniencia, es requisito metodológico. Lo posicionamos en el paper como domain-invariant learning, citando a Ganin y Lempitsky de 2015."

---

## Slide 27 — Threshold calibration *(~75 s)*

> "Cuatro puntos de operación obtenidos haciendo sweep del threshold de 0.05 a 0.95. El default 0.5 nos da FNR 0.182. Si bajamos a 0.4, el FNR cae a 0.098 — cumple la tolerancia conservadora de seguridad — a un costo modesto en precision. Para deployments más agresivos, threshold 0.3 lleva el FNR a 0.039 pero la precision baja a 0.61.
>
> El punto importante: el modelo es un buen ranker, el AUC es threshold-independent y alto. La elección del threshold es una decisión de deployment, no de modelo."

---

## Slide 28 — Part 05: Explainability & Deployment *(~15 s)*

> "Explicabilidad y deployment."

---

## Slide 29 — Grad-CAM *(~90 s)*

> "Aplicamos Grad-CAM al último bloque inverted-residual del MobileNetV2. A la izquierda, ejemplos representativos: 6 QRs benignos arriba, 6 phishing abajo, cada uno con su mapa de atención. Los finder patterns en las tres esquinas — top-left, top-right, bottom-left — quedan consistentemente oscuros. El modelo correctamente los ignora, porque son class-invariant.
>
> A la derecha, los mapas agregados sobre 200 muestras por clase. Los benignos concentran atención a la izquierda; los phishing a la centro-derecha. La interpretación plausible: las URLs phishing son más largas, empujan más codewords a posiciones de la derecha del QR."

---

## Slide 30 — SHAP + embeddings *(~75 s)*

> "A la izquierda, SHAP sobre las 128 dimensiones del embedding. La dimensión más importante contribuye 0.016 de SHAP promedio, decreciendo suavemente a 0.005 en la posición 20. Las otras 108 dimensiones contribuyen casi nada — el embedding está sobre-parametrizado para esta tarea binaria. Una versión podada a 32 o 64 dimensiones probablemente mantendría el rendimiento.
>
> A la derecha, distancias en el espacio de embedding. Benigno-benigno 0.501, phishing-phishing 0.458, benigno-phishing 0.928. Ratio inter sobre intra: 1.94. El contrastive learning hizo lo que tenía que hacer."

---

## Slide 31 — Per-dataset Grad-CAM *(~75 s)*

> "Una preocupación natural: ¿la asimetría izquierda-derecha que vimos antes es señal real o artefacto de mezclar matrices binarias 69 por 69 con PNGs antialiased? Para descartarlo, recomputamos los mapas Grad-CAM por separado en Trad y en CIC, y medimos la correlación pixel a pixel entre los mapas de diferencia.
>
> El resultado: r igual a 0.43, una correlación moderada. No es uno — no es un patrón perfectamente universal. No es cero — no es solo del dataset. La señal estructural de phishing es genuinamente compartida entre ambos corpus."

---

## Slide 32 — Inference cost *(~60 s)*

> "Costo de inferencia. Cada modelo es 3.08 millones de parámetros, 12 megabytes en disco. CPU latency 24.9 milisegundos para single-seed, 49.8 con TTA, 99.6 para el ensemble completo. En GPU T4 son 6, 12 y 24 milisegundos respectivamente.
>
> Los 100 milisegundos del ensemble caben dentro del presupuesto perceptivo móvil. Para deployments más restrictivos, el single-seed sacrifica 1.84 puntos de AUC a cambio de 4 veces menos cómputo."

---

## Slide 33 — Part 06: What's Next *(~15 s)*

> "Para cerrar: limitaciones y futuro."

---

## Slide 34 — Limitations *(~120 s)*

> "Reportamos siete limitaciones explícitas en la sección VI.B del paper. Primera: el FNR default de 0.199 está arriba del target de 0.10 — se mitiga con threshold calibration. Segunda: overfitting moderado en Phase 2 después del epoch 8, controlado con early stopping. Tercera: no verificamos URL overlap entre Trad y CIC porque Trad no redistribuye URLs.
>
> Cuarta: el rendimiento cae con QRs grandes — sobre 246 píxeles — porque el resize a 224 pierde detalle de módulo. Quinta: calibración probabilística imperfecta, ECE 0.13 — el modelo es buen ranker pero malo como estimador de probabilidades. Sexta: scope unimodal, no incluimos texto acompañante. Y séptima: no evaluamos robustez adversarial."

*Tu asesora valora que reportes esto. NO suavices, NO escondas. Reportarlo así te protege en el peer review.*

---

## Slide 35 — Future work *(~75 s)*

> "Cinco extensiones concretas. Primero, multimodal fusion: agregar una rama de texto. Segundo, multi-scale training. Tercero, provenance-aware detection — la próxima slide es un deep dive sobre esto. Cuarto, robustez adversarial. Quinto, deployment localizado por región — Yape en Perú, UPI en India, Pix en Brasil."

---

## Slide 36 — Provenance deep dive (Yape/BCP) *(~120 s)*

> "Este punto vale la pena desarrollarlo. Q-Shield responde una pregunta — ¿este QR tiene contenido malicioso? — pero no responde otra distinta — ¿fue generado por la fuente autorizada?
>
> El ejemplo concreto en contexto peruano: Yape, operado por BCP, genera QRs de comerciantes a través de un backend autenticado. Si un atacante físicamente pega un QR encima del QR legítimo de un comerciante en una bodega, o lo inyecta en la capa UI de un terminal comprometido, el QR puede tener contenido perfectamente válido — apunta a un número de cuenta real. Q-Shield no lo detectaría porque visualmente luce benigno.
>
> Para resolver eso necesitamos otra capa: firmas criptográficas en el payload del QR, validación del merchant ID contra el emisor, tokens de sesión, atestación de geolocalización. Q-Shield más provenance son capas ortogonales y complementarias, no competidoras. Lo dejamos planteado como future work directo."

*Esta slide aterriza el paper en contexto peruano. Tu asesora va a apreciar la concreción.*

---

## Slide 37 — Submission plan *(~60 s)*

> "El plan de submission. Primer target: IEEE Intercon — cabe perfectamente. Segundo: IEEE LA-CCI, también encaja. IEEE TrustCom como stretch.
>
> Antes de mandar queda recompilar el LaTeX en Overleaf, verificar que no queden referencias rotas, opcionalmente agregar una aclaración SimCLR vs supervised contrastive — el comentario que usted hizo, profesora — y un intervalo de confianza por bootstrap sobre el AUC para reforzar el claim estadístico."

*Aquí estás cerrando con un plan de acción. Si la asesora tiene comentarios, anótalos.*

---

## Slide 38 — Summary *(~75 s)*

> "El resumen en una slide: primer Siamese contrastive para quishing, benchmark 11 veces más grande, AUC 0.9146 supera el SOTA previo, variante single-seed para deployment más liviano, threshold calibrado para FNR menor a 10%, dual XAI validada cross-dataset, mobile-deployable, siete limitaciones reconocidas, cinco extensiones futuras. Listo para review y para submission a Intercon o LA-CCI."

---

## Slide 39 — Thank you *(~15 s)*

> "Gracias profesora. Quedo atento a sus preguntas y a sus sugerencias."

---

# Apéndice — Q&A anticipado

Respuestas listas para preguntas probables.

### "¿Por qué no usaron SimCLR si querían contrastive learning?"

> "Buena observación, profesora. Lo que hacemos en Phase 1 es supervised contrastive — usamos las etiquetas de clase para formar pares, citando a Chopra et al. 2005. SimCLR es self-supervised: forma pares con augmentations de la misma imagen, sin etiquetas. Una versión SimCLR-style sería pretraining sobre QRs no etiquetados antes del fine-tuning supervisado — lo dejamos como future work explícito. La cita moderna a lo que hacemos sería Khosla et al. 2020 — Supervised Contrastive Learning."

### "¿El +0.13 pp es estadísticamente significativo?"

> "Pregunta justa. Trad reporta sobre 1,998 muestras, intervalo de confianza al 95% aproximado de más-menos 0.012. Nosotros reportamos sobre 21,998, intervalo aproximado de más-menos 0.004 — once veces más estrecho. Los intervalos se sobreponen, pero el nuestro es estadísticamente mucho más confiable. Es la diferencia entre 'tenemos AUC similar' y 'tenemos AUC similar con 11 veces más certeza estadística'."

### "¿Por qué no entrenan un tercer seed para reforzar el ensemble?"

> "Lo consideramos. Los dos seeds que tenemos ya nos llevan al 0.9146 — supera el target. Un tercer seed probablemente agregue otros 0.5 pp pero también dobla el costo de inferencia. Es un trade-off que dejamos abierto."

### "¿La FNR de 0.199 en default es aceptable para producción?"

> "No directamente. Por eso reportamos la calibración: con threshold 0.4 el FNR cae a 0.098. La pregunta es de policy — qué tolerancia tiene el operador. El paper presenta el menú, no decide por el deployer."

### "¿Por qué MobileNetV2 y no ResNet o ViT?"

> "Restricción explícita: deployment móvil. ResNet-50 son 25 millones de parámetros, ViTs igual o más. Q-Shield son 3 millones por modelo. El delta de AUC en esta tarea es marginal, pero la diferencia de footprint es 8 veces. Para escanear QRs en un móvil, eso importa."

### "¿No deberían reentrenar la ablation A2-A5 sobre el set completo?"

> "Sí, sería más fuerte. Actualmente A2-A5 se entrenan sobre 40% del corpus por restricción de cómputo — está documentado en el footnote de la Tabla V. La nota explica que el ordenamiento cualitativo se preserva en ambos protocolos. Re-correr el ablation completo es realista en una próxima iteración con más GPU."

### "¿Por qué 1.94 de separation ratio? ¿Es un buen número?"

> "El ratio inter sobre intra de 1.94 significa que los pares de clases distintas están casi al doble de distancia que los pares de la misma clase, en promedio. En literatura de metric learning, ratios entre 1.5 y 2.5 se consideran buenos para tareas binarias — el 1.94 cae justo en ese rango. Si fuera 1.0 o menos, el contrastive no habría servido."

### "¿La diferencia con Trad no podría ser solo ruido del muestreo de CIC?"

> "Posible. Para hacer el claim más robusto, lo siguiente sería un bootstrap sobre el AUC — re-muestrear las 21,998 muestras con reemplazo varias veces y reportar el intervalo. Es un experimento de 30 minutos que vale la pena hacer antes del submit final."

### "¿Por qué no incluyen un comparador con Vision Transformers?"

> "Sería interesante. La razón principal: ViTs tienen un orden de magnitud más parámetros y necesitan datasets más grandes para aproximarse al optimum. Nuestro corpus de 100k es más natural para CNNs. Un comparador formal con ViT cabría como future work — si superan, el paper queda mejor; si no, refuerza la elección de MobileNetV2."

---

# Tips finales

- **Velocidad**: si terminas antes de los 30 minutos, mejor. Si te alargas, recorta los section dividers (slides 3, 8, 16, 19, 28, 33).
- **Cuando la asesora interrumpa**: para de avanzar, responde, después pregúntale "¿continúo?". No vuelvas a slides anteriores a menos que lo pida.
- **Si no sabes algo**: di "Eso no lo evalué directamente, pero si quiere lo investigo y le mando un follow-up esta semana." Mejor que inventar.
- **Cuándo enfatizar**: slides 18 (iteraciones), 20 (reconciliación), 31 (per-dataset Grad-CAM) y 36 (Yape/BCP). Esas son las slides donde se nota el rigor metodológico y la concreción del trabajo.
- **Cierre**: si pregunta cuándo enviamos a Intercon/LA-CCI, di "Apenas usted dé luz verde, profesora — el paper ya pasó por la auditoría completa. Si me pide los dos cambios opcionales que mencioné, los aplico esta semana."

---

# Tiempos resumen (39 slides)

| Sección | Slides | Tiempo aprox |
|---|---|---|
| Apertura (cover + agenda + divider) | 1–3 | 1.5 min |
| Problema + gaps + contribuciones + related | 4–7 | 5 min |
| Divider + arquitectura + fórmulas | 8–12 | 6 min |
| Código (3 slides) | 13–15 | 3.5 min |
| Divider + datasets + iteraciones | 16–18 | 4 min |
| Divider + reconciliación + hero + improvements | 19–22 | 6 min |
| Tablas y figuras de resultados | 23–27 | 6 min |
| Divider + XAI (3 slides) + inference cost | 28–32 | 6 min |
| Divider + limitations + future + provenance + submission | 33–37 | 7 min |
| Summary + thanks | 38–39 | 1.5 min |
| **Total** | **39** | **~46 min** |

**Si necesitas comprimir a 25 min**, recorta:
- Slides de código (14 y 15) — solo muestra una.
- Slide 27 (threshold) — comprime a 30 segundos.
- Slide 36 (provenance) — guárdala para Q&A solamente.

Eso te baja a ~30 min limpios.

Suerte.
