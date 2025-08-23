"""
Pydantic models for API request and response schemas.

This module defines the data structures used for:
- Market parameters (input validation with sensible defaults)
- Segmented market parameters (buyers/sellers with different price ranges)
- Price points in demand/supply schedules
- Market response with equilibrium results and surplus calculation

All models include validation and clear field descriptions.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator


class Segment(BaseModel):
    """A segment of buyers or sellers with specific parameters.
    
    Represents a group of market participants with similar price characteristics.
    """
    n: int = Field(
        ge=0,
        description="Number of participants in this segment"
    )
    p_min: int = Field(
        description="Minimum price for this segment (inclusive)"
    )
    p_max: int = Field(
        description="Maximum price for this segment (inclusive)"
    )
    dist: Literal["uniform", "normal"] = Field(
        default="uniform",
        description="Distribution type for generating values within the segment"
    )
    mean: Optional[float] = Field(
        default=None,
        description="Mean for normal distribution (defaults to midpoint if not provided)"
    )
    sd: Optional[float] = Field(
        default=None,
        description="Standard deviation for normal distribution (defaults to range/6 if not provided)"
    )


class MarketParams(BaseModel):
    """Parameters for generating a market simulation.
    
    Supports both legacy simple parameters and new segmented parameters.
    When segments are provided, they take precedence over simple parameters.
    """
    # Legacy simple params (keep for fallback)
    num_buyers: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of buyers to generate (used if buyer_segments not provided)"
    )
    num_sellers: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of sellers to generate (used if seller_segments not provided)"
    )
    min_wtp: int = Field(
        default=10,
        ge=0,
        description="Minimum willingness to pay (used if buyer_segments not provided)"
    )
    max_wtp: int = Field(
        default=40,
        ge=0,
        description="Maximum willingness to pay (used if buyer_segments not provided)"
    )
    min_cost: int = Field(
        default=5,
        ge=0,
        description="Minimum seller cost (used if seller_segments not provided)"
    )
    max_cost: int = Field(
        default=35,
        ge=0,
        description="Maximum seller cost (used if seller_segments not provided)"
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducible results (optional)"
    )

    # New segmented params (use these if provided and non-empty)
    buyer_segments: Optional[List[Segment]] = Field(
        default=None,
        description="Buyer segments with specific parameters (overrides simple buyer params)"
    )
    seller_segments: Optional[List[Segment]] = Field(
        default=None,
        description="Seller segments with specific parameters (overrides simple seller params)"
    )

    @model_validator(mode="after")
    def validate_segments(self):
        """Validate segment parameters if provided."""
        for name in ("buyer_segments", "seller_segments"):
            segs = getattr(self, name, None)
            if segs:
                if not (1 <= len(segs) <= 3):
                    raise ValueError(f"{name} must have between 1 and 3 segments")
                for s in segs:
                    if s.p_min > s.p_max:
                        raise ValueError(f"{name} has p_min > p_max")
        return self

    def model_post_init(self, __context) -> None:
        """Validate that max values are greater than min values for legacy params."""
        if self.max_wtp <= self.min_wtp:
            raise ValueError("max_wtp must be greater than min_wtp")
        if self.max_cost <= self.min_cost:
            raise ValueError("max_cost must be greater than min_cost")


class PricePoint(BaseModel):
    """A single point in a demand or supply schedule.
    
    Represents quantity q at price p.
    """
    q: int = Field(description="Quantity")
    p: int = Field(description="Price")


class Equilibrium(BaseModel):
    """Market equilibrium results.
    
    The quantity and price where supply meets demand.
    """
    quantity: int = Field(description="Equilibrium quantity")
    price: Optional[float] = Field(description="Equilibrium price")


class Surplus(BaseModel):
    """Economic surplus calculations.
    
    Represents the total economic welfare from market transactions.
    """
    total_max: float = Field(description="Maximum total surplus (area between curves up to Q*)")


class MarketResponse(BaseModel):
    """Complete market simulation results.
    
    Contains demand schedule, supply schedule, equilibrium, and surplus.
    """
    demand: List[PricePoint] = Field(description="Demand schedule (sorted high to low)")
    supply: List[PricePoint] = Field(description="Supply schedule (sorted low to high)")
    equilibrium: Equilibrium = Field(description="Market equilibrium")
    surplus: Surplus = Field(description="Economic surplus calculations")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="ok", description="Service status")
