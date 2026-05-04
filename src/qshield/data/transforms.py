"""Image preprocessing shared across phases. Everything is single-channel
grayscale at 224x224, scaled to [0, 1]. We do not normalize with ImageNet
statistics: the input distribution is binary-ish (QR modules) so a per-channel
mean/std subtract would be misleading.
"""

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image


TARGET_SIZE = 224


def array_to_tensor(arr):
    """Trad path: 69x69 binary matrix -> [1, 224, 224] tensor in [0, 1]."""
    arr = arr.astype(np.float32)
    if arr.max() > 1:
        arr = arr / 255.0
    t = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)
    t = F.interpolate(t, size=(TARGET_SIZE, TARGET_SIZE),
                      mode="bilinear", align_corners=False)
    return t.squeeze(0)


def png_to_tensor(path):
    """CIC path: variable-resolution PNG -> [1, 224, 224] tensor in [0, 1]."""
    img = Image.open(path).convert("L").resize((TARGET_SIZE, TARGET_SIZE))
    arr = np.array(img, dtype=np.float32) / 255.0
    return torch.from_numpy(arr).unsqueeze(0)
