"""Two-seed Q-Shield ensemble with TTA on the joint validation set.

Auto-detects which seed checkpoints exist in BASE:
    classifier_v3_phase2.pth          (seed 42 — required)
    classifier_v3_seed7_phase2.pth    (seed 7  — optional)
    classifier_v3_seed2024_phase2.pth (seed 2024 — optional)

Reports per-seed and ensemble metrics. Saves eval_ensemble_<n>seeds_tta.json.
"""

import json
import os
import sys

import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qshield.data import cic, splits, trad
from qshield.data.classify import ClassifyDataset
from qshield.eval import ensemble
from qshield.eval.metrics import pretty, report
from qshield.eval.tta import tta_probs
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

CANDIDATES = [
    ("seed42", "classifier_v3_phase2.pth"),
    ("seed7", "classifier_v3_seed7_phase2.pth"),
    ("seed2024", "classifier_v3_seed2024_phase2.pth"),
]
available = [(n, fn) for n, fn in CANDIDATES if os.path.exists(os.path.join(BASE, fn))]
assert len(available) >= 2, "Need at least 2 seeds for an ensemble."
print(f"Using {len(available)} seeds: {[n for n, _ in available]}")

per_seed = {}
all_probs = []
true = None
for name, fn in available:
    classifier = load_classifier(os.path.join(BASE, fn), device)
    p, t = tta_probs(classifier, val_loader, device)
    if true is None:
        true = t
    r = report(p, t)
    per_seed[name] = r
    all_probs.append(p)
    print(pretty(r, f"{name} TTA"))

ensemble_probs = ensemble.mean(all_probs)
ens = report(ensemble_probs, true)
print(pretty(ens, "ENSEMBLE TTA"))

trad_auc = 0.9133
delta = ens["auc"] - trad_auc
print(f"\nEnsemble vs Trad {trad_auc}: {delta:+.4f}")

out = {
    "n_seeds": len(available),
    "per_seed_tta": per_seed,
    "ensemble_tta": ens,
    "trad_sota_auc": trad_auc,
    "delta_ensemble_vs_trad": float(delta),
}
out_path = os.path.join(BASE, f"eval_ensemble_{len(available)}seeds_tta.json")
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"Saved: {out_path}")
