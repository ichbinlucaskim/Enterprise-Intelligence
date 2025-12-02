# Enterprise Risk Radar Dashboard - API Documentation

Complete API reference for the Enterprise Risk Radar Dashboard backend.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production use, implement authentication middleware.

## Endpoints

### Health Check

#### GET `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Risk Data

#### GET `/api/risk/radar`

Get complete risk radar data for all categories.

**Response:**
```json
{
  "market_risk": {
    "category": "market",
    "score": 45.5,
    "raw_data": {
      "stock_change": -2.3,
      "gdp_growth": 2.1,
      "unemployment": 3.7
    },
    "calculated_at": "2024-01-15T10:30:00"
  },
  "supply_chain_risk": {
    "category": "supply_chain",
    "score": 52.3,
    "raw_data": {
      "news_articles": 15,
      "recent_news": [...]
    },
    "calculated_at": "2024-01-15T10:30:00"
  },
  "regulatory_risk": {
    "category": "regulatory",
    "score": 38.2,
    "raw_data": {
      "revenue_volatility": 0.12,
      "filing_count": 8
    },
    "calculated_at": "2024-01-15T10:30:00"
  },
  "hr_risk": {
    "category": "hr",
    "score": 41.8,
    "raw_data": {
      "unemployment_rate": 3.7,
      "unemployment_change": 0.1
    },
    "calculated_at": "2024-01-15T10:30:00"
  },
  "overall_risk": 44.45,
  "last_updated": "2024-01-15T10:30:00"
}
```

**Risk Score Range:** 0-100
- 0-33: Low Risk (Green)
- 34-66: Medium Risk (Yellow)
- 67-100: High Risk (Red)

---

#### GET `/api/risk/{category}`

Get risk score for a specific category.

**Parameters:**
- `category` (path): One of `market`, `supply_chain`, `regulatory`, `hr`

**Example:**
```
GET /api/risk/market
```

**Response:**
```json
{
  "category": "market",
  "score": 45.5,
  "raw_data": {
    "stock_change": -2.3,
    "gdp_growth": 2.1,
    "unemployment": 3.7
  },
  "calculated_at": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `400`: Invalid category
- `500`: Internal server error

---

### Monte Carlo Simulations

#### POST `/api/monte-carlo/simulate`

Run Monte Carlo simulation for a risk category.

**Request Body:**
```json
{
  "risk_category": "market",
  "iterations": 5000,
  "use_cached_data": true
}
```

**Parameters:**
- `risk_category` (required): One of `market`, `supply_chain`, `regulatory`, `hr`
- `iterations` (optional): Number of simulations (100-100000, default: 5000)
- `use_cached_data` (optional): Use cached historical data (default: true)

**Response:**
```json
{
  "risk_category": "market",
  "mean": 45.2,
  "std": 12.5,
  "percentiles": {
    "5": 25.3,
    "50": 45.1,
    "95": 65.8
  },
  "iterations": 5000,
  "calculated_at": "2024-01-15T10:35:00"
}
```

**Percentiles Explanation:**
- `5`: 5th percentile (optimistic scenario)
- `50`: Median (most likely scenario)
- `95`: 95th percentile (pessimistic scenario)

**Error Responses:**
- `400`: Invalid category or parameters
- `500`: Simulation error

---

#### GET `/api/monte-carlo/scenarios/{category}`

Get multiple scenario simulations (optimistic, baseline, pessimistic).

**Parameters:**
- `category` (path): One of `market`, `supply_chain`, `regulatory`, `hr`

**Example:**
```
GET /api/monte-carlo/scenarios/market
```

**Response:**
```json
{
  "risk_category": "market",
  "scenarios": {
    "optimistic": {
      "mean": 30.5,
      "std": 5.2,
      "percentiles": {
        "5": 22.1,
        "50": 30.3,
        "95": 38.9
      }
    },
    "baseline": {
      "mean": 50.2,
      "std": 10.1,
      "percentiles": {
        "5": 33.6,
        "50": 50.0,
        "95": 66.8
      }
    },
    "pessimistic": {
      "mean": 70.8,
      "std": 15.3,
      "percentiles": {
        "5": 45.6,
        "50": 70.5,
        "95": 95.2
      }
    }
  },
  "calculated_at": "2024-01-15T10:40:00"
}
```

---

### Data Management

#### POST `/api/data/refresh`

Trigger background data refresh from APIs.

**Request Body:**
```json
{
  "data_types": ["market", "supply_chain"]
}
```

**Parameters:**
- `data_types` (optional): Array of data types to refresh. If `null` or omitted, refreshes all types.
  - Valid values: `market`, `supply_chain`, `regulatory`, `hr`

**Response:**
```json
{
  "refreshed_types": ["market", "supply_chain", "regulatory", "hr"],
  "success": true,
  "message": "Data refresh initiated in background",
  "refreshed_at": "2024-01-15T10:45:00"
}
```

**Note:** This endpoint returns immediately. Data refresh happens in the background. Wait a few seconds before querying risk data.

---

#### GET `/api/data/status`

Get status of cached data (freshness, expiry).

**Response:**
```json
{
  "status": {
    "market": {
      "sources": ["alpha_vantage", "fred"],
      "total_entries": 5,
      "expired_entries": 0
    },
    "supply_chain": {
      "sources": ["newsapi"],
      "total_entries": 3,
      "expired_entries": 1
    },
    "regulatory": {
      "sources": ["sec"],
      "total_entries": 2,
      "expired_entries": 0
    },
    "hr": {
      "sources": ["bls"],
      "total_entries": 1,
      "expired_entries": 0
    }
  },
  "checked_at": "2024-01-15T10:50:00"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid category. Must be one of: market, supply_chain, regulatory, hr"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error message]"
}
```

## Rate Limiting

Currently, no rate limiting is implemented on the API. However, the underlying data sources have rate limits:

- **Alpha Vantage**: 25 calls/day
- **NewsAPI**: 100 requests/day
- **BLS**: 500 calls/day
- **FRED**: Unlimited
- **SEC**: Unlimited

The system uses caching to minimize API calls. Data is cached for 24 hours by default.

## Data Caching

All API responses from external sources are cached in the database:
- Cache expiry: 24 hours (configurable)
- Cache is checked before making external API calls
- Expired cache entries are automatically refreshed

## Interactive API Documentation

When the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation where you can test endpoints directly.

## Example Usage

### Using cURL

```bash
# Get risk radar
curl http://localhost:8000/api/risk/radar

# Get market risk
curl http://localhost:8000/api/risk/market

# Run Monte Carlo simulation
curl -X POST http://localhost:8000/api/monte-carlo/simulate \
  -H "Content-Type: application/json" \
  -d '{"risk_category": "market", "iterations": 5000}'

# Refresh data
curl -X POST http://localhost:8000/api/data/refresh \
  -H "Content-Type: application/json" \
  -d '{"data_types": null}'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Get risk radar
response = requests.get(f"{BASE_URL}/api/risk/radar")
data = response.json()
print(f"Overall Risk: {data['overall_risk']}")

# Run simulation
response = requests.post(
    f"{BASE_URL}/api/monte-carlo/simulate",
    json={"risk_category": "market", "iterations": 5000}
)
simulation = response.json()
print(f"Mean: {simulation['mean']}, 95th Percentile: {simulation['percentiles']['95']}")
```

### Using JavaScript

```javascript
const API_BASE = 'http://localhost:8000';

// Get risk radar
fetch(`${API_BASE}/api/risk/radar`)
  .then(res => res.json())
  .then(data => console.log('Overall Risk:', data.overall_risk));

// Run simulation
fetch(`${API_BASE}/api/monte-carlo/simulate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    risk_category: 'market',
    iterations: 5000
  })
})
  .then(res => res.json())
  .then(data => console.log('Simulation Results:', data));
```

## Version

Current API version: **1.0.0**

## Support

For issues or questions:
1. Check the interactive documentation at `/docs`
2. Review the main README.md
3. Check backend logs for detailed error messages

