"""Standalone evaluation of the saved v3 classifier on the full combined validation set.

Run this as a single Colab cell (or sequence of cells). It reproduces the exact
validation split used by 06_Siamese_Training_v3.ipynb (SEED=42, stratified 80/20
for Trad, fixed random.sample-then-slice for CIC) and reports AUC, Precision,
Recall, F1, FNR, and the confusion matrix.

Expected checkpoints in BASE:
  - classifier_v3_phase2.pth  (QRClassifier state_dict)

Expected data in BASE:
  - QuishingDataset.zip           (Trad)
  - QR_benign_430K.zip            (CIC benign)
  - QR_malicious_576K.zip         (CIC malicious)
"""

import os, sys, glob, random, pickle, zipfile, json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import models
from sklearn.metrics import (roc_auc_score, f1_score, precision_score,
                             recall_score, confusion_matrix, classification_report)
from sklearn.model_selection import train_test_split
from PIL import Image

IN_COLAB = 'google.colab' in sys.modules
if IN_COLAB:
    from google.colab import drive
    drive.mount('/content/drive')

BASE = '/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas'
assert os.path.exists(BASE), f'BASE not found: {BASE}'

SEED = 42
torch.manual_seed(SEED); np.random.seed(SEED); random.seed(SEED)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Device: {device} | BASE: {BASE}')

class MobileNetV2Embedding(nn.Module):
    def __init__(self, emb_dim=128, pretrained=False, dropout=0.35):
        super().__init__()
        mn = models.mobilenet_v2(weights=None)
        self.features = mn.features
        self.features[0][0] = nn.Conv2d(1, 32, 3, stride=2, padding=1, bias=False)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.projection = nn.Sequential(
            nn.Linear(1280, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(True),
            nn.Dropout(dropout),
            nn.Linear(512, emb_dim),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x).flatten(1)
        x = self.projection(x)
        return F.normalize(x, p=2, dim=1)

class QRClassifier(nn.Module):
    def __init__(self, emb_dim=128):
        super().__init__()
        self.backbone = MobileNetV2Embedding(emb_dim=emb_dim)
        self.head = nn.Sequential(
            nn.Linear(emb_dim, 512), nn.BatchNorm1d(512), nn.ReLU(True), nn.Dropout(0.4),
            nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(True), nn.Dropout(0.3),
            nn.Linear(128, 32), nn.ReLU(True), nn.Dropout(0.2),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        return self.head(self.backbone(x))

WORK = '/content/qshield_eval'
os.makedirs(WORK, exist_ok=True)

trad_dir = os.path.join(WORK, 'trad')
if not os.path.exists(os.path.join(trad_dir, 'qr_codes_29.pickle')):
    os.makedirs(trad_dir, exist_ok=True)
    with zipfile.ZipFile(os.path.join(BASE, 'QuishingDataset.zip')) as z:
        z.extractall(trad_dir)
with open(os.path.join(trad_dir, 'qr_codes_29.pickle'), 'rb') as f:
    trad_qr = pickle.load(f)
with open(os.path.join(trad_dir, 'qr_codes_29_labels.pickle'), 'rb') as f:
    trad_labels = pickle.load(f)

cic_b_dir = os.path.join(WORK, 'cic_benign')
cic_m_dir = os.path.join(WORK, 'cic_malicious')
zip_b = os.path.join(BASE, 'QR_benign_430K.zip')
zip_m = os.path.join(BASE, 'QR_malicious_576K.zip')

if not os.path.exists(cic_b_dir) or len(os.listdir(cic_b_dir)) == 0:
    os.makedirs(cic_b_dir, exist_ok=True)
    with zipfile.ZipFile(zip_b) as z: z.extractall(cic_b_dir)
if not os.path.exists(cic_m_dir) or len(os.listdir(cic_m_dir)) == 0:
    os.makedirs(cic_m_dir, exist_ok=True)
    with zipfile.ZipFile(zip_m) as z: z.extractall(cic_m_dir)

cic_b_files = sorted(glob.glob(os.path.join(cic_b_dir, '**', '*.png'), recursive=True))
cic_m_files = sorted(glob.glob(os.path.join(cic_m_dir, '**', '*.png'), recursive=True))
random.seed(SEED)
cic_b_files = random.sample(cic_b_files, min(50000, len(cic_b_files)))
cic_m_files = random.sample(cic_m_files, min(50000, len(cic_m_files)))

idx_tr, idx_val = train_test_split(np.arange(len(trad_labels)), test_size=0.2,
                                   stratify=trad_labels, random_state=SEED)
qr_val, lab_val = trad_qr[idx_val], trad_labels[idx_val]

sb = int(len(cic_b_files) * 0.8)
sm = int(len(cic_m_files) * 0.8)
cic_b_val = cic_b_files[sb:]
cic_m_val = cic_m_files[sm:]

print(f'Val counts: Trad={len(qr_val):,}, CIC benign={len(cic_b_val):,}, '
      f'CIC malicious={len(cic_m_val):,}, total={len(qr_val)+len(cic_b_val)+len(cic_m_val):,}')

class ClassifyDataset(Dataset):
    def __init__(self, trad_qr, trad_labels, cic_b, cic_m):
        self.items = []
        for i in range(len(trad_qr)):
            self.items.append(('trad', i, int(trad_labels[i])))
        for i, _ in enumerate(cic_b):
            self.items.append(('cic_b', i, 0))
        for i, _ in enumerate(cic_m):
            self.items.append(('cic_m', i, 1))
        self.trad_qr = trad_qr.astype(np.float32)
        self.cic_b = cic_b
        self.cic_m = cic_m

    def __len__(self): return len(self.items)

    def __getitem__(self, idx):
        src, i, lbl = self.items[idx]
        if src == 'trad':
            t = torch.from_numpy(self.trad_qr[i]).unsqueeze(0).unsqueeze(0)
            t = F.interpolate(t, size=(224, 224), mode='bilinear', align_corners=False).squeeze(0)
        else:
            files = self.cic_b if src == 'cic_b' else self.cic_m
            img = Image.open(files[i]).convert('L').resize((224, 224))
            t = torch.from_numpy(np.array(img, dtype=np.float32) / 255.0).unsqueeze(0)
        return t, torch.tensor(float(lbl))

val_ds = ClassifyDataset(qr_val, lab_val, cic_b_val, cic_m_val)
val_loader = DataLoader(val_ds, batch_size=512, shuffle=False,
                        num_workers=4 if IN_COLAB else 0, pin_memory=True)
print(f'Total validation samples: {len(val_ds):,}')

classifier = QRClassifier(emb_dim=128).to(device)
ckpt_path = os.path.join(BASE, 'classifier_v3_phase2.pth')
assert os.path.exists(ckpt_path), f'Checkpoint not found: {ckpt_path}'
state = torch.load(ckpt_path, map_location=device)
classifier.load_state_dict(state)
classifier.eval()
n_params = sum(p.numel() for p in classifier.parameters())
print(f'Loaded {ckpt_path}  ({n_params:,} params)')

probs, true = [], []
with torch.no_grad():
    for imgs, lbls in val_loader:
        logits = classifier(imgs.to(device))
        probs.extend(torch.sigmoid(logits).cpu().numpy().flatten())
        true.extend(lbls.numpy().flatten())
probs = np.array(probs)
true = np.array(true).astype(int)

preds = (probs >= 0.5).astype(int)
auc = roc_auc_score(true, probs)
prec = precision_score(true, preds)
rec = recall_score(true, preds)
f1 = f1_score(true, preds)
cm = confusion_matrix(true, preds)
tn, fp, fn, tp = cm.ravel()
fnr = fn / (fn + tp)
fpr = fp / (fp + tn)

print()
print('=' * 60)
print(f' FINAL EVAL on {len(true):,} samples (threshold = 0.5)')
print('=' * 60)
print(f'AUC         : {auc:.4f}')
print(f'Precision   : {prec:.4f}')
print(f'Recall      : {rec:.4f}')
print(f'F1          : {f1:.4f}')
print(f'FNR         : {fnr:.4f}')
print(f'FPR         : {fpr:.4f}')
print(f'Confusion   : TN={tn}  FP={fp}  FN={fn}  TP={tp}')
print()
print('Comparison with Trad et al. (AUC 0.9133 on 1,998 samples):')
delta = auc - 0.9133
print(f'  Delta AUC vs Trad: {delta:+.4f}  '
      f'({"above" if delta > 0 else "below"} by {abs(delta)*100:.2f} pp)')
print('=' * 60)

out = {
    'n_samples': int(len(true)),
    'threshold': 0.5,
    'auc': float(auc),
    'precision': float(prec),
    'recall': float(rec),
    'f1': float(f1),
    'fnr': float(fnr),
    'fpr': float(fpr),
    'confusion_matrix': {'TN': int(tn), 'FP': int(fp), 'FN': int(fn), 'TP': int(tp)},
    'trad_sota_auc': 0.9133,
    'delta_vs_trad': float(delta),
}
out_path = os.path.join(BASE, 'eval_v3_full_set.json')
with open(out_path, 'w') as f:
    json.dump(out, f, indent=2)
print(f'Saved: {out_path}')
