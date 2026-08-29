import time
from pathlib import Path

from .base import ModelLoader, Prediction, PredictionResult

# PyTorch imports deferred to load() so the adapter can be imported without GPU/torch present
# PyTorch CPU inference does NOT release the GIL. Inference is serialized across threads.
# For the CPS showcase (3 models), sequential execution is acceptable and honest.


class ModernBERTAdapter(ModelLoader):
    """Loads a fine-tuned ModernBERT sequence-classification checkpoint.

    NOTE: PyTorch CPU inference holds the GIL. Multiple ModernBERT adapters
    in ThreadPoolExecutor run sequentially, not in parallel. Latency reported
    is wall-clock per model, not concurrent. This is expected behavior.
    """

    def __init__(self, head: str) -> None:
        """
        head: which taxonomy head this model predicts ('product_family', 'technology',
              'brand', 'toolname'). Determines which result field to populate.
        """
        self._head = head
        self._model = None
        self._tokenizer = None
        self._id2label: dict[int, str] = {}

    def load(self, model_path: str) -> None:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        p = str(Path(model_path))
        self._tokenizer = AutoTokenizer.from_pretrained(p, local_files_only=True)
        self._model = AutoModelForSequenceClassification.from_pretrained(p, local_files_only=True)
        self._model.eval()
        self._id2label = {int(k): v for k, v in self._model.config.id2label.items()}
        self._torch = torch

    def predict(self, part_number: str, description: str) -> PredictionResult:
        text = f"{part_number} {description}".strip()
        t0 = time.perf_counter()

        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with self._torch.no_grad():
            logits = self._model(**inputs).logits
        probs = self._torch.softmax(logits, dim=-1)[0]
        top_k = 3
        top_idx = probs.topk(min(top_k, len(probs))).indices.tolist()
        predictions = [
            Prediction(label=self._id2label[i], score=round(float(probs[i]), 4))
            for i in top_idx
        ]

        latency_ms = int((time.perf_counter() - t0) * 1000)

        empty: list[Prediction] = []
        return PredictionResult(
            product_family=predictions if self._head == "product_family" else empty,
            technology=predictions if self._head == "technology" else empty,
            brand=predictions if self._head == "brand" else empty,
            toolname=predictions if self._head == "toolname" else empty,
            latency_ms=latency_ms,
        )
