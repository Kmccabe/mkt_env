"""
A very simple supply and demand market model in pure Python.

What this script does:
1) Creates buyers with "willingness to pay" (WTP)
2) Creates sellers with "cost"
3) Sorts buyers (high to low) to form the demand schedule
4) Sorts sellers (low to high) to form the supply schedule
5) Prints demand and supply tables: Quantity vs Price
6) Finds equilibrium quantity and price by matching buyers and sellers
   (equilibrium is largest quantity where buyer WTP >= seller cost)
7) Prints the equilibrium

No external libraries are used; everything is built-in.
"""

from typing import List, Tuple
import random as rnd

def build_buyers() -> List[float]:
    """Create a list of buyers' willingness to pay (WTP).

    You can change these values to experiment.
    Higher numbers mean a buyer is willing to pay more.
    """
    return [rnd.randint(10, 40) for _ in range(9)]


def build_sellers() -> List[float]:
    """Create a list of sellers' costs.

    You can change these values to experiment.
    Lower numbers mean a seller can supply more cheaply.
    """
    return [rnd.randint(5, 30) for _ in range(9)]


def sort_demand(buyers_wtp: List[float]) -> List[float]:
    """Return buyers sorted from highest WTP to lowest (demand curve)."""
    return sorted(buyers_wtp, reverse=True)


def sort_supply(sellers_cost: List[float]) -> List[float]:
    """Return sellers sorted from lowest cost to highest (supply curve)."""
    return sorted(sellers_cost)


def print_schedule(title: str, prices: List[float]) -> None:
    """Print a schedule as a simple two-column table: Quantity and Price.

    Quantity counts up from 1 to len(prices). Price is the corresponding value.
    """
    print(f"{title}:")
    print("Quantity | Price")
    print("---------+------")
    for i, p in enumerate(prices, start=1):
        # Format quantity right-aligned to width 8, price right-aligned to width 6
        print(f"{i:>8} | {p:>6}")
    print()


def find_equilibrium(demand: List[float], supply: List[float]) -> Tuple[int, float]:
    """Find equilibrium quantity and price by matching buyers and sellers.

    We walk down the demand (high to low) and up the supply (low to high),
    matching pairs while buyer WTP >= seller cost.

    - Equilibrium quantity (Q*) is the number of successful matches.
    - Equilibrium price (P*) is set here as the average of the marginal matched
      buyer WTP and seller cost at Q*. This is a simple, common choice for
      classroom models; any price between them would also clear the market.

    If there is no trade (Q* == 0), we set price to the midpoint between the
    highest WTP and lowest cost just for reference.
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
        ref_high_wtp = demand[0] if demand else 0.0
        ref_low_cost = supply[0] if supply else 0.0
        price = (ref_high_wtp + ref_low_cost) / 2 if (demand and supply) else 0.0
        return 0, price

    # Use midpoint between marginal matched WTP and cost as a simple equilibrium price
    price = (last_matched_wtp + last_matched_cost) / 2  # type: ignore
    return matches, price


def main() -> None:
    # 1) and 2) Create buyers and sellers
    buyers_wtp = build_buyers()
    sellers_cost = build_sellers()

    # 3) and 4) Sort into demand and supply schedules
    demand = sort_demand(buyers_wtp)
    supply = sort_supply(sellers_cost)

    # 5) Print the demand and supply schedules as tables
    print_schedule("Demand", demand)
    print_schedule("Supply", supply)

    # 6) and 7) Find and print equilibrium quantity and price
    eq_qty, eq_price = find_equilibrium(demand, supply)
    print(f"Equilibrium Quantity: {eq_qty}")
    # Format price to 2 decimal places for readability
    print(f"Equilibrium Price: {eq_price:.2f}")


if __name__ == "__main__":
    main()


