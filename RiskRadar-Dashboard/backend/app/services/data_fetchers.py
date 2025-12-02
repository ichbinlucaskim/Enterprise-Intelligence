"""
Data fetching services for various free APIs
Implements caching and rate limit handling
"""

import requests
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
from sqlalchemy.orm import Session
from app.database import RiskDataCache, SessionLocal
import logging

logger = logging.getLogger(__name__)

# Cache expiry in hours
CACHE_EXPIRY_HOURS = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))


class DataFetcher:
    """Base class for data fetchers with caching"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Enterprise-Risk-Dashboard/1.0"})
    
    def _get_cached_data(self, data_type: str, source: str, symbol: str) -> Optional[Dict]:
        """Get cached data if not expired"""
        db = SessionLocal()
        try:
            cache_entry = db.query(RiskDataCache).filter(
                RiskDataCache.data_type == data_type,
                RiskDataCache.source == source,
                RiskDataCache.symbol == symbol,
                RiskDataCache.expires_at > datetime.utcnow()
            ).first()
            
            if cache_entry:
                return cache_entry.data
            return None
        finally:
            db.close()
    
    def _cache_data(self, data_type: str, source: str, symbol: str, data: Dict):
        """Cache API response"""
        db = SessionLocal()
        try:
            # Delete old cache entries
            db.query(RiskDataCache).filter(
                RiskDataCache.data_type == data_type,
                RiskDataCache.source == source,
                RiskDataCache.symbol == symbol
            ).delete()
            
            # Create new cache entry
            cache_entry = RiskDataCache(
                data_type=data_type,
                source=source,
                symbol=symbol,
                data=data,
                expires_at=datetime.utcnow() + timedelta(hours=CACHE_EXPIRY_HOURS)
            )
            db.add(cache_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            db.rollback()
        finally:
            db.close()


class AlphaVantageFetcher(DataFetcher):
    """Fetcher for Alpha Vantage stock data (25 calls/day free tier)"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get stock quote with caching"""
        # Check cache first
        cached = self._get_cached_data("market", "alpha_vantage", symbol)
        if cached:
            return cached
        
        if not self.api_key:
            logger.warning("Alpha Vantage API key not set")
            return None
        
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Handle API errors
            if "Error Message" in data or "Note" in data:
                logger.warning(f"Alpha Vantage API error: {data.get('Error Message', data.get('Note'))}")
                return None
            
            # Cache successful response
            if "Global Quote" in data:
                self._cache_data("market", "alpha_vantage", symbol, data)
                return data
            
            return None
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data: {e}")
            return None


class FREDFetcher(DataFetcher):
    """Fetcher for FRED economic indicators (unlimited free access)"""
    
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    
    def get_economic_indicator(self, series_id: str, limit: int = 100) -> Optional[Dict]:
        """Get economic indicator data"""
        cached = self._get_cached_data("market", "fred", series_id)
        if cached:
            return cached
        
        if not self.api_key:
            logger.warning("FRED API key not set")
            return None
        
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": limit,
                "sort_order": "desc"
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "observations" in data:
                self._cache_data("market", "fred", series_id, data)
                return data
            
            return None
        except Exception as e:
            logger.error(f"Error fetching FRED data: {e}")
            return None


class SECFetcher(DataFetcher):
    """Fetcher for SEC EDGAR filings (unlimited free access)"""
    
    BASE_URL = "https://data.sec.gov/api/xbrl/companyconcept/CIK"
    
    def get_company_filings(self, cik: str, taxonomy: str = "us-gaap", concept: str = "Revenues") -> Optional[Dict]:
        """Get SEC filings data (no API key required)"""
        cached = self._get_cached_data("regulatory", "sec", f"{cik}_{concept}")
        if cached:
            return cached
        
        try:
            # SEC requires User-Agent header
            headers = {
                "User-Agent": "Enterprise Risk Dashboard contact@example.com",
                "Accept": "application/json"
            }
            
            url = f"{self.BASE_URL}/{cik.zfill(10)}/{taxonomy}/{concept}.json"
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self._cache_data("regulatory", "sec", f"{cik}_{concept}", data)
            return data
        except Exception as e:
            logger.error(f"Error fetching SEC data: {e}")
            return None


class NewsAPIFetcher(DataFetcher):
    """Fetcher for NewsAPI (100 requests/day, 24-hour delay on free tier)"""
    
    BASE_URL = "https://newsapi.org/v2/everything"
    
    def get_risk_news(self, query: str, page_size: int = 10) -> Optional[Dict]:
        """Get news articles related to risk (cached to respect rate limits)"""
        cached = self._get_cached_data("supply_chain", "newsapi", query)
        if cached:
            return cached
        
        if not self.api_key:
            logger.warning("NewsAPI key not set")
            return None
        
        try:
            params = {
                "q": query,
                "apiKey": self.api_key,
                "pageSize": page_size,
                "sortBy": "publishedAt",
                "language": "en"
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                self._cache_data("supply_chain", "newsapi", query, data)
                return data
            
            return None
        except Exception as e:
            logger.error(f"Error fetching NewsAPI data: {e}")
            return None


class BLSFetcher(DataFetcher):
    """Fetcher for Bureau of Labor Statistics (500 calls/day free)"""
    
    BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data"
    
    def get_employment_data(self, series_id: str) -> Optional[Dict]:
        """Get BLS employment data"""
        cached = self._get_cached_data("hr", "bls", series_id)
        if cached:
            return cached
        
        try:
            # BLS doesn't require API key for public data
            payload = {
                "seriesid": [series_id],
                "startyear": "2020",
                "endyear": "2024"
            }
            
            response = self.session.post(self.BASE_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "REQUEST_SUCCEEDED":
                self._cache_data("hr", "bls", series_id, data)
                return data
            
            return None
        except Exception as e:
            logger.error(f"Error fetching BLS data: {e}")
            return None

