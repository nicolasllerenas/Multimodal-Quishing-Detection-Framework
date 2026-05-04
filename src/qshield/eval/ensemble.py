"""Ensemble averaging of probability arrays from multiple models.

We average sigmoid outputs (post-calibration) rather than logits because the
focal-loss classifier produces logits with non-uniform scale across seeds.
"""

import numpy as np


def mean(probs_list, weights=None):
    if weights is None:
        return np.mean(np.stack(probs_list, axis=0), axis=0)
    weights = np.asarray(weights, dtype=np.float64)
    weights = weights / weights.sum()
    stacked = np.stack(probs_list, axis=0)
    return (stacked * weights[:, None]).sum(axis=0)
