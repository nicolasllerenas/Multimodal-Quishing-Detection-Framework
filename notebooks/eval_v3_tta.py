"""Single-seed Q-Shield with horizontal-flip TTA on the joint validation set.

Reports three rows: original, flip-only, average. Saves eval_v3_tta.json.
"""

import json
import os
import sys

import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qshield.data import cic, splits, trad
from qshield.data.classify import ClassifyDataset
from qshield.eval.metrics import pretty, report
from qshield.eval.tta import plain_probs
from qshield.models.visual import load_classifier
from qshield.utils.paths import is_colab, mount_drive, resolve_base, resolve_work
from qshield.utils.seeds import set_all_seeds


SEED = 42
set_all_seeds(SEED)

if is_colab():
    mount_drive()
BASE = resolve_base()
WORK = resolve_work()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device} | BASE: {BASE}")

trad_qr, trad_labels = trad.load(BASE, WORK)
cic_b, cic_m = cic.load(BASE, WORK, n_per_class=50000, data_seed=SEED)
(_, _, _), (qr_val, lab_val, _) = splits.trad_split(trad_qr, trad_labels, SEED)
(_, _), (cic_b_val, cic_m_val) = splits.cic_split(cic_b, cic_m)

val_ds = ClassifyDataset(qr_val, lab_val, cic_b_val, cic_m_val)
val_loader = DataLoader(val_ds, batch_size=256, shuffle=False,
                        num_workers=2 if is_colab() else 0, pin_memory=True)
print(f"Validation samples: {len(val_ds):,}")

classifier = load_classifier(os.path.join(BASE, "classifier_v3_phase2.pth"), device)


def flipped_probs(loader):
    classifier.eval()
    probs, true = [], []
    with torch.no_grad():
        for imgs, lbls in loader:
            imgs = imgs.to(device)
            probs.extend(torch.sigmoid(
                classifier(torch.flip(imgs, dims=[-1]))).cpu().numpy().flatten())
            true.extend(lbls.numpy().flatten())
    return np.array(probs), np.array(true).astype(int)


p_orig, true = plain_probs(classifier, val_loader, device)
p_flip, _ = flipped_probs(val_loader)
p_avg = (p_orig + p_flip) / 2.0

r_orig = report(p_orig, true)
r_flip = report(p_flip, true)
r_tta = report(p_avg, true)

for r, label in [(r_orig, "no TTA"), (r_flip, "flip only"), (r_tta, "TTA avg")]:
    print(pretty(r, label))

trad_auc = 0.9133
out = {
    "no_tta": r_orig,
    "flip_only": r_flip,
    "tta_avg": r_tta,
    "tta_gain": float(r_tta["auc"] - r_orig["auc"]),
    "trad_sota_auc": trad_auc,
    "delta_no_tta_vs_trad": float(r_orig["auc"] - trad_auc),
    "delta_tta_vs_trad": float(r_tta["auc"] - trad_auc),
}
out_path = os.path.join(BASE, "eval_v3_tta.json")
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"Saved: {out_path}")
