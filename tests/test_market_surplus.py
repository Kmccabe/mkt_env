# tests/test_market_surplus.py
from backend.market import compute_total_surplus_max, create_schedule_table

def test_total_surplus_basic():
    demand = [50, 40, 30, 20]
    supply = [10, 15, 18, 22]
    # trades occur for first three pairs: (50-10) + (40-15) + (30-18)
    q_star = 3
    ts = compute_total_surplus_max(demand, supply, q_star)
    assert ts == (50-10) + (40-15) + (30-18)

def test_total_surplus_handles_qstar_bounds():
    demand = [30, 25]
    supply = [10, 20]
    # more q* than length should be clipped internally
    assert compute_total_surplus_max(demand, supply, 999) == (30-10) + (25-20)
    # zero/negative q* => 0.0
    assert compute_total_surplus_max(demand, supply, 0) == 0.0
    assert compute_total_surplus_max(demand, supply, -5) == 0.0

def test_create_schedule_table_shape_and_values():
    values = [40, 35, 30]
    table = create_schedule_table(values)
    assert table == [{"q": 1, "p": 40}, {"q": 2, "p": 35}, {"q": 3, "p": 30}]
