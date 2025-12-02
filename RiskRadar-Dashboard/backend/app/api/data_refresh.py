"""
API endpoints for data refresh operations
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import DataRefreshRequest, DataRefreshResponse
from app.services.risk_calculator import RiskCalculator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
calculator = RiskCalculator()


def refresh_data_background(data_types: list = None):
    """Background task to refresh data"""
    try:
        if data_types is None:
            data_types = ["market", "supply_chain", "regulatory", "hr"]
        
        refreshed = []
        for data_type in data_types:
            try:
                if data_type == "market":
                    calculator.calculate_market_risk()
                elif data_type == "supply_chain":
                    calculator.calculate_supply_chain_risk()
                elif data_type == "regulatory":
                    calculator.calculate_regulatory_risk()
                elif data_type == "hr":
                    calculator.calculate_hr_risk()
                refreshed.append(data_type)
            except Exception as e:
                logger.error(f"Error refreshing {data_type}: {e}")
        
        return refreshed
    except Exception as e:
        logger.error(f"Error in background refresh: {e}")
        return []


@router.post("/refresh", response_model=DataRefreshResponse)
async def refresh_data(
    request: DataRefreshRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger data refresh from APIs
    Runs in background to avoid blocking
    """
    try:
        data_types = request.data_types or ["market", "supply_chain", "regulatory", "hr"]
        
        # Add background task
        background_tasks.add_task(refresh_data_background, data_types)
        
        return {
            "refreshed_types": data_types,
            "success": True,
            "message": "Data refresh initiated in background",
            "refreshed_at": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error initiating data refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_data_status():
    """
    Get status of cached data (freshness, expiry)
    """
    from app.database import RiskDataCache, SessionLocal
    from datetime import datetime
    
    db = SessionLocal()
    try:
        cache_entries = db.query(RiskDataCache).all()
        
        status = {}
        for entry in cache_entries:
            if entry.data_type not in status:
                status[entry.data_type] = {
                    "sources": [],
                    "total_entries": 0,
                    "expired_entries": 0
                }
            
            status[entry.data_type]["total_entries"] += 1
            if entry.expires_at < datetime.utcnow():
                status[entry.data_type]["expired_entries"] += 1
            
            if entry.source not in status[entry.data_type]["sources"]:
                status[entry.data_type]["sources"].append(entry.source)
        
        return {
            "status": status,
            "checked_at": datetime.utcnow()
        }
    finally:
        db.close()

