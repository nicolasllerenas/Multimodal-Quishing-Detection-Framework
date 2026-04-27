"""Ensemble evaluation: averages probabilities from multiple v3 checkpoints,
each with TTA (original + horizontal flip), on the full 21,998 validation set.

Auto-detects which seeds are available in BASE:
  - classifier_v3_phase2.pth          (seed 42 — required)
  - classifier_v3_seed7_phase2.pth    (seed 7  — optional)
  - classifier_v3_seed2024_phase2.pth (seed 2024 — optional)

Reports per-seed and ensemble metrics, with delta vs Trad (0.9133).
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

DATA_SEED = 42  # frozen — must match train script
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
if not os.path.exists(cic_b_dir) or len(os.listdir(cic_b_dir)) == 0:
    os.makedirs(cic_b_dir, exist_ok=True)
    with zipfile.ZipFile(os.path.join(BASE, 'QR_benign_430K.zip')) as z:
        z.extractall(cic_b_dir)
if not os.path.exists(cic_m_dir) or len(os.listdir(cic_m_dir)) == 0:
    os.makedirs(cic_m_dir, exist_ok=True)
    with zipfile.ZipFile(os.path.join(BASE, 'QR_malicious_576K.zip')) as z:
        z.extractall(cic_m_dir)

cic_b_files = sorted(glob.glob(os.path.join(cic_b_dir, '**', '*.png'), recursive=True))
cic_m_files = sorted(glob.glob(os.path.join(cic_m_dir, '**', '*.png'), recursive=True))

data_rng = random.Random(DATA_SEED)
cic_b_files = data_rng.sample(cic_b_files, min(50000, len(cic_b_files)))
cic_m_files = data_rng.sample(cic_m_files, min(50000, len(cic_m_files)))

idx_tr, idx_val = train_test_split(np.arange(len(trad_labels)), test_size=0.2,
                                   stratify=trad_labels, random_state=DATA_SEED)
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
        self.cic_b = cic_b; self.cic_m = cic_m

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
print(f'Validation samples: {len(val_ds):,}')

CHECKPOINTS = [
    ('seed42', 'classifier_v3_phase2.pth'),
    ('seed7', 'classifier_v3_seed7_phase2.pth'),
    ('seed2024', 'classifier_v3_seed2024_phase2.pth'),
]
available = [(name, fn) for name, fn in CHECKPOINTS if os.path.exists(os.path.join(BASE, fn))]
print(f'Found {len(available)} checkpoint(s): {[n for n, _ in available]}')
assert len(available) >= 2, 'Need at least 2 checkpoints for an ensemble.'

def tta_probs(classifier):
    """Return probabilities averaged over original + horizontal-flip pass."""
    p_orig, p_flip, true = [], [], []
    classifier.eval()
    with torch.no_grad():
        for imgs, lbls in val_loader:
            imgs = imgs.to(device)
            logits_o = classifier(imgs)
            logits_f = classifier(torch.flip(imgs, dims=[-1]))
            p_orig.extend(torch.sigmoid(logits_o).cpu().numpy().flatten())
            p_flip.extend(torch.sigmoid(logits_f).cpu().numpy().flatten())
            true.extend(lbls.numpy().flatten())
    return (np.array(p_orig) + np.array(p_flip)) / 2.0, np.array(true).astype(int)

def metrics(probs, true):
    preds = (probs >= 0.5).astype(int)
    cm = confusion_matrix(true, preds)
    tn, fp, fn, tp = cm.ravel()
    return {
        'auc': float(roc_auc_score(true, probs)),
        'precision': float(precision_score(true, preds)),
        'recall': float(recall_score(true, preds)),
        'f1': float(f1_score(true, preds)),
        'fnr': float(fn / (fn + tp)),
        'fpr': float(fp / (fp + tn)),
        'cm': {'TN': int(tn), 'FP': int(fp), 'FN': int(fn), 'TP': int(tp)},
    }

per_seed_probs = []
per_seed_metrics = {}
true_labels = None

for name, fn in available:
    print(f'\n[+] Loading {name} from {fn}')
    classifier = QRClassifier(emb_dim=128).to(device)
    state = torch.load(os.path.join(BASE, fn), map_location=device)
    classifier.load_state_dict(state)
    p, t = tta_probs(classifier)
    if true_labels is None:
        true_labels = t
    per_seed_probs.append(p)
    per_seed_metrics[name] = metrics(p, t)
    print(f'    {name} TTA  AUC={per_seed_metrics[name]["auc"]:.4f}  '
          f'F1={per_seed_metrics[name]["f1"]:.4f}  '
          f'FNR={per_seed_metrics[name]["fnr"]:.4f}')

ensemble_probs = np.mean(per_seed_probs, axis=0)
ensemble_m = metrics(ensemble_probs, true_labels)

print()
print('=' * 80)
print(f' ENSEMBLE TTA on {len(true_labels):,} samples (threshold = 0.5)')
print('=' * 80)
for name, m in per_seed_metrics.items():
    print(f"{name + ' TTA':<22}  AUC={m['auc']:.4f}  P={m['precision']:.4f}  "
          f"R={m['recall']:.4f}  F1={m['f1']:.4f}  FNR={m['fnr']:.4f}")
print('-' * 80)
print(f"{'ENSEMBLE TTA':<22}  AUC={ensemble_m['auc']:.4f}  "
      f"P={ensemble_m['precision']:.4f}  R={ensemble_m['recall']:.4f}  "
      f"F1={ensemble_m['f1']:.4f}  FNR={ensemble_m['fnr']:.4f}")
print('=' * 80)

trad_auc = 0.9133
delta = ensemble_m['auc'] - trad_auc
print(f'\nEnsemble vs Trad 0.9133: {delta:+.4f}  '
      f'({"ABOVE" if delta > 0 else "below"} by {abs(delta) * 100:.2f} pp)')
cm_e = ensemble_m['cm']
print(f"Ensemble CM: TN={cm_e['TN']}  FP={cm_e['FP']}  "
      f"FN={cm_e['FN']}  TP={cm_e['TP']}")

if delta > 0:
    print('\n>>> ENSEMBLE BEATS TRAD. Stop training; update paper with these numbers.')
else:
    print(f'\n>>> Ensemble still below Trad by {abs(delta) * 100:.2f} pp.')
    if len(available) < 3:
        next_seed = 'seed2024' if 'seed7' in dict(available) else 'seed7'
        print(f'    Train next seed ({next_seed}) and re-run this script.')
    else:
        print('    All 3 seeds trained. Consider Camino A (reframe) or further tuning.')

out = {
    'n_samples': int(len(true_labels)),
    'threshold': 0.5,
    'per_seed_tta': per_seed_metrics,
    'ensemble_tta': ensemble_m,
    'trad_sota_auc': trad_auc,
    'delta_ensemble_vs_trad': float(delta),
    'n_seeds': len(available),
}
out_path = os.path.join(BASE, f'eval_ensemble_{len(available)}seeds_tta.json')
with open(out_path, 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: {out_path}')
