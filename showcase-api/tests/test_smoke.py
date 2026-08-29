"""
Smoke tests — one per active model.
Verifies that each model loads and returns a non-empty top-1 PF prediction
for the canonical test input. Run before every deploy.

Requires MODEL_ROOT env var pointing to real or synthesized model artifacts.
"""
import os
import pytest

# Skip entire suite if MODEL_ROOT not set (e.g. CI without model assets)
pytestmark = pytest.mark.skipif(
    not os.getenv("MODEL_ROOT"),
    reason="MODEL_ROOT not set — model smoke tests require artifact access",
)

CANONICAL_PN = "100390315"
CANONICAL_DESC = "FLOW CROSSOVER ASSY"


@pytest.fixture(scope="session", autouse=True)
def load_registry():
    import registry
    registry.load_all()


def test_tfidf_v3_smoke():
    import registry
    result = registry.get("tfidf-v3").predict(CANONICAL_PN, CANONICAL_DESC)
    assert result.product_family, "TF-IDF v3: no PF predictions returned"
    assert result.product_family[0].score > 0
    assert result.latency_ms >= 0


def test_modernbert_pf_smoke():
    import registry
    result = registry.get("modernbert-pf-v1").predict(CANONICAL_PN, CANONICAL_DESC)
    assert result.product_family, "ModernBERT PF: no predictions returned"
    assert result.product_family[0].score > 0


def test_modernbert_tech_smoke():
    import registry
    result = registry.get("modernbert-tech-v1").predict(CANONICAL_PN, CANONICAL_DESC)
    assert result.technology, "ModernBERT TECH: no predictions returned"


def test_modernbert_brand_smoke():
    import registry
    result = registry.get("modernbert-brand-v1").predict(CANONICAL_PN, CANONICAL_DESC)
    assert result.brand, "ModernBERT BRAND: no predictions returned"
