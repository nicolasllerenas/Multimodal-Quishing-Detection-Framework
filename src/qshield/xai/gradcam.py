"""Grad-CAM on the last inverted residual block of MobileNetV2.

Returns a heatmap normalized to [0, 1] with the same spatial size as the
input image (224x224 by default). Use `overlay` to render it on top of the
QR for the figures.
"""

import numpy as np
import torch
import torch.nn.functional as F


class GradCAM:
    def __init__(self, classifier, target_layer=None):
        self.classifier = classifier
        self.target_layer = target_layer or classifier.backbone.features[-1]
        self._activations = None
        self._gradients = None
        self._handles = []
        self._register()

    def _register(self):
        def fwd(_, __, output):
            self._activations = output

        def bwd(_, __, grad_output):
            self._gradients = grad_output[0]

        self._handles.append(self.target_layer.register_forward_hook(fwd))
        self._handles.append(self.target_layer.register_full_backward_hook(bwd))

    def remove(self):
        for h in self._handles:
            h.remove()
        self._handles = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.remove()

    def __call__(self, x, target_class=None):
        """x: tensor [B, 1, 224, 224] on the same device as the classifier."""
        self.classifier.zero_grad()
        logits = self.classifier(x)
        # binary classification: gradient on the (sigmoid pre-image) logit
        score = logits.sum() if target_class is None else logits[:, target_class].sum()
        score.backward(retain_graph=True)
        weights = self._gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self._activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=x.shape[-2:], mode="bilinear",
                            align_corners=False)
        cam = cam.squeeze(1)  # [B, H, W]
        cam_min = cam.flatten(1).min(dim=1).values[:, None, None]
        cam_max = cam.flatten(1).max(dim=1).values[:, None, None]
        cam = (cam - cam_min) / (cam_max - cam_min + 1e-8)
        return cam.detach().cpu().numpy()


def overlay(image_2d, heatmap_2d, alpha=0.5):
    """Returns an RGB float array in [0, 1] suitable for matplotlib.imshow."""
    import matplotlib.cm as cm
    img = np.stack([image_2d] * 3, axis=-1)
    heat = cm.get_cmap("jet")(heatmap_2d)[..., :3]
    return (1 - alpha) * img + alpha * heat
