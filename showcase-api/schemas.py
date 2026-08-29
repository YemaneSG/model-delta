from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    model_ids: list[str] = Field(min_length=1, max_length=4)
    part_number: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=2000)


class PredictionItem(BaseModel):
    label: str
    score: float


class ModelResult(BaseModel):
    product_family: list[PredictionItem]
    technology: list[PredictionItem]
    brand: list[PredictionItem]
    toolname: list[PredictionItem]
    latency_ms: int


class PredictResponse(BaseModel):
    results: dict[str, ModelResult]
    selected_models: list[str]
    input: dict[str, str]


class ModelEntry(BaseModel):
    id: str
    label: str
    color: str
    metrics: dict[str, float]
    memory_mb: int
