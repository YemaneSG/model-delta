from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Prediction:
    label: str
    score: float


@dataclass
class PredictionResult:
    product_family: list[Prediction]
    technology: list[Prediction]
    brand: list[Prediction]
    toolname: list[Prediction]
    latency_ms: int


class ModelLoader(ABC):
    """Contract every model adapter must satisfy. No shared global state."""

    @abstractmethod
    def load(self, model_path: str) -> None:
        """Load model weights from disk into memory."""

    @abstractmethod
    def predict(self, part_number: str, description: str) -> PredictionResult:
        """Run inference. Must be thread-safe — called from ThreadPoolExecutor."""
