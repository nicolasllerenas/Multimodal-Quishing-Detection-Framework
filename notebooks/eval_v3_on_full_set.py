"""Single-seed Q-Shield baseline on the joint 21,998-sample validation set.

Loads classifier_v3_phase2.pth from BASE and reports default-threshold metrics
plus the Trad-comparison delta. Output is written to eval_v3_full_set.json.

Run as a standalone script:
    python notebooks/eval_v3_on_full_set.py
or as a Colab cell after `pip install -e .`.
"""

import json
import os
import sys

import torch
from torch.utils.data import DataLoader

# Allow `from qshield...` imports when this script is run directly from the
# notebooks folder without `pip install -e .`.
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
val_loader = DataLoader(val_ds, batch_size=512, shuffle=False,
                        num_workers=4 if is_colab() else 0, pin_memory=True)
print(f"Validation samples: {len(val_ds):,}")

ckpt_path = os.path.join(BASE, "classifier_v3_phase2.pth")
classifier = load_classifier(ckpt_path, device)
print(f"Loaded {ckpt_path}")

probs, true = plain_probs(classifier, val_loader, device)
r = report(probs, true, threshold=0.5)
trad_auc = 0.9133
delta = r["auc"] - trad_auc

print(pretty(r, "single seed, no TTA"))
print(f"Delta vs Trad {trad_auc}: {delta:+.4f} "
      f"({'above' if delta > 0 else 'below'} by {abs(delta) * 100:.2f} pp)")

out = dict(r, trad_sota_auc=trad_auc, delta_vs_trad=float(delta))
out_path = os.path.join(BASE, "eval_v3_full_set.json")
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"Saved: {out_path}")
