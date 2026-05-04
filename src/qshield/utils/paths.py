"""Resolves the project base path. Works on Colab (Drive) and locally."""

import os
import sys


def is_colab():
    return "google.colab" in sys.modules


def mount_drive():
    if is_colab():
        from google.colab import drive
        drive.mount("/content/drive")


DEFAULT_BASE = "/content/drive/MyDrive/Proyecto_Quishing_Detection_Nicolas"
DEFAULT_WORK = "/content/qshield_work"


def resolve_base(base=None):
    """Return the project base directory (where checkpoints/zips/cache live).

    Search order:
      1. explicit `base` argument
      2. QSHIELD_BASE environment variable
      3. DEFAULT_BASE on Drive
    """
    if base is not None:
        return base
    env = os.environ.get("QSHIELD_BASE")
    if env:
        return env
    return DEFAULT_BASE


def resolve_work(work=None):
    if work is not None:
        return work
    env = os.environ.get("QSHIELD_WORK")
    if env:
        return env
    return DEFAULT_WORK
