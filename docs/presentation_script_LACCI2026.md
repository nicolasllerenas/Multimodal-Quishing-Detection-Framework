# Q-Shield — Presentation Script (IEEE LA-CCI 2026, Paper 47)

Speaker script for `Q-Shield_LACCI2026_Presentacion.pptx`. The same text is in the
speaker notes of each slide, so you can read it in PowerPoint's Presenter View.

- **Length:** about 1,600 words, around **14 minutes** at a calm speed. This fits a 15-minute talk plus questions.
- **Level:** simple, intermediate English. Short sentences. You do not need to memorize it word by word —
  learn the idea of each slide and the key numbers.
- **Section slides** (dark title on the left, question on the right) only need one short sentence. Do not stop there.
- **If you need to save time:** shorten Related Work (slide 7) and Experiment 3 (slide 19), and skip the quote slide (slide 4).

---

## Script, slide by slide

### Slide 1 — Q-Shield (cover)  *(~30 s)*

Good morning, everyone. My name is Nicolás Llerena, and I am from UTEC, in Lima, Peru. Today I will present Q-Shield. Q-Shield is a system that detects phishing attacks that use QR codes. We call these attacks "quishing". This is joint work with Rensso Mora-Colque and Aurea Soriano-Vargas, also from UTEC.

### Slide 2 — Section: Motivation  *(~5 s)*

Let me start with the motivation. Why does quishing detection matter?

### Slide 3 — Motivation  *(~45 s)*

QR codes are everywhere: in restaurant menus, invoices, and parking meters. But they are also a perfect tool for attackers, for three reasons. First, people cannot read a QR code, so they have to trust the scanner. Second, it is just one tap. There is no preview and no address bar to check. Third, QR codes appear in places that we already trust. And there is one more problem. In our data, 4.3% of real QR codes cannot be decoded at all. For these codes, tools that check the URL have nothing to analyze.

### Slide 4 — Key idea (quote)  *(~10 s)*

So, in one sentence: a QR code is a URL you cannot read... and 4.3% of the time, neither can the scanner. [Pause for two seconds.]

### Slide 5 — Section: Problem Statement  *(~5 s)*

So, what exactly is the problem we want to solve?

### Slide 6 — Problem Statement  *(~45 s)*

Today, there are two kinds of defenses. The first kind decodes the QR code and checks the URL. This is very accurate, but it only works if the code can be decoded. The second kind looks only at the image of the QR code. This always works, but it is less accurate on real, mixed data. The problem is that these two families are used separately, so each one is blind exactly where the other one works. Also, no previous work tests these models across independent datasets.

### Slide 7 — Related Work  *(~40 s)*

We can organize previous work in five directions. URL-based methods are accurate, but they need decoding. Visual methods work before decoding, but they are weaker on mixed data. Multimodal work uses the image and the URL, but as separate baselines, not as one pipeline. Human-centered studies explain why people trust QR codes, but they do not protect users at scan time. And commercial tools work only after decoding. Q-Shield joins both stages in one detector.

### Slide 8 — Section: Contributions  *(~5 s)*

So, what does our paper do differently?

### Slide 9 — Contributions  *(~45 s)*

Our main idea is simple: one detector that works both before and after decoding. We have four contributions. One: a two-stage fusion that combines the image, the URL, and a flag that says if decoding worked. Two: a mixed benchmark with almost twenty-two thousand test samples from two independent datasets. Three: a cross-dataset study that shows that training on only one dataset is not enough. And four: explainability at two levels, with Grad-CAM and SHAP.

### Slide 10 — Section: Methodology  *(~5 s)*

Now, let me explain how the system works.

### Slide 11 — Methodology Overview  *(~50 s)*

This is the full pipeline. The input is a QR image. After preprocessing, it goes into two branches in parallel. The visual branch, at the top, looks at the image directly, without decoding. The text branch, at the bottom, decodes the QR code and reads the URL. Each branch gives a score, called a logit. Then, a small fusion module combines the two scores, plus a flag that says if decoding worked. The output is the probability that the QR code is phishing.

### Slide 12 — Visual branch — two-phase training  *(~50 s)*

Let's look at the visual branch. We use MobileNetV2, a small and fast network, with grayscale images. Training has two phases. In phase one, we use a Siamese network with contrastive learning. In simple words, the model learns to put QR codes of the same class close together, and different classes far apart. In phase two, we fine-tune the model with focal loss. Focal loss gives more weight to hard examples. We keep the best model at epoch eight, to avoid overfitting. At test time, an image flip and a two-model ensemble raise the AUC from 0.896 to 0.915.

### Slide 13 — Text branch and fusion module  *(~50 s)*

The text branch decodes the QR code locally, with a library called pyzbar. There is no internet connection, so the link is never opened. Then, DistilBERT reads the URL. If decoding fails, we use a special token: "undecodable". The fusion module is very small: only 81 parameters. It trains in less than one minute on a CPU. The key is the flag. When decoding works, the model trusts the text more. When decoding fails, it trusts the image. The model learns this by itself. We do not write any rules.

### Slide 14 — Section: Experimentation  *(~5 s)*

Now, the experimental setup.

### Slide 15 — Datasets  *(~45 s)*

We use two datasets that are very different, on purpose. The Trad dataset has about ten thousand clean QR codes, all with the same size: sixty-nine by sixty-nine pixels. CIC-Trap4Phish has more than one million real QR codes, with different sizes and versions. We take fifty thousand samples per class from CIC, we split each dataset eighty-twenty, and we join the test sets. This gives 21,998 test samples. Note that the decoder works on all Trad codes, but only on 95.7% of CIC codes. Those 4.3% are exactly where the visual branch is the only signal.

### Slide 16 — Section: Results  *(~5 s)*

Let's see the results. We ran six experiments.

### Slide 17 — Experiment 1 — the visual fallback  *(~45 s)*

Experiment one tests the visual branch alone. This is the fallback, for when the QR code cannot be decoded. Our best visual model reaches an AUC of 0.915. That is about 0.10 better than the classic baselines, Random Forest and XGBoost. It also matches the best previous visual result, but on a benchmark eleven times larger. Remember, this is the floor of the system: what Q-Shield can still do without the URL.

### Slide 18 — Experiment 2 — multimodal fusion  *(~50 s)*

Experiment two is our main result. Here we compare the visual branch, the text branch, and the fusion. The fusion is the best: AUC 0.975, F1 0.936, and a false negative rate of only 0.057. A false negative is a phishing code that we miss. Compared to the visual branch alone, we miss three and a half times fewer attacks. The gain over the text branch is small on average, but it is concentrated in the 4.3% of codes that cannot be decoded.

### Slide 19 — Experiment 3 — ablation study  *(~35 s)*

Experiment three is an ablation study: we remove one part at a time. Without Siamese pretraining, the false negative rate goes up from 0.20 to 0.27. Without focal loss, the AUC is almost the same, but again the false negative rate goes up, to 0.27. So, both parts help us to miss fewer attacks.

### Slide 20 — Experiment 4 — cross-dataset generalization  *(~45 s)*

Experiment four is about generalization. What happens if we train on one dataset and test on the other? If we train on Trad and test on CIC, the AUC is 0.52. That is almost random. If we train on CIC and test on Trad, the model says "phishing" for almost everything. But when we train on both datasets, the AUC goes back to 0.896. Our message is clear: training on one dataset is not enough. Mixed training is a requirement.

### Slide 21 — Experiment 5 — operational trade-offs  *(~45 s)*

Experiment five is about real deployment. On the left, the threshold. For the visual fallback, if we lower the threshold to 0.40, the false negative rate goes below 0.10, without retraining. The fusion model already meets this target with the default threshold. On the right, the cost. The visual model has only three million parameters and runs in 25 milliseconds on a CPU. The full model takes about 100 milliseconds. Both are fast enough for a mobile phone.

### Slide 22 — Experiment 6 — explainability  *(~45 s)*

Finally, experiment six: explainability. We want to know if the model looks at the real QR structure, or if it learns tricks from the dataset. Grad-CAM shows that the model looks at the alignment patterns and the data regions: the parts that carry the information. The attention maps of the two datasets are correlated, with r equal to 0.43. And SHAP shows that a few dimensions of the embedding drive the decision. This suggests that the model learns real structural patterns, not dataset shortcuts.

### Slide 23 — Section: Limitations  *(~5 s)*

Of course, our work has some limitations.

### Slide 24 — Limitations  *(~40 s)*

First, the visual fallback still misses about 20% of attacks, with an FNR of 0.199. Second, we see mild overfitting in phase two, which we control with early stopping. Third, the performance is lower on large, high-resolution QR codes. And fourth, the probabilities of the visual branch are not perfectly calibrated. Also, we only look at the QR image and its URL, not the message around it. So, Q-Shield is one layer of defense, not the complete solution.

### Slide 25 — Section: Conclusions  *(~5 s)*

To conclude, let me go back to our three objectives.

### Slide 26 — Conclusions  *(~50 s)*

Our main finding is this: multimodal fusion is not just a small improvement. It reduces the false negative rate from 0.202 to 0.057, and it still covers the QR codes that cannot be decoded. About our three objectives. One: by following the two stages of a QR scan, we miss three and a half times fewer attacks. Two: for generalization, training on both datasets raises the AUC from 0.52 to 0.896. And three: for explainability, the attention maps agree across datasets, with r equal to 0.43.

### Slide 27 — Section: Future Work  *(~5 s)*

And what comes next?

### Slide 28 — Future Work  *(~35 s)*

We see four directions. First, a third branch that reads the context: the message, the sender, and the web page. Second, multi-scale training, to improve on large QR codes. Third, robustness against adversarial and stylized QR codes. And fourth, adapting the model to QR payment systems in Latin America.

### Slide 29 — Thank you  *(~10 s)*

Thank you very much for your attention. I am happy to answer your questions.

**Total planned time:** about 14 minutes.

---

## How to say the difficult words

| Word | Say it like |
|---|---|
| quishing / phishing | **KWISH**-ing / **FISH**-ing |
| Siamese | sigh-uh-**MEEZ** |
| contrastive | kun-**TRAS**-tiv |
| MobileNetV2 | **MO**-bile-net vee-**two** |
| DistilBERT | **DIS**-til-bert |
| pyzbar | **PIE**-zee-bar |
| Grad-CAM | **grad**-kam |
| SHAP | shap (like "map") |
| logit | **LOH**-jit |
| epoch | **EE**-pok |
| ensemble | on-**SOM**-bul |
| ablation | ab-**LAY**-shun |
| calibrated | **KAL**-ih-bray-tid |
| explainability | ex-PLAY-nuh-**BIL**-ih-tee |
| multimodal | mul-tee-**MO**-dul |
| threshold | **THRESH**-hold |
| Pearson | **PEER**-sun |

## How to say the numbers

| On the slide | Say |
|---|---|
| 4.3% | four point three percent |
| 0.9749 | zero point nine seven four nine |
| 0.057 | zero point zero five seven |
| 21,998 | twenty-one thousand, nine hundred ninety-eight (or "almost twenty-two thousand") |
| 1,005,738 | more than one million |
| 69 × 69 | sixty-nine by sixty-nine |
| 3.5× | three and a half times |
| τ = 0.40 | tau equals zero point four (tau rhymes with "how") |
| r = 0.43 | r equals zero point four three |
| 3.08 M | three point zero eight million |
| ℓv, ℓt | "the visual logit", "the text logit" |
| AUC, FNR, F1 | A-U-C, F-N-R (false negative rate), F-one |

## Key numbers to remember

| What | Number |
|---|---|
| Undecodable QR codes in CIC | 4.3% (decoder works on 95.7%) |
| Test set (joint benchmark) | 21,998 samples |
| Visual branch (fallback), best | AUC 0.9146, FNR 0.199 |
| Visual branch, single model | AUC 0.8962, FNR 0.202 |
| Text branch | AUC 0.9592, FNR 0.069 |
| **Fusion (main result)** | **AUC 0.9749, F1 0.936, FNR 0.057** |
| Fewer missed attacks vs. visual | 3.5× |
| Cross-dataset: Trad → CIC / CIC → Trad / both | AUC 0.52 / 0.72 / 0.896 |
| Fusion module | 81 parameters, 3 → 16 → 1 |
| Cost | visual 3.08 M params, ~25 ms CPU; full model 69.1 M params, ~100 ms CPU |
| Explainability | r = 0.43 across datasets; inter/intra distance ratio 1.94 |

---

## Questions you may get (with simple answers)

**1. Why is the false negative rate of the visual branch still high (0.199)?**
The visual branch is only the fallback, for codes that cannot be decoded. If we lower the threshold to 0.40,
the FNR goes down to 0.098, without retraining. And the full model already has an FNR of 0.057 with the default threshold.

**2. Isn't the fusion module too simple?**
It is small on purpose. Both branches are frozen, so the fusion only receives three numbers. A small model is
enough, and it is hard to overfit. Also, with logits we can see how much each branch contributes.

**3. Did you try feature-level fusion?**
Yes. We joined the 128-dimensional visual embedding with the 768-dimensional DistilBERT output. It needs both
full networks at inference time, and it gave no measurable gain. So we kept logit-level fusion.

**4. Is it safe to decode the QR code?**
Yes. pyzbar works locally. There is no internet connection, no DNS lookup, and we never open the link.
Reading the text is not the same as visiting the page.

**5. How do you compare with Trad et al.?**
Our visual branch reaches an AUC of 0.915, which matches their result of about 0.913. But we test on a benchmark
eleven times larger, with real-world images.

**6. Can it run on a phone?**
The visual model has 3.08 million parameters, about 12 MB, and runs in about 25 milliseconds on a CPU.
The full model has 69.1 million parameters, about 267 MB, and runs in about 100 milliseconds.
Both fit a normal mobile time budget, and the full model can also run on a server.

**7. What about QR codes with Wi-Fi or payment data, not URLs?**
The visual branch still works, because it does not need a URL. But we did not test non-URL payloads at scale.
That is part of our future work.

**8. What about adversarial or stylized QR codes?**
We did not test them in this paper. It is one of our next steps.

**9. Why only 50,000 samples per class from CIC?**
To keep training time reasonable. It is a stratified sample, so the classes stay balanced.

**10. How do you know the model is not learning dataset shortcuts?**
Two reasons. First, we train on both datasets, because training on one dataset fails on the other.
Second, the Grad-CAM difference maps of the two datasets are correlated, with r equal to 0.43.
This suggests that the model uses similar structural cues in both datasets.

### Useful phrases for the Q&A

- "Sorry, could you repeat the question, please?"
- "Thank you, that is a great question."
- "If I understand correctly, you are asking about ... Is that right?"
- "We did not test that in this paper, but it is a good idea for future work."
- "I am not completely sure, but I think ..."
