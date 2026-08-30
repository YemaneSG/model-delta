# model-delta — Project Status

_Last updated: 2026-08-30_

---

## Phase Status

| Phase | Status | Notes |
|---|---|---|
| 0 — Scaffold + BLOCKERs resolved | ✅ Done | ModelLoader ABC, MODEL_ROOT, rate limiting, /health, two Dockerfiles, CI model source |
| 1 — FastAPI backend | ✅ Done | 4 models serving at localhost:8000 — /health, /models, /predict |
| 2 — Angular frontend | ✅ Done | Live inference UI at localhost:4200 — model selector, side-by-side columns, delta badges |
| 3 — Local Docker | 🔄 Built, pending test | docker-compose, nginx UI, CPU-only PyTorch. Run `docker compose up --build` to verify. |
| 4 — Fly.io public deploy | 🔒 Blocked | Needs synthesized aerospace proxy models. No real SLB data in public image. |
| 5 — UI polish | ⏳ Queued | Premium dark mode, hierarchy paths, per-model colors, error/retry, mobile layout |

---

## Current Model Registry

Defined in `showcase-api/models.yaml`:

| Model ID | Type | Head | Top-1 | Memory |
|---|---|---|---|---|
| tfidf-v3 | sklearn | all 4 heads | PF 0.788 / TECH 0.661 / BRAND 0.529 / TOOLNAME 0.818 | 50 MB |
| modernbert-pf-v1 | modernbert | product_family | 0.859 | 620 MB |
| modernbert-tech-v1 | modernbert | technology | 0.765 | 620 MB |
| modernbert-brand-v1 | modernbert | brand | 0.803 | 620 MB |

Total RAM at inference: ~2.2 GB (safe on 4 GB Fly.io machine).

---

## How to Run

### Dev (no Docker)
```powershell
# Terminal 1 — API
cd showcase-api
$env:MODEL_ROOT="C:\Users\YGebremedhin\Code\asset-taxonomy-classifier\ml_pipeline"
uv run uvicorn main:app --reload

# Terminal 2 — UI
cd showcase-ui
ng serve
```

### Docker (Phase 3)
```bash
# 1. Set ML_PIPELINE_PATH in .env (copy from .env.example)
# 2. Build and run
docker compose up --build
# API → http://localhost:8000
# UI  → http://localhost:4200
```

---

## What Blocks Phase 4

Phase 4 (public Fly.io deploy) requires synthesized proxy models — trained on fake aerospace-domain data so no real SLB records are in the public image.

**Plan (from synthesis agent evaluation, 2026-08-30):**
- Generate 5,000 synthetic records via Claude Haiku API (~$1–2, ~20 min)
- Use real taxonomy label names from `taxonomy_tree.json` (industry-standard, not PII)
- Train TF-IDF proxy on Windows (~5 min), ModernBERT proxy on Mac Mini MPS (~2 hrs, 3 heads)
- Package as GitHub Release asset (`synthesized-models-v1`) — CI pulls via `gh release download`
- Add "DEMO — synthetic data" banner to UI before Phase 4 ships

**Total estimated time: ~3 hours (mostly waiting on Mac Mini).**

---

## Security Invariants

- Real SLB model weights — never in any public image, ever
- `Dockerfile.internal` — volume mount only, never pushed to public registry
- `Dockerfile.public` — build fails if `MODEL_SET != "public"` or path contains enterprise keywords
- `.env` — gitignored, contains only `ML_PIPELINE_PATH`
- CORS — only `localhost:4200` and `https://model-delta.fly.dev` allowed
- Rate limit — 10 req/min per IP on `/predict`
