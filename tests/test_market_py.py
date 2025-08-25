"""
Unit tests for market logic functions.

Run with: python -m pytest test_market.py -v
"""

import pytest
from backend.market import (
    find_equilibrium, 
    build_buyers_and_sellers, 
    compute_total_surplus_max,
    create_schedule_table,
    analyze_market_structure
)
from backend.models import MarketParams, Segment


class TestEquilibrium:
    """Test equilibrium finding logic."""

    def test_basic_equilibrium(self):
        """Test basic equilibrium with simple matching."""
        demand = [10, 8, 6, 4]  # sorted high to low
        supply = [3, 5, 7, 9]   # sorted low to high
        
        q, p = find_equilibrium(demand, supply)
        
        # Should match: (10,3), (8,5) - 2 trades
        # Next buyer wants 6, last matched seller cost 5
        # Price = (6 + 5) / 2 = 5.5
        assert q == 2
        assert p == 5.5

    def test_no_equilibrium(self):
        """Test case where no trades are possible."""
        demand = [5, 3]
        supply = [8, 10]
        
        q, p = find_equilibrium(demand, supply)
        
        assert q == 0
        assert p == 6.5  # (5 + 8) / 2

    def test_full_trade_equilibrium(self):
        """Test case where all participants can trade."""
        demand = [10, 8]
        supply = [6, 7]
        
        q, p = find_equilibrium(demand, supply)
        
        assert q == 2
        assert p == 7.5  # (8 + 7) / 2 - midpoint of last matched pair

    def test_empty_markets(self):
        """Test edge cases with empty markets."""
        assert find_equilibrium([], []) == (0, 0.0)
        assert find_equilibrium([10], []) == (0, 10.0)
        assert find_equilibrium([], [5]) == (0, 5.0)


class TestSurplusCalculation:
    """Test total surplus calculations."""

    def test_basic_surplus(self):
        """Test surplus calculation with basic trades."""
        demand = [10, 8, 6]
        supply = [3, 5, 7]
        q_star = 3
        
        surplus = compute_total_surplus_max(demand, supply, q_star)
        
        # (10-3) + (8-5) + (6-7) = 7 + 3 - 1 = 9
        assert surplus == 9.0

    def test_zero_quantity_surplus(self):
        """Test surplus when no trades occur."""
        demand = [10, 8]
        supply = [3, 5]
        
        surplus = compute_total_surplus_max(demand, supply, 0)
        
        assert surplus == 0.0

    def test_surplus_limited_by_participants(self):
        """Test surplus calculation when q_star exceeds participants."""
        demand = [10, 8]
        supply = [3, 5]
        
        # Request surplus for 5 trades, but only 2 possible
        surplus = compute_total_surplus_max(demand, supply, 5)
        
        # Should only calculate for 2 trades: (10-3) + (8-5) = 10
        assert surplus == 10.0


class TestMarketConstruction:
    """Test market building from parameters."""

    def test_simple_parameters(self):
        """Test building market from simple parameters."""
        params = MarketParams(
            num_buyers=3,
            num_sellers=3,
            min_wtp=10,
            max_wtp=20,
            min_cost=5,
            max_cost=15,
            seed=42
        )
        
        buyers, sellers = build_buyers_and_sellers(params)
        
        assert len(buyers) == 3
        assert len(sellers) == 3
        assert all(10 <= b <= 20 for b in buyers)
        assert all(5 <= s <= 15 for s in sellers)
        # Should be sorted
        assert buyers == sorted(buyers, reverse=True)
        assert sellers == sorted(sellers)

    def test_segmented_parameters(self):
        """Test building market from segmented parameters."""
        params = MarketParams(
            seed=123,
            buyer_segments=[
                Segment(n=2, p_min=20, p_max=30),
                Segment(n=2, p_min=10, p_max=19)
            ],
            seller_segments=[
                Segment(n=2, p_min=5, p_max=10),
                Segment(n=2, p_min=11, p_max=15)
            ]
        )
        
        buyers, sellers = build_buyers_and_sellers(params)
        
        assert len(buyers) == 4
        assert len(sellers) == 4
        assert all(10 <= b <= 30 for b in buyers)
        assert all(5 <= s <= 15 for s in sellers)

    def test_reproducible_with_seed(self):
        """Test that same seed produces same results."""
        params = MarketParams(num_buyers=5, num_sellers=5, seed=42)
        
        buyers1, sellers1 = build_buyers_and_sellers(params)
        buyers2, sellers2 = build_buyers_and_sellers(params)
        
        assert buyers1 == buyers2
        assert sellers1 == sellers2


class TestScheduleTable:
    """Test schedule table creation."""

    def test_demand_schedule(self):
        """Test creating demand schedule table."""
        buyers = [10, 8, 6, 4]
        
        schedule = create_schedule_table(buyers)
        
        expected = [
            {"q": 1, "p": 10},
            {"q": 2, "p": 8},
            {"q": 3, "p": 6},
            {"q": 4, "p": 4}
        ]
        assert schedule == expected

    def test_empty_schedule(self):
        """Test empty schedule table."""
        schedule = create_schedule_table([])
        assert schedule == []


class TestMarketAnalysis:
    """Test market analysis utilities."""

    def test_basic_analysis(self):
        """Test basic market structure analysis."""
        demand = [10, 8, 6]
        supply = [4, 6, 8]
        
        analysis = analyze_market_structure(demand, supply)
        
        assert analysis["demand_size"] == 3
        assert analysis["supply_size"] == 3
        assert analysis["demand_range"] == (6, 10)
        assert analysis["supply_range"] == (4, 8)
        assert analysis["potential_trades"] == 3
        assert analysis["price_overlap"] == True  # 10 >= 4


class TestValidation:
    """Test input validation and error handling."""

    def test_invalid_segment_parameters(self):
        """Test validation of invalid segment parameters."""
        with pytest.raises(ValueError, match="p_min.*p_max"):
            build_buyers_and_sellers(MarketParams(
                buyer_segments=[Segment(n=1, p_min=20, p_max=10)]
            ))

    def test_zero_participants_in_segments(self):
        """Test handling of segments with zero participants."""
        params = MarketParams(
            buyer_segments=[Segment(n=0, p_min=10, p_max=20)],
            seller_segments=[Segment(n=1, p_min=5, p_max=15)]
        )
        
        with pytest.raises(ValueError, match="zero buyers"):
            build_buyers_and_sellers(params)


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])