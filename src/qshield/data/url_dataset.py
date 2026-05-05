"""Multimodal datasets.

Two flavors:
  - MultimodalDataset: yields (image, url, label). Used by precompute_logits
    where both branches need to run.
  - URLOnlyDataset: yields (zero_tensor, url, label). Used during text-branch
    fine-tuning where the image is irrelevant. Avoids ~20 minutes of wasted
    image I/O over 3 epochs of 100k samples.

Both pull the URL from a JSON cache built by data.decode.build_cache_for_dataset.
Samples whose decode failed get the UNDECODABLE sentinel.
"""

import torch
from torch.utils.data import Dataset

from .decode import UNDECODABLE
from .transforms import array_to_tensor, png_to_tensor


class MultimodalDataset(Dataset):
    def __init__(self, base_dataset, url_cache, augment=False):
        """base_dataset: a ClassifyDataset with return_index=True semantics."""
        self.base = base_dataset
        self.url_cache = url_cache
        self.augment = augment

    def __len__(self):
        return len(self.base)

    def _image(self, src, idx):
        if src == "trad":
            return array_to_tensor(self.base.trad_qr[idx])
        files = self.base.cic_b if src == "cic_b" else self.base.cic_m
        return png_to_tensor(files[idx])

    def __getitem__(self, i):
        src, idx, lbl = self.base.items[i]
        img = self._image(src, idx)
        if self.augment:
            from torchvision.transforms.functional import hflip
            if torch.rand(1).item() < 0.5:
                img = hflip(img)
        gid = self.base.global_id(src, idx)
        url = self.url_cache.get(gid, UNDECODABLE)
        return img, url, torch.tensor(float(lbl))


class URLOnlyDataset(Dataset):
    """Skips image loading. The text-training loop ignores the image slot anyway."""

    def __init__(self, base_dataset, url_cache):
        self.base = base_dataset
        self.url_cache = url_cache

    def __len__(self):
        return len(self.base)

    def __getitem__(self, i):
        src, idx, lbl = self.base.items[i]
        gid = self.base.global_id(src, idx)
        url = self.url_cache.get(gid, UNDECODABLE)
        return torch.zeros(1), url, torch.tensor(float(lbl))
