# Architecture Overview

## System Architecture

The Enterprise Risk Radar Dashboard follows a modern microservices-inspired architecture with clear separation between backend API and frontend presentation layers.

```
┌─────────────────┐
│   React Frontend │
│   (Port 3000)    │
└────────┬─────────┘
         │ HTTP/REST
         │
┌────────▼─────────┐
│  FastAPI Backend │
│   (Port 8000)    │
└────────┬─────────┘
         │
    ┌────┴────┬──────────┬──────────┬──────────┐
    │         │          │          │          │
┌───▼───┐ ┌──▼───┐  ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│SQLite │ │Alpha │  │ FRED  │ │  SEC  │ │NewsAPI│
│  DB   │ │Vantage│  │       │ │ EDGAR │ │       │
└───────┘ └───────┘  └───────┘ └───────┘ └───────┘
```

## Component Breakdown

### Frontend Layer

**Technology:** React 18 + Vite + Recharts

**Components:**
- `App.jsx`: Main application container
- `RiskRadarChart.jsx`: Central radar visualization
- `RiskGauges.jsx`: Individual risk category displays
- `MonteCarloPanel.jsx`: Simulation interface
- `DataRefreshButton.jsx`: Manual data refresh trigger

**Key Features:**
- Responsive design (mobile-friendly)
- Real-time data updates
- Interactive charts
- Auto-refresh every 5 minutes

### Backend Layer

**Technology:** FastAPI + SQLAlchemy + NumPy

**Structure:**
```
app/
├── api/              # API endpoints
│   ├── risk.py      # Risk data endpoints
│   ├── monte_carlo.py # Simulation endpoints
│   └── data_refresh.py # Data management
├── services/         # Business logic
│   ├── data_fetchers.py # API integration
│   ├── risk_calculator.py # Risk scoring
│   └── monte_carlo.py # Simulation engine
├── database.py       # Database models
├── models.py         # Pydantic schemas
└── main.py          # Application entry
```

**Key Features:**
- RESTful API design
- Automatic API documentation (Swagger/ReDoc)
- Background task processing
- Intelligent caching

### Data Layer

**Database:** SQLite (prototype) / PostgreSQL (production-ready)

**Tables:**
- `risk_data_cache`: Cached API responses
- `risk_scores`: Calculated risk scores
- `monte_carlo_results`: Simulation results

**Caching Strategy:**
- 24-hour default expiry
- Automatic cache invalidation
- Background refresh to avoid blocking

### External APIs

**Data Sources:**
1. **Alpha Vantage** - Stock market data
   - Rate limit: 25 calls/day
   - Caching: 24 hours
   
2. **FRED** - Economic indicators
   - Rate limit: Unlimited
   - Caching: 24 hours
   
3. **SEC EDGAR** - Regulatory filings
   - Rate limit: Unlimited
   - Caching: 24 hours
   
4. **NewsAPI** - News sentiment
   - Rate limit: 100 requests/day
   - Caching: 24 hours
   - Note: 24-hour delay on free tier
   
5. **BLS** - Labor statistics
   - Rate limit: 500 calls/day
   - Caching: 24 hours

## Data Flow

### Risk Calculation Flow

```
1. User requests risk data
   ↓
2. Backend checks cache
   ↓
3a. Cache hit → Return cached data
3b. Cache miss → Fetch from APIs
   ↓
4. Calculate risk scores
   ↓
5. Store in database
   ↓
6. Return to frontend
```

### Monte Carlo Simulation Flow

```
1. User requests simulation
   ↓
2. Fetch historical risk scores
   ↓
3. Calculate mean and std
   ↓
4. Run NumPy simulations
   ↓
5. Calculate percentiles
   ↓
6. Store results
   ↓
7. Return to frontend
```

## Risk Calculation Logic

### Market Risk
- **Sources:** Stock volatility, GDP growth, unemployment
- **Formula:** Weighted combination of:
  - Stock price volatility (40%)
  - GDP growth trend (30%)
  - Unemployment rate (30%)
- **Normalization:** 0-100 scale

### Supply Chain Risk
- **Sources:** News sentiment, article count
- **Formula:** Base score + news impact
- **Normalization:** 0-100 scale

### Regulatory Risk
- **Sources:** SEC filings, revenue volatility
- **Formula:** Filing frequency + volatility analysis
- **Normalization:** 0-100 scale

### HR Risk
- **Sources:** BLS unemployment data
- **Formula:** Unemployment rate + trend
- **Normalization:** 0-100 scale

### Overall Risk
- **Formula:** Weighted average
  - Market: 30%
  - Supply Chain: 25%
  - Regulatory: 25%
  - HR: 20%

## Monte Carlo Simulation

**Method:** Normal distribution sampling

**Process:**
1. Extract historical risk scores
2. Calculate mean (μ) and standard deviation (σ)
3. Generate N random samples from N(μ, σ)
4. Clip values to [0, 100] range
5. Calculate statistics:
   - Mean
   - Standard deviation
   - Percentiles (5th, 50th, 95th)

**Assumptions:**
- Risk scores follow normal distribution
- Historical patterns predict future
- Independent risk categories

## Security Considerations

### Current State (Prototype)
- No authentication
- No authorization
- CORS configured for localhost
- API keys in environment variables

### Production Recommendations
- Implement JWT authentication
- Add role-based access control
- Use secrets management (AWS Secrets Manager, etc.)
- Enable HTTPS/TLS
- Implement rate limiting
- Add input validation and sanitization
- Regular security audits

## Scalability

### Current Limitations
- SQLite database (single file)
- No horizontal scaling
- Synchronous API calls
- Single server deployment

### Scaling Path
1. **Database:** Migrate to PostgreSQL
2. **Caching:** Add Redis for distributed cache
3. **API:** Implement async/await for concurrent requests
4. **Deployment:** Container orchestration (Kubernetes)
5. **Load Balancing:** Multiple backend instances
6. **CDN:** Static frontend assets

## Performance Optimizations

### Implemented
- Database query caching
- API response caching
- Background task processing
- Efficient NumPy operations

### Future Enhancements
- Redis caching layer
- Database query optimization
- API response compression
- Frontend code splitting
- Lazy loading of components

## Error Handling

### Strategy
- Graceful degradation (default values)
- Comprehensive logging
- User-friendly error messages
- Retry logic for API calls
- Fallback data sources

### Error Types
1. **API Errors:** Cached data or defaults
2. **Database Errors:** Logged, user notified
3. **Calculation Errors:** Default risk scores
4. **Network Errors:** Retry with exponential backoff

## Monitoring and Observability

### Current
- Application logs (file + console)
- Health check endpoint
- Cache status endpoint

### Recommended
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Metrics collection (Prometheus)
- Log aggregation (ELK stack)
- Uptime monitoring

## Deployment Architecture

### Development
```
Local Machine
├── Backend (Python venv)
└── Frontend (Vite dev server)
```

### Production (Recommended)
```
Load Balancer
├── Backend Instances (Docker containers)
│   ├── FastAPI app
│   └── PostgreSQL
├── Frontend (Static hosting / CDN)
└── Redis Cache
```

## Technology Choices Rationale

### Backend: FastAPI
- **Why:** Modern, fast, automatic docs
- **Alternatives considered:** Flask, Django
- **Decision:** FastAPI's async support and auto-docs

### Frontend: React
- **Why:** Industry standard, component-based
- **Alternatives considered:** Vue, Angular
- **Decision:** React's ecosystem and familiarity

### Database: SQLite → PostgreSQL
- **Why:** SQLite for prototyping, PostgreSQL for production
- **Decision:** Easy migration path, same SQLAlchemy ORM

### Charts: Recharts
- **Why:** React-native, responsive, customizable
- **Alternatives considered:** Chart.js, D3.js
- **Decision:** Better React integration

## Future Architecture Enhancements

1. **Microservices:** Split into risk calculation, data fetching, simulation services
2. **Event-Driven:** Message queue for async processing
3. **Real-time:** WebSocket for live updates
4. **Machine Learning:** Predictive risk models
5. **Multi-tenancy:** Support multiple organizations
6. **API Gateway:** Centralized API management

