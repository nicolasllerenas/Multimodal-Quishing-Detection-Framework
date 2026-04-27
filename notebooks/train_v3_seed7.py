"""Train a second v3 checkpoint with TRAIN_SEED=7 for ensemble.

Data preparation uses DATA_SEED=42 (so the validation split is IDENTICAL to the
seed-42 model). Only weight init and pair-sampling stochasticity vary, giving
the diversity required for a valid ensemble.

Saves: classifier_v3_seed7_phase2.pth in BASE.
"""

import os, sys, glob, random, pickle, zipfile, copy, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, ConcatDataset
from torchvision import models
import torchvision.transforms as T
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from PIL import Image
from tqdm.auto import tqdm
import warnings
warnings.filterwarnings('ignore')

IN_COLAB = 'google.colab' in sys.modules
if IN_COLAB:
    from google.colab import drive
    drive.mount('/content/drive')

BASE = '/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas'
assert os.path.exists(BASE), f'BASE not found: {BASE}'

DATA_SEED = 42       # frozen so val set matches seed-42 model
TRAIN_SEED = 7       # varied across ensemble members
EMB_DIM = 128
MARGIN = 1.5
LR1 = 2e-4
EPOCHS1 = 40
WD = 2e-4
BATCH = 64           # T4 fits 64 (Siamese doubles forward memory). Use 128 only on A100.
BATCH_CLS = 128      # Phase 2 single-image, can be larger
PAIRS_TR = 60000
PAIRS_VAL = 8000
EPOCHS2 = 20
FROZEN_EP = 5
USE_AMP = True       # mixed precision saves ~40% memory on T4

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Device: {device} | DATA_SEED={DATA_SEED} | TRAIN_SEED={TRAIN_SEED}')
if device.type != 'cuda':
    print('WARNING: GPU not available. Training will take 10+ hours on CPU.')

torch.manual_seed(TRAIN_SEED); np.random.seed(TRAIN_SEED); random.seed(TRAIN_SEED)
if device.type == 'cuda':
    torch.cuda.manual_seed_all(TRAIN_SEED)
    torch.backends.cudnn.benchmark = True

WORK = '/content/qshield_data'
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

# DATA SPLITS USE DATA_SEED (frozen) so val matches seed-42 model
data_rng = random.Random(DATA_SEED)
cic_b_files = data_rng.sample(cic_b_files, min(50000, len(cic_b_files)))
cic_m_files = data_rng.sample(cic_m_files, min(50000, len(cic_m_files)))

idx_tr, idx_val = train_test_split(np.arange(len(trad_labels)), test_size=0.2,
                                   stratify=trad_labels, random_state=DATA_SEED)
qr_tr, lab_tr = trad_qr[idx_tr], trad_labels[idx_tr]
qr_val, lab_val = trad_qr[idx_val], trad_labels[idx_val]

sb = int(len(cic_b_files) * 0.8)
sm = int(len(cic_m_files) * 0.8)
cic_b_tr, cic_b_val = cic_b_files[:sb], cic_b_files[sb:]
cic_m_tr, cic_m_val = cic_m_files[:sm], cic_m_files[sm:]

print(f'Trad: {len(qr_tr):,} train / {len(qr_val):,} val')
print(f'CIC:  {len(cic_b_tr) + len(cic_m_tr):,} train / {len(cic_b_val) + len(cic_m_val):,} val')

torch.manual_seed(TRAIN_SEED); np.random.seed(TRAIN_SEED); random.seed(TRAIN_SEED)

train_aug = T.Compose([T.RandomHorizontalFlip(p=0.5)])

class TradPairDataset(Dataset):
    def __init__(self, qr, labels, n_pairs, augment=False):
        self.qr = qr.astype(np.float32)
        self.labels = np.array(labels)
        self.n = n_pairs
        self.idx = {0: np.where(self.labels == 0)[0], 1: np.where(self.labels == 1)[0]}
        self.aug = train_aug if augment else None

    def __len__(self): return self.n

    def _tensor(self, i):
        t = torch.from_numpy(self.qr[i]).unsqueeze(0).unsqueeze(0)
        t = F.interpolate(t, size=(224, 224), mode='bilinear', align_corners=False).squeeze(0)
        return self.aug(t) if self.aug else t

    def __getitem__(self, _):
        same = random.random() < 0.5
        c = random.choice([0, 1]); i1 = random.choice(self.idx[c])
        c2 = c if same else 1 - c; i2 = random.choice(self.idx[c2])
        return self._tensor(i1), self._tensor(i2), torch.tensor(0.0 if same else 1.0)

class CICPairDataset(Dataset):
    def __init__(self, benign, mal, n_pairs, augment=False):
        self.files = {0: benign, 1: mal}
        self.n = n_pairs
        self.aug = train_aug if augment else None

    def __len__(self): return self.n

    def _load(self, cls, idx):
        img = Image.open(self.files[cls][idx]).convert('L').resize((224, 224))
        arr = np.array(img, dtype=np.float32) / 255.0
        t = torch.from_numpy(arr).unsqueeze(0)
        return self.aug(t) if self.aug else t

    def __getitem__(self, _):
        same = random.random() < 0.5
        c = random.choice([0, 1]); i1 = random.randint(0, len(self.files[c]) - 1)
        c2 = c if same else 1 - c; i2 = random.randint(0, len(self.files[c2]) - 1)
        return self._load(c, i1), self._load(c2, i2), torch.tensor(0.0 if same else 1.0)

class ClassifyDataset(Dataset):
    def __init__(self, trad_qr, trad_labels, cic_b, cic_m, augment=False):
        self.items = []
        for i in range(len(trad_qr)):
            self.items.append(('trad', i, int(trad_labels[i])))
        for i, _ in enumerate(cic_b):
            self.items.append(('cic_b', i, 0))
        for i, _ in enumerate(cic_m):
            self.items.append(('cic_m', i, 1))
        self.trad_qr = trad_qr.astype(np.float32)
        self.cic_b = cic_b; self.cic_m = cic_m
        self.aug = train_aug if augment else None

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
        if self.aug: t = self.aug(t)
        return t, torch.tensor(float(lbl))

class MobileNetV2Embedding(nn.Module):
    def __init__(self, emb_dim=128, dropout=0.35):
        super().__init__()
        mn = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        orig = mn.features[0][0]
        self.features = mn.features
        self.features[0][0] = nn.Conv2d(1, 32, 3, stride=2, padding=1, bias=False)
        with torch.no_grad():
            self.features[0][0].weight = nn.Parameter(orig.weight.mean(dim=1, keepdim=True))
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

class SiameseQRNet(nn.Module):
    def __init__(self, emb_dim=128, dropout=0.35):
        super().__init__()
        self.backbone = MobileNetV2Embedding(emb_dim, dropout)

    def forward(self, x1, x2):
        return self.backbone(x1), self.backbone(x2)

class ContrastiveLoss(nn.Module):
    def __init__(self, margin=1.5):
        super().__init__(); self.margin = margin

    def forward(self, e1, e2, y):
        d = F.pairwise_distance(e1, e2)
        return ((1 - y) * 0.5 * d.pow(2) + y * 0.5 * F.relu(self.margin - d).pow(2)).mean()

class FocalLoss(nn.Module):
    def __init__(self, alpha=0.5, gamma=2.0):
        super().__init__(); self.alpha = alpha; self.gamma = gamma

    def forward(self, logits, targets):
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        p = torch.sigmoid(logits)
        pt = p * targets + (1 - p) * (1 - targets)
        alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        return (alpha_t * (1 - pt).pow(self.gamma) * bce).mean()

train_ds = ConcatDataset([
    TradPairDataset(qr_tr, lab_tr, PAIRS_TR, augment=True),
    CICPairDataset(cic_b_tr, cic_m_tr, PAIRS_TR, augment=True),
])
val_ds = ConcatDataset([
    TradPairDataset(qr_val, lab_val, PAIRS_VAL, augment=False),
    CICPairDataset(cic_b_val, cic_m_val, PAIRS_VAL, augment=False),
])
nw = 2 if IN_COLAB else 0
train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True,
                          num_workers=nw, pin_memory=(device.type == 'cuda'))
val_loader = DataLoader(val_ds, batch_size=BATCH, shuffle=False,
                        num_workers=nw, pin_memory=(device.type == 'cuda'))

print('\n========================================')
print(' PHASE 1: Siamese contrastive pretraining')
print('========================================')

model = SiameseQRNet(emb_dim=EMB_DIM, dropout=0.35).to(device)
criterion = ContrastiveLoss(margin=MARGIN)
optimizer = optim.AdamW(model.parameters(), lr=LR1, weight_decay=WD)
scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=15, T_mult=1, eta_min=1e-6)
scaler = torch.cuda.amp.GradScaler(enabled=(USE_AMP and device.type == 'cuda'))

best_vl = float('inf'); best_state = None; patience = 0
print(f'{"Ep":>3} {"TrLoss":>8} {"VaLoss":>8} {"TrAcc":>7} {"VaAcc":>7} {"LR":>10} {"Time":>6}')
print('-' * 60)

for ep in range(1, EPOCHS1 + 1):
    t0 = time.time()
    model.train()
    tl, tc, tt = 0, 0, 0
    for x1, x2, y in train_loader:
        x1, x2, y = x1.to(device), x2.to(device), y.to(device)
        optimizer.zero_grad()
        with torch.cuda.amp.autocast(enabled=(USE_AMP and device.type == 'cuda')):
            e1, e2 = model(x1, x2)
            loss = criterion(e1, e2, y)
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()
        tl += loss.item() * x1.size(0)
        with torch.no_grad():
            d = F.pairwise_distance(e1.float(), e2.float())
            tc += ((d > MARGIN / 2).float() == y).sum().item()
            tt += y.size(0)

    model.eval()
    vl, vc, vt = 0, 0, 0
    with torch.no_grad():
        for x1, x2, y in val_loader:
            x1, x2, y = x1.to(device), x2.to(device), y.to(device)
            with torch.cuda.amp.autocast(enabled=(USE_AMP and device.type == 'cuda')):
                e1, e2 = model(x1, x2)
                vloss = criterion(e1, e2, y)
            vl += vloss.item() * x1.size(0)
            d = F.pairwise_distance(e1.float(), e2.float())
            vc += ((d > MARGIN / 2).float() == y).sum().item()
            vt += y.size(0)

    scheduler.step()
    tl_a, vl_a = tl / tt, vl / vt
    ta, va = tc / tt, vc / vt
    mk = ''
    if vl_a < best_vl:
        best_vl = vl_a; best_state = copy.deepcopy(model.state_dict()); patience = 0; mk = ' *'
    else:
        patience += 1
    lr = optimizer.param_groups[0]['lr']
    print(f'{ep:>3} {tl_a:>8.4f} {vl_a:>8.4f} {ta:>6.1%} {va:>6.1%} {lr:>10.6f} {time.time() - t0:>5.0f}s{mk}')
    if patience >= 8:
        print(f'\nEarly stop at epoch {ep}')
        break

model.load_state_dict(best_state)
torch.save(best_state, os.path.join(BASE, f'siamese_v3_seed{TRAIN_SEED}_phase1.pth'))
print(f'\nPhase 1 best val loss: {best_vl:.4f}')

del train_loader, val_loader, train_ds, val_ds, scaler, optimizer, scheduler
import gc; gc.collect()
if device.type == 'cuda':
    torch.cuda.empty_cache()

print('\n========================================')
print(' PHASE 2: Supervised classification')
print('========================================')

class QRClassifier(nn.Module):
    def __init__(self, backbone, emb_dim=128):
        super().__init__()
        self.backbone = backbone
        self.head = nn.Sequential(
            nn.Linear(emb_dim, 512), nn.BatchNorm1d(512), nn.ReLU(True), nn.Dropout(0.4),
            nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(True), nn.Dropout(0.3),
            nn.Linear(128, 32), nn.ReLU(True), nn.Dropout(0.2),
            nn.Linear(32, 1),
        )

    def set_backbone_grad(self, requires_grad):
        for p in self.backbone.parameters():
            p.requires_grad = requires_grad

    def forward(self, x):
        return self.head(self.backbone(x))

classifier = QRClassifier(model.backbone, EMB_DIM).to(device)

tr_cls = ClassifyDataset(qr_tr, lab_tr, cic_b_tr, cic_m_tr, augment=True)
val_cls = ClassifyDataset(qr_val, lab_val, cic_b_val, cic_m_val, augment=False)
tr_loader = DataLoader(tr_cls, batch_size=BATCH_CLS, shuffle=True,
                       num_workers=nw, pin_memory=(device.type == 'cuda'))
va_loader = DataLoader(val_cls, batch_size=256, shuffle=False,
                       num_workers=nw, pin_memory=(device.type == 'cuda'))
print(f'{len(tr_cls):,} train, {len(val_cls):,} val')

focal = FocalLoss(alpha=0.5, gamma=2.0)
classifier.set_backbone_grad(False)
opt2 = optim.AdamW([p for p in classifier.parameters() if p.requires_grad],
                   lr=5e-4, weight_decay=1e-4)
sch2 = None
scaler2 = torch.cuda.amp.GradScaler(enabled=(USE_AMP and device.type == 'cuda'))

best_auc = 0; best_cls = None
print(f'{"Ep":>3} {"Phase":<10} {"TrLoss":>8} {"VaLoss":>8} {"AUC":>7} {"F1":>7}')
print('-' * 56)

for ep in range(1, EPOCHS2 + 1):
    if ep == FROZEN_EP + 1:
        classifier.set_backbone_grad(True)
        opt2 = optim.AdamW(classifier.parameters(), lr=1e-4, weight_decay=2e-4)
        sch2 = optim.lr_scheduler.CosineAnnealingLR(opt2, T_max=EPOCHS2 - FROZEN_EP, eta_min=1e-6)
        scaler2 = torch.cuda.amp.GradScaler(enabled=(USE_AMP and device.type == 'cuda'))
        phase = 'unfrozen'
    elif ep > FROZEN_EP:
        phase = 'unfrozen'
    else:
        phase = 'frozen'

    classifier.train()
    tl = 0; n = 0
    for imgs, lbls in tr_loader:
        imgs, lbls = imgs.to(device), lbls.to(device).unsqueeze(1)
        opt2.zero_grad()
        with torch.cuda.amp.autocast(enabled=(USE_AMP and device.type == 'cuda')):
            loss = focal(classifier(imgs), lbls)
        scaler2.scale(loss).backward()
        scaler2.step(opt2)
        scaler2.update()
        tl += loss.item() * imgs.size(0); n += imgs.size(0)

    classifier.eval()
    vl = 0; probs, true = [], []; nv = 0
    with torch.no_grad():
        for imgs, lbls in va_loader:
            imgs, lbls = imgs.to(device), lbls.to(device).unsqueeze(1)
            with torch.cuda.amp.autocast(enabled=(USE_AMP and device.type == 'cuda')):
                logits = classifier(imgs)
                vloss = focal(logits, lbls)
            vl += vloss.item() * imgs.size(0); nv += imgs.size(0)
            probs.extend(torch.sigmoid(logits).cpu().numpy().flatten())
            true.extend(lbls.cpu().numpy().flatten())

    if ep > FROZEN_EP and sch2 is not None:
        sch2.step()

    probs, true = np.array(probs), np.array(true)
    preds = (probs >= 0.5).astype(int)
    auc = roc_auc_score(true, probs)
    f1 = f1_score(true, preds)
    mk = ''
    if auc > best_auc:
        best_auc = auc; best_cls = copy.deepcopy(classifier.state_dict()); mk = ' *'
    print(f'{ep:>3} {phase:<10} {tl / n:>8.4f} {vl / nv:>8.4f} {auc:>6.4f} {f1:>6.4f}{mk}')

classifier.load_state_dict(best_cls)
out_path = os.path.join(BASE, f'classifier_v3_seed{TRAIN_SEED}_phase2.pth')
torch.save(best_cls, out_path)
print(f'\nPhase 2 best AUC: {best_auc:.4f}')
print(f'Saved: {out_path}')
print('\nNext: run eval_ensemble_tta.py')
