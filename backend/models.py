"""
Pydantic models for API request and response schemas.

This module defines the data structures used for:
- Market parameters (input validation with sensible defaults)
- Segmented market parameters (buyers/sellers with different price ranges)
- Price points in demand/supply schedules
- Market response with equilibrium results and surplus calculation

All models include validation and clear field descriptions.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, model_validator

from .config import settings


class Segment(BaseModel):
    """A segment of buyers or sellers with specific parameters.
    
    Represents a group of market participants with similar price characteristics.
    """
    n: int = Field(
        ge=0,
        le=settings.max_buyers,  # Use config for limits
        description="Number of participants in this segment"
    )
    p_min: int = Field(
        ge=0,
        le=settings.max_price,
        description="Minimum price for this segment (inclusive)"
    )
    p_max: int = Field(
        ge=0,
        le=settings.max_price,
        description="Maximum price for this segment (inclusive)"
    )
    dist: Literal["uniform", "normal"] = Field(
        default="uniform",
        description="Distribution type for generating values within the segment"
    )
    mean: Optional[float] = Field(
        default=None,
        ge=0,
        le=settings.max_price,
        description="Mean for normal distribution (defaults to midpoint if not provided)"
    )
    sd: Optional[float] = Field(
        default=None,
        gt=0,
        description="Standard deviation for normal distribution (defaults to range/6 if not provided)"
    )

    @model_validator(mode="after")
    def validate_price_range(self):
        """Ensure p_min <= p_max and validate normal distribution parameters."""
        if self.p_min > self.p_max:
            raise ValueError(f"p_min ({self.p_min}) must be <= p_max ({self.p_max})")
        
        if self.dist == "normal":
            # Validate mean is within range if provided
            if self.mean is not None and not (self.p_min <= self.mean <= self.p_max):
                raise ValueError(f"mean ({self.mean}) must be between p_min ({self.p_min}) and p_max ({self.p_max})")
        
        return self


class MarketParams(BaseModel):
    """Parameters for generating a market simulation.
    
    Supports both legacy simple parameters and new segmented parameters.
    When segments are provided, they take precedence over simple parameters.
    """
    # Legacy simple params (keep for fallback)
    num_buyers: int = Field(
        default=10,
        ge=1,
        le=settings.max_buyers,
        description="Number of buyers to generate (used if buyer_segments not provided)"
    )
    num_sellers: int = Field(
        default=10,
        ge=1,
        le=settings.max_sellers,
        description="Number of sellers to generate (used if seller_segments not provided)"
    )
    min_wtp: int = Field(
        default=10,
        ge=0,
        le=settings.max_price,
        description="Minimum willingness to pay (used if buyer_segments not provided)"
    )
    max_wtp: int = Field(
        default=40,
        ge=0,
        le=settings.max_price,
        description="Maximum willingness to pay (used if buyer_segments not provided)"
    )
    min_cost: int = Field(
        default=5,
        ge=0,
        le=settings.max_price,
        description="Minimum seller cost (used if seller_segments not provided)"
    )
    max_cost: int = Field(
        default=35,
        ge=0,
        le=settings.max_price,
        description="Maximum seller cost (used if seller_segments not provided)"
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducible results (optional)"
    )

    # New segmented params (use these if provided and non-empty)
    buyer_segments: Optional[List[Segment]] = Field(
        default=None,
        max_length=settings.max_segments,
        description="Buyer segments with specific parameters (overrides simple buyer params)"
    )
    seller_segments: Optional[List[Segment]] = Field(
        default=None,
        max_length=settings.max_segments,
        description="Seller segments with specific parameters (overrides simple seller params)"
    )

    @model_validator(mode="after")
    def validate_segments_and_feasibility(self):
        """Validate segment parameters and market feasibility."""
        
        # Validate segment counts and totals
        for name in ("buyer_segments", "seller_segments"):
            segs = getattr(self, name, None)
            if segs:
                if not (1 <= len(segs) <= settings.max_segments):
                    raise ValueError(f"{name} must have between 1 and {settings.max_segments} segments")
                
                # Check total participants don't exceed limits
                total_n = sum(s.n for s in segs)
                max_limit = settings.max_buyers if name == "buyer_segments" else settings.max_sellers
                if total_n > max_limit:
                    raise ValueError(f"Total participants in {name} ({total_n}) exceeds limit ({max_limit})")
        
        # Check market feasibility - warn if no overlap possible
        self._check_market_feasibility()
        
        return self
    
    def _check_market_feasibility(self):
        """Check if the market parameters allow for any possible trades."""
        if self.buyer_segments and self.seller_segments:
            # For segmented markets, check if any buyer segment can trade with any seller segment
            max_buyer_price = max(seg.p_max for seg in self.buyer_segments)
            min_seller_price = min(seg.p_min for seg in self.seller_segments)
            if max_buyer_price < min_seller_price:
                raise ValueError(
                    f"No trades possible: highest buyer max ({max_buyer_price}) "
                    f"< lowest seller min ({min_seller_price})"
                )
        elif not self.buyer_segments and not self.seller_segments:
            # For simple parameters, check basic feasibility
            if self.max_wtp < self.min_cost:
                raise ValueError(
                    f"No trades possible: max_wtp ({self.max_wtp}) < min_cost ({self.min_cost})"
                )

    def model_post_init(self, __context) -> None:
        """Additional validation after model creation."""
        # Only validate legacy params if segments aren't provided
        if not self.buyer_segments:
            if self.max_wtp <= self.min_wtp:
                raise ValueError(f"max_wtp ({self.max_wtp}) must be greater than min_wtp ({self.min_wtp})")
        if not self.seller_segments:
            if self.max_cost <= self.min_cost:
                raise ValueError(f"max_cost ({self.max_cost}) must be greater than min_cost ({self.min_cost})")


class PricePoint(BaseModel):
    """A single point in a demand or supply schedule.
    
    Represents quantity q at price p.
    """
    q: int = Field(ge=0, description="Quantity")
    p: int = Field(ge=0, description="Price")


class Equilibrium(BaseModel):
    """Market equilibrium results.
    
    The quantity and price where supply meets demand.
    """
    quantity: int = Field(ge=0, description="Equilibrium quantity")
    price: Optional[float] = Field(ge=0, description="Equilibrium price")


class Surplus(BaseModel):
    """Economic surplus calculations.
    
    Represents the total economic welfare from market transactions.
    """
    total_max: float = Field(ge=0, description="Maximum total surplus (area between curves up to Q*)")


class MarketResponse(BaseModel):
    """Complete market simulation results.
    
    Contains demand schedule, supply schedule, equilibrium, surplus, and execution metadata.
    """
    demand: List[PricePoint] = Field(description="Demand schedule (sorted high to low)")
    supply: List[PricePoint] = Field(description="Supply schedule (sorted low to high)")
    equilibrium: Equilibrium = Field(description="Market equilibrium")
    surplus: Surplus = Field(description="Economic surplus calculations")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution metadata (timing, participant counts, efficiency metrics)"
    )


class HealthResponse(BaseModel):
    """Health check response with optional details."""
    status: str = Field(
        default="ok", 
        description="Service status (ok/degraded/error)"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional health check details"
    )