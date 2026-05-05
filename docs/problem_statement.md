# Problem Statement: The Quishing Threat in Emerging Economies

## 1. Background

### 1.1 The QR Code Revolution

QR (Quick Response) codes have become ubiquitous in digital payment ecosystems. In Latin America, mobile payment platforms have driven mass adoption:

- **Yape** (Peru): 15M+ users, QR-based P2P payments
- **Plin** (Peru): Interbank coalition QR payments
- **PIX** (Brazil): 150M+ users, QR-based instant transfers
- **CoDi** (Mexico): Central bank QR payment system

This creates an unprecedented attack surface where a single malicious QR code can redirect millions of users to credential-harvesting pages.

### 1.2 Quishing Defined

**Quishing** (QR + Phishing) is a social engineering attack where adversaries distribute malicious QR codes that redirect victims to phishing websites. Unlike traditional phishing:

- The malicious URL is **invisible** to the human eye (encoded in the QR pattern)
- The attack leverages **trust** in QR codes as a legitimate technology
- Detection requires **visual processing** that traditional text-based filters lack

## 2. The Three Fundamental Problems

### Problem 1: Visual Blindness

Current phishing detection systems analyze:
- Email headers and body text
- URL patterns and domain reputation
- HTML content of landing pages

**None of these approaches can detect a malicious URL embedded inside a QR code image.** The QR code is treated as an opaque image attachment, not as a container for a URL. This is analogous to a security guard who reads every letter but ignores packages.

**Evidence:** Major email security providers (Google Safe Browsing, Microsoft Defender) flag malicious URLs in text but pass through the same URLs when encoded as QR images (Trad & Chehab, 2025).

### Problem 2: Single-Modality Limits and the Decoding Question

The intuitive solution — "decode the QR and analyze the URL" — was historically framed as creating a security paradox, but a careful reading dissolves the paradox into two separable steps:

1. **Reading the encoded string** (e.g., with `pyzbar` / libzbar) is local, deterministic, and offline. It does not perform a network call, DNS lookup, or browser render. This step is safe.
2. **Opening the URL** (browser fetch + JavaScript execution) is what carries the actual exposure risk.

What does remain a real challenge is that **either modality alone is insufficient in heterogeneous deployments**:

- A **URL-only detector** assumes the QR can be decoded; it has no signal when decoding fails (low contrast, missing quiet zone, damaged finder pattern, non-URL payloads such as Wi-Fi or vCard).
- An **image-only detector** has weaker discriminative power on visually heterogeneous QR distributions (CIC Trap4Phish 2025 reports SSIM benign↔malicious ≈ 0.34 and CNN F1 0.88 for the image-only branch versus F1 0.97-0.99 for an LLM over the decoded URL on the same corpus).

Q-Shield operates in both regimes simultaneously. A pre-decode visual branch (Siamese MobileNetV2) consumes the QR image; an offline URL decoder feeds the post-decode payload to a transformer (DistilBERT) text branch; a small late-fusion head with an explicit *undecodability* flag produces the final probability. The fusion inherits the URL branch's accuracy when decoding succeeds and the visual branch's score when it does not, achieving AUC 0.9749 on the joint validation set.

### Problem 3: Localization Gap

Existing phishing detection models are predominantly trained on English-language campaigns. In Peru and Latin America, attackers exploit:

- **Local platforms**: "Tu cuenta Yape ha sido suspendida" (Your Yape account has been suspended)
- **Currency-specific lures**: "Gana S/500 ahora" (Win S/500 now)
- **Cultural trust cues**: References to SUNAT (tax authority), BCP (largest bank), or Reniec (ID authority)
- **Urgency in local context**: "Regulariza tu situacion antes de las 24h" (Regularize your situation within 24h)
- **Slang and informal language**: "Yapeame", "Plineame", colloquial financial terms

No existing quishing detection system understands these linguistic patterns.

## 3. Threat Model

### 3.1 Attack Vector

```
Attacker creates       Distributes via        Victim scans QR       Redirected to
malicious QR     -->   SMS, social media, --> code with phone  -->  phishing page
code                   physical stickers      camera                that mimics Yape/
                                                                    Plin/BCP login
```

### 3.2 Attack Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Credential Harvesting** | Fake login pages for banks/apps | "Verifica tu identidad Yape" + QR to fake login |
| **Financial Fraud** | Redirect to attacker's payment QR | QR sticker placed over legitimate merchant QR |
| **Malware Distribution** | QR leads to APK download | "Actualiza tu app BCP" + QR to malicious APK |
| **Data Exfiltration** | QR encodes Wi-Fi credentials | "WiFi gratis" QR that captures device traffic |

### 3.3 Social Engineering Tactics

Based on our analysis of Peruvian phishing campaigns:

| Tactic | Mechanism | Prevalence |
|--------|-----------|------------|
| **Urgency** | "Act now or lose access" | High |
| **Authority** | Impersonation of banks, SUNAT, police | High |
| **Reward** | Free money, prizes, discounts | Medium |
| **Scarcity** | "Limited time offer" | Medium |
| **Social Proof** | "1000+ users already verified" | Low |

## 4. Why Existing Solutions Fail

| Approach | Failure Mode for Quishing |
|----------|--------------------------|
| URL blacklists | QR payload is not in the message text — URL never reaches the filter |
| Email text analysis | The malicious content is in the image, not the text |
| Browser-based detection | By the time the browser loads the page, the redirect chain has started |
| QR decoder + URL check | Requires decoding (security risk); fails against shorteners and redirects |
| Image-based phishing detection | Trained on webpage screenshots, not QR code structural analysis |

## 5. Our Proposed Solution: Q-Shield

Q-Shield addresses all three problems simultaneously:

| Problem | Solution |
|---------|----------|
| Visual Blindness | MobileNetV2 visual branch extracts structural features from QR images |
| Decoding Paradox | Analysis operates on the QR image structure — payload is NEVER decoded |
| Localization Gap | DistilBERT semantic branch understands Peruvian Spanish social engineering |

### Additional Design Goals

- **Edge Deployable**: Must run on mid-range Android devices (MobileNetV2 + DistilBERT)
- **Explainable**: Security analysts need to understand WHY a QR code is flagged (Grad-CAM + SHAP)
- **Real-time**: Detection must complete before the user acts on the QR code

## 6. Scope and Limitations

### In Scope
- Binary classification: benign vs. phishing QR codes
- SMS/message text analysis for social engineering detection
- Peruvian/Latin American fintech context
- Mobile-deployable model architecture

### Out of Scope (Future Work)
- Multi-class classification (phishing subtypes)
- Real-time mobile app deployment
- Non-QR visual phishing (e.g., fake app screenshots)
- Audio-based social engineering
