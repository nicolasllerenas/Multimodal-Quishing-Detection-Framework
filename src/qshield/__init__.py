"""Q-Shield multimodal quishing detection framework.

Two branches operating on the same QR sample:
  - visual:   MobileNetV2 backbone over the QR image (Siamese pretraining + focal head)
  - text:     transformer encoder over the offline-decoded URL string

A late-fusion module combines both. Modules are organized by concern
(data / models / training / eval / xai). Notebooks are thin orchestrators.
"""

__version__ = "0.2.0"
