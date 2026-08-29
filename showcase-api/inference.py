import asyncio
from concurrent.futures import ThreadPoolExecutor

from adapters.base import PredictionResult
import registry

# PyTorch CPU inference does NOT release the GIL — models run sequentially.
# TF-IDF (sklearn) releases the GIL and benefits from threading.
# max_workers is configurable via env var for the rare case we switch to GPU workers.
import os
_POOL = ThreadPoolExecutor(max_workers=int(os.getenv("INFERENCE_WORKERS", str(os.cpu_count() or 2))))


async def run_parallel(model_ids: list[str], part_number: str, description: str) -> dict[str, PredictionResult]:
    loop = asyncio.get_running_loop()
    tasks = {
        mid: loop.run_in_executor(_POOL, registry.get(mid).predict, part_number, description)
        for mid in model_ids
    }
    results = {}
    for mid, coro in tasks.items():
        results[mid] = await coro
    return results
