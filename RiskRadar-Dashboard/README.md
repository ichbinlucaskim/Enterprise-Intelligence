# Enterprise Risk Radar Dashboard

A comprehensive enterprise risk monitoring dashboard that aggregates risk data from multiple free APIs, performs Monte Carlo simulations, and provides executive-level visualizations.

## Overview

This dashboard provides unified risk visualizations across four key categories:
- **Market Risk**: Stock volatility, economic indicators (GDP, unemployment)
- **Supply Chain Risk**: News sentiment analysis, disruption alerts
- **Regulatory Risk**: SEC filings analysis, compliance monitoring
- **HR Risk**: Labor market data, employment trends

The system is designed to work with free API tiers, using intelligent caching to respect rate limits while maintaining functionality.

## Features

- **Unified Risk Radar**: Single-screen visualization of all risk categories
- **Monte Carlo Simulations**: Forecast risk distributions using historical data
- **Real-time Data Refresh**: Background data updates from multiple APIs
- **Intelligent Caching**: Respects API rate limits while maintaining data freshness
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **NumPy/SciPy**: Monte Carlo simulations and data processing
- **SQLite**: Lightweight database (easily upgradeable to PostgreSQL)

### Frontend
- **React 18**: Modern UI framework
- **Recharts**: Beautiful, responsive charts
- **Vite**: Fast build tool and dev server

### Data Sources (Free APIs)
- **Alpha Vantage**: Stock market data (25 calls/day)
- **FRED**: Economic indicators (unlimited)
- **SEC EDGAR**: Regulatory filings (unlimited)
- **NewsAPI**: News sentiment (100 requests/day)
- **BLS**: Labor statistics (500 calls/day)

## Project Structure

```
RiskRadar-Dashboard/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── database.py     # Database models
│   │   ├── models.py       # Pydantic models
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Free API keys (see Setup section)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. Initialize database:
```bash
python -c "from app.database import init_db; init_db()"
```

6. Run the server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## API Keys Setup

### Required API Keys

1. **Alpha Vantage** (Optional but recommended)
   - Sign up at: https://www.alphavantage.co/support/#api-key
   - Free tier: 25 API calls per day
   - Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key`

2. **FRED** (Optional but recommended)
   - Sign up at: https://fred.stlouisfed.org/docs/api/api_key.html
   - Free tier: Unlimited calls
   - Add to `.env`: `FRED_API_KEY=your_key`

3. **NewsAPI** (Optional)
   - Sign up at: https://newsapi.org/register
   - Free tier: 100 requests/day, 24-hour delay
   - Add to `.env`: `NEWS_API_KEY=your_key`

4. **BLS** (No key required)
   - Public API, no registration needed
   - Free tier: 500 calls/day

5. **SEC EDGAR** (No key required)
   - Public API, no registration needed
   - Unlimited access

### Note on Rate Limits

The system uses intelligent caching to respect API rate limits:
- Data is cached for 24 hours by default
- Cache expiry can be configured in `.env`
- Background refresh avoids blocking requests
- System works with default values if APIs are unavailable

## API Endpoints

### Risk Data
- `GET /api/risk/radar` - Get complete risk radar data
- `GET /api/risk/{category}` - Get risk for specific category

### Monte Carlo
- `POST /api/monte-carlo/simulate` - Run Monte Carlo simulation
- `GET /api/monte-carlo/scenarios/{category}` - Get scenario simulations

### Data Management
- `POST /api/data/refresh` - Trigger data refresh
- `GET /api/data/status` - Get cache status

Full API documentation available at `/docs` when server is running.

## Configuration

### Environment Variables

Edit `backend/.env`:

```env
# API Keys
ALPHA_VANTAGE_API_KEY=your_key
FRED_API_KEY=your_key
NEWS_API_KEY=your_key

# Database
DATABASE_URL=sqlite:///./risk_data.db

# Cache Settings
CACHE_EXPIRY_HOURS=24
DATA_REFRESH_INTERVAL_HOURS=24

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Deployment

### Local Development
Both backend and frontend can run locally as described in Quick Start.

### Production Deployment

#### Option 1: Docker (Recommended)

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

#### Option 2: Heroku Free Tier

**Backend:**
```bash
cd backend
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set ALPHA_VANTAGE_API_KEY=your_key
# ... set other keys
git push heroku main
```

**Frontend:**
```bash
cd frontend
npm run build
# Deploy dist/ folder to static hosting
```

#### Option 3: VPS/Cloud Server

1. Install Python, Node.js, and PostgreSQL
2. Set up reverse proxy (Nginx)
3. Use systemd for process management
4. Configure SSL certificates

## Usage

### Dashboard Features

1. **Risk Radar Chart**: Central visualization showing all risk categories
2. **Risk Gauges**: Individual category breakdowns with progress bars
3. **Monte Carlo Panel**: Run simulations to forecast risk distributions
4. **Data Refresh**: Manually trigger data updates from APIs

### Running Simulations

1. Select a risk category (Market, Supply Chain, Regulatory, HR)
2. Set number of iterations (default: 5000)
3. Click "Run Simulation"
4. View results including mean, standard deviation, and percentiles

### Understanding Risk Scores

- **0-33**: Low Risk (Green)
- **34-66**: Medium Risk (Yellow)
- **67-100**: High Risk (Red)

Scores are calculated from multiple data sources and normalized to 0-100 scale.

## Limitations and Considerations

### Free Tier Limitations

1. **Rate Limits**: 
   - Alpha Vantage: 25 calls/day
   - NewsAPI: 100 requests/day with 24-hour delay
   - BLS: 500 calls/day

2. **Data Freshness**:
   - Some APIs have delays (NewsAPI: 24 hours)
   - Caching reduces real-time accuracy but ensures availability

3. **Historical Data**:
   - Limited historical depth on free tiers
   - FRED provides longer time series

### Scaling Considerations

For production use with higher traffic:
- Upgrade to paid API tiers
- Implement Redis for distributed caching
- Use PostgreSQL instead of SQLite
- Add authentication and authorization
- Implement rate limiting on API endpoints

## Troubleshooting

### Backend Issues

**Database errors:**
```bash
# Reinitialize database
python -c "from app.database import init_db; init_db()"
```

**API key errors:**
- Check `.env` file exists and has correct keys
- Verify API keys are valid
- Check API service status

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
- Verify backend is running on port 8000
- Check CORS settings in backend
- Verify API_BASE_URL in frontend

## Development

### Adding New Data Sources

1. Create fetcher class in `app/services/data_fetchers.py`
2. Implement caching logic
3. Add to `RiskCalculator` in `app/services/risk_calculator.py`
4. Update API endpoints if needed

### Adding New Risk Categories

1. Add calculation method to `RiskCalculator`
2. Update `RiskRadarResponse` model
3. Add frontend visualization component
4. Update radar chart data

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the troubleshooting section
- Check API provider status pages

## Roadmap

- [ ] Add authentication and user management
- [ ] Implement alerting system
- [ ] Add export functionality (PDF, Excel)
- [ ] Enhance Monte Carlo with more distributions
- [ ] Add historical trend analysis
- [ ] Implement custom risk thresholds
- [ ] Add multi-company comparison
- [ ] Mobile app version

## Acknowledgments

- Alpha Vantage for stock market data
- FRED for economic indicators
- SEC for regulatory data access
- NewsAPI for news sentiment
- BLS for labor statistics

