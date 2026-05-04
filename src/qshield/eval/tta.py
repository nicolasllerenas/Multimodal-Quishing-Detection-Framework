"""Horizontal-flip TTA. Produces per-sample probabilities by averaging the
original and flipped forward passes. Used by both single-seed and ensemble eval.
"""

import numpy as np
import torch


def tta_probs(classifier, loader, device):
    """Returns (probs, true) numpy arrays, with TTA averaging."""
    classifier.eval()
    p_orig, p_flip, true = [], [], []
    with torch.no_grad():
        for batch in loader:
            imgs, lbls = batch[0], batch[1]
            imgs = imgs.to(device)
            logits_o = classifier(imgs)
            logits_f = classifier(torch.flip(imgs, dims=[-1]))
            p_orig.extend(torch.sigmoid(logits_o).cpu().numpy().flatten())
            p_flip.extend(torch.sigmoid(logits_f).cpu().numpy().flatten())
            true.extend(lbls.numpy().flatten())
    return (np.array(p_orig) + np.array(p_flip)) / 2.0, np.array(true).astype(int)


def plain_probs(classifier, loader, device):
    classifier.eval()
    probs, true = [], []
    with torch.no_grad():
        for batch in loader:
            imgs, lbls = batch[0], batch[1]
            imgs = imgs.to(device)
            probs.extend(torch.sigmoid(classifier(imgs)).cpu().numpy().flatten())
            true.extend(lbls.numpy().flatten())
    return np.array(probs), np.array(true).astype(int)
