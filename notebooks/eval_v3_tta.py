"""Test-Time Augmentation evaluation of the saved v3 classifier on the full
combined validation set.

For each image x we run two forward passes:
  - p1 = sigmoid(classifier(x))
  - p2 = sigmoid(classifier(hflip(x)))
and report metrics using the averaged probability (p1 + p2) / 2.

Same data split as eval_v3_on_full_set.py (SEED=42, stratified 80/20 for Trad,
random.sample-then-slice for CIC). Loads classifier_v3_phase2.pth.
"""

import os, sys, glob, random, pickle, zipfile, json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import models
from sklearn.metrics import (roc_auc_score, f1_score, precision_score,
                             recall_score, confusion_matrix)
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
    def __init__(self, emb_dim=128, dropout=0.35):
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
nw = 2 if IN_COLAB else 0
val_loader = DataLoader(val_ds, batch_size=256, shuffle=False,
                        num_workers=nw, pin_memory=(device.type == 'cuda'))
print(f'Total validation samples: {len(val_ds):,}')

classifier = QRClassifier(emb_dim=128).to(device)
ckpt_path = os.path.join(BASE, 'classifier_v3_phase2.pth')
state = torch.load(ckpt_path, map_location=device)
classifier.load_state_dict(state)
classifier.eval()
print(f'Loaded {ckpt_path}')

def run_pass(loader, flip):
    probs, true = [], []
    with torch.no_grad():
        for imgs, lbls in loader:
            imgs = imgs.to(device)
            if flip:
                imgs = torch.flip(imgs, dims=[-1])
            logits = classifier(imgs)
            probs.extend(torch.sigmoid(logits).cpu().numpy().flatten())
            true.extend(lbls.numpy().flatten())
    return np.array(probs), np.array(true).astype(int)

print('\n[1/2] Forward pass on original images...')
p_orig, true = run_pass(val_loader, flip=False)
print('[2/2] Forward pass on horizontal-flipped images...')
p_flip, _ = run_pass(val_loader, flip=True)

def report(probs, true, label):
    preds = (probs >= 0.5).astype(int)
    auc = roc_auc_score(true, probs)
    prec = precision_score(true, preds)
    rec = recall_score(true, preds)
    f1 = f1_score(true, preds)
    cm = confusion_matrix(true, preds)
    tn, fp, fn, tp = cm.ravel()
    fnr = fn / (fn + tp)
    fpr = fp / (fp + tn)
    return {
        'label': label,
        'auc': float(auc),
        'precision': float(prec),
        'recall': float(rec),
        'f1': float(f1),
        'fnr': float(fnr),
        'fpr': float(fpr),
        'cm': {'TN': int(tn), 'FP': int(fp), 'FN': int(fn), 'TP': int(tp)},
    }

r_orig = report(p_orig, true, 'no TTA (original only)')
r_flip = report(p_flip, true, 'flip only')
p_avg = (p_orig + p_flip) / 2.0
r_tta = report(p_avg, true, 'TTA (avg of both)')

def _print(r):
    print(f"{r['label']:<28}  AUC={r['auc']:.4f}  P={r['precision']:.4f}  "
          f"R={r['recall']:.4f}  F1={r['f1']:.4f}  FNR={r['fnr']:.4f}")

print()
print('=' * 80)
print(f' TTA EVAL on {len(true):,} samples (threshold = 0.5)')
print('=' * 80)
_print(r_orig)
_print(r_flip)
_print(r_tta)
print('=' * 80)
print()

trad_auc = 0.9133
delta_orig = r_orig['auc'] - trad_auc
delta_tta = r_tta['auc'] - trad_auc
gain = r_tta['auc'] - r_orig['auc']

print(f'TTA gain over no-TTA   : {gain:+.4f}')
print(f'No-TTA  vs Trad 0.9133 : {delta_orig:+.4f}  '
      f'({"above" if delta_orig > 0 else "below"} by {abs(delta_orig)*100:.2f} pp)')
print(f'TTA     vs Trad 0.9133 : {delta_tta:+.4f}  '
      f'({"above" if delta_tta > 0 else "below"} by {abs(delta_tta)*100:.2f} pp)')

cm_t = r_tta['cm']
print(f"\nTTA confusion matrix : TN={cm_t['TN']}  FP={cm_t['FP']}  "
      f"FN={cm_t['FN']}  TP={cm_t['TP']}")

out = {
    'n_samples': int(len(true)),
    'threshold': 0.5,
    'no_tta': r_orig,
    'flip_only': r_flip,
    'tta_avg': r_tta,
    'trad_sota_auc': trad_auc,
    'delta_no_tta_vs_trad': float(delta_orig),
    'delta_tta_vs_trad': float(delta_tta),
    'tta_gain': float(gain),
}
out_path = os.path.join(BASE, 'eval_v3_tta.json')
with open(out_path, 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: {out_path}')
