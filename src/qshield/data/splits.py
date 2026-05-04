"""Canonical 80/20 train/validation split shared by every Q-Shield experiment.

Trad split is stratified on label; CIC split is a contiguous slice of the
DATA_SEED-shuffled file list (i.e. first 80% train, last 20% val). Both
splits are pinned to DATA_SEED=42 so that every checkpoint's validation
set is byte-identical, which is what makes seed-ensembling honest.
"""

import numpy as np
from sklearn.model_selection import train_test_split


def trad_split(qr, labels, data_seed=42, val_size=0.2):
    idx_tr, idx_val = train_test_split(
        np.arange(len(labels)),
        test_size=val_size,
        stratify=labels,
        random_state=data_seed,
    )
    return (qr[idx_tr], labels[idx_tr], idx_tr), (qr[idx_val], labels[idx_val], idx_val)


def cic_split(benign_files, malicious_files, val_size=0.2):
    sb = int(len(benign_files) * (1 - val_size))
    sm = int(len(malicious_files) * (1 - val_size))
    return (benign_files[:sb], malicious_files[:sm]), (benign_files[sb:], malicious_files[sm:])
