# model-delta

**From TF-IDF to SLM: measuring what fine-tuning actually gains.**

Live inference showcase. Select model versions, enter a part number and description, compare taxonomy predictions side-by-side with latency and accuracy delta.

## What it shows

| Model | PF top-1 | TECH top-1 | BRAND top-1 | TOOLNAME top-1 |
|---|---|---|---|---|
| TF-IDF v3 (baseline) | 0.788 | 0.661 | 0.529 | 0.818 |
| ModernBERT fine-tuned | 0.859 | 0.765 | 0.803 | — |
| **Delta** | **+7.1pp** | **+10.4pp** | **+27.4pp** | — |

The TOOLNAME head stays with TF-IDF — ModernBERT lost by 12.9pp there. This app shows that too.

## Stack

- **Backend**: FastAPI + PyTorch + scikit-learn
- **Frontend**: Angular v21 standalone + PrimeNG
- **Hosting**: Fly.io (public) / localhost (internal)
- **Models**: synthesized aerospace domain data (public build) / real enterprise data (internal only)

## Run locally

### Docker (Phase 3 — recommended)

```bash
# 1. Create .env from the example
cp .env.example .env
# Edit .env — set ML_PIPELINE_PATH to your local ml_pipeline directory
# Windows:  ML_PIPELINE_PATH=C:/Users/YGebremedhin/Code/asset-taxonomy-classifier/ml_pipeline
# Mac Mini: ML_PIPELINE_PATH=/Users/yemane/Code/asset-taxonomy-classifier/ml_pipeline

# 2. Build and run
docker compose up --build

# API → http://localhost:8000
# UI  → http://localhost:4200
```

The API container waits until all models are loaded before marking itself healthy; the UI container starts only after the health check passes (~60-90s on first load).

### Dev mode (no Docker)

```bash
# Backend
cd showcase-api
MODEL_ROOT=/path/to/ml_pipeline uv run uvicorn main:app --reload

# Frontend
cd showcase-ui
ng serve
```

## Add a model

1. Add an entry to `showcase-api/models.yaml`
2. Set `active: true`
3. Redeploy — no code changes required

## Project parent

Built on top of [`asset-taxonomy-classifier`](https://github.com/YemaneSG/asset-taxonomy-classifier) (private) — the full training pipeline, data enrichment, and evaluation framework.
