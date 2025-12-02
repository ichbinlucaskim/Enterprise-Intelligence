# Enterprise Risk Radar Dashboard - Setup Guide

This guide provides step-by-step instructions for setting up the Enterprise Risk Radar Dashboard from scratch.

## Prerequisites Checklist

- [ ] Python 3.9 or higher installed
- [ ] Node.js 18 or higher installed
- [ ] Git installed
- [ ] Text editor or IDE
- [ ] Internet connection for API access

## Step 1: Clone or Navigate to Project

If you have the project in a repository:
```bash
git clone <repository-url>
cd Enterprise-Intelligence/RiskRadar-Dashboard
```

Or navigate to the project directory if already available.

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI and Uvicorn (web server)
- SQLAlchemy (database ORM)
- NumPy, Pandas, SciPy (data processing)
- Requests (HTTP client)
- Other required packages

### 2.3 Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your preferred text editor:

```env
# API Keys - Get these from respective providers (see below)
ALPHA_VANTAGE_API_KEY=your_key_here
FRED_API_KEY=your_key_here
NEWS_API_KEY=your_key_here

# Database (SQLite by default, no changes needed)
DATABASE_URL=sqlite:///./risk_data.db

# Cache Settings (24 hours default)
CACHE_EXPIRY_HOURS=24
DATA_REFRESH_INTERVAL_HOURS=24

# Server Settings
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 2.4 Get API Keys

#### Alpha Vantage (Optional but Recommended)
1. Visit: https://www.alphavantage.co/support/#api-key
2. Fill out the form (name, email)
3. Copy the API key
4. Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key`

**Note:** Free tier allows 25 calls per day. The system caches data to work within this limit.

#### FRED (Recommended)
1. Visit: https://fred.stlouisfed.org/docs/api/api_key.html
2. Sign up for a free account
3. Generate an API key
4. Add to `.env`: `FRED_API_KEY=your_key`

**Note:** FRED has unlimited free access - no rate limits!

#### NewsAPI (Optional)
1. Visit: https://newsapi.org/register
2. Sign up with email
3. Copy the API key from dashboard
4. Add to `.env`: `NEWS_API_KEY=your_key`

**Note:** Free tier: 100 requests/day with 24-hour delay on news articles.

#### BLS and SEC (No Keys Required)
- BLS: Public API, no registration needed
- SEC EDGAR: Public API, no registration needed

### 2.5 Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

This creates the SQLite database file (`risk_data.db`) with required tables.

### 2.6 Test Backend

```bash
python run.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Open your browser and visit:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

If you see JSON responses, the backend is working!

**Stop the server** with `Ctrl+C` when done testing.

## Step 3: Frontend Setup

### 3.1 Install Dependencies

Open a **new terminal window** (keep backend terminal running or start it later):

```bash
cd frontend
npm install
```

This installs:
- React and React DOM
- Recharts (charting library)
- Axios (HTTP client)
- Vite (build tool)
- Other dependencies

### 3.2 Configure API URL (Optional)

If your backend runs on a different URL, create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

Default is `http://localhost:8000`, so this is usually not needed.

### 3.3 Start Frontend

```bash
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
```

## Step 4: Verify Installation

### 4.1 Check Backend

1. Visit http://localhost:8000/docs
2. You should see FastAPI interactive documentation
3. Try the `/health` endpoint - should return `{"status": "healthy"}`

### 4.2 Check Frontend

1. Visit http://localhost:3000
2. You should see the dashboard interface
3. It may show loading or default data initially

### 4.3 Test Data Fetching

1. In the dashboard, click "Refresh Data"
2. Wait a few seconds
3. Risk scores should appear (may be default values if APIs aren't configured)

## Step 5: First Data Refresh

### 5.1 Using Dashboard

1. Click "Refresh Data" button in the dashboard
2. Wait for background processing
3. Data will appear automatically

### 5.2 Using API Directly

```bash
curl -X POST http://localhost:8000/api/data/refresh \
  -H "Content-Type: application/json" \
  -d '{"data_types": null}'
```

### 5.3 Check Data Status

```bash
curl http://localhost:8000/api/data/status
```

This shows cache status and data freshness.

## Common Issues and Solutions

### Issue: "Module not found" errors

**Solution:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Issue: Port already in use

**Solution:**
- Backend: Change `PORT=8000` to another port in `.env`
- Frontend: Change port in `vite.config.js` or use `npm run dev -- --port 3001`

### Issue: API keys not working

**Solution:**
1. Verify keys are correct in `.env` file
2. Check for extra spaces or quotes
3. Restart backend after changing `.env`
4. Test API keys directly with curl or Postman

### Issue: Database errors

**Solution:**
```bash
cd backend
rm risk_data.db  # Delete old database
python -c "from app.database import init_db; init_db()"  # Recreate
```

### Issue: CORS errors in browser

**Solution:**
1. Check `CORS_ORIGINS` in backend `.env`
2. Ensure frontend URL matches (http://localhost:3000)
3. Restart backend after changes

### Issue: No data showing

**Solution:**
1. Check browser console for errors (F12)
2. Verify backend is running
3. Check API keys are set
4. Try manual refresh
5. Check `/api/data/status` endpoint

## Next Steps

1. **Explore the Dashboard:**
   - View risk radar chart
   - Check individual risk gauges
   - Run Monte Carlo simulations

2. **Customize Settings:**
   - Adjust cache expiry times
   - Change risk calculation weights
   - Add custom risk categories

3. **Monitor API Usage:**
   - Check cache status regularly
   - Monitor rate limit compliance
   - Upgrade to paid tiers if needed

4. **Production Deployment:**
   - Review deployment section in README.md
   - Set up proper authentication
   - Configure production database

## Getting Help

1. Check the main README.md for detailed documentation
2. Review API documentation at http://localhost:8000/docs
3. Check browser console and backend logs for errors
4. Verify API provider status pages

## Production Checklist

Before deploying to production:

- [ ] All API keys are set and valid
- [ ] Database is properly configured
- [ ] CORS origins are restricted to production domains
- [ ] Environment variables are secure
- [ ] Error logging is configured
- [ ] Rate limiting is implemented
- [ ] Authentication is added (if needed)
- [ ] SSL/TLS certificates are configured
- [ ] Backup strategy is in place

## Support

For additional help:
- Review troubleshooting section in README.md
- Check API provider documentation
- Review FastAPI and React documentation

