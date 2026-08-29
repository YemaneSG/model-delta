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

```bash
# Backend
cd showcase-api
pip install -r requirements.txt
MODEL_ROOT=/path/to/ml_pipeline uvicorn main:app --reload

# Frontend (Phase 2)
cd showcase-ui
ng serve
```

## Add a model

1. Add an entry to `showcase-api/models.yaml`
2. Set `active: true`
3. Redeploy — no code changes required

## Project parent

Built on top of [`asset-taxonomy-classifier`](https://github.com/YemaneSG/asset-taxonomy-classifier) (private) — the full training pipeline, data enrichment, and evaluation framework.
