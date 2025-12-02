"""
Risk calculation service
Aggregates data from various sources to calculate risk scores
"""

import numpy as np
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.database import RiskScore, SessionLocal
from app.services.data_fetchers import (
    AlphaVantageFetcher, FREDFetcher, SECFetcher, 
    NewsAPIFetcher, BLSFetcher
)
import os
import logging

logger = logging.getLogger(__name__)


class RiskCalculator:
    """Calculate risk scores from various data sources"""
    
    def __init__(self):
        self.alpha_vantage = AlphaVantageFetcher(os.getenv("ALPHA_VANTAGE_API_KEY"))
        self.fred = FREDFetcher(os.getenv("FRED_API_KEY"))
        self.sec = SECFetcher()
        self.news = NewsAPIFetcher(os.getenv("NEWS_API_KEY"))
        self.bls = BLSFetcher()
    
    def calculate_market_risk(self, symbol: str = "SPY") -> Dict:
        """
        Calculate market risk from stock volatility and economic indicators
        Returns normalized score 0-100
        """
        try:
            # Get stock data
            stock_data = self.alpha_vantage.get_stock_quote(symbol)
            
            # Get economic indicators (GDP growth, unemployment)
            gdp_data = self.fred.get_economic_indicator("GDPC1", limit=20)  # Real GDP
            unrate_data = self.fred.get_economic_indicator("UNRATE", limit=20)  # Unemployment
            
            score = 50.0  # Base score
            raw_data = {}
            
            # Calculate volatility from stock price change
            if stock_data and "Global Quote" in stock_data:
                quote = stock_data["Global Quote"]
                change_percent = float(quote.get("10. change percent", "0%").replace("%", ""))
                # Higher volatility = higher risk
                volatility_score = min(100, 50 + abs(change_percent) * 2)
                score = (score + volatility_score) / 2
                raw_data["stock_change"] = change_percent
            
            # Factor in economic indicators
            if gdp_data and "observations" in gdp_data:
                observations = gdp_data["observations"][:2]
                if len(observations) >= 2:
                    recent = float(observations[0].get("value", 0))
                    previous = float(observations[1].get("value", 0))
                    if previous > 0:
                        gdp_growth = ((recent - previous) / previous) * 100
                        # Negative growth increases risk
                        if gdp_growth < 0:
                            score += abs(gdp_growth) * 5
                        raw_data["gdp_growth"] = gdp_growth
            
            if unrate_data and "observations" in unrate_data:
                latest = unrate_data["observations"][0]
                unemployment = float(latest.get("value", 0))
                # Higher unemployment = higher risk
                score += unemployment * 2
                raw_data["unemployment"] = unemployment
            
            # Normalize to 0-100
            final_score = max(0, min(100, score))
            
            # Store in database
            self._store_risk_score("market", final_score, raw_data)
            
            return {
                "category": "market",
                "score": round(final_score, 2),
                "raw_data": raw_data,
                "calculated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error calculating market risk: {e}")
            return self._default_risk("market")
    
    def calculate_supply_chain_risk(self) -> Dict:
        """
        Calculate supply chain risk from news sentiment and trade data
        """
        try:
            score = 50.0
            raw_data = {}
            
            # Get news about supply chain disruptions
            news_data = self.news.get_risk_news("supply chain disruption OR logistics OR shipping delay", page_size=20)
            
            if news_data and "articles" in news_data:
                article_count = len(news_data["articles"])
                # More negative news = higher risk
                # Simple heuristic: more articles = more disruption awareness
                risk_adjustment = min(30, article_count * 1.5)
                score += risk_adjustment
                raw_data["news_articles"] = article_count
                raw_data["recent_news"] = [
                    {
                        "title": article.get("title", ""),
                        "published": article.get("publishedAt", "")
                    }
                    for article in news_data["articles"][:5]
                ]
            
            final_score = max(0, min(100, score))
            self._store_risk_score("supply_chain", final_score, raw_data)
            
            return {
                "category": "supply_chain",
                "score": round(final_score, 2),
                "raw_data": raw_data,
                "calculated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error calculating supply chain risk: {e}")
            return self._default_risk("supply_chain")
    
    def calculate_regulatory_risk(self, cik: str = "0000789019") -> Dict:  # Default: Apple Inc
        """
        Calculate regulatory risk from SEC filings frequency and changes
        """
        try:
            score = 50.0
            raw_data = {}
            
            # Get revenue data to check for volatility (proxy for regulatory impact)
            sec_data = self.sec.get_company_filings(cik, concept="Revenues")
            
            if sec_data and "units" in sec_data:
                # Analyze filing frequency and revenue trends
                units = sec_data.get("units", {})
                if "USD" in units:
                    revenues = units["USD"]
                    if len(revenues) >= 2:
                        # Calculate revenue volatility
                        values = [float(r.get("val", 0)) for r in revenues[-4:]]
                        if len(values) >= 2:
                            volatility = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
                            # Higher volatility might indicate regulatory uncertainty
                            score += volatility * 20
                            raw_data["revenue_volatility"] = volatility
                            raw_data["filing_count"] = len(revenues)
            
            final_score = max(0, min(100, score))
            self._store_risk_score("regulatory", final_score, raw_data)
            
            return {
                "category": "regulatory",
                "score": round(final_score, 2),
                "raw_data": raw_data,
                "calculated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error calculating regulatory risk: {e}")
            return self._default_risk("regulatory")
    
    def calculate_hr_risk(self) -> Dict:
        """
        Calculate HR risk from labor market data
        """
        try:
            score = 50.0
            raw_data = {}
            
            # Get unemployment data from BLS
            bls_data = self.bls.get_employment_data("LNS14000000")  # Unemployment rate
            
            if bls_data and "Results" in bls_data:
                series = bls_data["Results"].get("series", [])
                if series and len(series) > 0:
                    data = series[0].get("data", [])
                    if len(data) >= 2:
                        recent = float(data[0].get("value", 0))
                        previous = float(data[1].get("value", 0))
                        # Rising unemployment = higher HR risk
                        if recent > previous:
                            score += (recent - previous) * 10
                        raw_data["unemployment_rate"] = recent
                        raw_data["unemployment_change"] = recent - previous
            
            final_score = max(0, min(100, score))
            self._store_risk_score("hr", final_score, raw_data)
            
            return {
                "category": "hr",
                "score": round(final_score, 2),
                "raw_data": raw_data,
                "calculated_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error calculating HR risk: {e}")
            return self._default_risk("hr")
    
    def calculate_all_risks(self) -> Dict:
        """Calculate all risk categories and overall risk"""
        market = self.calculate_market_risk()
        supply_chain = self.calculate_supply_chain_risk()
        regulatory = self.calculate_regulatory_risk()
        hr = self.calculate_hr_risk()
        
        # Overall risk is weighted average
        overall = (
            market["score"] * 0.3 +
            supply_chain["score"] * 0.25 +
            regulatory["score"] * 0.25 +
            hr["score"] * 0.2
        )
        
        return {
            "market_risk": market,
            "supply_chain_risk": supply_chain,
            "regulatory_risk": regulatory,
            "hr_risk": hr,
            "overall_risk": round(overall, 2),
            "last_updated": datetime.utcnow()
        }
    
    def _store_risk_score(self, category: str, score: float, raw_data: Dict):
        """Store risk score in database"""
        db = SessionLocal()
        try:
            risk_score = RiskScore(
                risk_category=category,
                score=score,
                raw_data=raw_data
            )
            db.add(risk_score)
            db.commit()
        except Exception as e:
            logger.error(f"Error storing risk score: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _default_risk(self, category: str) -> Dict:
        """Return default risk score when calculation fails"""
        return {
            "category": category,
            "score": 50.0,
            "raw_data": {"error": "Calculation failed, using default"},
            "calculated_at": datetime.utcnow()
        }

