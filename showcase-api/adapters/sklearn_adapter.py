import time
import joblib
from pathlib import Path

from .base import ModelLoader, Prediction, PredictionResult


class SklearnAdapter(ModelLoader):
    """Loads TF-IDF + LogisticRegression joblib pipelines.
    Sklearn releases the GIL during predict() — safe for ThreadPoolExecutor.
    """

    def __init__(self) -> None:
        self._clf_pf = None
        self._clf_tech = None
        self._clf_brand = None
        self._clf_toolname = None

    def load(self, model_path: str) -> None:
        p = Path(model_path)
        self._clf_pf = joblib.load(p / "clf_pf.joblib")
        self._clf_tech = joblib.load(p / "clf_tech.joblib")
        self._clf_brand = joblib.load(p / "clf_brand.joblib")
        self._clf_toolname = joblib.load(p / "clf_toolname.joblib")

    def predict(self, part_number: str, description: str) -> PredictionResult:
        text = f"{part_number} {description}".strip()
        t0 = time.perf_counter()

        pf = self._top_k(self._clf_pf, text, k=3)
        tech = self._top_k(self._clf_tech, text, k=3)
        brand = self._top_k(self._clf_brand, text, k=3)
        toolname = self._top_k(self._clf_toolname, text, k=3)

        latency_ms = int((time.perf_counter() - t0) * 1000)
        return PredictionResult(
            product_family=pf,
            technology=tech,
            brand=brand,
            toolname=toolname,
            latency_ms=latency_ms,
        )

    @staticmethod
    def _top_k(clf, text: str, k: int) -> list[Prediction]:
        proba = clf.predict_proba([text])[0]
        top_idx = proba.argsort()[::-1][:k]
        return [Prediction(label=clf.classes_[i], score=round(float(proba[i]), 4)) for i in top_idx]
