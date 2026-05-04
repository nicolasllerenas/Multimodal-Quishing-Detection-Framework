"""Pair samplers for Phase-1 contrastive training.

Each __getitem__ flips a fair coin to decide same-class vs different-class,
then samples two indices accordingly. This is simpler than precomputing pair
indices and avoids ordering biases.
"""

import random

import numpy as np
import torch
import torchvision.transforms as T
from torch.utils.data import Dataset

from .transforms import array_to_tensor, png_to_tensor


_FLIP = T.RandomHorizontalFlip(p=0.5)


def _maybe_aug(t, augment):
    return _FLIP(t) if augment else t


class TradPairDataset(Dataset):
    def __init__(self, qr, labels, n_pairs, augment=False):
        self.qr = qr.astype(np.float32)
        self.labels = np.asarray(labels)
        self.n = n_pairs
        self.augment = augment
        self.idx = {0: np.where(self.labels == 0)[0],
                    1: np.where(self.labels == 1)[0]}

    def __len__(self):
        return self.n

    def _tensor(self, i):
        return _maybe_aug(array_to_tensor(self.qr[i]), self.augment)

    def __getitem__(self, _):
        same = random.random() < 0.5
        c = random.choice([0, 1])
        i1 = random.choice(self.idx[c])
        c2 = c if same else 1 - c
        i2 = random.choice(self.idx[c2])
        return self._tensor(i1), self._tensor(i2), torch.tensor(0.0 if same else 1.0)


class CICPairDataset(Dataset):
    def __init__(self, benign, malicious, n_pairs, augment=False):
        self.files = {0: benign, 1: malicious}
        self.n = n_pairs
        self.augment = augment

    def __len__(self):
        return self.n

    def _load(self, cls, idx):
        return _maybe_aug(png_to_tensor(self.files[cls][idx]), self.augment)

    def __getitem__(self, _):
        same = random.random() < 0.5
        c = random.choice([0, 1])
        i1 = random.randint(0, len(self.files[c]) - 1)
        c2 = c if same else 1 - c
        i2 = random.randint(0, len(self.files[c2]) - 1)
        return self._load(c, i1), self._load(c2, i2), torch.tensor(0.0 if same else 1.0)
