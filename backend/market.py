"""
Market logic module for supply and demand calculations.

Pure functions for:
- Building buyers/sellers from segments or simple params (integers only)
- Sorting into demand (desc) and supply (asc)
- Finding equilibrium (Q*, P*) by matching
- Computing maximum total surplus up to Q*
"""

import random
from .models import MarketParams, Segment  # Segment: n, p_min, p_max, dist ('uniform'|'normal'), mean, sd


# ---- helpers -----------------------------------------------------------------

def _validate_segment(seg: Segment) -> None:
    if seg.n < 0:
        raise ValueError("Segment.n must be >= 0")
    if seg.p_min > seg.p_max:
        raise ValueError("Segment p_min must be <= p_max")
    if seg.dist not in ("uniform", "normal"):
        raise ValueError("Segment.dist must be 'uniform' or 'normal'")


def _clamp_int(x: float, lo: int, hi: int) -> int:
    """Round symmetrically, then clamp to inclusive bounds."""
    xi = int(round(x))
    if xi < lo:
        return lo
    if xi > hi:
        return hi
    return xi


# ---- sampling ----------------------------------------------------------------

def sample_from_segments(segments: list[Segment], rng: random.Random) -> list[int]:
    """
    Sample integer values from market segments using the provided RNG.
    Uses 'uniform' or 'normal' per segment; normal draws are clamped and rounded.
    """
    vals: list[int] = []
    for seg in segments:
        _validate_segment(seg)
        span = seg.p_max - seg.p_min

        if seg.dist == "uniform":
            # Deterministic: use injected RNG
            for _ in range(seg.n):
                vals.append(rng.randint(seg.p_min, seg.p_max))  # inclusive
        else:  # "normal"
            mean = seg.mean if seg.mean is not None else (seg.p_min + seg.p_max) / 2
            # If sd is given, use it; else fall back to span/6 (≈95% within bounds), min 1.0
            sigma = float(seg.sd) if seg.sd is not None else max(1.0, span / 6.0)
            for _ in range(seg.n):
                x = rng.gauss(mean, sigma)
                vals.append(_clamp_int(x, seg.p_min, seg.p_max))
    return vals


# ---- construction -------------------------------------------------------------

def build_buyers_and_sellers(params: MarketParams) -> tuple[list[int], list[int]]:
    """
    Build buyers and sellers from either segments (preferred) or simple params (legacy).
    Returns (buyers_sorted_desc, sellers_sorted_asc).
    """
    rng = random.Random(params.seed)

    if params.buyer_segments:
        buyers = sample_from_segments(params.buyer_segments, rng)
    else:
        buyers = [rng.randint(params.min_wtp, params.max_wtp) for _ in range(params.num_buyers)]

    if params.seller_segments:
        sellers = sample_from_segments(params.seller_segments, rng)
    else:
        sellers = [rng.randint(params.min_cost, params.max_cost) for _ in range(params.num_sellers)]

    return sorted(buyers, reverse=True), sorted(sellers)


# ---- legacy builders (kept pure; no global seeding) --------------------------

def build_buyers(num_buyers: int, min_wtp: int, max_wtp: int, seed: int | None = None) -> list[int]:
    """LEGACY: Prefer build_buyers_and_sellers(). Pure: uses a local RNG."""
    rng = random.Random(seed)
    return [rng.randint(min_wtp, max_wtp) for _ in range(num_buyers)]


def build_sellers(num_sellers: int, min_cost: int, max_cost: int, seed: int | None = None) -> list[int]:
    """LEGACY: Prefer build_buyers_and_sellers(). Pure: uses a local RNG."""
    rng = random.Random(seed)
    return [rng.randint(min_cost, max_cost) for _ in range(num_sellers)]


# ---- sorting helpers ----------------------------------------------------------

def sort_demand(buyers_wtp: list[int]) -> list[int]:
    """Sort WTP high→low."""
    return sorted(buyers_wtp, reverse=True)


def sort_supply(sellers_cost: list[int]) -> list[int]:
    """Sort costs low→high."""
    return sorted(sellers_cost)


# ---- equilibrium & surplus ----------------------------------------------------

def find_equilibrium(demand: list[int], supply: list[int]) -> tuple[int, float]:
    matches = 0
    last_wtp: int | None = None
    last_cost: int | None = None

    for wtp, cost in zip(demand, supply):
        if wtp >= cost:
            matches += 1
            last_wtp = wtp
            last_cost = cost
        else:
            break

    if matches == 0:
        if demand and supply:
            return 0, (demand[0] + supply[0]) / 2.0
        if demand:
            return 0, float(demand[0])
        if supply:
            return 0, float(supply[0])
        return 0, 0.0

    # If we consumed all comparable pairs (no cutoff encountered),
    # price at the last matched pair midpoint (full-trade case).
    n = min(len(demand), len(supply))
    if matches == n:
        return matches, (last_wtp + last_cost) / 2.0  # type: ignore

    # Otherwise, price across the margin: next unmatched buyer vs last matched seller.
    next_unmatched_buyer = demand[matches] if matches < len(demand) else last_wtp  # fallback
    return matches, (next_unmatched_buyer + last_cost) / 2.0  # type: ignore


def compute_total_surplus_max(demand: list[int], supply: list[int], q_star: int) -> float:
    """Sum of (demand[i] - supply[i]) for i=0..q*-1 (discrete area between curves)."""
    if q_star <= 0:
        return 0.0
    n = min(q_star, len(demand), len(supply))
    return float(sum(demand[i] - supply[i] for i in range(n)))


# ---- tables ------------------------------------------------------------------

def create_schedule_table(values: list[int]) -> list[dict]:
    """Create step schedule as [{q, p}]. Assumes 'values' already sorted appropriately."""
    return [{"q": i + 1, "p": v} for i, v in enumerate(values)]
