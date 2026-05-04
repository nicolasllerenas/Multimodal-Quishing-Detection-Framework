"""Fine-tune the URL text branch on the decoded URLs of the multimodal split.

We treat decoding failures as their own token (UNDECODABLE). The model is
small enough to fit on T4 with batch 64; a couple of epochs over 80k URLs
finishes in <10 min.
"""

import copy

import numpy as np
import torch
import torch.optim as optim
from sklearn.metrics import f1_score, roc_auc_score


def _eval_text(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    n = 0
    probs, true = [], []
    with torch.no_grad():
        for _, ids, mask, labels in loader:
            ids = ids.to(device)
            mask = mask.to(device)
            labels = labels.to(device).unsqueeze(1)
            logits = model(ids, mask)
            loss = criterion(logits, labels)
            total_loss += loss.item() * ids.size(0)
            n += ids.size(0)
            probs.extend(torch.sigmoid(logits).cpu().numpy().flatten())
            true.extend(labels.cpu().numpy().flatten())
    probs = np.array(probs)
    true = np.array(true)
    auc = roc_auc_score(true, probs)
    f1 = f1_score(true, (probs >= 0.5).astype(int))
    return total_loss / n, auc, f1


def train(model, train_loader, val_loader, criterion,
          epochs=3, lr=2e-5, weight_decay=1e-2,
          warmup_ratio=0.1, device=None, log=print):
    """Standard transformer fine-tune: AdamW + linear warmup + linear decay.

    `train_loader` and `val_loader` must yield tuples produced by
    qshield.models.text.collate_multimodal: (images, ids, mask, labels).
    The image tensor is ignored here; it is included in the batch so a single
    DataLoader can serve both branches without re-iterating the dataset.
    """
    device = device or next(model.parameters()).device

    no_decay = ["bias", "LayerNorm.weight"]
    grouped = [
        {"params": [p for n, p in model.named_parameters()
                    if not any(nd in n for nd in no_decay)],
         "weight_decay": weight_decay},
        {"params": [p for n, p in model.named_parameters()
                    if any(nd in n for nd in no_decay)],
         "weight_decay": 0.0},
    ]
    optimizer = optim.AdamW(grouped, lr=lr)

    steps_per_epoch = max(len(train_loader), 1)
    total_steps = steps_per_epoch * epochs
    warmup_steps = max(int(total_steps * warmup_ratio), 1)

    def lr_lambda(step):
        if step < warmup_steps:
            return step / max(1, warmup_steps)
        return max(0.0, (total_steps - step) / max(1, total_steps - warmup_steps))

    scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    best_auc = 0.0
    best_state = None
    history = []
    log(f'{"Ep":>3} {"TrLoss":>8} {"VaLoss":>8} {"AUC":>7} {"F1":>7}')
    log("-" * 44)
    for ep in range(1, epochs + 1):
        model.train()
        running = 0.0
        seen = 0
        for _, ids, mask, labels in train_loader:
            ids = ids.to(device)
            mask = mask.to(device)
            labels = labels.to(device).unsqueeze(1)
            optimizer.zero_grad()
            logits = model(ids, mask)
            loss = criterion(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            running += loss.item() * ids.size(0)
            seen += ids.size(0)

        val_loss, auc, f1 = _eval_text(model, val_loader, criterion, device)
        marker = ""
        if auc > best_auc:
            best_auc = auc
            best_state = copy.deepcopy(model.state_dict())
            marker = " *"
        log(f"{ep:>3} {running / seen:>8.4f} {val_loss:>8.4f} {auc:>6.4f} {f1:>6.4f}{marker}")
        history.append({"epoch": ep, "train_loss": running / seen,
                        "val_loss": val_loss, "auc": auc, "f1": f1})

    if best_state is not None:
        model.load_state_dict(best_state)
    return model, {"best_auc": best_auc, "history": history}
