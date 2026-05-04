"""Train the seed-7 ensemble member.

DATA_SEED is fixed at 42 so the validation split is byte-identical to the
seed-42 model already on Drive. Only TRAIN_SEED varies (weight init plus
pair-sampling stochasticity), which is what makes the two-seed ensemble
non-trivial.

Outputs (in BASE):
    siamese_v3_seed7_phase1.pth
    classifier_v3_seed7_phase2.pth
"""

import os
import sys

import torch
from torch.utils.data import ConcatDataset, DataLoader

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qshield.data import cic, splits, trad
from qshield.data.classify import ClassifyDataset
from qshield.data.pairs import CICPairDataset, TradPairDataset
from qshield.models.losses import ContrastiveLoss, FocalLoss
from qshield.models.visual import QRClassifier, SiameseQRNet
from qshield.training.phase1 import train as train_phase1
from qshield.training.phase2 import train as train_phase2
from qshield.utils.paths import is_colab, mount_drive, resolve_base, resolve_work
from qshield.utils.seeds import set_all_seeds


DATA_SEED = 42
TRAIN_SEED = 7
PAIRS_TR = 60000
PAIRS_VAL = 8000
BATCH = 64
BATCH_CLS = 128
EMB_DIM = 128

if is_colab():
    mount_drive()
BASE = resolve_base()
WORK = resolve_work()
os.makedirs(WORK, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device} | DATA_SEED={DATA_SEED} | TRAIN_SEED={TRAIN_SEED}")

# Data identical to seed-42 -- DATA_SEED governs the splits
set_all_seeds(DATA_SEED)
trad_qr, trad_labels = trad.load(BASE, WORK)
cic_b, cic_m = cic.load(BASE, WORK, n_per_class=50000, data_seed=DATA_SEED)
(qr_tr, lab_tr, _), (qr_val, lab_val, _) = splits.trad_split(trad_qr, trad_labels, DATA_SEED)
(cic_b_tr, cic_m_tr), (cic_b_val, cic_m_val) = splits.cic_split(cic_b, cic_m)
print(f"Trad: {len(qr_tr):,} train / {len(qr_val):,} val")
print(f"CIC : {len(cic_b_tr) + len(cic_m_tr):,} train / "
      f"{len(cic_b_val) + len(cic_m_val):,} val")

# Train-time stochasticity flips to TRAIN_SEED
set_all_seeds(TRAIN_SEED)

train_ds = ConcatDataset([
    TradPairDataset(qr_tr, lab_tr, PAIRS_TR, augment=True),
    CICPairDataset(cic_b_tr, cic_m_tr, PAIRS_TR, augment=True),
])
val_ds = ConcatDataset([
    TradPairDataset(qr_val, lab_val, PAIRS_VAL, augment=False),
    CICPairDataset(cic_b_val, cic_m_val, PAIRS_VAL, augment=False),
])
nw = 2 if is_colab() else 0
train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True,
                          num_workers=nw, pin_memory=(device.type == "cuda"))
val_loader = DataLoader(val_ds, batch_size=BATCH, shuffle=False,
                        num_workers=nw, pin_memory=(device.type == "cuda"))

print("\n[Phase 1] Siamese contrastive pretraining")
model = SiameseQRNet(embedding_dim=EMB_DIM, dropout=0.35).to(device)
criterion = ContrastiveLoss(margin=1.5)
model, history1 = train_phase1(model, train_loader, val_loader, criterion,
                               epochs=40, lr=2e-4, weight_decay=2e-4,
                               warm_restart_period=15, patience=8, device=device)
phase1_path = os.path.join(BASE, f"siamese_v3_seed{TRAIN_SEED}_phase1.pth")
torch.save(model.state_dict(), phase1_path)
print(f"Saved: {phase1_path}  best_val={history1['best_val_loss']:.4f}")

del train_loader, val_loader, train_ds, val_ds
import gc
gc.collect()
if device.type == "cuda":
    torch.cuda.empty_cache()

print("\n[Phase 2] Supervised classification with focal loss")
tr_cls = ClassifyDataset(qr_tr, lab_tr, cic_b_tr, cic_m_tr, augment=True)
val_cls = ClassifyDataset(qr_val, lab_val, cic_b_val, cic_m_val, augment=False)
tr_loader = DataLoader(tr_cls, batch_size=BATCH_CLS, shuffle=True,
                       num_workers=nw, pin_memory=(device.type == "cuda"))
va_loader = DataLoader(val_cls, batch_size=256, shuffle=False,
                       num_workers=nw, pin_memory=(device.type == "cuda"))
print(f"{len(tr_cls):,} train, {len(val_cls):,} val")

classifier = QRClassifier(siamese_model=model, embedding_dim=EMB_DIM).to(device)
classifier, history2 = train_phase2(
    classifier, tr_loader, va_loader, FocalLoss(alpha=0.5, gamma=2.0),
    epochs=20, frozen_epochs=5, device=device,
)
phase2_path = os.path.join(BASE, f"classifier_v3_seed{TRAIN_SEED}_phase2.pth")
torch.save(classifier.state_dict(), phase2_path)
print(f"Saved: {phase2_path}  best_auc={history2['best_auc']:.4f}")
print("\nNext: run eval_ensemble_tta.py")
