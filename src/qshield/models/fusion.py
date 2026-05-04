"""Late fusion of the visual and text branches.

Two fusion strategies, both implemented:

  LogitFusion        — learns a 2-input MLP over [logit_visual, logit_text]
                       (4 trainable params for the simple linear case, 161
                       for the 2->16->1 MLP). Tiny, regularizes well, and
                       bypasses the heavy backbones at inference because we
                       only need the precomputed logits.

  EmbeddingFusion    — concatenates the 128-d visual embedding and the text
                       encoder pooled output (768 for DistilBERT) and runs
                       them through a 2-layer MLP. More expressive but costs
                       a forward pass through both backbones at inference.

Default for the paper: LogitFusion. EmbeddingFusion is provided as an
ablation row.
"""

import torch
import torch.nn as nn


class LogitFusion(nn.Module):
    """MLP over [visual_logit, text_logit, decode_failed_flag]."""

    def __init__(self, hidden=16, use_decode_flag=True):
        super().__init__()
        self.use_decode_flag = use_decode_flag
        in_dim = 3 if use_decode_flag else 2
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(inplace=True),
            nn.Linear(hidden, 1),
        )

    def forward(self, visual_logit, text_logit, decode_failed=None):
        feats = [visual_logit, text_logit]
        if self.use_decode_flag:
            if decode_failed is None:
                decode_failed = torch.zeros_like(visual_logit)
            feats.append(decode_failed)
        x = torch.cat([f.view(-1, 1) for f in feats], dim=1)
        return self.mlp(x)


class EmbeddingFusion(nn.Module):
    """Concatenates [visual_embedding (128), text_pooled (H), decode_flag (1)]
    and runs a 2-layer MLP.
    """

    def __init__(self, visual_dim=128, text_dim=768, hidden=128,
                 use_decode_flag=True, dropout=0.3):
        super().__init__()
        self.use_decode_flag = use_decode_flag
        in_dim = visual_dim + text_dim + (1 if use_decode_flag else 0)
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1),
        )

    def forward(self, visual_emb, text_pooled, decode_failed=None):
        parts = [visual_emb, text_pooled]
        if self.use_decode_flag:
            if decode_failed is None:
                decode_failed = torch.zeros(visual_emb.size(0), 1,
                                            device=visual_emb.device)
            parts.append(decode_failed)
        return self.mlp(torch.cat(parts, dim=1))


def weighted_average(visual_probs, text_probs, alpha=0.5):
    """Tunable convex combination — useful as a no-train baseline."""
    return alpha * visual_probs + (1 - alpha) * text_probs
