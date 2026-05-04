"""Threshold calibration: sweep operating points and locate the threshold that
satisfies a target FNR (security-critical deployments).
"""

import numpy as np

from .metrics import report


def sweep(probs, true, thresholds=None):
    if thresholds is None:
        thresholds = np.arange(0.05, 0.96, 0.025)
    return [report(probs, true, threshold=float(t)) for t in thresholds]


def find_threshold_for_fnr(probs, true, target_fnr=0.10):
    """Return the largest threshold whose FNR is <= target_fnr.

    A larger threshold means stricter benign criterion (more positives ->
    lower FNR), so we want the right-most threshold that still meets the bound.
    """
    rows = sweep(probs, true)
    eligible = [r for r in rows if r["fnr"] <= target_fnr]
    if not eligible:
        return None
    return max(eligible, key=lambda r: r["threshold"])
