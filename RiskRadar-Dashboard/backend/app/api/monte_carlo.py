"""
API endpoints for Monte Carlo simulations
"""

from fastapi import APIRouter, HTTPException
from app.models import MonteCarloRequest, MonteCarloResponse
from app.services.monte_carlo import MonteCarloSimulator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
simulator = MonteCarloSimulator()


@router.post("/simulate", response_model=MonteCarloResponse)
async def run_monte_carlo(request: MonteCarloRequest):
    """
    Run Monte Carlo simulation for a risk category
    Uses historical data to estimate future risk distributions
    """
    valid_categories = ["market", "supply_chain", "regulatory", "hr"]
    if request.risk_category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    try:
        result = simulator.run_simulation(
            risk_category=request.risk_category,
            iterations=request.iterations,
            use_cached_data=request.use_cached_data
        )
        return result
    except Exception as e:
        logger.error(f"Error running Monte Carlo simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios/{category}")
async def get_scenarios(category: str):
    """
    Get multiple scenario simulations (optimistic, baseline, pessimistic)
    """
    valid_categories = ["market", "supply_chain", "regulatory", "hr"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    try:
        result = simulator.run_multiple_scenarios(category)
        return result
    except Exception as e:
        logger.error(f"Error running scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

