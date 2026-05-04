"""Multimodal dataset: yields (image_tensor, url_string, label) tuples.

The decoded URL is read from a cache built by data.decode.build_cache_for_dataset.
Samples whose decode failed receive the UNDECODABLE sentinel; the text branch
embeds that sentinel as a normal token, so "undecodable" itself becomes a
learnable feature.
"""

import torch
from torch.utils.data import Dataset

from .decode import UNDECODABLE
from .transforms import array_to_tensor, png_to_tensor


class MultimodalDataset(Dataset):
    def __init__(self, base_dataset, url_cache, augment=False):
        """base_dataset: a ClassifyDataset with return_index=True semantics.

        We don't subclass ClassifyDataset because we need the URL cache joined
        in by global ID, but we reuse its `items` list and per-source loaders.
        """
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
