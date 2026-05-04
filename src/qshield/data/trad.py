"""Loader for the Trad et al. (2025) QR dataset.

The corpus ships as two pickles inside QuishingDataset.zip:
    qr_codes_29.pickle          -> ndarray of shape (N, 69, 69), values in {0, 1} or {0, 255}
    qr_codes_29_labels.pickle   -> ndarray of shape (N,), int labels (0=benign, 1=phishing)
"""

import os
import pickle
import zipfile

import numpy as np


def extract(base_dir, work_dir, archive="QuishingDataset.zip"):
    out = os.path.join(work_dir, "trad")
    if not os.path.exists(os.path.join(out, "qr_codes_29.pickle")):
        os.makedirs(out, exist_ok=True)
        with zipfile.ZipFile(os.path.join(base_dir, archive)) as z:
            z.extractall(out)
    return out


def load(base_dir, work_dir, archive="QuishingDataset.zip"):
    """Return (qr_arrays, labels) as numpy arrays."""
    out = extract(base_dir, work_dir, archive=archive)
    with open(os.path.join(out, "qr_codes_29.pickle"), "rb") as f:
        qr = pickle.load(f)
    with open(os.path.join(out, "qr_codes_29_labels.pickle"), "rb") as f:
        labels = pickle.load(f)
    return np.asarray(qr), np.asarray(labels)
