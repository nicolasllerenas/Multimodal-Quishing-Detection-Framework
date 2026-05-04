"""Loader for the CIC Trap4Phish 2025 QR images.

Two zips on Drive: QR_benign_430K.zip and QR_malicious_576K.zip. We sample
50k per class (stratified) using DATA_SEED=42 to keep the validation set
identical across all training runs.
"""

import glob
import os
import random
import zipfile


def _extract(zip_path, out_dir):
    if not os.path.exists(out_dir) or len(os.listdir(out_dir)) == 0:
        os.makedirs(out_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(out_dir)


def load(base_dir, work_dir, n_per_class=50000, data_seed=42,
         benign_zip="QR_benign_430K.zip", malicious_zip="QR_malicious_576K.zip"):
    """Extract zips (idempotent), list PNGs, and return (benign_files, malicious_files).

    Lists are deterministic: sorted glob, then reproducible random.sample with data_seed.
    """
    benign_dir = os.path.join(work_dir, "cic_benign")
    mal_dir = os.path.join(work_dir, "cic_malicious")
    _extract(os.path.join(base_dir, benign_zip), benign_dir)
    _extract(os.path.join(base_dir, malicious_zip), mal_dir)

    benign = sorted(glob.glob(os.path.join(benign_dir, "**", "*.png"), recursive=True))
    mal = sorted(glob.glob(os.path.join(mal_dir, "**", "*.png"), recursive=True))

    rng = random.Random(data_seed)
    benign = rng.sample(benign, min(n_per_class, len(benign)))
    mal = rng.sample(mal, min(n_per_class, len(mal)))
    return benign, mal
