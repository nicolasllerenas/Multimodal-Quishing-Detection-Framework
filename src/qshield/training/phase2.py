"""Phase-2 training: focal-loss classifier head on top of the Siamese backbone.

Schedule: 5 epochs frozen backbone (head only), then unfreeze and fine-tune
end-to-end. Early stop on validation AUC.
"""

import copy

import numpy as np
import torch
import torch.optim as optim
from sklearn.metrics import f1_score, roc_auc_score


def _eval(classifier, loader, criterion, device, use_amp):
    classifier.eval()
    total_loss = 0.0
    n = 0
    probs, true = [], []
    autocast_ctx = (torch.cuda.amp.autocast(enabled=True)
                    if use_amp and device.type == "cuda"
                    else _NullCtx())
    with torch.no_grad():
        for imgs, lbls in loader:
            imgs = imgs.to(device)
            lbls = lbls.to(device).unsqueeze(1)
            with autocast_ctx:
                logits = classifier(imgs)
                loss = criterion(logits, lbls)
            total_loss += loss.item() * imgs.size(0)
            n += imgs.size(0)
            probs.extend(torch.sigmoid(logits).cpu().numpy().flatten())
            true.extend(lbls.cpu().numpy().flatten())
    probs = np.array(probs)
    true = np.array(true)
    auc = roc_auc_score(true, probs)
    f1 = f1_score(true, (probs >= 0.5).astype(int))
    return total_loss / n, auc, f1


class _NullCtx:
    def __enter__(self):
        return None

    def __exit__(self, *exc):
        return False


def train(classifier, train_loader, val_loader, criterion,
          epochs=20, frozen_epochs=5,
          head_lr=5e-4, head_wd=1e-4,
          ft_lr=1e-4, ft_wd=2e-4,
          use_amp=True, device=None, log=print):
    device = device or next(classifier.parameters()).device

    classifier.set_backbone_grad(False)
    optimizer = optim.AdamW(
        [p for p in classifier.parameters() if p.requires_grad],
        lr=head_lr, weight_decay=head_wd,
    )
    scheduler = None
    scaler = torch.cuda.amp.GradScaler(enabled=(use_amp and device.type == "cuda"))

    best_auc = 0.0
    best_state = None
    history = []

    log(f'{"Ep":>3} {"Phase":<10} {"TrLoss":>8} {"VaLoss":>8} {"AUC":>7} {"F1":>7}')
    log("-" * 56)

    for ep in range(1, epochs + 1):
        if ep == frozen_epochs + 1:
            classifier.set_backbone_grad(True)
            optimizer = optim.AdamW(classifier.parameters(), lr=ft_lr, weight_decay=ft_wd)
            scheduler = optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=epochs - frozen_epochs, eta_min=1e-6,
            )
            scaler = torch.cuda.amp.GradScaler(enabled=(use_amp and device.type == "cuda"))
        phase = "frozen" if ep <= frozen_epochs else "unfrozen"

        classifier.train()
        running_loss = 0.0
        seen = 0
        autocast_ctx = (torch.cuda.amp.autocast(enabled=True)
                        if use_amp and device.type == "cuda"
                        else _NullCtx())
        for imgs, lbls in train_loader:
            imgs = imgs.to(device)
            lbls = lbls.to(device).unsqueeze(1)
            optimizer.zero_grad()
            with autocast_ctx:
                logits = classifier(imgs)
                loss = criterion(logits, lbls)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            running_loss += loss.item() * imgs.size(0)
            seen += imgs.size(0)

        if scheduler is not None:
            scheduler.step()

        val_loss, auc, f1 = _eval(classifier, val_loader, criterion, device, use_amp)
        marker = ""
        if auc > best_auc:
            best_auc = auc
            best_state = copy.deepcopy(classifier.state_dict())
            marker = " *"
        log(f"{ep:>3} {phase:<10} {running_loss / seen:>8.4f} "
            f"{val_loss:>8.4f} {auc:>6.4f} {f1:>6.4f}{marker}")
        history.append({"epoch": ep, "phase": phase,
                        "train_loss": running_loss / seen, "val_loss": val_loss,
                        "auc": auc, "f1": f1})

    if best_state is not None:
        classifier.load_state_dict(best_state)
    return classifier, {"best_auc": best_auc, "history": history}
