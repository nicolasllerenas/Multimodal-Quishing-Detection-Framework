# Q-Shield: Presentation Script (IEEE LA-CCI 2026, Paper 47)

Speaker script for `Q-Shield_LACCI2026_Presentacion.pptx`. The same text is in the
speaker notes of each slide, so you can read it in PowerPoint's Presenter View.

- **Length:** about 2,100 words, around **20 minutes** at a calm speed (about 110 words per minute).
  The time next to each slide is an estimate. Practice with a timer and check the total.
- **Level:** simple, intermediate English. Short sentences. You do not need to memorize it word by word.
  Learn the idea of each slide and the key numbers.
- **Section slides** (cyan title on the left, question on the right) only need one short sentence. Do not stop there.
- **If you need to save time:** skip the quote slide (slide 5), shorten the Related Work table (slide 11)
  and Experiment 3 (slide 23). That saves about one minute.
- **If you have extra time:** slow down on Motivation (slides 3 and 4) and Experiment 2 (slide 22).

## Script, slide by slide

### Slide 1: Q-Shield (cover)  *(~35 s)*

Good morning, everyone. My name is Nicolás Llerena, and I am from UTEC, in Lima, Peru. Today I will present our paper, Q-Shield. Q-Shield is a system that detects phishing attacks that use QR codes. We call these attacks "quishing". This is joint work with Rensso Mora-Colque and Aurea Soriano-Vargas, also from UTEC.

### Slide 2: Section: Motivation  *(~5 s)*

Let me start with the motivation. Why does quishing detection matter?

### Slide 3: Motivation: QR codes in daily life  *(~75 s)*

QR codes are now part of our daily life. Around the world, more than two billion people were expected to pay with QR codes by 2025. That is almost one in three mobile phone users. In Peru, the growth is very fast. QR payments grew 85% in 2024, and today there are more than 26 million QR payments every month. Also, 67% of Peruvian adults now have a bank account or a digital wallet, like Yape or Plin. But what is inside a QR code? A QR code can hold many kinds of data: a web link, plain text, a Wi-Fi password, a contact card, or payment data. In daily use, most QR codes hold a web link, a URL. And that is the case we study in this work.

### Slide 4: Motivation: easy to abuse  *(~75 s)*

The same things that make QR codes easy to use also make them easy to abuse. There are three reasons. First, a person cannot read a QR code. We need a scanner device and a decoding algorithm. Second, it is just one tap. There is no preview and no address bar to check before the page opens. Third, QR codes appear in places that we already trust, like restaurant menus, payment stands, and parking meters. And this is already happening in Peru. The police warn that criminals put fake QR stickers on top of the real Yape and Plin codes of small shops. So the money goes to the criminal. There are also fake traffic fines and fake DNI procedures, with QR codes that open fake bank pages or install malware.

### Slide 5: Key idea (quote)  *(~10 s)*

So, in one sentence: anyone can create a QR code, but nobody can read one without a scanner. [Pause for two seconds.]

### Slide 6: Section: Problem Statement  *(~5 s)*

So, what is quishing exactly, and how big is the problem?

### Slide 7: Problem Statement: what is quishing?  *(~70 s)*

Quishing is a mix of two words: QR and phishing. A criminal hides a malicious link inside a QR code, to steal passwords, money, or personal data. A typical attack has four steps. One: the criminal creates a QR code that opens a fake login page or a fake payment page. Two: the criminal places the code in an email, on a poster, on a parking meter, or on top of a real code. Three: the victim scans it with a phone. Note that the phone is often far from the security tools of a company. And four: the fake page asks for a password, a card number, or a payment. Quishing is social engineering. It uses trust and speed, not a software bug.

### Slide 8: Problem Statement: how big is it?  *(~55 s)*

And how big is the problem? This chart shows the share of phishing attacks that use a QR code. In 2021, it was less than one percent. In 2023, it was 12.4%. That is about one in eight phishing attacks. And it is still growing. Kaspersky saw five times more QR phishing emails between August and November of 2025. And Palo Alto Networks detects more than eleven thousand malicious QR codes every day. So, the question for our work is simple: can we detect a malicious QR code automatically, at the moment of the scan?

### Slide 9: Section: Related Work  *(~5 s)*

Before our solution, let me show how current defenses work.

### Slide 10: Related Work: two families of defenses  *(~60 s)*

Today, there are two families of defenses. The first family decodes the QR code and checks the URL. This is very accurate, but it only works when the code can be decoded. The second family looks only at the image of the QR code, without decoding. This always works, but it is less accurate on real, mixed data. The problem is that these two families are used separately. So each one is weak exactly where the other one is strong. Also, no previous work tests these models across independent datasets. This is the gap that we want to close.

### Slide 11: Related Work: five directions  *(~50 s)*

In more detail, we can organize previous work in five directions. URL-based methods are accurate, but they need decoding, and they only work with URLs. Visual methods work before decoding, but they are weaker on mixed, real data. Multimodal work uses the image and the URL, but as separate baselines, not as one pipeline. Human-centered studies explain why people trust QR codes, but they do not protect users at scan time. And commercial tools work only after decoding. Q-Shield is different, because it joins both stages in one detector.

### Slide 12: Section: Contributions  *(~5 s)*

So, what does our paper do differently?

### Slide 13: Contributions  *(~50 s)*

Our main idea is simple: one detector that works both before and after decoding. We have four contributions. One: a two-stage fusion. It combines the image, the URL, and a flag that says if decoding worked. Two: a mixed benchmark, with almost twenty-two thousand test samples from two independent datasets. Three: a cross-dataset study. It shows that training on only one dataset is not enough. And four: explainability at two levels. We use Grad-CAM on the pixels, and SHAP on the embedding.

### Slide 14: Section: Methodology  *(~5 s)*

Now, let me explain how the system works.

### Slide 15: Methodology Overview  *(~60 s)*

This is the full pipeline. The input is a QR image. After preprocessing, the image goes into two branches in parallel. The visual branch, at the top, looks at the image directly, without decoding. The text branch, at the bottom, decodes the QR code and reads the URL. Each branch gives a score, called a logit. Then, a small fusion module combines the two scores, plus a flag that says if decoding worked. The equation at the bottom shows this idea. The probability of phishing is the sigmoid of the fusion function, and its inputs are the visual logit, the text logit, and the decode flag.

### Slide 16: Visual branch: two-phase training  *(~65 s)*

Let's look at the visual branch. We use MobileNetV2, a small and fast network, with grayscale images of two hundred twenty-four by two hundred twenty-four pixels. Training has two phases. In phase one, we use a Siamese network with contrastive learning. In simple words, the model learns to put QR codes of the same class close together, and QR codes of different classes far apart. In phase two, we fine-tune the model with focal loss. Focal loss gives more weight to the hard examples. We keep the best model at epoch eight, to avoid overfitting. At test time, an image flip and a two-model ensemble raise the AUC from 0.896 to 0.915.

### Slide 17: Text branch and fusion module  *(~60 s)*

Now, the text branch. It decodes the QR code locally, with a library called pyzbar. There is no internet connection, so the link is never opened. Then, DistilBERT reads the URL. DistilBERT is a small language model. If decoding fails, we use a special token: "undecodable". After that, the fusion module combines both branches. It is very small: only 81 parameters, and it trains in less than one minute on a CPU. The key is the flag. When decoding works, the model trusts the text more. When decoding fails, it trusts the image. The model learns this by itself. We do not write any rules.

### Slide 18: Section: Experimentation  *(~5 s)*

Now, the experimental setup.

### Slide 19: Datasets  *(~60 s)*

We use two datasets that are very different, on purpose. The Trad dataset has about ten thousand clean QR codes. They all have the same size: sixty-nine by sixty-nine pixels. CIC-Trap4Phish has more than one million real QR codes, with different sizes and versions. We take fifty thousand samples per class from CIC. Then we split each dataset eighty-twenty, and we join the test sets. This gives 21,998 test samples. Note that the decoder works on all Trad codes, but only on 95.7% of CIC codes. The other 4.3% are exactly where the visual branch is the only signal.

### Slide 20: Section: Results  *(~5 s)*

Let's see the results. We ran six experiments.

### Slide 21: Experiment 1: the visual fallback  *(~45 s)*

Experiment one tests the visual branch alone. This is the fallback, for when the QR code cannot be decoded. Our best visual model reaches an AUC of 0.915. That is about 0.10 better than the classic baselines, Random Forest and XGBoost. It also matches the best previous visual result, from Trad and colleagues, but on a benchmark eleven times larger. Remember, this is the floor of the system. It is what Q-Shield can still do without the URL.

### Slide 22: Experiment 2: multimodal fusion  *(~55 s)*

Experiment two is our main result. Here we compare the visual branch, the text branch, and the fusion. The fusion is the best: AUC 0.975, F1 0.936, and a false negative rate of only 0.057. A false negative is a phishing code that we miss. In security, this is the most expensive error. Compared to the visual branch alone, we miss three and a half times fewer attacks. The gain over the text branch is small on average, but it is concentrated in the 4.3% of codes that cannot be decoded.

### Slide 23: Experiment 3: ablation study  *(~40 s)*

Experiment three is an ablation study. We remove one part at a time, and we see what happens. Without Siamese pretraining, the false negative rate goes up from 0.20 to 0.27. Without focal loss, the AUC is almost the same, but again the false negative rate goes up, to 0.27. So, both parts help us to miss fewer attacks. When a missed attack is expensive, the loss function matters.

### Slide 24: Experiment 4: cross-dataset generalization  *(~50 s)*

Experiment four is about generalization. What happens if we train on one dataset and test on the other? If we train on Trad and test on CIC, the AUC is 0.52. That is almost random. If we train on CIC and test on Trad, the model says "phishing" for almost everything. But when we train on both datasets, the AUC goes back to 0.896. Our message is clear: training on one dataset is not enough. Mixed training is a requirement, not a tuning choice.

### Slide 25: Experiment 5: operational trade-offs  *(~55 s)*

Experiment five is about real deployment. On the left, the threshold. For the visual fallback, if we lower the threshold from 0.50 to 0.40, the false negative rate goes below 0.10, without retraining. The price is lower precision, so we get more false alarms. The fusion model already meets this target with the default threshold. On the right, the cost. The visual model has only three million parameters and runs in 25 milliseconds on a CPU. The full model takes about 100 milliseconds. Both are fast enough for a mobile phone.

### Slide 26: Experiment 6: explainability  *(~50 s)*

Finally, experiment six: explainability. We want to know if the model looks at the real QR structure, or if it learns tricks from the dataset. Grad-CAM shows where the model looks. It looks at the alignment patterns and the data regions, the parts that carry the information. The attention maps of the two datasets are correlated, with r equal to 0.43. And SHAP shows that a few dimensions of the embedding drive the decision. This suggests that the model learns real structural patterns, not dataset shortcuts.

### Slide 27: Section: Limitations  *(~5 s)*

Of course, our work has some limitations.

### Slide 28: Limitations  *(~45 s)*

First, the visual fallback still misses about 20% of attacks, with an FNR of 0.199. Second, we see mild overfitting in phase two, and we control it with early stopping. Third, the performance is lower on large, high-resolution QR codes. And fourth, the probabilities of the visual branch are not perfectly calibrated. Also, we only look at the QR image and its URL, not the message around it. So, Q-Shield is one layer of defense, not the complete solution.

### Slide 29: Section: Conclusions  *(~5 s)*

To conclude, let me go back to our three objectives.

### Slide 30: Conclusions  *(~50 s)*

Our main finding is this: multimodal fusion is not just a small improvement. It reduces the false negative rate from 0.202 to 0.057, and it still covers the QR codes that cannot be decoded. About our three objectives. One: by following the two stages of a QR scan, we miss three and a half times fewer attacks. Two: for generalization, training on both datasets raises the AUC from 0.52 to 0.896. And three: for explainability, the attention maps agree across datasets, with r equal to 0.43.

### Slide 31: Section: Future Work  *(~5 s)*

And what comes next?

### Slide 32: Future Work  *(~45 s)*

We see four directions. First, a third branch that reads the context: the message, the sender, and the web page. Second, multi-scale training, to improve the results on large QR codes. Third, robustness against adversarial and stylized QR codes. And fourth, adapting the model to QR payment systems in Latin America, like Yape and Plin here in Peru. This is very important for our region, because QR payments are growing so fast.

### Slide 33: Thank you  *(~10 s)*

Thank you very much for your attention. I am happy to answer your questions.

**Total planned time:** about 20 minutes (1220 seconds).

## How to say the difficult words

| Word | Say it like |
|---|---|
| quishing / phishing | **KWISH**-ing / **FISH**-ing |
| Yape / Plin | **YAH**-peh / pleen |
| Kaspersky | kas-**PER**-skee |
| Siamese | sigh-uh-**MEEZ** |
| contrastive | kun-**TRAS**-tiv |
| MobileNetV2 | **MO**-bile-net vee-**two** |
| DistilBERT | **DIS**-til-bert |
| pyzbar | **PIE**-zee-bar |
| sigmoid | **SIG**-moyd |
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
| 2.2 billion | two point two billion |
| +85% | eighty-five percent more |
| 26M | twenty-six million |
| 67% | sixty-seven percent |
| 12.4% | twelve point four percent (about one in eight) |
| 5× | five times |
| 11,000+ | more than eleven thousand |
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
| p(y=1 \| x) | "the probability of phishing, given the image" |
| AUC, FNR, F1 | A-U-C, F-N-R (false negative rate), F-one |

## Key numbers to remember

| What | Number | Source |
|---|---|---|
| QR payment users in the world | 2.2 billion by 2025 (forecast, 29% of mobile users) | Juniper Research, 2021 |
| QR payments in Peru | +85% in 2024; more than 26 million per month | BCRP, 2025 |
| Peruvian adults with an account or digital wallet | 67% (end of 2025) | SBS |
| Phishing attacks that use a QR code | 0.8% (2021), 1.4% (2022), 12.4% (2023) | Egress, Phishing Threat Trends Report 2024 |
| QR phishing emails | 46,969 (Aug 2025) to 249,723 (Nov 2025), about 5× | Kaspersky |
| Malicious QR detections | more than 11,000 per day | Palo Alto Networks Unit 42, 2026 |
| Undecodable QR codes in CIC | 4.3% (decoder works on 95.7%) | our data |
| Test set (joint benchmark) | 21,998 samples | our data |
| Visual branch (fallback), best | AUC 0.9146, FNR 0.199 | paper |
| Visual branch, single model | AUC 0.8962, FNR 0.202 | paper |
| Text branch | AUC 0.9592, FNR 0.069 | paper |
| **Fusion (main result)** | **AUC 0.9749, F1 0.936, FNR 0.057** | paper |
| Fewer missed attacks vs. visual | 3.5× | paper |
| Cross-dataset: Trad to CIC / CIC to Trad / both | AUC 0.52 / 0.72 / 0.896 | paper |
| Fusion module | 81 parameters, 3 to 16 to 1 | paper |
| Cost | visual 3.08 M params, ~25 ms CPU; full model 69.1 M params, ~100 ms CPU | paper |
| Explainability | r = 0.43 across datasets; inter/intra distance ratio 1.94 | paper |

## Questions you may get (with simple answers)

**1. Where do the statistics in the first slides come from?**
They come from public reports. The world numbers are from Juniper Research, Egress, Kaspersky and
Palo Alto Networks. The Peru numbers are from the Central Reserve Bank (BCRP) and the SBS.
They are industry numbers, so we use them only for motivation, not as experimental results.

**2. A QR code can hold many things. Why do you only study URLs?**
Most QR codes in daily use hold a URL, and most quishing attacks use a URL. Our text branch reads URLs.
But our visual branch does not need the content at all, so it can still help with other payloads.
Testing Wi-Fi or payment payloads at scale is future work.

**3. Why is the false negative rate of the visual branch still high (0.199)?**
The visual branch is only the fallback, for codes that cannot be decoded. If we lower the threshold to 0.40,
the FNR goes down to 0.098, without retraining. And the full model already has an FNR of 0.057 with the default threshold.

**4. Isn't the fusion module too simple?**
It is small on purpose. Both branches are frozen, so the fusion only receives three numbers. A small model is
enough, and it is hard to overfit. Also, with logits we can see how much each branch contributes.

**5. Did you try feature-level fusion?**
Yes. We joined the 128-dimensional visual embedding with the 768-dimensional DistilBERT output. It needs both
full networks at inference time, and it gave no measurable gain. So we kept logit-level fusion.

**6. Is it safe to decode the QR code?**
Yes. pyzbar works locally. There is no internet connection, no DNS lookup, and we never open the link.
Reading the text is not the same as visiting the page.

**7. How do you compare with Trad et al.?**
Our visual branch reaches an AUC of 0.915, which matches their result of about 0.913. But we test on a benchmark
eleven times larger, with real-world images.

**8. Can it run on a phone?**
The visual model has 3.08 million parameters, about 12 MB, and runs in about 25 milliseconds on a CPU.
The full model has 69.1 million parameters, about 267 MB, and runs in about 100 milliseconds.
Both fit a normal mobile time budget, and the full model can also run on a server.

**9. Can Q-Shield stop the fake sticker scam on Yape and Plin?**
Not directly. In that scam, the fake code often holds a real payment account, not a phishing link.
Our model looks for phishing QR codes. Payment checks, like showing the name of the receiver before paying,
are a better defense for that case. Adapting to QR payment systems is part of our future work.

**10. What about adversarial or stylized QR codes?**
We did not test them in this paper. It is one of our next steps.

**11. Why only 50,000 samples per class from CIC?**
To keep training time reasonable. It is a stratified sample, so the classes stay balanced.

**12. How do you know the model is not learning dataset shortcuts?**
Two reasons. First, we train on both datasets, because training on one dataset fails on the other.
Second, the Grad-CAM difference maps of the two datasets are correlated, with r equal to 0.43.
This suggests that the model uses similar structural cues in both datasets.

### Useful phrases for the Q&A

- "Sorry, could you repeat the question, please?"
- "Thank you, that is a great question."
- "If I understand correctly, you are asking about ... Is that right?"
- "We did not test that in this paper, but it is a good idea for future work."
- "I am not completely sure, but I think ..."
