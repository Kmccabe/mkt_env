"""
FastAPI application for supply and demand market simulation.

This is the main entry point for the market simulation API.
It provides endpoints for:
- Health check (/health)
- Market simulation (/market) with support for segmented inputs

Setup instructions:
1. Install dependencies: pip install fastapi uvicorn "pydantic>=2"
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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import MarketParams, MarketResponse, HealthResponse, PricePoint, Equilibrium, Surplus
from .market import (
    build_buyers_and_sellers, find_equilibrium, create_schedule_table, compute_total_surplus_max
)

# Create FastAPI app
app = FastAPI(
    title="Market Simulation API",
    description="A simple supply and demand market simulation API with support for segmented markets",
    version="2.0.0"
)

# Add CORS middleware for frontend development

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify the API is running."""
    return HealthResponse(status="ok")


@app.post("/market", response_model=MarketResponse)
async def simulate_market(params: MarketParams):
    """Simulate a market with the given parameters.
    
    Generates random buyers and sellers (either from segments or simple parameters),
    sorts them into demand and supply schedules, finds the equilibrium quantity
    and price, and calculates the maximum total surplus.
    
    Supports both legacy simple parameters and new segmented parameters.
    When segments are provided, they take precedence over simple parameters.
    """
    try:
        # Build buyers and sellers using the new segmented logic
        buyers_sorted, sellers_sorted = build_buyers_and_sellers(params)
        
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
        
        return MarketResponse(
            demand=demand_schedule,
            supply=supply_schedule,
            equilibrium=equilibrium,
            surplus=surplus
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market simulation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
