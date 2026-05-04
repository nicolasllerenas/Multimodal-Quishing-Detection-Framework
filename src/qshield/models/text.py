"""URL text branch: a transformer encoder fine-tuned for binary phishing
classification.

Defaults to DistilBERT (66M params, ~250MB). For tighter latency budgets
swap in `prajjwal1/bert-tiny` (4M params) by passing model_name='bert-tiny'.
The architecture below is agnostic to the exact backbone; whatever HuggingFace
returns from from_pretrained gets a single linear classifier on top of the
[CLS] pooled output.
"""

import torch
import torch.nn as nn


_ALIASES = {
    "distilbert": "distilbert-base-uncased",
    "bert-tiny": "prajjwal1/bert-tiny",
    "modernbert-tiny": "answerdotai/ModernBERT-base",  # large but optional
}

DEFAULT_MAX_LEN = 96


def resolve_model_name(name):
    return _ALIASES.get(name, name)


class URLClassifier(nn.Module):
    """Transformer encoder + 1-d head producing a phishing logit."""

    def __init__(self, model_name="distilbert", dropout=0.1):
        super().__init__()
        from transformers import AutoConfig, AutoModel

        full_name = resolve_model_name(model_name)
        config = AutoConfig.from_pretrained(full_name)
        self.encoder = AutoModel.from_pretrained(full_name)
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(config.hidden_size, 1)
        self.hidden_size = config.hidden_size

    def encode(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        # use CLS hidden state (first token) - works for BERT and DistilBERT
        if hasattr(out, "pooler_output") and out.pooler_output is not None:
            pooled = out.pooler_output
        else:
            pooled = out.last_hidden_state[:, 0]
        return pooled

    def forward(self, input_ids, attention_mask):
        pooled = self.encode(input_ids, attention_mask)
        return self.head(self.dropout(pooled))


class URLTokenizer:
    """Thin wrapper around AutoTokenizer with sane defaults for URL strings."""

    def __init__(self, model_name="distilbert", max_length=DEFAULT_MAX_LEN):
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(resolve_model_name(model_name))
        self.max_length = max_length

    def __call__(self, urls):
        if isinstance(urls, str):
            urls = [urls]
        return self.tokenizer(
            list(urls),
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )


def collate_multimodal(batch, tokenizer):
    """Collate function for MultimodalDataset.

    batch is a list of (image, url, label). Returns (images, input_ids,
    attention_mask, labels).
    """
    images = torch.stack([b[0] for b in batch], dim=0)
    urls = [b[1] for b in batch]
    labels = torch.stack([b[2] for b in batch], dim=0)
    enc = tokenizer(urls)
    return images, enc["input_ids"], enc["attention_mask"], labels


def load(path, model_name="distilbert", device="cpu"):
    model = URLClassifier(model_name=model_name)
    state = torch.load(path, map_location=device)
    model.load_state_dict(state)
    model.to(device).eval()
    return model
