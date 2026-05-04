"""Visual branch: MobileNetV2 with a 128-d L2-normalized projection head,
wrapped as a Siamese network for contrastive pretraining and as a binary
classifier for Phase 2.

Architecture is fixed: changing the dropouts or projection sizes here will
break the seed-42 / seed-7 checkpoints already saved on Drive. Don't.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models


class MobileNetV2Embedding(nn.Module):
    def __init__(self, embedding_dim=128, pretrained=True, dropout=0.35):
        super().__init__()
        weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
        mn = models.mobilenet_v2(weights=weights)
        original_conv = mn.features[0][0]
        self.features = mn.features
        self.features[0][0] = nn.Conv2d(1, 32, 3, stride=2, padding=1, bias=False)
        if pretrained:
            with torch.no_grad():
                # collapse RGB pretraining weights to grayscale by channel-mean
                self.features[0][0].weight = nn.Parameter(
                    original_conv.weight.mean(dim=1, keepdim=True)
                )
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.projection = nn.Sequential(
            nn.Linear(1280, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, embedding_dim),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x).flatten(1)
        x = self.projection(x)
        return F.normalize(x, p=2, dim=1)


class SiameseQRNet(nn.Module):
    def __init__(self, embedding_dim=128, pretrained=True, dropout=0.35):
        super().__init__()
        self.backbone = MobileNetV2Embedding(embedding_dim, pretrained, dropout)

    def forward_one(self, x):
        return self.backbone(x)

    def forward(self, x1, x2):
        return self.backbone(x1), self.backbone(x2)


class QRClassifier(nn.Module):
    """Phase-2 head on top of a (pretrained) Siamese backbone.

    Construct either by passing a SiameseQRNet (training) or with no backbone
    and load the full state_dict from disk (eval).
    """

    def __init__(self, siamese_model=None, embedding_dim=128, dropout=0.35):
        super().__init__()
        if siamese_model is None:
            self.backbone = MobileNetV2Embedding(embedding_dim, pretrained=False,
                                                 dropout=dropout)
        else:
            self.backbone = siamese_model.backbone
        self.head = nn.Sequential(
            nn.Linear(embedding_dim, 512), nn.BatchNorm1d(512),
            nn.ReLU(inplace=True), nn.Dropout(0.4),
            nn.Linear(512, 128), nn.BatchNorm1d(128),
            nn.ReLU(inplace=True), nn.Dropout(0.3),
            nn.Linear(128, 32), nn.ReLU(inplace=True), nn.Dropout(0.2),
            nn.Linear(32, 1),
        )

    def set_backbone_grad(self, requires_grad):
        for p in self.backbone.parameters():
            p.requires_grad = requires_grad

    def embed(self, x):
        return self.backbone(x)

    def forward(self, x):
        return self.head(self.backbone(x))


def load_classifier(path, device, embedding_dim=128):
    """Convenience loader for a saved Phase-2 checkpoint."""
    model = QRClassifier(None, embedding_dim).to(device)
    state = torch.load(path, map_location=device)
    model.load_state_dict(state)
    model.eval()
    return model
