from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

import registry
import inference
from schemas import PredictRequest, PredictResponse, ModelResult, PredictionItem, ModelEntry

ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "https://model-delta.fly.dev",
]

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading models...")
    registry.load_all()
    print(f"Ready — {len(registry.known_ids())} models loaded.")
    yield


app = FastAPI(title="model-delta API", lifespan=lifespan, docs_url=None, redoc_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
async def health():
    """Returns 200 only after all registry models are loaded."""
    loaded = registry.known_ids()
    return {"status": "ok", "models_loaded": len(loaded), "model_ids": sorted(loaded)}


@app.get("/models", response_model=list[ModelEntry])
async def list_models():
    return [
        ModelEntry(
            id=m["id"],
            label=m["label"],
            color=m["color"],
            metrics=m.get("metrics", {}),
            memory_mb=m.get("memory_mb", 0),
        )
        for m in registry.list_models()
    ]


@app.post("/predict", response_model=PredictResponse)
@limiter.limit("10/minute")
async def predict(request: Request, body: PredictRequest):
    invalid = [mid for mid in body.model_ids if mid not in registry.known_ids()]
    if invalid:
        raise HTTPException(status_code=422, detail={"invalid_model_ids": invalid})

    raw = await inference.run_parallel(body.model_ids, body.part_number, body.description)

    results = {
        mid: ModelResult(
            product_family=[PredictionItem(label=p.label, score=p.score) for p in r.product_family],
            technology=[PredictionItem(label=p.label, score=p.score) for p in r.technology],
            brand=[PredictionItem(label=p.label, score=p.score) for p in r.brand],
            toolname=[PredictionItem(label=p.label, score=p.score) for p in r.toolname],
            latency_ms=r.latency_ms,
        )
        for mid, r in raw.items()
    }

    return PredictResponse(
        results=results,
        selected_models=body.model_ids,
        input={"part_number": body.part_number, "description": body.description},
    )
