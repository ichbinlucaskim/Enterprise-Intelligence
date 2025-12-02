"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class RiskScoreResponse(BaseModel):
    """Risk score response model"""
    category: str
    score: float = Field(..., ge=0, le=100, description="Risk score from 0-100")
    raw_data: Optional[Dict] = None
    calculated_at: datetime


class RiskRadarResponse(BaseModel):
    """Complete risk radar data for dashboard"""
    market_risk: RiskScoreResponse
    supply_chain_risk: RiskScoreResponse
    regulatory_risk: RiskScoreResponse
    hr_risk: RiskScoreResponse
    overall_risk: float = Field(..., ge=0, le=100)
    last_updated: datetime


class MonteCarloRequest(BaseModel):
    """Monte Carlo simulation request"""
    risk_category: str = Field(..., description="Risk category: market, supply_chain, regulatory, hr")
    iterations: int = Field(5000, ge=100, le=100000, description="Number of simulations")
    use_cached_data: bool = Field(True, description="Use cached historical data")


class MonteCarloResponse(BaseModel):
    """Monte Carlo simulation results"""
    risk_category: str
    mean: float
    std: float
    percentiles: Dict[str, float] = Field(..., description="5th, 50th, 95th percentiles")
    iterations: int
    calculated_at: datetime


class DataRefreshRequest(BaseModel):
    """Request to refresh data from APIs"""
    data_types: Optional[List[str]] = Field(None, description="Specific data types to refresh, or all if None")


class DataRefreshResponse(BaseModel):
    """Data refresh status"""
    refreshed_types: List[str]
    success: bool
    message: str
    refreshed_at: datetime

