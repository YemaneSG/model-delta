import os
from pathlib import Path

import yaml

from adapters import ModelLoader, ModernBERTAdapter, SklearnAdapter

_REGISTRY: dict[str, ModelLoader] = {}
_METADATA: list[dict] = []


def load_all() -> None:
    """Load all active models at startup. Fail fast with clear errors."""
    model_root = Path(os.environ["MODEL_ROOT"])
    app_env = os.environ.get("APP_ENV", "internal")
    config_file = "models-public.yaml" if app_env == "public" else "models.yaml"
    config_path = Path(__file__).parent / config_file

    with config_path.open() as f:
        config = yaml.safe_load(f)

    for entry in config["models"]:
        if not entry.get("active"):
            continue

        model_id = entry["id"]
        checkpoint = entry.get("checkpoint")
        if checkpoint:
            model_path = model_root / entry["path"] / checkpoint
        else:
            model_path = model_root / entry["path"]

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model '{model_id}' path not found: {model_path}\n"
                f"Check MODEL_ROOT={model_root} and models.yaml path/checkpoint fields."
            )

        adapter = _build_adapter(entry)
        adapter.load(str(model_path))
        _REGISTRY[model_id] = adapter
        _METADATA.append(entry)
        print(f"  [ok] {model_id} loaded from {model_path}")


def get(model_id: str) -> ModelLoader:
    return _REGISTRY[model_id]


def list_models() -> list[dict]:
    return _METADATA


def known_ids() -> set[str]:
    return set(_REGISTRY.keys())


def _build_adapter(entry: dict) -> ModelLoader:
    model_type = entry["type"]
    if model_type == "sklearn":
        return SklearnAdapter()
    elif model_type == "modernbert":
        return ModernBERTAdapter(head=entry["head"])
    else:
        raise ValueError(f"Unknown model type '{model_type}' for model '{entry['id']}'")
