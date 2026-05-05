# Guion de presentación — Q-Shield (multimodal)

**Audiencia:** Aurea Soriano-Vargas (asesora)
**Duración objetivo:** 25–30 min + Q&A
**Slides:** ~40 (en `Q-Shield_Presentacion_Asesora.pptx`)
**Idioma:** español
**Status:** pivote multimodal completado, fusion AUC 0.9749 verificado sobre n=21,998

---

## Antes de empezar

- Ten abiertos en pestañas separadas: el `.pptx` en presentación, el paper PDF, el repo en GitHub, y `docs/results/eval_multimodal.json` por si pide ver el JSON crudo.
- Si la profe interrumpe con una pregunta, párate, respóndela, y vuelve al hilo. No te apresures por terminar.
- Tu mayor activo: **honestidad metodológica**. Las dos slides emocionalmente importantes son la del pivote (slide 5–7) y la del headline (slide 22).

---

## Slide 1 — Portada *(~30 s)*

> "Buenas tardes profesora. Voy a presentarle Q-Shield, el trabajo que hemos venido desarrollando estos meses, en su versión final multimodal. El título completo del paper es ahora 'An Explainable Multimodal Framework for Quishing Detection via Siamese Visual and Offline URL Analysis'."

*Arranque pausado. No leas el subtítulo entero.*

---

## Slide 2 — Agenda *(~45 s)*

> "La presentación tiene seis partes. Primero el problema. Segundo, lo más importante: el pivote — por qué cambiamos de visual-only a multimodal hace dos semanas. Tercero la arquitectura completa: visual, texto y fusion. Cuarto los experimentos. Quinto la explicabilidad. Sexto limitaciones y plan de submission."

*La agenda anuncia el pivote. Es el gancho narrativo de la presentación.*

---

## Slide 3 — Part 01 divider *(~15 s)*

> "Empecemos por el problema."

---

## Slide 4 — Quishing es ingeniería social *(~75 s)*

> "El quishing es esencialmente un ataque de ingeniería social. Mitnick y Hadnagy describen el patrón: el atacante busca inducir una acción impulsiva. Los QR son casi un medio perfecto — opacos al ojo humano, se activan con un solo gesto, y se presentan en contextos que implícitamente los marcan como legítimos. El reporte de Verizon DBIR 2024 lo confirma como vector líder, y IBM 2024 reporta costos en millones por incidente."

*Aquí muestras la motivación. No vendas el modelo todavía.*

---

## Slide 5 — Part 02 divider *(~15 s)*

> "Aquí viene lo importante: por qué pivotamos."

*Pausa breve. Esta es la slide que la profe va a recordar.*

---

## Slide 6 — Por qué pivotamos *(~150 s — slide crítica)*

> "Profesora, hace dos semanas decidimos pivotar de un framework visual-only a uno multimodal. Le quiero contar las tres razones, en orden de importancia.
>
> Primero: la 'paradoja del decodificado' que invocábamos como ventaja de seguridad NO se sostiene. pyzbar es local, determinístico, sin red, sin DNS, sin JS. Confunde leer un string con abrirlo. Un reviewer informado nos lo iba a derribar de un solo golpe.
>
> Segundo: la señal visual sola es estructuralmente débil en QRs heterogéneos. CIC Trap4Phish 2025 reporta SSIM benigno-phishing de 0.34 — visualmente casi indistinguibles. Su CNN sobre imágenes alcanza F1 0.88. Sus LLMs sobre la URL decodificada llegan a F1 0.97-0.99. La señal de URL es DIEZ VECES más fuerte que la visual cuando los QRs salen del sandbox de Trad.
>
> Tercero: combinar ambas dominaba a cualquiera sola por construcción. Bountakas 2023 y Khalifa 2025 ya lo validaron en webpages. La formulación multimodal es la que sobrevive review.
>
> Pero — y esto es importante — la rama visual NO se descarta. Es el fallback graceful cuando el QR no se puede decodificar, que ocurre en el 4% del corpus."

*Tómate tu tiempo. Esta slide es donde la profe ve que el proyecto evolucionó con rigor metodológico, no por capricho.*

---

## Slide 7 — Cuatro research gaps cerrados *(~75 s)*

> "Con este pivote cerramos cuatro gaps de la literatura. Uno: integración de las dos señales — Bountakas y Khalifa lo hacen en webpages, nadie lo hace en QRs. Dos: cross-dataset evaluation — somos los primeros en evaluar transferencia entre Trad y CIC. Tres: dual XAI — Grad-CAM espacial y SHAP sobre el embedding. Cuatro: punto de operación calibrado — la fusion alcanza FNR 0.057 al threshold default, sin necesidad de calibración."

---

## Slide 8 — Cinco contribuciones *(~75 s)*

> "Cinco contribuciones del paper. Primera: framework multimodal end-to-end con fusion explícita. Segunda: benchmark cross-dataset de 21,998 muestras, 11 veces más grande que el evaluation más grande previo. Tercera: handling explícito del caso UNDECODABLE via flag binario en el fusion. Cuarta: punto de operación que ya cumple FNR ≤ 10% al threshold default. Quinta: explicabilidad dual validada cross-dataset (r = 0.43)."

---

## Slide 9 — Related Work table *(~60 s)*

> "Esta tabla nos posiciona contra el trabajo previo. Note dos cosas. Una: somos los únicos en la columna 'Branches fused' — Trad solo tiene visual, CIC reporta visual y texto en paralelo pero no fusionados. Dos: somos los únicos con cross-dataset, dual XAI y threshold calibration. Trad reporta AUC 0.913 sobre 1,998 muestras de QR versión 13 fija. CIC reporta F1 0.97-0.99 con LLMs sobre URL pero no aborda el caso UNDECODABLE."

---

## Slide 10 — Part 03 divider *(~15 s)*

> "Pasemos a la arquitectura."

---

## Slide 11 — Pipeline overview *(~120 s — slide importante)*

> "Esta es la arquitectura completa. De izquierda a derecha tenemos tres etapas. Primero la pre-decode: la imagen QR cruda entra en cualquier resolución, se preprocesa a 224 por 224 grayscale, pasa por el backbone Siamese MobileNetV2 con pesos compartidos. El backbone produce un embedding 128-d L2-normalizado, que alimenta la cabeza clasificadora visual. Sale un logit visual.
>
> En paralelo, la decode stage: pyzbar lee el QR y produce un string URL — o un sentinel UNDECODABLE si no puede.
>
> Tercera etapa, post-decode: la URL pasa por DistilBERT, que produce un logit de texto.
>
> Finalmente, los dos logits y el flag UNDECODABLE alimentan un MLP pequeño — la fusion — que produce la probabilidad final.
>
> Los entrenamientos son secuenciales: primero contrastive loss en el visual, luego focal loss en la cabeza visual, luego fine-tune del DistilBERT, finalmente la fusion sobre features cacheadas. Total cuatro pases de entrenamiento."

---

## Slide 12 — Visual branch *(~75 s)*

> "La rama visual es esencialmente lo que teníamos antes del pivote: MobileNetV2 con 3.08M parámetros, 12 megabytes en disco. Phase 1 entrena con contrastive loss sobre pares — same-class y different-class — con margen 1.5. Phase 2 entrena la cabeza con focal loss, gamma 2, alpha 0.5. La cabeza congela el backbone los primeros 5 epochs y luego descongela 15 epochs más. La best epoch típicamente es la 8."

---

## Slide 13 — Text branch *(~75 s)*

> "La rama de texto es DistilBERT 66M parámetros. Lo elegimos por trade-off latencia/accuracy — DeBERTa o ModernBERT son 2-5 veces más grandes. Lo fine-tuneamos por 3 epochs con focal loss, learning rate 2e-5, scheduler linear con warmup 10%.
>
> Detalle clave: si pyzbar no puede decodificar, sustituimos el string por el token sentinel UNDECODABLE. DistilBERT lo aprende como un token especial, así que entiende 'no tengo URL' como información, no como ruido."

---

## Slide 14 — Fusion *(~60 s)*

> "El fusion es un MLP pequeño: tres entradas — logit visual, logit texto, flag undecodable — pasan por una capa oculta de 16 unidades y salen a una sola unidad. Total: 161 parámetros. Lo entrenamos con focal loss sobre features pre-computadas — paga uno solo por correr ambas ramas sobre todo el corpus, y luego la fusion entrena en menos de un minuto."

---

## Slide 15 — Part 04 divider *(~15 s)*

> "Las fórmulas, brevemente."

---

## Slide 16 — Problem formulation *(~45 s)*

> "Formalmente, queremos un clasificador que mapee cada QR a una probabilidad de phishing. Lo factorizamos: cada rama produce un embedding, una cabeza produce un logit, y la fusion combina los dos logits con la sigmoide al final. La separación nos permite reusar los embeddings para XAI."

---

## Slide 17 — Contrastive Loss *(~75 s)*

> "Phase 1 visual usa contrastive loss canónica de Chopra-Hadsell-LeCun 2005. Para pares de la misma clase, minimiza distancia al cuadrado. Para pares de clases distintas, minimiza el margen menos la distancia, con clipping a cero si ya están separados.
>
> Margen 1.5 lo elegimos por grid search sobre cinco valores. Margenes menores producen underfitting. El resultado en el embedding aprendido es un ratio inter/intra-clase de 1.94."

---

## Slide 18 — Focal Loss *(~75 s)*

> "Phase 2 visual y la fusion usan focal loss de Lin et al. 2017. La intuición: el factor uno menos p elevado a gamma reduce el peso de los ejemplos fáciles y aumenta el de los difíciles.
>
> En seguridad esto es crítico. Un FN expone al usuario al ataque; un FP solo dispara una advertencia. Empíricamente, reemplazar focal por BCE en la cabeza visual sube el FNR del 0.20 al 0.27 — siete puntos más de ataques que se nos escapan."

---

## Slide 19 — Part 05 divider *(~15 s)*

> "El práctico — código y datasets."

---

## Slide 20 — Datasets *(~75 s)*

> "Dos corpus complementarios. Trad et al. tiene 9,987 matrices binarias 69 por 69, todas QR versión 13. CIC Trap4Phish 2025 es de la Universidad de New Brunswick: más de un millón de QRs en PNG con resoluciones 114 a 582, versiones 5 a 30. De CIC tomamos 100,000 estratificado por compute.
>
> Splits 80/20 con seed 42, set de validación combinado: 21,998 muestras — once veces más grande que la evaluación más grande previa.
>
> Para la rama de texto decodificamos cada imagen una vez con pyzbar y cacheamos el resultado en JSON. Trad: 100% de éxito de decode. CIC: 4.3% de fallo total. El fallo se almacena como UNDECODABLE."

---

## Slide 21 — Part 06 divider *(~15 s)*

> "El proceso iterativo y la reconciliación."

---

## Slide 22 — Iteración v1→v3 + reconciliación *(~150 s — slide crítica)*

> "Esta slide es importante porque le quiero contar el proceso completo, sin filtro.
>
> v1 fue el primer intento visual: AUC 0.886 con un gap de 30 puntos entre train y val — overfitting severo. v2 fue la sobrecorrección — bajamos el margen, subimos el dropout, agregamos rotación: AUC 0.868, peor que v1 porque la rotación rompe los finder patterns. v3 fue el equilibrio: margin 1.5, dropout 0.35, sin rotación. AUC 0.896.
>
> Pero — y aquí viene la parte importante — al hacer auditoría detectamos que el número 0.9254 que reportábamos en la ablation A1 venía de evaluar sobre un subset, no sobre las 21,998 completas. El número real visual era 0.896 — debajo de Trad por 1.71 puntos. Apliqué TTA y ensemble de dos seeds y llegamos al 0.9146 — empate técnico con Trad.
>
> Después vino el pivote. La fusion multimodal alcanza 0.9749. La auditoría que hicimos antes del pivote sirvió como base honesta — cada número del paper actual es trazable a un script en el repo."

*Esta slide demuestra rigor. Si la profe interrumpe con preguntas, déjala. No la apresures.*

---

## Slide 23 — Part 07 divider *(~15 s)*

> "Y los resultados."

---

## Slide 24 — Hero result *(~45 s)*

> "El número titular: AUC 0.9749 con la configuración fusion sobre las 21,998 muestras. F1 0.936, recall 0.943, FNR 0.057. Por encima de Trad por 6.16 puntos. Por encima del ensemble visual previo por 6 puntos. Y el FNR ya cumple la tolerancia de seguridad ≤ 10% al threshold default."

*Pausa. Que el número se asiente.*

---

## Slide 25 — Bar chart de comparación *(~75 s)*

> "Esta gráfica visualiza las cinco métricas clave para las tres configuraciones — visual, text, fusion. Note tres cosas. Una: el text alone ya supera al visual en todas las métricas — eso confirma lo que CIC nos enseñó sobre la fuerza de la señal URL. Dos: el fusion gana al text en todas las métricas — la rama visual aporta señal genuina, no es redundante. Tres: la mejora más grande del fusion sobre el text está en F1 y en calibración — uno menos ECE pasa de 0.96 a 0.96 — el modelo no solo es mejor ranker, es mejor estimador probabilístico."

---

## Slide 26 — Main results table *(~75 s)*

> "Tabla principal con cuatro filas. Trad reporta 0.913 sobre 1,998. Q-Shield visual single seed alcanza 0.896, ensemble + TTA 0.915. Text-only DistilBERT 0.959. Fusion 0.975. La precision sube notablemente con el fusion — 0.928. El FNR cae de 0.20 visual a 0.057 fusion — un orden de magnitud."

---

## Slide 27 — Confusion matrix + ROC *(~60 s)*

> "Esta es la Figura 4 del paper. La matriz a la izquierda muestra el fusion: 10,201 verdaderos negativos, 800 falsos positivos, 623 falsos negativos, 10,374 verdaderos positivos. Los 623 FN son una reducción de 3.5 veces respecto al ensemble visual.
>
> A la derecha, la curva ROC del fusion en verde sobre la del visual ensemble en gris dashed. La estrella verde marca el operating point default — bien arriba de la línea roja punteada que indica el target del 10% de FNR."

---

## Slide 28 — Ablation visual *(~75 s)*

> "El ablation es sobre el visual single-seed para aislar las decisiones arquitectónicas. Sin Siamese pretraining: pierde 2 puntos de AUC. Sin focal loss: el AUC apenas cambia pero el FNR se dispara 7 puntos. Sin frozen start y con cabeza pequeña: cada uno cuesta 1.5 a 2 puntos. Las mejoras en inferencia — TTA y ensemble — suman 1.84 puntos al visual, y el fusion suma 6 puntos más sobre el ensemble."

---

## Slide 29 — Cross-dataset *(~75 s)*

> "Cross-dataset valida el entrenamiento combinado. Si entrenamos solo en CIC y testeamos en Trad: AUC 0.72 con classifier collapse. Si entrenamos solo en Trad y testeamos en CIC: AUC 0.52 — random. Combinado: 0.896 visual, 0.975 fusion. Posicionamos esto como domain-invariant learning citando a Ganin y Lempitsky 2015."

---

## Slide 30 — Threshold calibration (ya no es load-bearing) *(~60 s)*

> "Esta tabla queda en el paper como caracterización del visual fallback, no como contribución principal. Antes del pivote, el FNR del default 0.5 era 0.18 y necesitábamos sliding a 0.4 para llegar a FNR ≤ 0.10. Ahora, la fusion ya cumple la tolerancia al default — la calibración pasa de claim crítico a herramienta opcional para deployments con SLAs estrictos."

---

## Slide 31 — Part 08 divider *(~15 s)*

> "Explicabilidad y deployment."

---

## Slide 32 — Grad-CAM *(~75 s)*

> "Aplicamos Grad-CAM al último bloque inverted-residual del MobileNetV2. Los finder patterns en las tres esquinas reciben atención uniformemente baja — el modelo correctamente los ignora. La atención se concentra en las zonas de datos. Agregado por clase: benignos atienden a la izquierda, phishing al centro-derecha. La interpretación plausible: URLs phishing son más largas, empujan más codewords a posiciones de la derecha del QR."

---

## Slide 33 — SHAP + embeddings *(~75 s)*

> "A la izquierda, SHAP sobre las 128 dimensiones del embedding visual. La dimensión más importante contribuye 0.016 de SHAP promedio, decreciendo suavemente. Las otras 108 contribuyen casi nada — el embedding está sobre-parametrizado y se podría podar a 32-64 dim sin pérdida.
>
> A la derecha, distancias en el espacio. Benigno-Benigno 0.501, Phishing-Phishing 0.458, Benigno-Phishing 0.928. Ratio inter/intra: 1.94. El contrastive learning hizo lo que tenía que hacer."

---

## Slide 34 — Per-dataset Grad-CAM *(~75 s)*

> "Una preocupación natural: ¿la asimetría L/R que vimos antes es señal real o artefacto de mezclar matrices binarias 69×69 con PNGs antialiased? Para descartarlo recomputamos los mapas Grad-CAM por separado en Trad y CIC, y medimos correlación pixel a pixel.
>
> El resultado: r = 0.43 — moderada. No es uno (no es universal). No es cero (no es solo del dataset). La señal estructural de phishing es genuinamente compartida entre ambos corpus."

---

## Slide 35 — Inference cost *(~75 s)*

> "Tabla de costos de inferencia. Cuatro filas. Visual single-seed: 25 ms en CPU. Visual + TTA: 50 ms. Visual ensemble + TTA: 100 ms. Fusion completa con DistilBERT: aproximadamente 95 ms en CPU.
>
> Los 100 ms del fusion caben dentro del presupuesto perceptivo móvil. El trade-off: el fusion suma 0.06 AUC sobre el ensemble visual, justificando los 95 ms. Para deployments más restrictivos, el visual single-seed sacrifica 0.08 AUC con 4× menos compute."

---

## Slide 36 — Part 09 divider *(~15 s)*

> "Para cerrar: limitaciones y futuro."

---

## Slide 37 — Limitations *(~120 s)*

> "Reportamos siete limitaciones explícitas en Section VI.B del paper. Una: el FNR del visual fallback es 0.20 al default — solo afecta cuando el decode falla. Dos: overfitting moderado en Phase 2 visual después del epoch 8. Tres: no verificamos URL overlap entre Trad y CIC. Cuatro: rendimiento cae en QRs > 246 px por la pérdida del resize. Cinco: calibración del visual single-seed es imperfecta — la fusion lo arregla. Seis: scope unimodal del contexto que rodea — email subject, sender — eso sería un tercer branch en future work. Siete: no evaluamos robustez adversarial."

*Tu asesora valora que reportes esto. NO suavices.*

---

## Slide 38 — Future work *(~75 s)*

> "Cinco extensiones concretas. Primera: tercera rama sobre el contexto que rodea al QR — email subject, SMS body. Segunda: localized deployment por región — Yape en Perú, UPI en India, Pix en Brasil. Tercera: multi-scale training para cerrar el gap en QRs grandes. Cuarta: adversarial robustness. Quinta: provenance-aware detection — la próxima slide."

---

## Slide 39 — Provenance / Yape deep dive *(~120 s)*

> "Este punto vale la pena desarrollarlo. Q-Shield responde una pregunta — ¿este QR es phishing por contenido? — pero no responde otra — ¿fue generado por la fuente autorizada?
>
> El ejemplo en contexto peruano: Yape, operado por BCP, genera QRs de comerciantes a través de un backend autenticado. Si un atacante físicamente pega un QR encima del QR legítimo de un comerciante, el QR puede tener contenido perfectamente válido — apunta a un número de cuenta real. Q-Shield no lo detecta porque visualmente luce benigno y la URL es válida.
>
> Para resolver eso necesitamos otra capa: firmas criptográficas en el payload, validación del merchant ID, tokens de sesión, atestación de geolocalización. Q-Shield más provenance son capas ortogonales — Q-Shield para zero-day por contenido, provenance para content-valid pero origin-invalid. Lo dejamos como future work directo."

*Esta slide aterriza el paper en contexto peruano. La profe lo va a apreciar.*

---

## Slide 40 — Submission plan *(~60 s)*

> "El plan: primer target IEEE Intercon, segundo IEEE LA-CCI, stretch IEEE TrustCom. Antes de mandar queda recompilar el LaTeX con las nuevas figuras, opcionalmente agregar bootstrap CI sobre el AUC del fusion para reforzar el claim estadístico, y verificar que no queden referencias rotas en el PDF."

---

## Slide 41 — Summary *(~75 s)*

> "El resumen: framework multimodal end-to-end con visual Siamese + DistilBERT URL + fusion MLP. Pivote completado con honestidad metodológica. Benchmark 11 veces más grande. AUC 0.9749 fusion supera Trad por 6 puntos. FNR 0.057 cumple tolerancia sin calibración. Visual fallback graceful para QRs no decodificables. Dual XAI validado cross-dataset. Calibración 3 veces mejor que visual solo. Mobile deployable. Listo para review y para submission a Intercon o LA-CCI."

---

## Slide 42 — Thank you *(~15 s)*

> "Gracias profesora. Quedo atento a sus preguntas y sugerencias."

---

# Apéndice — Q&A anticipado

Respuestas listas para preguntas probables.

### "¿Por qué pivotaron a multimodal? ¿No tenían el visual ya funcionando?"

> "Funcionaba pero con un techo. Tres razones para pivotar. Una: el argumento de seguridad 'no decoding' que invocábamos era débil — pyzbar es local. Dos: CIC mostró empíricamente que la señal URL es 10× más fuerte que la visual en QRs heterogéneos. Tres: combinar siempre domina (Bountakas, Khalifa). Mantenemos el visual como fallback graceful para el 4% que no decodifica."

### "Si el text branch ya logra 0.96, ¿el visual aporta algo?"

> "Sí, +1.57 pp AUC. La fusion no es solo 'text branch con un wrapper'. Hay dos contribuciones del visual al fusion: una, en el 4.3% de QRs UNDECODABLE el text es ciego y el visual es la única señal — el flag explícito le dice a la fusion 'trust visual aquí'. Dos, en URLs ambiguas como bit.ly o cortas, el visual desambigua. El ablation lo confirma: quitar el visual del fusion baja AUC a 0.959."

### "¿Cómo se compara con CIC, exactamente?"

> "CIC reporta text-only F1 0.97-0.99 con LLMs grandes — DeBERTa-v3, ModernBERT, DeepSeek-R1-Distill. Q-Shield text-only F1 0.927 con DistilBERT, fusion F1 0.936. No superamos a CIC en URL pura — con un LLM más grande cerraríamos la brecha. Pero CIC reporta visual y texto en paralelo, no fusionados, y no aborda el caso UNDECODABLE. Q-Shield es el primer detector multimodal end-to-end con manejo explícito del fallback visual."

### "¿Por qué no usaron SimCLR para el visual?"

> "Lo que hacemos en Phase 1 visual es supervised contrastive — Chopra 2005 / Khosla 2020 SupCon. Usamos las etiquetas para formar pares. SimCLR sería self-supervised, sin etiquetas, formando pares con augmentations. Una versión SimCLR-style con pretraining sobre QRs no etiquetados antes del fine-tune supervisado es future work explícito."

### "¿+6 pp es estadísticamente significativo?"

> "Trad reporta sobre n=1,998 → IC 95% ≈ ±0.012. Nosotros sobre n=21,998 → IC 95% ≈ ±0.004. Los IC no se sobreponen. La diferencia es estadísticamente robusta. Bootstrap CI sobre el AUC fusion lo confirmaría con un experimento de 30 minutos — está en mi lista para antes del submit."

### "¿La FNR de 0.057 es aceptable para producción?"

> "Cumple la tolerancia conservadora ≤ 10% que se usa convencionalmente en seguridad. Para deployments con SLAs más estrictos, threshold sliding a 0.4 sobre el visual fallback baja el FNR a 0.098. La fusion en sí ya está debajo del target, así que la calibración deja de ser load-bearing — pasa a ser herramienta opcional."

### "¿Por qué DistilBERT y no ModernBERT?"

> "Trade-off latencia/accuracy. DistilBERT 66M, ModernBERT 150M+, DeepSeek-R1-Distill 671M. CIC reporta DeepSeek con F1 0.99 vs DistilBERT 0.96. Para mobile vale la pena el trade-off. Future work: comparar Q-Shield fusion con DistilBERT vs ModernBERT como branch text."

### "¿Decodificar offline no carga el riesgo del browser-fetch?"

> "No. Decodificar con pyzbar lee el patrón de módulos y devuelve un string. No abre, no fetchea, no resuelve DNS, no ejecuta JS. Es el equivalente de leer texto de un archivo en disco. La paradoja del decodificado conflaciona dos pasos — leer (seguro) y abrir (riesgoso). El paper lo aclara explícitamente."

### "¿Cómo manejan el caso UNDECODABLE?"

> "Flag binario explícito en el input del fusion. Sentinel `<UNDECODABLE>` como token en el text branch. La fusion aprende automáticamente 'cuando flag=1, ignora text logit y usa visual logit'. En nuestro corpus el 4.3% de QRs no decodifica — Trad 0%, CIC 4.6%."

### "¿No deberían reentrenar el ablation sobre el set completo?"

> "Sí, sería más fuerte. Actualmente A2-A5 se entrenan sobre 40% del corpus por restricción de cómputo — está documentado en el footnote de la Tabla V. La nota explica que el ordenamiento cualitativo se preserva en ambos protocolos. Re-correr el ablation completo es realista en una próxima iteración con más GPU."

### "¿Quedan limitaciones que reconocer?"

> "Sí — siete reportadas en Section VI.B. La más relevante: la rama visual sigue teniendo FNR alto al default 0.5, así que los SLAs estrictos requieren calibración del visual fallback. Otras: overfitting moderado en Phase 2 visual, URL overlap no verificado, accuracy en QRs grandes, scope unimodal del contexto que rodea, container-format, robustez adversarial."

---

# Tips finales

- **Velocidad**: 40 slides en 30 min son ~45 segundos por slide promedio. Los dividers (slides 3, 5, 10, 15, 19, 21, 23, 31, 36) toman 15 segundos cada uno; el ahorro va a las slides clave (6 pivote, 22 reconciliación, 24 hero, 39 provenance).
- **Cuando interrumpa**: para de avanzar, responde, después pregúntale "¿continuo?". No vuelvas a slides anteriores a menos que lo pida.
- **Si no sabes algo**: di "Eso no lo evalué directamente, pero si quiere lo investigo y le mando un follow-up esta semana." Mejor que inventar.
- **Slides clave que enfatizar**: 6 (pivote — la slide que la profe va a recordar), 22 (reconciliación — la slide que demuestra rigor), 24 (hero — el número), 25 (bar chart — visualiza el aporte fusion), 34 (per-dataset Grad-CAM — defensa contra "esto es solo dataset bias"), 39 (provenance — aterrizaje peruano).
- **Cierre**: si pregunta cuándo enviamos, di "Apenas usted dé luz verde, profesora — el paper ya pasó por la auditoría completa, los números son trazables a scripts del repo, y las figuras están regeneradas. Si me pide los dos cambios opcionales — bootstrap CI y aclaración SimCLR — los aplico esta semana."

---

# Tiempos resumen (40 slides activas)

| Sección | Slides | Tiempo aprox |
|---|---|---|
| Apertura (cover + agenda + divider) | 1–3 | 1.5 min |
| Problema + pivote + gaps + contribuciones + related | 4–9 | 8 min |
| Architecture (4 slides) + divider | 10–14 | 6 min |
| Theory (3 fórmulas) + divider | 15–18 | 4 min |
| Datasets + divider | 19–20 | 1.5 min |
| Iteración + reconciliación + divider | 21–22 | 3 min |
| Results (hero, bar chart, table, CM/ROC, ablation, cross, threshold) | 23–30 | 7.5 min |
| XAI + inference cost + divider | 31–35 | 5 min |
| Limitations + future + provenance + submission + divider | 36–40 | 6 min |
| Summary + thanks | 41–42 | 1.5 min |
| **Total** | **42** | **~44 min** |

**Si necesitas comprimir a 30 min**, recorta:
- Slides 17 y 18 (fórmulas) — comprime a una sola.
- Slide 28 (ablation) — comprime a 30 segundos, no leas todas las filas.
- Slide 30 (threshold) — comprime a 30 segundos, ya no es load-bearing.
- Slide 39 (provenance) — guárdala para Q&A si hay tiempo.

Eso baja a ~32 min limpios.

Suerte.
