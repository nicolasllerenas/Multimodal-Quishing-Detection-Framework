# Gemini prompt: improve the Q-Shield LA-CCI 2026 slides

This file holds a ready-to-paste prompt for Gemini to improve the visual design of
`Q-Shield_LACCI2026_Presentacion.pptx` (33 slides) and to add images that support the talk.
The content, numbers and order of the slides are already final (reviewed by both advisors),
so Gemini should only work on the design and the images.

## How to use it

**Option A: Google Slides + Gemini (recommended)**

1. Upload `Q-Shield_LACCI2026_Presentacion.pptx` to Google Drive and open it with Google Slides.
2. Open the Gemini side panel ("Ask Gemini") and paste the full prompt below.
3. Then go slide by slide and use the image ideas in Part 3 with "Create image" / "Help me visualize".
4. Download the result as `.pptx` and check the speaker notes are still there.

**Option B: Gemini app (gemini.google.com)**

1. Attach the `.pptx` (or a PDF export of it) and paste the full prompt below.
2. Ask for the result as Google Slides (Canvas) and export it to `.pptx` when you are happy.

After Gemini finishes, check every number against the table in Part 2. If Gemini changed a number,
a title or the order of the slides, undo that change.

## Part 1: the prompt (copy everything inside the box)

```text
You are a senior presentation designer for academic conferences. I attached my slide deck for a
20 minute talk at IEEE LA-CCI 2026 (paper: "Q-Shield: An Explainable Multimodal Framework for
QR Code Phishing (Quishing) Detection"). The content is final and approved by my advisors.
Your job is to make the slides look more professional, clear and visual, and to add images or icons
that help the audience understand each idea. Do NOT change the message of any slide.

HARD RULES (do not break them)
1. Keep all 33 slides in the same order. Do not add, remove, merge or split slides.
2. Keep every slide title, subtitle, number, percentage and reference exactly as they are.
   Never invent or round numbers. Never add new statistics.
3. Keep the section-divider format: a short cyan line, the section name in cyan on the left,
   and a question in dark bold text on the right.
4. Keep the content-slide format: title in cyan bold at the top left, one-line subtitle under it.
5. Keep the UTEC template: white background with the light hexagon pattern, UTEC logo at the top right,
   the small UTEC symbol at the bottom right, and the footer "Llerena et al. · IEEE LA-CCI 2026".
6. Do not use em dashes or double hyphens anywhere. Use a colon, a comma or a new sentence instead.
7. Keep the speaker notes of every slide exactly as they are.
8. Keep charts and tables editable (native), keep the native equation on the Methodology Overview slide,
   and keep the small superscript reference numbers and the reference list on the Related Work slides.
9. Keep the scientific figures from the paper unchanged: the pipeline figure (Methodology Overview)
   and the Grad-CAM samples (Experiment 6). Do not redraw them.
10. Text stays in simple English. You may shorten a sentence, but never change its meaning.

DESIGN DIRECTION
- Colors: cyan #00BFFF as the only accent, dark text #1A1A1A, gray text #595959, navy #1A1A2E for
  table headers, light cyan #EAF7FD for highlighted boxes, red #C8463D only for weaknesses or bad results.
- Font: Arial for everything (it must look the same on the conference computer).
- One idea per slide. Big numbers (24 to 40 pt) with short labels. Body text at least 12 pt.
- One visual motif across the deck: simple line icons inside cyan circles. Use the same icon style everywhere.
- Rounded cards with a thin light-gray border; a cyan border only for the key card on each slide.
- No heavy shadows, no gradients, no 3D, no clip art, no stock photos with forced smiles.
- Leave white space. Align everything to the same left margin and grid.
- Images: realistic photos or clean flat illustrations, no recognizable faces, no real brand logos
  (do not use the Yape, Plin, BCP or bank logos). Any QR code that appears in an image must be generic,
  or must encode my repository URL: https://github.com/nicolasllerenas/Multimodal-Quishing-Detection-Framework
- Add short alt text to every image you insert.

SLIDE-BY-SLIDE CONTENT AND WHAT TO IMPROVE
(Content in quotes must stay. "Visual idea" is my suggestion; improve it if you have a better one.)

1. Cover. Keep as it is (title, authors, UTEC building photo).
2. Divider: "Motivation" / "Why does quishing detection matter?"
3. Motivation: "QR codes are part of daily life, in the world and in Peru".
   In the world: "2.2 billion" people expected to pay with QR codes by 2025 (29% of mobile users).
   In Peru: "+85%" growth of QR payments in 2024; "26M" QR payments every month (end of 2024);
   "67%" of adults have a bank account or a digital wallet (2025).
   "What can a QR code hold?": Web link (URL), Plain text, Wi-Fi password, Contact card, Payment data.
   "Most QR codes in daily use hold a web link. This is the case we study."
   Visual idea: a small globe icon for "In the world" and a Peru map outline for "In Peru";
   one icon per data type (link, text, Wi-Fi, contact card, wallet), the URL one highlighted.
4. Motivation: "What makes QR codes easy to use also makes them easy to abuse".
   1 Needs a machine; 2 One tap; 3 Trusted places; box "This is already happening in Peru"
   (fake QR stickers on top of real Yape and Plin codes; fake traffic fines and fake DNI procedures).
   Visual idea: a photo of a QR sticker pasted on top of another QR code on a small shop's payment stand.
5. Quote: "Anyone can create a QR code. Nobody can read one without a scanner."
   Visual idea: a very light, large QR pattern in the background (10% opacity), quote centered.
6. Divider: "Problem Statement" / "What is quishing, and how big is it?"
7. Problem Statement: "What is quishing?" Definition box plus a 4-step attack flow:
   1 Create, 2 Place, 3 Scan, 4 Steal. Visual idea: one icon per step (criminal with laptop,
   QR code on a poster, phone scanning, fake login page with a padlock), connected by arrows.
8. Problem Statement: "How big is the problem?" Chart of the share of phishing attacks that use a
   QR code: 0.8% (2021), 1.4% (2022), 12.4% (2023). Cards: "1 in 8", "5×", "11,000+".
   Box: "Our question: can we detect a malicious QR code automatically, at the moment of the scan?"
   Visual idea: keep the chart; add a small icon to each card (email with QR, radar or shield).
9. Divider: "Related Work" / "How do current defenses work?"
10. Related Work: "Two families of defenses: each one fails where the other one works".
    "Read the URL" (post-decode) vs "Look at the image" (pre-decode), strengths and weaknesses,
    and "The gap" box. Visual idea: a link icon with a magnifying glass vs a QR icon with an eye.
11. Related Work: five research directions table with superscript references and Q-Shield highlighted.
    Visual idea: keep the table; make the Q-Shield row stand out more.
12. Divider: "Contributions" / "What does this paper do differently?"
13. Contributions: 01 Two-stage fusion, 02 Mixed benchmark, 03 Cross-dataset test,
    04 Two-level explainability. Visual idea: one icon per card (merge arrows, stacked datasets,
    crossing arrows, heat map with magnifying glass).
14. Divider: "Methodology" / "How the two stages fit together"
15. Methodology Overview: pipeline figure plus the native equation p(y=1|x) = σ(g_fuse(ℓv, ℓt, f)).
    Keep both. Only improve spacing and the legend under the equation.
16. Visual branch: two-phase training (Input, Phase 1 Siamese pretraining, Phase 2 Fine-tuning,
    Output) plus cards MobileNetV2, 3.08 M parameters, AUC 0.896 → 0.915.
    Visual idea: a tiny diagram of two QR images going into twin networks with shared weights,
    with "pull together" (same class) and "push apart" (different class).
17. Text branch and fusion module: pyzbar offline decoding, DistilBERT, <UNDECODABLE> token;
    fusion MLP 3 → 16 → 1 with 81 parameters; "Decoding works (f = 0)" and "Decoding fails (f = 1)".
    Visual idea: an offline icon (no Wi-Fi) for decoding, and a balance scale for the fusion.
18. Divider: "Experimentation" / "Two datasets, one joint benchmark"
19. Datasets: comparison table (Trad et al. 2025 vs CIC-Trap4Phish 2025), joint benchmark 21,998,
    and the 4.3% box. Visual idea: leave a placeholder for one real sample image from each dataset
    (I will insert them; do not generate fake QR samples).
20. Divider: "Results" / "Six experiments, one benchmark"
21 to 26. Experiments 1 to 6. Keep every chart, table, number and figure. Only improve alignment,
    spacing and emphasis (for example, make the main number of each slide the clear focal point).
27. Divider: "Limitations" / "What is still missing?"
28. Limitations: four numbered cards plus the scope box. Keep it sober, no decorative images.
29. Divider: "Conclusions" / "Closing the three objectives"
30. Conclusions: main finding banner plus three objective cards (0.202 → 0.057, 0.52 → 0.896, r = 0.43).
31. Divider: "Future Work" / "Where this goes next"
32. Future Work: 01 Context branch, 02 Multi-scale training, 03 Adversarial robustness,
    04 Regional adaptation. Visual idea: icons (message bubble, zoom, shield with warning,
    Latin America map).
33. Thank you. Keep the design. Visual idea: add a small QR code that opens my repository
    https://github.com/nicolasllerenas/Multimodal-Quishing-Detection-Framework with the caption
    "Code and paper (this one is safe)".

WHAT TO GIVE BACK
1. The improved deck (same 33 slides, same order, speaker notes kept).
2. A short list of what you changed on each slide.
3. A list of any place where you were not sure, instead of guessing.
```

## Part 2: numbers that must not change

Check these after Gemini finishes. They come from the paper (`paper/main.tex`) and from the sources
listed on the slides.

| Slide | Numbers |
|---|---|
| 3 | 2.2 billion, 29%, +85%, 26M, 67% |
| 8 | 0.8%, 1.4%, 12.4%, 1 in 8, 5×, 11,000+ |
| 16 | 224 × 224, epoch 8, 3.08 M, 0.896 → 0.915 |
| 17 | 3 → 16 → 1, 81 parameters, under 1 minute |
| 19 | 9,987; 1,005,738; 69 × 69; 114 to 582 px; V13; V5 to V30; 100%; 95.7%; 21,998; 50,000 per class; 80/20; 4.3% |
| 21 | 0.813, 0.810, 0.896, 0.915, +0.10 AUC, 0.913, 11× |
| 22 | 0.202, 0.069, 0.057, 0.9749, 0.936, 3.5×, +0.016 AUC, 4.3% |
| 23 | 0.202, 0.267, 0.271, about 0.02 |
| 24 | 0.52, 0.72, 0.896 |
| 25 | τ 0.50 / 0.40 / 0.30 with recall 0.818 / 0.902 / 0.961, FNR 0.182 / 0.098 / 0.039, precision 0.860 / 0.752 / 0.607; 3.08 M, 6.16 M, 69.1 M; 25 ms, 100 ms, ~100 ms; AUC 0.896, 0.915, 0.975 |
| 26 | r = 0.43, 1.94, 128 dimensions |
| 28 | ~20%, FNR 0.199, epoch 8 |
| 30 | 0.202 → 0.057, 0.52 → 0.896, r = 0.43 |

## Part 3: image prompts (one per slide that needs an image)

Use these with Gemini's image generation ("Create image") in Google Slides. Ask for a 16:9 or square image,
and place it where it does not cover text.

| Slide | Image prompt |
|---|---|
| 3 | "Flat minimal illustration, white background, cyan #00BFFF accents: a smartphone scanning a QR code on a small market stall payment stand in Lima, Peru. No text, no logos, no faces." |
| 3 (icons) | "Set of five simple line icons in a cyan circle style: web link, text document, Wi-Fi, contact card, wallet. Same stroke width, transparent background." |
| 4 | "Realistic close-up photo of a QR code sticker pasted on top of another QR code on a shop counter payment stand, slightly misaligned, natural light, shallow depth of field. No brand logos, no readable text." |
| 5 | "Very light gray QR code pattern texture, large, centered, minimal, white background, 10% opacity look." |
| 7 | "Four flat icons in a row connected by cyan arrows: a hooded figure at a laptop, a QR code on a poster, a hand holding a phone scanning, a fake login page with a padlock. White background, cyan and dark gray only." |
| 8 | "Two small flat icons, cyan and dark gray: an email envelope with a QR code inside, and a shield with a radar wave." |
| 10 | "Two flat icons side by side, cyan style: a web link with a magnifying glass, and a QR code with an eye." |
| 13 | "Four flat line icons, cyan circle style: two arrows merging into one, stacked database cylinders, two crossing arrows, a heat map with a magnifying glass." |
| 16 | "Clean diagram style illustration: two QR code images entering two identical neural networks with shared weights, arrows showing 'pull together' for the same class and 'push apart' for different classes. White background, cyan and gray." |
| 17 | "Two flat icons, cyan style: a Wi-Fi symbol crossed out (offline), and a balance scale." |
| 32 | "Four flat line icons, cyan circle style: a message bubble, a zoom magnifier, a shield with an exclamation mark, a map of Latin America." |
| 33 | No generated image. Create a real QR code for https://github.com/nicolasllerenas/Multimodal-Quishing-Detection-Framework with any QR generator and scan it with your phone before the talk. |

Slides 1, 2, 6, 9, 11, 12, 14, 15, 18 and 20 to 31 do not need generated images: keep their charts,
tables and paper figures as they are. Slide 19 gets your own real samples from each dataset.
