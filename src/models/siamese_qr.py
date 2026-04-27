"""Siamese network for QR-image quishing detection.

Backbone: MobileNetV2 with a 128-d L2-normalized projection head.
Phase 1: contrastive pretraining on class-balanced pairs.
Phase 2: classification head (focal loss) on top of the pretrained backbone.
"""

import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import Dataset
from torchvision import models


class MobileNetV2Embedding(nn.Module):
    def __init__(self, embedding_dim=128, pretrained=True):
        super().__init__()
        mobilenet = models.mobilenet_v2(
            weights=models.MobileNet_V2_Weights.DEFAULT if pretrained else None
        )
        original_conv = mobilenet.features[0][0]
        self.features = mobilenet.features
        self.features[0][0] = nn.Conv2d(
            1, 32, kernel_size=3, stride=2, padding=1, bias=False
        )
        if pretrained:
            with torch.no_grad():
                self.features[0][0].weight = nn.Parameter(
                    original_conv.weight.mean(dim=1, keepdim=True)
                )
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.projection = nn.Sequential(
            nn.Linear(1280, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, embedding_dim),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x).flatten(1)
        x = self.projection(x)
        return F.normalize(x, p=2, dim=1)


class SiameseQRNet(nn.Module):
    def __init__(self, embedding_dim=128, pretrained=True):
        super().__init__()
        self.backbone = MobileNetV2Embedding(embedding_dim, pretrained)

    def forward_one(self, x):
        return self.backbone(x)

    def forward(self, x1, x2):
        return self.backbone(x1), self.backbone(x2)


class ContrastiveLoss(nn.Module):
    def __init__(self, margin=1.5):
        super().__init__()
        self.margin = margin

    def forward(self, emb1, emb2, label):
        distance = F.pairwise_distance(emb1, emb2)
        loss = (1 - label) * 0.5 * distance.pow(2) \
             + label * 0.5 * F.relu(self.margin - distance).pow(2)
        return loss.mean()


class FocalLoss(nn.Module):
    def __init__(self, alpha=0.5, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits, targets):
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        p = torch.sigmoid(logits)
        pt = p * targets + (1 - p) * (1 - targets)
        alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        return (alpha_t * (1 - pt).pow(self.gamma) * bce).mean()


class QRPairDataset(Dataset):
    """Pair sampler over PNG QR images. Returns (img1, img2, label)
    with label 0 for same-class pairs and 1 for different-class pairs.
    """

    def __init__(self, image_paths, labels, transform=None, pair_count=None):
        self.image_paths = image_paths
        self.labels = np.array(labels)
        self.transform = transform
        self.pair_count = pair_count or (2 * len(image_paths))
        self.class_indices = {
            0: np.where(self.labels == 0)[0],
            1: np.where(self.labels == 1)[0],
        }

    def __len__(self):
        return self.pair_count

    def _load_image(self, idx):
        img = Image.open(self.image_paths[idx]).convert('L').resize((224, 224), Image.BILINEAR)
        tensor = torch.from_numpy(np.array(img, dtype=np.float32) / 255.0).unsqueeze(0)
        if self.transform:
            tensor = self.transform(tensor)
        return tensor

    def __getitem__(self, _):
        same_class = random.random() < 0.5
        anchor_class = random.choice([0, 1])
        anchor_idx = random.choice(self.class_indices[anchor_class])
        if same_class:
            pair_idx = random.choice(self.class_indices[anchor_class])
            label = 0
        else:
            pair_idx = random.choice(self.class_indices[1 - anchor_class])
            label = 1
        return self._load_image(anchor_idx), self._load_image(pair_idx), \
               torch.tensor(float(label))


class QRArrayPairDataset(Dataset):
    """Pair sampler over numpy QR matrices (Trad et al. format), upsampled to 224x224."""

    def __init__(self, qr_arrays, labels, pair_count=None):
        self.qr_arrays = qr_arrays
        self.labels = np.array(labels)
        self.pair_count = pair_count or (2 * len(qr_arrays))
        self.class_indices = {
            0: np.where(self.labels == 0)[0],
            1: np.where(self.labels == 1)[0],
        }

    def __len__(self):
        return self.pair_count

    def _load_array(self, idx):
        arr = self.qr_arrays[idx].astype(np.float32)
        if arr.max() > 1:
            arr = arr / 255.0
        tensor = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)
        tensor = F.interpolate(tensor, size=(224, 224), mode='bilinear', align_corners=False)
        return tensor.squeeze(0)

    def __getitem__(self, _):
        same_class = random.random() < 0.5
        anchor_class = random.choice([0, 1])
        anchor_idx = random.choice(self.class_indices[anchor_class])
        if same_class:
            pair_idx = random.choice(self.class_indices[anchor_class])
            label = 0
        else:
            pair_idx = random.choice(self.class_indices[1 - anchor_class])
            label = 1
        return self._load_array(anchor_idx), self._load_array(pair_idx), \
               torch.tensor(float(label))


class QRClassifier(nn.Module):
    """Phase-2 classifier head on top of a pretrained Siamese backbone."""

    def __init__(self, siamese_model, embedding_dim=128):
        super().__init__()
        self.backbone = siamese_model.backbone
        self.head = nn.Sequential(
            nn.Linear(embedding_dim, 512), nn.BatchNorm1d(512), nn.ReLU(inplace=True), nn.Dropout(0.4),
            nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(inplace=True), nn.Dropout(0.3),
            nn.Linear(128, 32), nn.ReLU(inplace=True), nn.Dropout(0.2),
            nn.Linear(32, 1),
        )

    def set_backbone_grad(self, requires_grad):
        for p in self.backbone.parameters():
            p.requires_grad = requires_grad

    def forward(self, qr_image):
        return self.head(self.backbone(qr_image))


def train_siamese_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    for img1, img2, labels in dataloader:
        img1, img2, labels = img1.to(device), img2.to(device), labels.to(device)
        optimizer.zero_grad()
        emb1, emb2 = model(img1, img2)
        loss = criterion(emb1, emb2, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * img1.size(0)
        with torch.no_grad():
            dist = F.pairwise_distance(emb1, emb2)
            predicted = (dist > criterion.margin / 2).float()
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
    return total_loss / total, correct / total


def evaluate_siamese(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for img1, img2, labels in dataloader:
            img1, img2, labels = img1.to(device), img2.to(device), labels.to(device)
            emb1, emb2 = model(img1, img2)
            loss = criterion(emb1, emb2, labels)
            total_loss += loss.item() * img1.size(0)
            dist = F.pairwise_distance(emb1, emb2)
            predicted = (dist > criterion.margin / 2).float()
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
    return total_loss / total, correct / total


if __name__ == '__main__':
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SiameseQRNet(embedding_dim=128, pretrained=True).to(device)
    total = sum(p.numel() for p in model.parameters())
    print(f'Device: {device}')
    print(f'Total params: {total:,}')

    x1 = torch.randn(4, 1, 224, 224).to(device)
    x2 = torch.randn(4, 1, 224, 224).to(device)
    emb1, emb2 = model(x1, x2)
    print(f'Embedding shape: {tuple(emb1.shape)}')

    labels = torch.tensor([0, 1, 0, 1], dtype=torch.float32).to(device)
    loss = ContrastiveLoss(margin=1.5)(emb1, emb2, labels)
    print(f'Contrastive loss: {loss.item():.4f}')

    classifier = QRClassifier(model).to(device)
    logits = classifier(x1)
    print(f'Classifier output shape: {tuple(logits.shape)}')
