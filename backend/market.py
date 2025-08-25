"""
Market logic module for supply and demand calculations.

Pure functions for:
- Building buyers/sellers from segments or simple params (integers only)
- Sorting into demand (desc) and supply (asc)
- Finding equilibrium (Q*, P*) by matching
- Computing maximum total surplus up to Q*

All functions are pure (no side effects) for easy testing and reliability.
"""

import random
import logging
from typing import List, Tuple, Dict, Any

from .models import MarketParams, Segment

logger = logging.getLogger(__name__)


# ---- validation helpers -------------------------------------------------------

def _validate_segment(seg: Segment) -> None:
    """Validate a market segment with detailed error messages."""
    if seg.n < 0:
        raise ValueError(f"Segment size must be >= 0, got {seg.n}")
    if seg.p_min > seg.p_max:
        raise ValueError(f"Invalid price range in segment: p_min ({seg.p_min}) > p_max ({seg.p_max})")
    if seg.dist not in ("uniform", "normal"):
        raise ValueError(f"Segment distribution must be 'uniform' or 'normal', got '{seg.dist}'")
    if seg.dist == "normal":
        if seg.mean is not None and not (seg.p_min <= seg.mean <= seg.p_max):
            raise ValueError(f"Normal distribution mean ({seg.mean}) must be between p_min ({seg.p_min}) and p_max ({seg.p_max})")
        if seg.sd is not None and seg.sd <= 0:
            raise ValueError(f"Normal distribution standard deviation must be > 0, got {seg.sd}")


def _clamp_int(x: float, lo: int, hi: int) -> int:
    """Round symmetrically, then clamp to inclusive bounds."""
    xi = int(round(x))
    return max(lo, min(xi, hi))


# ---- sampling functions -------------------------------------------------------

def sample_from_segments(segments: List[Segment], rng: random.Random) -> List[int]:
    """
    Sample integer values from market segments using the provided RNG.
    
    Uses 'uniform' or 'normal' distribution per segment; normal draws are 
    clamped to segment bounds and rounded to integers.
    
    Args:
        segments: List of market segments to sample from
        rng: Random number generator for deterministic results
        
    Returns:
        List of integer values sampled from all segments
        
    Raises:
        ValueError: If any segment has invalid parameters
    """
    if not segments:
        return []
    
    vals: List[int] = []
    
    for i, seg in enumerate(segments):
        try:
            _validate_segment(seg)
        except ValueError as e:
            raise ValueError(f"Invalid segment {i}: {e}")
        
        if seg.n == 0:
            continue  # Skip empty segments
            
        span = seg.p_max - seg.p_min

        if seg.dist == "uniform":
            # Uniform distribution within bounds
            for _ in range(seg.n):
                vals.append(rng.randint(seg.p_min, seg.p_max))  # inclusive
        else:  # "normal"
            # Normal distribution with clamping
            mean = seg.mean if seg.mean is not None else (seg.p_min + seg.p_max) / 2
            # Default sigma: span/6 gives ~95% within bounds, minimum 1.0
            sigma = float(seg.sd) if seg.sd is not None else max(1.0, span / 6.0)
            
            for _ in range(seg.n):
                x = rng.gauss(mean, sigma)
                vals.append(_clamp_int(x, seg.p_min, seg.p_max))
    
    logger.debug(f"Sampled {len(vals)} values from {len(segments)} segments")
    return vals


# ---- market construction -------------------------------------------------------

def build_buyers_and_sellers(params: MarketParams) -> Tuple[List[int], List[int]]:
    """
    Build buyers and sellers from either segments (preferred) or simple params (legacy).
    
    Args:
        params: Market parameters containing either segments or simple parameters
        
    Returns:
        Tuple of (buyers_sorted_desc, sellers_sorted_asc)
        
    Raises:
        ValueError: If parameters are invalid or result in empty markets
    """
    rng = random.Random(params.seed)

    # Build buyers
    if params.buyer_segments:
        buyers = sample_from_segments(params.buyer_segments, rng)
        if not buyers:
            raise ValueError("Buyer segments resulted in zero buyers")
    else:
        if params.num_buyers <= 0:
            raise ValueError(f"Number of buyers must be > 0, got {params.num_buyers}")
        buyers = [rng.randint(params.min_wtp, params.max_wtp) for _ in range(params.num_buyers)]

    # Build sellers
    if params.seller_segments:
        sellers = sample_from_segments(params.seller_segments, rng)
        if not sellers:
            raise ValueError("Seller segments resulted in zero sellers")
    else:
        if params.num_sellers <= 0:
            raise ValueError(f"Number of sellers must be > 0, got {params.num_sellers}")
        sellers = [rng.randint(params.min_cost, params.max_cost) for _ in range(params.num_sellers)]

    # Sort for demand (high to low) and supply (low to high)
    buyers_sorted = sorted(buyers, reverse=True)
    sellers_sorted = sorted(sellers)
    
    logger.debug(
        f"Built market: {len(buyers_sorted)} buyers (WTP: {min(buyers_sorted)}-{max(buyers_sorted)}), "
        f"{len(sellers_sorted)} sellers (Cost: {min(sellers_sorted)}-{max(sellers_sorted)})"
    )
    
    return buyers_sorted, sellers_sorted


# ---- legacy builders (kept for compatibility) ---------------------------------

def build_buyers(num_buyers: int, min_wtp: int, max_wtp: int, seed: int = None) -> List[int]:
    """LEGACY: Build buyers with simple parameters. Prefer build_buyers_and_sellers()."""
    if num_buyers <= 0:
        raise ValueError(f"Number of buyers must be > 0, got {num_buyers}")
    if max_wtp <= min_wtp:
        raise ValueError(f"max_wtp ({max_wtp}) must be > min_wtp ({min_wtp})")
    
    rng = random.Random(seed)
    return [rng.randint(min_wtp, max_wtp) for _ in range(num_buyers)]


def build_sellers(num_sellers: int, min_cost: int, max_cost: int, seed: int = None) -> List[int]:
    """LEGACY: Build sellers with simple parameters. Prefer build_buyers_and_sellers()."""
    if num_sellers <= 0:
        raise ValueError(f"Number of sellers must be > 0, got {num_sellers}")
    if max_cost <= min_cost:
        raise ValueError(f"max_cost ({max_cost}) must be > min_cost ({min_cost})")
    
    rng = random.Random(seed)
    return [rng.randint(min_cost, max_cost) for _ in range(num_sellers)]


# ---- sorting helpers ----------------------------------------------------------

def sort_demand(buyers_wtp: List[int]) -> List[int]:
    """Sort willingness-to-pay values from high to low (demand curve)."""
    return sorted(buyers_wtp, reverse=True)


def sort_supply(sellers_cost: List[int]) -> List[int]:
    """Sort cost values from low to high (supply curve)."""
    return sorted(sellers_cost)


# ---- equilibrium & surplus calculations ---------------------------------------

def find_equilibrium(demand: List[int], supply: List[int]) -> Tuple[int, float]:
    """
    Find market equilibrium quantity and price through buyer-seller matching.
    
    Args:
        demand: Buyer WTP values sorted high to low
        supply: Seller cost values sorted low to high
        
    Returns:
        Tuple of (equilibrium_quantity, equilibrium_price)
        
    Algorithm:
        1. Match buyers and sellers where WTP >= Cost
        2. Equilibrium quantity = number of successful matches
        3. Equilibrium price = midpoint of marginal matched pair
        4. If no matches, price = midpoint of best buyer and best seller
    """
    if not demand and not supply:
        logger.warning("Empty demand and supply curves")
        return 0, 0.0
    
    if not demand:
        logger.warning("Empty demand curve")
        return 0, float(supply[0]) if supply else 0.0
    
    if not supply:
        logger.warning("Empty supply curve")
        return 0, float(demand[0])
    
    # Early feasibility check - if highest WTP < lowest cost, no trades possible
    if demand[0] < supply[0]:
        logger.debug(f"No trades possible: highest WTP ({demand[0]}) < lowest cost ({supply[0]})")
        return 0, (demand[0] + supply[0]) / 2.0

    # Find matches where WTP >= Cost
    matches = 0
    last_wtp: int = None
    last_cost: int = None

    for wtp, cost in zip(demand, supply):
        if wtp >= cost:
            matches += 1
            last_wtp = wtp
            last_cost = cost
        else:
            break

    if matches == 0:
        # No successful matches - return midpoint of best offers
        price = (demand[0] + supply[0]) / 2.0
        logger.debug(f"No equilibrium matches found, price set to midpoint: {price}")
        return 0, price

    # Determine equilibrium price based on market structure
    n_comparable = min(len(demand), len(supply))
    
    if matches == n_comparable:
        # Full trade case - all comparable pairs matched
        price = (last_wtp + last_cost) / 2.0
        logger.debug(f"Full trade equilibrium: Q={matches}, P={price}")
        return matches, price

    # Partial trade case - price set by marginal units
    # Next unmatched buyer vs last matched seller
    next_unmatched_buyer = demand[matches] if matches < len(demand) else last_wtp
    price = (next_unmatched_buyer + last_cost) / 2.0
    
    logger.debug(f"Partial trade equilibrium: Q={matches}, P={price}")
    return matches, price


def compute_total_surplus_max(demand: List[int], supply: List[int], q_star: int) -> float:
    """
    Calculate maximum total surplus (consumer + producer surplus).
    
    Args:
        demand: Buyer WTP values sorted high to low
        supply: Seller cost values sorted low to high  
        q_star: Equilibrium quantity
        
    Returns:
        Total surplus as sum of (WTP - Cost) for all traded units
    """
    if q_star <= 0:
        return 0.0
    
    # Ensure we don't exceed available participants
    n_tradeable = min(q_star, len(demand), len(supply))
    
    if n_tradeable == 0:
        return 0.0
    
    # Sum (demand[i] - supply[i]) for each traded unit
    total_surplus = sum(demand[i] - supply[i] for i in range(n_tradeable))
    
    logger.debug(f"Total surplus calculated: {total_surplus} over {n_tradeable} units")
    return float(total_surplus)


# ---- schedule table generation ------------------------------------------------

def create_schedule_table(values: List[int]) -> List[Dict[str, int]]:
    """
    Create step schedule table from sorted values.
    
    Args:
        values: Sorted price values (demand: high->low, supply: low->high)
        
    Returns:
        List of {"q": quantity, "p": price} dictionaries
    """
    if not values:
        return []
    
    return [{"q": i + 1, "p": v} for i, v in enumerate(values)]


# ---- market analysis utilities ------------------------------------------------

def analyze_market_structure(demand: List[int], supply: List[int]) -> Dict[str, Any]:
    """
    Analyze market structure and return key statistics.
    
    Args:
        demand: Buyer WTP values sorted high to low
        supply: Seller cost values sorted low to high
        
    Returns:
        Dictionary with market analysis metrics
    """
    analysis = {
        "demand_size": len(demand),
        "supply_size": len(supply),
        "demand_range": (min(demand), max(demand)) if demand else (0, 0),
        "supply_range": (min(supply), max(supply)) if supply else (0, 0),
        "potential_trades": min(len(demand), len(supply)),
    }
    
    if demand and supply:
        # Market overlap analysis
        analysis["demand_avg"] = sum(demand) / len(demand)
        analysis["supply_avg"] = sum(supply) / len(supply)
        analysis["price_overlap"] = demand[0] >= supply[0]  # Best buyer can afford cheapest seller
        
        # Efficiency potential
        eq_q, eq_p = find_equilibrium(demand, supply)
        analysis["equilibrium_quantity"] = eq_q
        analysis["equilibrium_price"] = eq_p
        analysis["market_efficiency"] = eq_q / analysis["potential_trades"] if analysis["potential_trades"] > 0 else 0
    
    return analysis


def validate_market_inputs(demand: List[int], supply: List[int]) -> None:
    """
    Validate market inputs and raise descriptive errors if invalid.
    
    Args:
        demand: Buyer WTP values
        supply: Seller cost values
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not isinstance(demand, list):
        raise ValueError(f"Demand must be a list, got {type(demand)}")
    if not isinstance(supply, list):
        raise ValueError(f"Supply must be a list, got {type(supply)}")
    
    if not demand and not supply:
        raise ValueError("Both demand and supply are empty")
    
    # Check for non-numeric values
    for i, val in enumerate(demand):
        if not isinstance(val, (int, float)) or val < 0:
            raise ValueError(f"Invalid demand value at index {i}: {val} (must be non-negative number)")
    
    for i, val in enumerate(supply):
        if not isinstance(val, (int, float)) or val < 0:
            raise ValueError(f"Invalid supply value at index {i}: {val} (must be non-negative number)")