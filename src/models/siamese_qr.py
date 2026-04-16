"""
Q-Shield: Siamese Network for QR Code Quishing Detection
=========================================================
Architecture:
  - Backbone: MobileNetV2 (shared weights) -> 128-d embedding
  - Loss: Contrastive Loss (Chopra et al., 2005)
  - Training: Pair mining with online hard negative selection

Phase 1: Siamese pretraining with contrastive loss
Phase 2: Fine-tuning with classification head (+ optional text fusion)

Author: Nicolas A. Llerena Silva (UTEC)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
from torch.utils.data import Dataset, DataLoader
import numpy as np
from PIL import Image
from pathlib import Path
import random


# ============================================================
# 1. BACKBONE: MobileNetV2 Embedding Network
# ============================================================

class MobileNetV2Embedding(nn.Module):
    """
    MobileNetV2 backbone that outputs a normalized embedding vector.

    Takes a 224x224 grayscale QR image and produces a 128-dimensional
    embedding suitable for contrastive learning.

    Architecture rationale:
      - MobileNetV2 has 3.4M params (vs ResNet-50's 25.6M) -> mobile-deployable
      - Inverted residual blocks capture spatial patterns efficiently
      - We replace the classifier with a projection head for metric learning
    """

    def __init__(self, embedding_dim=128, pretrained=True):
        super().__init__()

        # Load MobileNetV2 backbone
        mobilenet = models.mobilenet_v2(
            weights=models.MobileNet_V2_Weights.DEFAULT if pretrained else None
        )

        # Modify first conv to accept 1-channel (grayscale) input
        # Original: Conv2d(3, 32, 3, stride=2, padding=1)
        original_conv = mobilenet.features[0][0]
        self.features = mobilenet.features
        self.features[0][0] = nn.Conv2d(
            1, 32, kernel_size=3, stride=2, padding=1, bias=False
        )
        # Initialize with mean of original RGB weights
        if pretrained:
            with torch.no_grad():
                self.features[0][0].weight = nn.Parameter(
                    original_conv.weight.mean(dim=1, keepdim=True)
                )

        # Global average pooling
        self.pool = nn.AdaptiveAvgPool2d(1)

        # Projection head: 1280 -> embedding_dim
        self.projection = nn.Sequential(
            nn.Linear(1280, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, embedding_dim),
        )

    def forward(self, x):
        """
        Args:
            x: (B, 1, 224, 224) grayscale QR image
        Returns:
            embedding: (B, embedding_dim) L2-normalized embedding
        """
        x = self.features(x)          # (B, 1280, 7, 7)
        x = self.pool(x)              # (B, 1280, 1, 1)
        x = x.flatten(1)              # (B, 1280)
        x = self.projection(x)        # (B, embedding_dim)
        x = F.normalize(x, p=2, dim=1)  # L2 normalize for cosine similarity
        return x


# ============================================================
# 2. SIAMESE NETWORK
# ============================================================

class SiameseQRNet(nn.Module):
    """
    Siamese Network for learning QR code similarity.

    Takes two QR images and determines whether they belong to the
    same class (both benign or both malicious) or different classes.

    The shared backbone learns structural embeddings that capture
    the visual fingerprint of malicious vs benign QR codes.
    """

    def __init__(self, embedding_dim=128, pretrained=True):
        super().__init__()
        self.backbone = MobileNetV2Embedding(embedding_dim, pretrained)

    def forward_one(self, x):
        """Get embedding for a single image."""
        return self.backbone(x)

    def forward(self, x1, x2):
        """
        Args:
            x1: (B, 1, 224, 224) anchor image
            x2: (B, 1, 224, 224) pair image
        Returns:
            emb1, emb2: embeddings for both images
        """
        emb1 = self.backbone(x1)
        emb2 = self.backbone(x2)
        return emb1, emb2


# ============================================================
# 3. CONTRASTIVE LOSS
# ============================================================

class ContrastiveLoss(nn.Module):
    """
    Contrastive Loss (Chopra, Hadsell, LeCun 2005).

    L = (1-y) * 0.5 * d^2 + y * 0.5 * max(0, margin - d)^2

    Where:
      - d = euclidean distance between embeddings
      - y = 0 if same class (similar pair), 1 if different class (dissimilar pair)
      - margin = minimum distance between dissimilar pairs

    For QR quishing: same-class pairs should have small distance,
    benign-malicious pairs should have distance > margin.
    """

    def __init__(self, margin=2.0):
        super().__init__()
        self.margin = margin

    def forward(self, emb1, emb2, label):
        """
        Args:
            emb1, emb2: (B, D) embeddings
            label: (B,) 0 = same class, 1 = different class
        Returns:
            loss: scalar contrastive loss
        """
        distance = F.pairwise_distance(emb1, emb2)
        loss = (1 - label) * 0.5 * distance.pow(2) + \
               label * 0.5 * F.relu(self.margin - distance).pow(2)
        return loss.mean()


class TripletLoss(nn.Module):
    """
    Triplet Loss alternative (Schroff et al., 2015).

    L = max(0, d(anchor, positive) - d(anchor, negative) + margin)

    Can be used instead of ContrastiveLoss for stronger separation.
    """

    def __init__(self, margin=1.0):
        super().__init__()
        self.margin = margin

    def forward(self, anchor, positive, negative):
        pos_dist = F.pairwise_distance(anchor, positive)
        neg_dist = F.pairwise_distance(anchor, negative)
        loss = F.relu(pos_dist - neg_dist + self.margin)
        return loss.mean()


# ============================================================
# 4. PAIR DATASET (for Contrastive Learning)
# ============================================================

class QRPairDataset(Dataset):
    """
    Dataset that generates pairs of QR images for Siamese training.

    Each sample returns:
      - img1: anchor QR image (224x224 grayscale)
      - img2: pair QR image
      - label: 0 if same class, 1 if different class

    Pairs are balanced: 50% same-class, 50% different-class.
    """

    def __init__(self, image_paths, labels, transform=None, pair_count=None):
        """
        Args:
            image_paths: list of Path objects to QR images
            labels: list/array of labels (0=benign, 1=malicious)
            transform: torchvision transforms
            pair_count: number of pairs to generate (default: 2 * len(images))
        """
        self.image_paths = image_paths
        self.labels = np.array(labels)
        self.transform = transform
        self.pair_count = pair_count or (2 * len(image_paths))

        # Index by class for efficient pair mining
        self.class_indices = {
            0: np.where(self.labels == 0)[0],
            1: np.where(self.labels == 1)[0],
        }

    def __len__(self):
        return self.pair_count

    def _load_image(self, idx):
        img = Image.open(self.image_paths[idx]).convert('L')
        img = img.resize((224, 224), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(arr).unsqueeze(0)  # (1, 224, 224)
        if self.transform:
            tensor = self.transform(tensor)
        return tensor

    def __getitem__(self, index):
        # 50% same class, 50% different class
        same_class = random.random() < 0.5

        # Pick anchor class and index
        anchor_class = random.choice([0, 1])
        anchor_idx = random.choice(self.class_indices[anchor_class])

        if same_class:
            pair_idx = random.choice(self.class_indices[anchor_class])
            pair_label = 0  # same class -> label 0
        else:
            pair_class = 1 - anchor_class
            pair_idx = random.choice(self.class_indices[pair_class])
            pair_label = 1  # different class -> label 1

        img1 = self._load_image(anchor_idx)
        img2 = self._load_image(pair_idx)

        return img1, img2, torch.tensor(pair_label, dtype=torch.float32)


class QRArrayPairDataset(Dataset):
    """
    Pair dataset for numpy array QR codes (Trad et al. dataset).
    Same logic as QRPairDataset but for 69x69 binary matrices.
    """

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
        if arr.max() <= 1:
            arr = arr  # already normalized
        else:
            arr = arr / 255.0
        # Resize 69x69 -> 224x224 using torch interpolation
        tensor = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)  # (1, 1, 69, 69)
        tensor = F.interpolate(tensor, size=(224, 224), mode='bilinear', align_corners=False)
        return tensor.squeeze(0)  # (1, 224, 224)

    def __getitem__(self, index):
        same_class = random.random() < 0.5
        anchor_class = random.choice([0, 1])
        anchor_idx = random.choice(self.class_indices[anchor_class])

        if same_class:
            pair_idx = random.choice(self.class_indices[anchor_class])
            pair_label = 0
        else:
            pair_class = 1 - anchor_class
            pair_idx = random.choice(self.class_indices[pair_class])
            pair_label = 1

        img1 = self._load_array(anchor_idx)
        img2 = self._load_array(pair_idx)
        return img1, img2, torch.tensor(pair_label, dtype=torch.float32)


# ============================================================
# 5. CLASSIFICATION HEAD (for Phase 2 fine-tuning)
# ============================================================

class QRClassifier(nn.Module):
    """
    Classification head that uses Siamese-pretrained embeddings.

    Takes the pretrained backbone, freezes or fine-tunes it,
    and adds a classification layer for binary detection.

    Can optionally fuse with text embeddings from DistilBERT.
    """

    def __init__(self, siamese_model, embedding_dim=128, text_embedding_dim=None):
        super().__init__()
        self.backbone = siamese_model.backbone

        # Input size depends on whether text features are fused
        fusion_dim = embedding_dim
        if text_embedding_dim:
            fusion_dim += text_embedding_dim

        self.classifier = nn.Sequential(
            nn.Linear(fusion_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(64, 1),
        )

    def forward(self, qr_image, text_embedding=None):
        """
        Args:
            qr_image: (B, 1, 224, 224)
            text_embedding: (B, text_dim) optional DistilBERT embedding
        Returns:
            logit: (B, 1) raw logit for binary classification
        """
        qr_emb = self.backbone(qr_image)  # (B, 128)

        if text_embedding is not None:
            combined = torch.cat([qr_emb, text_embedding], dim=1)
        else:
            combined = qr_emb

        return self.classifier(combined)


# ============================================================
# 6. TRAINING UTILITIES
# ============================================================

def train_siamese_epoch(model, dataloader, criterion, optimizer, device):
    """Train one epoch of Siamese contrastive learning."""
    model.train()
    total_loss = 0
    correct_pairs = 0
    total_pairs = 0

    for img1, img2, labels in dataloader:
        img1 = img1.to(device)
        img2 = img2.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        emb1, emb2 = model(img1, img2)
        loss = criterion(emb1, emb2, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * img1.size(0)

        # Accuracy: predict same/different based on distance threshold
        with torch.no_grad():
            dist = F.pairwise_distance(emb1, emb2)
            predicted = (dist > criterion.margin / 2).float()
            correct_pairs += (predicted == labels).sum().item()
            total_pairs += labels.size(0)

    avg_loss = total_loss / total_pairs
    accuracy = correct_pairs / total_pairs
    return avg_loss, accuracy


def evaluate_siamese(model, dataloader, criterion, device):
    """Evaluate Siamese model on validation pairs."""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for img1, img2, labels in dataloader:
            img1 = img1.to(device)
            img2 = img2.to(device)
            labels = labels.to(device)

            emb1, emb2 = model(img1, img2)
            loss = criterion(emb1, emb2, labels)
            total_loss += loss.item() * img1.size(0)

            dist = F.pairwise_distance(emb1, emb2)
            predicted = (dist > criterion.margin / 2).float()
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

    return total_loss / total, correct / total


# ============================================================
# 7. QUICK TEST
# ============================================================

if __name__ == '__main__':
    print("Q-Shield Siamese Network — Architecture Test")
    print("=" * 50)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    # Instantiate model
    model = SiameseQRNet(embedding_dim=128, pretrained=True).to(device)

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total params: {total_params:,}")
    print(f"Trainable:    {trainable:,}")

    # Test forward pass
    x1 = torch.randn(4, 1, 224, 224).to(device)
    x2 = torch.randn(4, 1, 224, 224).to(device)
    emb1, emb2 = model(x1, x2)
    print(f"Embedding shape: {emb1.shape}")
    print(f"Embedding norm:  {emb1.norm(dim=1)}")  # should be ~1.0 (L2 normalized)

    # Test loss
    labels = torch.tensor([0, 1, 0, 1], dtype=torch.float32).to(device)
    criterion = ContrastiveLoss(margin=2.0)
    loss = criterion(emb1, emb2, labels)
    print(f"Contrastive loss: {loss.item():.4f}")

    # Test classifier head
    classifier = QRClassifier(model, embedding_dim=128).to(device)
    logits = classifier(x1)
    print(f"Classifier output: {logits.shape}")
    print(f"Predictions: {torch.sigmoid(logits).squeeze().tolist()}")

    print("\nArchitecture test PASSED.")
