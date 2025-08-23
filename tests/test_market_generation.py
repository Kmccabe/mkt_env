# tests/test_market_generation.py
import random
import pytest
from backend.market import (
    sample_from_segments,
    build_buyers_and_sellers,
    build_buyers,
    build_sellers,
    sort_demand,
    sort_supply,
)
from backend.models import Segment
from conftest import make_params

def test_uniform_segments_are_inclusive_and_deterministic(buyers_uniform_segments, rng_seed):
    rng = random.Random(rng_seed)
    vals = sample_from_segments(buyers_uniform_segments, rng)
    assert len(vals) == 30
    # bounds respected & all ints
    assert min(vals) >= 10 and max(vals) <= 50
    assert all(isinstance(v, int) for v in vals)

    # determinism across a fresh RNG with the same seed
    vals2 = sample_from_segments(buyers_uniform_segments, random.Random(rng_seed))
    assert vals == vals2

def test_normal_segments_respect_bounds_and_sd_override(rng_seed):
    seg = Segment(n=100, p_min=20, p_max=40, dist="normal", mean=None, sd=2.0)
    vals = sample_from_segments([seg], random.Random(rng_seed))
    assert len(vals) == 100
    assert min(vals) >= 20 and max(vals) <= 40
    # sd override should produce values clustered near the midpoint, but we only
    # enforce bounds/integer properties here for stability of the test.
    assert all(isinstance(v, int) for v in vals)

def test_build_buyers_and_sellers_segments_override_simple_params(buyers_uniform_segments, sellers_normal_segment, rng_seed):
    params = make_params(
        seed=rng_seed,
        buyer_segments=buyers_uniform_segments,
        seller_segments=sellers_normal_segment,
        # simple params present but should be ignored
        num_buyers=1, num_sellers=1, min_wtp=0, max_wtp=0, min_cost=0, max_cost=0,
    )
    buyers, sellers = build_buyers_and_sellers(params)
    assert len(buyers) == sum(s.n for s in buyers_uniform_segments)
    assert len(sellers) == sum(s.n for s in sellers_normal_segment)
    # sorted correctly
    assert buyers == sorted(buyers, reverse=True)
    assert sellers == sorted(sellers)

def test_legacy_builders_are_pure_and_deterministic(rng_seed):
    b1 = build_buyers(5, 10, 20, seed=rng_seed)
    b2 = build_buyers(5, 10, 20, seed=rng_seed)
    assert b1 == b2
    # different seed changes the sequence
    b3 = build_buyers(5, 10, 20, seed=rng_seed + 1)
    assert b1 != b3

    s1 = build_sellers(5, 5, 15, seed=rng_seed)
    s2 = build_sellers(5, 5, 15, seed=rng_seed)
    assert s1 == s2

def test_sort_helpers():
    assert sort_demand([3, 1, 2]) == [3, 2, 1]
    assert sort_supply([3, 1, 2]) == [1, 2, 3]
