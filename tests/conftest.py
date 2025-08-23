# tests/conftest.py
import pytest
from backend.models import Segment, MarketParams

@pytest.fixture
def rng_seed() -> int:
    # fixed seed gives reproducibility across the whole test run
    return 12345

@pytest.fixture
def buyers_uniform_segments():
    # two segments, non-overlapping, uniform draws
    return [
        Segment(n=20, p_min=30, p_max=50, dist="uniform"),
        Segment(n=10, p_min=10, p_max=20, dist="uniform"),
    ]

@pytest.fixture
def sellers_normal_segment():
    # one normal segment; sd defaulted from span unless provided
    return [Segment(n=25, p_min=15, p_max=35, dist="normal")]

def make_params(
    *,
    seed: int | None = None,
    buyer_segments=None,
    seller_segments=None,
    num_buyers: int = 10,
    num_sellers: int = 10,
    min_wtp: int = 10,
    max_wtp: int = 40,
    min_cost: int = 5,
    max_cost: int = 35,
) -> MarketParams:
    return MarketParams(
        seed=seed,
        buyer_segments=buyer_segments,
        seller_segments=seller_segments,
        num_buyers=num_buyers,
        num_sellers=num_sellers,
        min_wtp=min_wtp,
        max_wtp=max_wtp,
        min_cost=min_cost,
        max_cost=max_cost,
    )
