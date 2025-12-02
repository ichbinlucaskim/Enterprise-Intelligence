# Quick Start Guide

Get the Enterprise Risk Radar Dashboard running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed

## Step 1: Backend (2 minutes)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python run.py
```

Backend runs on http://localhost:8000

## Step 2: Frontend (2 minutes)

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000

## Step 3: Configure API Keys (1 minute)

1. Edit `backend/.env` (create from `.env.example` if needed)
2. Add your API keys (optional - system works with defaults):
   - Alpha Vantage: https://www.alphavantage.co/support/#api-key
   - FRED: https://fred.stlouisfed.org/docs/api/api_key.html
   - NewsAPI: https://newsapi.org/register

## Step 4: View Dashboard

Open http://localhost:3000 in your browser!

## That's It!

The dashboard will:
- Show default risk scores initially
- Use cached data when available
- Work even without API keys (with limited functionality)

For detailed setup, see [SETUP_GUIDE.md](./SETUP_GUIDE.md)

