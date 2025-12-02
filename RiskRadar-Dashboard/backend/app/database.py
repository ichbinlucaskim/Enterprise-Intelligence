"""
Database configuration and initialization
Uses SQLite for prototyping, easily upgradeable to PostgreSQL
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./risk_data.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class RiskDataCache(Base):
    """Cache table for risk data from various APIs"""
    __tablename__ = "risk_data_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String, index=True)  # e.g., "market", "supply_chain", "regulatory", "hr"
    source = Column(String)  # e.g., "alpha_vantage", "fred", "sec"
    symbol = Column(String, index=True)  # e.g., stock ticker, indicator code
    data = Column(JSON)  # Cached API response
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, index=True)


class RiskScore(Base):
    """Stored risk scores for dashboard display"""
    __tablename__ = "risk_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_category = Column(String, index=True)  # market, supply_chain, regulatory, hr
    score = Column(Float)  # Normalized score 0-100
    raw_data = Column(JSON)  # Source data used for calculation
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)


class MonteCarloResult(Base):
    """Cached Monte Carlo simulation results"""
    __tablename__ = "monte_carlo_results"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_category = Column(String, index=True)
    mean = Column(Float)
    std = Column(Float)
    percentiles = Column(JSON)  # {5: value, 50: value, 95: value}
    iterations = Column(Integer)
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

