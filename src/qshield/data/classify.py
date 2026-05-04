"""Single-image dataset for Phase-2 supervised classification and evaluation.

Mixes Trad arrays and CIC PNGs in a uniform interface. Labels are 0/1.
The optional `return_index` mode also yields a global ID per sample so that
the multimodal pipeline can join image samples with their decoded URL cache.
"""

import numpy as np
import torch
import torchvision.transforms as T
from torch.utils.data import Dataset

from .transforms import array_to_tensor, png_to_tensor


_FLIP = T.RandomHorizontalFlip(p=0.5)


class ClassifyDataset(Dataset):
    """items[i] = (source, idx_in_source, label).

    source is one of: 'trad', 'cic_b', 'cic_m'. idx_in_source indexes
    into the corresponding array/list. With return_index=True __getitem__
    additionally returns a stable global ID (str) usable as a cache key.
    """

    def __init__(self, trad_qr, trad_labels, cic_b, cic_m,
                 augment=False, return_index=False):
        self.items = []
        for i in range(len(trad_qr)):
            self.items.append(("trad", i, int(trad_labels[i])))
        for i in range(len(cic_b)):
            self.items.append(("cic_b", i, 0))
        for i in range(len(cic_m)):
            self.items.append(("cic_m", i, 1))
        self.trad_qr = np.asarray(trad_qr, dtype=np.float32)
        self.cic_b = cic_b
        self.cic_m = cic_m
        self.augment = augment
        self.return_index = return_index

    def __len__(self):
        return len(self.items)

    def _load_image(self, src, i):
        if src == "trad":
            return array_to_tensor(self.trad_qr[i])
        files = self.cic_b if src == "cic_b" else self.cic_m
        return png_to_tensor(files[i])

    def global_id(self, src, i):
        if src == "trad":
            return f"trad:{i}"
        if src == "cic_b":
            return f"cic_b:{self.cic_b[i]}"
        return f"cic_m:{self.cic_m[i]}"

    def __getitem__(self, idx):
        src, i, lbl = self.items[idx]
        t = self._load_image(src, i)
        if self.augment:
            t = _FLIP(t)
        out = [t, torch.tensor(float(lbl))]
        if self.return_index:
            out.append(self.global_id(src, i))
        return tuple(out)
