"""
FastAPI application for supply and demand market simulation.

This is the main entry point for the market simulation API.
It provides endpoints for:
- Health check (/health)
- Market simulation (/market) with support for segmented inputs

Setup instructions:
1. Install dependencies: pip install fastapi uvicorn "pydantic>=2" slowapi
2. Run the server: python -m uvicorn backend.main:app --reload --port 8001
3. Test with curl:
   curl -X POST http://127.0.0.1:8001/market \
     -H "Content-Type: application/json" \
     -d '{"num_buyers": 5, "num_sellers": 5, "seed": 42}'

   Or test with segmented inputs:
   curl -X POST http://127.0.0.1:8001/market \
     -H "Content-Type: application/json" \
     -d '{
       "seed": 123,
       "buyer_segments": [
         {"n": 6, "p_min": 30, "p_max": 40},
         {"n": 4, "p_min": 20, "p_max": 29}
       ],
       "seller_segments": [
         {"n": 5, "p_min": 10, "p_max": 15},
         {"n": 5, "p_min": 16, "p_max": 25}
       ]
     }'

The API will be available at http://127.0.0.1:8001
Interactive docs at http://127.0.0.1:8001/docs
"""

import logging
import time
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .models import MarketParams, MarketResponse, HealthResponse, PricePoint, Equilibrium, Surplus
from .market import (
    build_buyers_and_sellers, find_equilibrium, create_schedule_table, compute_total_surplus_max
)
from .config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Market Simulation API",
    description="A simple supply and demand market simulation API with support for segmented markets",
    version="2.1.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware - temporarily allow all origins for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify the API is running."""
    logger.info("Health check requested")
    
    # Basic functionality test
    try:
        # Test market logic with minimal data
        from .market import find_equilibrium
        test_eq = find_equilibrium([10], [5])
        
        return HealthResponse(
            status="ok", 
            details={"market_logic_test": "passed", "test_equilibrium": test_eq}
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return HealthResponse(status="degraded", details={"error": str(e)})


@app.post("/market", response_model=MarketResponse, tags=["simulation"])
@limiter.limit("30/minute")  # Allow 30 requests per minute
async def simulate_market(request: Request, params: MarketParams):
    """Simulate a market with the given parameters.
    
    Generates random buyers and sellers (either from segments or simple parameters),
    sorts them into demand and supply schedules, finds the equilibrium quantity
    and price, and calculates the maximum total surplus.
    
    Supports both legacy simple parameters and new segmented parameters.
    When segments are provided, they take precedence over simple parameters.
    """
    start_time = time.time()
    
    # Log incoming request details
    total_buyers = (
        sum(seg.n for seg in params.buyer_segments) if params.buyer_segments 
        else params.num_buyers
    )
    total_sellers = (
        sum(seg.n for seg in params.seller_segments) if params.seller_segments 
        else params.num_sellers
    )
    
    logger.info(
        f"Market simulation requested - Buyers: {total_buyers}, "
        f"Sellers: {total_sellers}, Seed: {params.seed}, "
        f"Using segments: {bool(params.buyer_segments or params.seller_segments)}"
    )
    
    try:
        # Build buyers and sellers using the new segmented logic
        buyers_sorted, sellers_sorted = build_buyers_and_sellers(params)
        logger.debug(f"Generated {len(buyers_sorted)} buyers, {len(sellers_sorted)} sellers")
        
        # Find equilibrium
        eq_quantity, eq_price = find_equilibrium(buyers_sorted, sellers_sorted)
        equilibrium = Equilibrium(quantity=eq_quantity, price=eq_price)
        
        # Calculate maximum total surplus
        total_surplus = compute_total_surplus_max(buyers_sorted, sellers_sorted, eq_quantity)
        surplus = Surplus(total_max=total_surplus)
        
        # Create schedule tables
        demand_schedule = [PricePoint(q=point["q"], p=point["p"]) 
                          for point in create_schedule_table(buyers_sorted)]
        supply_schedule = [PricePoint(q=point["q"], p=point["p"]) 
                          for point in create_schedule_table(sellers_sorted)]
        
        # Calculate execution time and create metadata
        execution_time = time.time() - start_time
        metadata = {
            "execution_time_ms": round(execution_time * 1000, 2),
            "total_buyers": len(buyers_sorted),
            "total_sellers": len(sellers_sorted),
            "trades_possible": eq_quantity > 0,
            "efficiency_ratio": round(eq_quantity / min(len(buyers_sorted), len(sellers_sorted)), 3) if min(len(buyers_sorted), len(sellers_sorted)) > 0 else 0
        }
        
        logger.info(
            f"Market simulation completed - Q*: {eq_quantity}, P*: {eq_price:.2f}, "
            f"Surplus: {total_surplus:.2f}, Time: {execution_time*1000:.1f}ms"
        )
        
        return MarketResponse(
            demand=demand_schedule,
            supply=supply_schedule,
            equilibrium=equilibrium,
            surplus=surplus,
            metadata=metadata
        )
        
    except ValueError as e:
        logger.warning(f"Invalid market parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"Market simulation failed after {execution_time*1000:.1f}ms: {str(e)}", 
            exc_info=True
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Market simulation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {settings.default_port}")
    uvicorn.run(app, host="0.0.0.0", port=settings.default_port)
    