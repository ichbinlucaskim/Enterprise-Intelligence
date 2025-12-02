"""
Monte Carlo simulation engine for risk analysis
Uses NumPy for efficient simulations with cached historical data
"""

import numpy as np
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import MonteCarloResult, RiskScore, SessionLocal
import logging

logger = logging.getLogger(__name__)


class MonteCarloSimulator:
    """Monte Carlo simulation for risk forecasting"""
    
    def run_simulation(
        self,
        risk_category: str,
        iterations: int = 5000,
        use_cached_data: bool = True
    ) -> Dict:
        """
        Run Monte Carlo simulation for a risk category
        
        Args:
            risk_category: One of 'market', 'supply_chain', 'regulatory', 'hr'
            iterations: Number of simulation iterations (default 5000)
            use_cached_data: Use cached risk scores for historical data
        
        Returns:
            Dictionary with mean, std, and percentiles
        """
        try:
            # Get historical data for the risk category
            if use_cached_data:
                historical_scores = self._get_historical_scores(risk_category)
            else:
                historical_scores = []
            
            # If no historical data, use default parameters
            if not historical_scores or len(historical_scores) < 2:
                logger.warning(f"Insufficient historical data for {risk_category}, using defaults")
                risk_mean = 50.0
                risk_std = 15.0
            else:
                # Calculate mean and standard deviation from historical data
                scores_array = np.array(historical_scores)
                risk_mean = float(np.mean(scores_array))
                risk_std = float(np.std(scores_array))
                
                # Ensure minimum std to avoid zero variance
                if risk_std < 1.0:
                    risk_std = 10.0
            
            # Run Monte Carlo simulation using normal distribution
            # This assumes risk scores follow a normal distribution
            simulations = np.random.normal(risk_mean, risk_std, iterations)
            
            # Clip values to valid range [0, 100]
            simulations = np.clip(simulations, 0, 100)
            
            # Calculate statistics
            sim_mean = float(np.mean(simulations))
            sim_std = float(np.std(simulations))
            percentiles = {
                "5": float(np.percentile(simulations, 5)),
                "50": float(np.percentile(simulations, 50)),
                "95": float(np.percentile(simulations, 95))
            }
            
            # Store result in database
            result = {
                "risk_category": risk_category,
                "mean": sim_mean,
                "std": sim_std,
                "percentiles": percentiles,
                "iterations": iterations,
                "calculated_at": datetime.utcnow()
            }
            
            self._store_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error running Monte Carlo simulation: {e}")
            # Return default result on error
            return {
                "risk_category": risk_category,
                "mean": 50.0,
                "std": 10.0,
                "percentiles": {"5": 35.0, "50": 50.0, "95": 65.0},
                "iterations": iterations,
                "calculated_at": datetime.utcnow()
            }
    
    def _get_historical_scores(self, risk_category: str, limit: int = 30) -> list:
        """Get historical risk scores from database"""
        db = SessionLocal()
        try:
            scores = db.query(RiskScore).filter(
                RiskScore.risk_category == risk_category
            ).order_by(
                RiskScore.calculated_at.desc()
            ).limit(limit).all()
            
            return [score.score for score in scores]
        except Exception as e:
            logger.error(f"Error fetching historical scores: {e}")
            return []
        finally:
            db.close()
    
    def _store_result(self, result: Dict):
        """Store Monte Carlo result in database"""
        db = SessionLocal()
        try:
            mc_result = MonteCarloResult(
                risk_category=result["risk_category"],
                mean=result["mean"],
                std=result["std"],
                percentiles=result["percentiles"],
                iterations=result["iterations"]
            )
            db.add(mc_result)
            db.commit()
        except Exception as e:
            logger.error(f"Error storing Monte Carlo result: {e}")
            db.rollback()
        finally:
            db.close()
    
    def run_multiple_scenarios(
        self,
        risk_category: str,
        scenarios: Dict[str, Dict] = None
    ) -> Dict:
        """
        Run multiple Monte Carlo scenarios with different parameters
        
        Args:
            risk_category: Risk category to simulate
            scenarios: Dictionary of scenario names to parameters
                      e.g., {"optimistic": {"mean": 30, "std": 5}, ...}
        
        Returns:
            Dictionary with results for each scenario
        """
        if scenarios is None:
            scenarios = {
                "optimistic": {"mean": 30, "std": 5},
                "baseline": {"mean": 50, "std": 10},
                "pessimistic": {"mean": 70, "std": 15}
            }
        
        results = {}
        for scenario_name, params in scenarios.items():
            iterations = 5000
            simulations = np.random.normal(
                params["mean"],
                params["std"],
                iterations
            )
            simulations = np.clip(simulations, 0, 100)
            
            results[scenario_name] = {
                "mean": float(np.mean(simulations)),
                "std": float(np.std(simulations)),
                "percentiles": {
                    "5": float(np.percentile(simulations, 5)),
                    "50": float(np.percentile(simulations, 50)),
                    "95": float(np.percentile(simulations, 95))
                }
            }
        
        return {
            "risk_category": risk_category,
            "scenarios": results,
            "calculated_at": datetime.utcnow()
        }

