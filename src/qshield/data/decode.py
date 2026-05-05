"""Offline decoding of QR images.

Decoding here is **strictly local**: the QR matrix is read into a string with
pyzbar (libzbar). No network call, no payload execution. The decoded string
is then fed to the text branch. If decoding fails (low contrast, missing
quiet zone, damaged finder pattern) we emit a sentinel UNDECODABLE marker
that the text branch maps to a learned "unknown" embedding.

Decoding is the slow part of the pipeline (a few hundred microseconds per
QR with pyzbar). To keep the multimodal training loop fast we cache decodes
to a JSON file, keyed by the global ID emitted by ClassifyDataset.
"""

import json
import os

import numpy as np
from PIL import Image


UNDECODABLE = "<UNDECODABLE>"


def _ensure_pyzbar():
    try:
        from pyzbar.pyzbar import decode  # noqa: F401
        return True
    except (ImportError, OSError):
        return False


def decode_image(pil_image):
    """Single-image decoder. Returns the first detected payload or UNDECODABLE."""
    from pyzbar.pyzbar import decode
    results = decode(pil_image)
    for r in results:
        if r.type == "QRCODE":
            try:
                return r.data.decode("utf-8", errors="replace")
            except Exception:
                return UNDECODABLE
    return UNDECODABLE


def decode_array(arr):
    """Trad path: 69x69 binary matrix -> upscaled grayscale PIL -> decode.

    pyzbar is sensitive to quiet zone, polarity, and resolution. We try a
    cascade: padded + multiple upscales, both polarities. The first success
    wins; if every variant fails we return UNDECODABLE.
    """
    a = arr.astype(np.uint8)
    if a.max() <= 1:
        a = a * 255

    h, w = a.shape

    # The matrix may arrive as either black-on-white or inverted; pyzbar wants
    # black modules on white background, so we try both.
    polarities = [a]
    if a.mean() < 64:           # mostly black -> definitely needs inverting too
        polarities.append(255 - a)
    elif a.mean() > 192:        # mostly white -> rare, only one polarity needed
        pass
    else:
        polarities.append(255 - a)

    # Quiet-zone padding (modules) and upscale factors (per module).
    # Larger pad helps pyzbar lock onto finder patterns; multiple scales help
    # cover the resolution range pyzbar's heuristics expect.
    pad_choices = [8, 4]
    scale_choices = [8, 12, 4]

    for variant in polarities:
        for pad in pad_choices:
            padded = np.full((h + 2 * pad, w + 2 * pad), 255, dtype=np.uint8)
            padded[pad:pad + h, pad:pad + w] = variant
            for scale in scale_choices:
                target = (padded.shape[1] * scale, padded.shape[0] * scale)
                img = Image.fromarray(padded, mode="L").resize(target, Image.NEAREST)
                payload = decode_image(img)
                if payload != UNDECODABLE:
                    return payload
    return UNDECODABLE


def decode_path(path):
    img = Image.open(path).convert("L")
    return decode_image(img)


def load_cache(cache_path):
    if cache_path and os.path.exists(cache_path):
        with open(cache_path) as f:
            return json.load(f)
    return {}


def save_cache(cache, cache_path):
    if not cache_path:
        return
    tmp = cache_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cache, f)
    os.replace(tmp, cache_path)


def build_cache_for_dataset(dataset, cache_path=None, log_every=2000, log=print):
    """Walks a ClassifyDataset(return_index=True), decodes every sample once,
    and writes the result to cache_path. Idempotent: pre-existing entries are
    skipped, so re-running tops up missing ones.
    """
    if not _ensure_pyzbar():
        raise RuntimeError("pyzbar not available. In Colab run "
                           "`!apt-get -qq install libzbar0` and `!pip install pyzbar`.")

    cache = load_cache(cache_path)
    new = 0
    for i in range(len(dataset)):
        src, idx, _ = dataset.items[i]
        gid = dataset.global_id(src, idx)
        if gid in cache:
            continue
        if src == "trad":
            url = decode_array(dataset.trad_qr[idx])
        else:
            files = dataset.cic_b if src == "cic_b" else dataset.cic_m
            url = decode_path(files[idx])
        cache[gid] = url
        new += 1
        if new % log_every == 0:
            log(f"  decoded {new:,} new samples (cache total {len(cache):,})")
            save_cache(cache, cache_path)
    save_cache(cache, cache_path)
    return cache
