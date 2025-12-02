"""
Helper script to create .env file from template
"""

import os

env_template = """# API Keys (Get free keys from respective providers)
# Alpha Vantage: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# FRED: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=your_fred_key_here

# NewsAPI: https://newsapi.org/register
NEWS_API_KEY=your_newsapi_key_here

# Database
DATABASE_URL=sqlite:///./risk_data.db

# Cache Settings
CACHE_EXPIRY_HOURS=24
DATA_REFRESH_INTERVAL_HOURS=24

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
"""

if __name__ == "__main__":
    env_path = ".env"
    
    if os.path.exists(env_path):
        response = input(".env file already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            exit(0)
    
    with open(env_path, 'w') as f:
        f.write(env_template)
    
    print(f".env file created at {os.path.abspath(env_path)}")
    print("\nNext steps:")
    print("1. Edit .env and add your API keys")
    print("2. API keys are optional - system works with defaults")
    print("3. See SETUP_GUIDE.md for where to get API keys")

