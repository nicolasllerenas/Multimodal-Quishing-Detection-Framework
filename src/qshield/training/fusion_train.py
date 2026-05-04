"""Train the fusion head on top of frozen visual and text branches.

Two stages:
  1. Build a cache of (visual_logit, text_logit, decode_failed_flag, label) tuples
     by running both branches once over the train and val splits.
  2. Train the small fusion MLP on the cached features. Fast (<1 minute on CPU).
"""

import copy

import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from ..data.decode import UNDECODABLE
from ..eval.metrics import report
from ..models.losses import FocalLoss


def precompute_logits(visual_model, text_model, tokenizer, dataset,
                      batch_size=128, device="cpu"):
    """Iterate `dataset` once, return tensors ready for the fusion trainer.

    dataset: an instance of MultimodalDataset (yields (image, url, label)).
    """
    visual_model.eval()
    text_model.eval()
    visual_logits, text_logits, decode_flags, labels = [], [], [], []

    loader = DataLoader(
        dataset, batch_size=batch_size, shuffle=False,
        collate_fn=_passthrough_collate, num_workers=0,
    )
    with torch.no_grad():
        for images, urls, lbls in loader:
            images = images.to(device)
            v_logits = visual_model(images).squeeze(1).cpu()
            visual_logits.append(v_logits)

            enc = tokenizer(urls)
            ids = enc["input_ids"].to(device)
            mask = enc["attention_mask"].to(device)
            t_logits = text_model(ids, mask).squeeze(1).cpu()
            text_logits.append(t_logits)

            flag = torch.tensor([1.0 if u == UNDECODABLE else 0.0 for u in urls])
            decode_flags.append(flag)
            labels.append(lbls)

    return (torch.cat(visual_logits), torch.cat(text_logits),
            torch.cat(decode_flags), torch.cat(labels))


def _passthrough_collate(batch):
    images = torch.stack([b[0] for b in batch], dim=0)
    urls = [b[1] for b in batch]
    labels = torch.stack([b[2] for b in batch], dim=0)
    return images, urls, labels


def train(fusion_model, train_features, val_features,
          epochs=20, lr=1e-3, weight_decay=1e-3,
          batch_size=512, focal_gamma=2.0, focal_alpha=0.5,
          device="cpu", log=print):
    """train_features / val_features: tuples returned by precompute_logits()."""
    fusion_model = fusion_model.to(device)

    def to_dataset(features):
        v, t, f, y = features
        return TensorDataset(v, t, f, y)

    train_loader = DataLoader(to_dataset(train_features), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(to_dataset(val_features), batch_size=batch_size, shuffle=False)

    criterion = FocalLoss(alpha=focal_alpha, gamma=focal_gamma)
    optimizer = optim.AdamW(fusion_model.parameters(), lr=lr, weight_decay=weight_decay)

    best_auc = 0.0
    best_state = None
    history = []
    log(f'{"Ep":>3} {"TrLoss":>8} {"VaLoss":>8} {"AUC":>7} {"F1":>7}')
    log("-" * 44)
    for ep in range(1, epochs + 1):
        fusion_model.train()
        running = 0.0
        seen = 0
        for v, t, f, y in train_loader:
            v, t, f, y = v.to(device), t.to(device), f.to(device), y.to(device).unsqueeze(1)
            optimizer.zero_grad()
            logits = fusion_model(v, t, f)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            running += loss.item() * v.size(0)
            seen += v.size(0)

        val_loss, val_probs, val_true = _eval(fusion_model, val_loader, criterion, device)
        r = report(val_probs, val_true)
        marker = ""
        if r["auc"] > best_auc:
            best_auc = r["auc"]
            best_state = copy.deepcopy(fusion_model.state_dict())
            marker = " *"
        log(f"{ep:>3} {running / seen:>8.4f} {val_loss:>8.4f} "
            f"{r['auc']:>6.4f} {r['f1']:>6.4f}{marker}")
        history.append({"epoch": ep, "train_loss": running / seen,
                        "val_loss": val_loss, "auc": r["auc"], "f1": r["f1"]})

    if best_state is not None:
        fusion_model.load_state_dict(best_state)
    return fusion_model, {"best_auc": best_auc, "history": history}


def _eval(model, loader, criterion, device):
    model.eval()
    total = 0.0
    n = 0
    probs, true = [], []
    with torch.no_grad():
        for v, t, f, y in loader:
            v, t, f, y = v.to(device), t.to(device), f.to(device), y.to(device).unsqueeze(1)
            logits = model(v, t, f)
            loss = criterion(logits, y)
            total += loss.item() * v.size(0)
            n += v.size(0)
            probs.extend(torch.sigmoid(logits).cpu().numpy().flatten())
            true.extend(y.cpu().numpy().flatten())
    return total / n, np.array(probs), np.array(true)
