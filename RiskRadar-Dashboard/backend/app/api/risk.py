"""
API endpoints for risk data
"""

from fastapi import APIRouter, HTTPException
from app.models import RiskRadarResponse, RiskScoreResponse
from app.services.risk_calculator import RiskCalculator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
calculator = RiskCalculator()


@router.get("/radar", response_model=RiskRadarResponse)
async def get_risk_radar():
    """
    Get complete risk radar data for all categories
    Returns aggregated risk scores for dashboard visualization
    """
    try:
        risks = calculator.calculate_all_risks()
        return risks
    except Exception as e:
        logger.error(f"Error getting risk radar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{category}", response_model=RiskScoreResponse)
async def get_risk_category(category: str):
    """
    Get risk score for a specific category
    Categories: market, supply_chain, regulatory, hr
    """
    valid_categories = ["market", "supply_chain", "regulatory", "hr"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    try:
        if category == "market":
            result = calculator.calculate_market_risk()
        elif category == "supply_chain":
            result = calculator.calculate_supply_chain_risk()
        elif category == "regulatory":
            result = calculator.calculate_regulatory_risk()
        elif category == "hr":
            result = calculator.calculate_hr_risk()
        
        return result
    except Exception as e:
        logger.error(f"Error calculating {category} risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

