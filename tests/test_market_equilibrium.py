# tests/test_market_equilibrium.py
import pytest
from backend.market import find_equilibrium

def test_equilibrium_midpoint_example():
    demand = [40, 35, 30, 20]   # already sorted high->low
    supply = [10, 15, 18, 22]   # already sorted low->high
    q, p = find_equilibrium(demand, supply)
    assert q == 3
    assert p == (20 + 18) / 2.0

def test_no_trade_case_returns_informative_price_when_possible():
    demand = [10, 9]
    supply = [12, 13]
    q, p = find_equilibrium(demand, supply)
    assert q == 0
    # midpoint of best bid/ask
    assert p == (10 + 12) / 2.0

def test_no_trade_with_one_empty_side():
    # empty supply
    q, p = find_equilibrium([10, 8], [])
    assert q == 0 and p == 10.0
    # empty demand
    q, p = find_equilibrium([], [5, 7])
    assert q == 0 and p == 5.0
    # both empty
    q, p = find_equilibrium([], [])
    assert q == 0 and p == 0.0

def test_full_trade_case():
    demand = [50, 40, 30]
    supply = [5, 10, 20]
    q, p = find_equilibrium(demand, supply)
    assert q == 3
    # price is midpoint of the last matched pair
    assert p == (30 + 20) / 2.0
