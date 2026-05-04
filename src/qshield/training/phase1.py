"""Phase-1 training loop: Siamese contrastive pretraining of the visual backbone.

Public entry point: `train(model, train_loader, val_loader, ...)`. Returns the
trained model (loaded with its best checkpoint) plus a history dict.
"""

import copy
import time

import torch
import torch.nn.functional as F
import torch.optim as optim


def _step_one(model, loader, criterion, optimizer, scaler, device, train, use_amp):
    if train:
        model.train()
    else:
        model.eval()

    total_loss = 0.0
    correct = 0
    total = 0
    margin = criterion.margin
    autocast = torch.cuda.amp.autocast if use_amp and device.type == "cuda" else _noop_autocast

    with torch.set_grad_enabled(train):
        for x1, x2, y in loader:
            x1, x2, y = x1.to(device), x2.to(device), y.to(device)
            if train:
                optimizer.zero_grad()
            with autocast(enabled=(use_amp and device.type == "cuda")):
                e1, e2 = model(x1, x2)
                loss = criterion(e1, e2, y)
            if train:
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()

            total_loss += loss.item() * x1.size(0)
            with torch.no_grad():
                d = F.pairwise_distance(e1.float(), e2.float())
                pred = (d > margin / 2).float()
                correct += (pred == y).sum().item()
                total += y.size(0)

    return total_loss / total, correct / total


class _noop_autocast:
    def __init__(self, enabled=True):
        self.enabled = enabled

    def __enter__(self):
        return None

    def __exit__(self, *exc):
        return False


def train(model, train_loader, val_loader, criterion,
          epochs=40, lr=2e-4, weight_decay=2e-4,
          warm_restart_period=15, patience=8, use_amp=True,
          device=None, log=print):
    device = device or next(model.parameters()).device
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=warm_restart_period, T_mult=1, eta_min=1e-6
    )
    scaler = torch.cuda.amp.GradScaler(enabled=(use_amp and device.type == "cuda"))

    best_val = float("inf")
    best_state = None
    bad_epochs = 0
    history = []

    log(f'{"Ep":>3} {"TrLoss":>8} {"VaLoss":>8} {"TrAcc":>7} {"VaAcc":>7} {"LR":>10} {"Time":>6}')
    log("-" * 60)

    for ep in range(1, epochs + 1):
        t0 = time.time()
        tl, ta = _step_one(model, train_loader, criterion, optimizer, scaler,
                           device, train=True, use_amp=use_amp)
        vl, va = _step_one(model, val_loader, criterion, optimizer, scaler,
                           device, train=False, use_amp=use_amp)
        scheduler.step()
        marker = ""
        if vl < best_val:
            best_val = vl
            best_state = copy.deepcopy(model.state_dict())
            bad_epochs = 0
            marker = " *"
        else:
            bad_epochs += 1

        lr_now = optimizer.param_groups[0]["lr"]
        log(f"{ep:>3} {tl:>8.4f} {vl:>8.4f} {ta:>6.1%} {va:>6.1%} "
            f"{lr_now:>10.6f} {time.time() - t0:>5.0f}s{marker}")
        history.append({"epoch": ep, "train_loss": tl, "val_loss": vl,
                        "train_acc": ta, "val_acc": va, "lr": lr_now})
        if bad_epochs >= patience:
            log(f"Early stop at epoch {ep}")
            break

    if best_state is not None:
        model.load_state_dict(best_state)
    return model, {"best_val_loss": best_val, "history": history}
