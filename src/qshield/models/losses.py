"""Contrastive loss for the Siamese phase, focal loss for the classifier head."""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ContrastiveLoss(nn.Module):
    """Hadsell-Chopra-LeCun contrastive loss.

    label = 0 for same-class pairs (pull together), label = 1 for different-class
    pairs (push apart up to the margin).
    """

    def __init__(self, margin=1.5):
        super().__init__()
        self.margin = margin

    def forward(self, e1, e2, label):
        d = F.pairwise_distance(e1, e2)
        return ((1 - label) * 0.5 * d.pow(2)
                + label * 0.5 * F.relu(self.margin - d).pow(2)).mean()


class FocalLoss(nn.Module):
    """Binary focal loss (Lin et al., 2017). gamma=2, alpha=0.5 by default.

    Down-weights easy examples and concentrates gradient on the hard ones,
    which in our setting are the missed phishing samples.
    """

    def __init__(self, alpha=0.5, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits, targets):
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
        p = torch.sigmoid(logits)
        pt = p * targets + (1 - p) * (1 - targets)
        alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        return (alpha_t * (1 - pt).pow(self.gamma) * bce).mean()
