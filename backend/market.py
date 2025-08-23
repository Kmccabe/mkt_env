"""
Market logic module for supply and demand calculations.

This module contains pure functions for:
- Building random buyers and sellers with specified parameters or segments
- Sorting buyers into demand schedule (high to low WTP)
- Sorting sellers into supply schedule (low to high cost)
- Finding equilibrium quantity and price by matching buyers and sellers
- Calculating maximum total surplus (area between curves up to Q*)

All functions are pure (no side effects) and include type hints for clarity.
"""

import random
from typing import List, Tuple, Optional
from .models import MarketParams, Segment


def sample_from_segments(segments: List[Segment], rng: random.Random) -> List[int]:
    """Sample integer values from market segments based on their distribution parameters.
    
    Args:
        segments: List of segments with n, p_min, p_max, and distribution parameters
        rng: Random number generator instance
    
    Returns:
        List of sampled integer values from all segments combined
    """
    vals: List[int] = []
    for seg in segments:
        if seg.dist == "uniform":
            # Uniform distribution within segment bounds, converted to integers
            for _ in range(seg.n):
                # Generate random integer
                int_val = random.randint(seg.p_min, seg.p_max)
                vals.append(int_val)
        else:  # "normal" distribution
            # Calculate mean and standard deviation if not provided
            mean = seg.mean if seg.mean is not None else (seg.p_min + seg.p_max) / 2
            sd = seg.sd if seg.sd is not None else (seg.p_max - seg.p_min) / 6 or 1.0
            
            # Sample from normal distribution, clamp to segment bounds, and convert to integer
            for _ in range(seg.n):
                x = rng.gauss(mean, sd)
                x = min(max(x, seg.p_min), seg.p_max)  # Clamp to [p_min, p_max]
                int_val = round(x)
                # Ensure the value stays within bounds after rounding
                int_val = max(seg.p_min, min(seg.p_max, int_val))
                vals.append(int_val)
    return vals


def build_buyers_and_sellers(params: MarketParams) -> Tuple[List[int], List[int]]:
    """Build buyers and sellers based on parameters or segments.
    
    If segments are provided, they take precedence over simple parameters.
    Otherwise, falls back to legacy simple parameter generation.
    
    Args:
        params: Market parameters (may include segments or simple params)
    
    Returns:
        Tuple of (buyers_sorted, sellers_sorted) where both are sorted appropriately
    """
    rng = random.Random(params.seed)
    
    # Build buyers from segments if provided, otherwise from simple params
    if params.buyer_segments and len(params.buyer_segments) > 0:
        buyers = sample_from_segments(params.buyer_segments, rng)
    else:
        # Legacy simple parameter generation - generate integers
        buyers = [rng.randint(params.min_wtp, params.max_wtp) for _ in range(params.num_buyers)]
    
    # Build sellers from segments if provided, otherwise from simple params
    if params.seller_segments and len(params.seller_segments) > 0:
        sellers = sample_from_segments(params.seller_segments, rng)
    else:
        # Legacy simple parameter generation - generate integers
        sellers = [rng.randint(params.min_cost, params.max_cost) for _ in range(params.num_sellers)]
    
    # Sort buyers high to low (demand curve) and sellers low to high (supply curve)
    buyers_sorted = sorted(buyers, reverse=True)
    sellers_sorted = sorted(sellers)
    
    return buyers_sorted, sellers_sorted


def build_buyers(num_buyers: int, min_wtp: int, max_wtp: int, seed: Optional[int] = None) -> List[int]:
    """Create a list of buyers' willingness to pay (WTP) - LEGACY FUNCTION.
    
    This function is kept for backward compatibility but is deprecated.
    Use build_buyers_and_sellers() with MarketParams instead.
    
    Args:
        num_buyers: Number of buyers to create
        min_wtp: Minimum WTP value (inclusive)
        max_wtp: Maximum WTP value (inclusive)
        seed: Random seed for reproducible results (optional)
    
    Returns:
        List of buyer WTP values as integers
    """
    if seed is not None:
        random.seed(seed)
    
    return [random.randint(min_wtp, max_wtp) for _ in range(num_buyers)]


def build_sellers(num_sellers: int, min_cost: int, max_cost: int, seed: Optional[int] = None) -> List[int]:
    """Create a list of sellers' costs - LEGACY FUNCTION.
    
    This function is kept for backward compatibility but is deprecated.
    Use build_buyers_and_sellers() with MarketParams instead.
    
    Args:
        num_sellers: Number of sellers to create
        min_cost: Minimum cost value (inclusive)
        max_cost: Maximum cost value (inclusive)
        seed: Random seed for reproducible results (optional)
    
    Returns:
        List of seller cost values as integers
    """
    if seed is not None:
        random.seed(seed)
    
    return [random.randint(min_cost, max_cost) for _ in range(num_sellers)]


def sort_demand(buyers_wtp: List[int]) -> List[int]:
    """Return buyers sorted from highest WTP to lowest (demand curve).
    
    Args:
        buyers_wtp: List of buyer WTP values
    
    Returns:
        Demand schedule sorted high to low
    """
    return sorted(buyers_wtp, reverse=True)


def sort_supply(sellers_cost: List[int]) -> List[int]:
    """Return sellers sorted from lowest cost to highest (supply curve).
    
    Args:
        sellers_cost: List of seller cost values
    
    Returns:
        Supply schedule sorted low to high
    """
    return sorted(sellers_cost)


def find_equilibrium(demand: List[int], supply: List[int]) -> Tuple[int, float]:
    """Find equilibrium quantity and price by matching buyers and sellers.
    
    We walk down the demand (high to low) and up the supply (low to high),
    matching pairs while buyer WTP >= seller cost.
    
    - Equilibrium quantity (Q*) is the number of successful matches.
    - Equilibrium price (P*) is the average of the marginal matched
      buyer WTP and seller cost at Q*.
    
    If there is no trade (Q* == 0), we set price to the midpoint between the
    highest WTP and lowest cost just for reference.
    
    Args:
        demand: Demand schedule (sorted high to low)
        supply: Supply schedule (sorted low to high)
    
    Returns:
        Tuple of (equilibrium_quantity, equilibrium_price)
    """
    matches = 0
    last_matched_wtp = None
    last_matched_cost = None

    # Iterate pairwise until one list runs out
    for wtp, cost in zip(demand, supply):
        if wtp >= cost:
            matches += 1
            last_matched_wtp = wtp
            last_matched_cost = cost
        else:
            # As soon as WTP < cost, further matches won't work because
            # demand descends while supply ascends.
            break

    if matches == 0:
        # No trade possible; set a reference price between highest WTP and lowest cost
        ref_high_wtp = demand[0] if demand else 0
        ref_low_cost = supply[0] if supply else 0
        price = (ref_high_wtp + ref_low_cost) / 2 if (demand and supply) else 0.0
        return 0, price

    # Use midpoint between marginal matched WTP and cost as equilibrium price
    price = (last_matched_wtp + last_matched_cost) / 2  # type: ignore
    return matches, price


def compute_total_surplus_max(demand: List[int], supply: List[int], q_star: int) -> float:
    """Compute maximum total surplus (area between demand and supply curves up to Q*).
    
    Maximum total surplus is the discrete "area" between curves up to Q*:
    TS_max = sum_{i=0..Q*-1} (demand[i] - supply[i])
    
    This represents the total economic welfare that would be created if all
    transactions up to Q* occurred at the equilibrium price.
    
    Args:
        demand: Demand schedule (sorted high to low)
        supply: Supply schedule (sorted low to high)
        q_star: Equilibrium quantity
    
    Returns:
        Maximum total surplus as a float
    """
    if q_star == 0:
        return 0.0
    
    # Sum the differences between demand and supply prices up to Q*
    surplus = 0.0
    for i in range(q_star):
        if i < len(demand) and i < len(supply):
            surplus += demand[i] - supply[i]
    
    return surplus


def create_schedule_table(values: List[int]) -> List[dict]:
    """Create a step-function schedule table from sorted values.
    
    Args:
        values: Sorted list of values (demand or supply)
    
    Returns:
        List of dicts with "q" (quantity) and "p" (price) keys
    """
    return [{"q": i + 1, "p": value} for i, value in enumerate(values)]
