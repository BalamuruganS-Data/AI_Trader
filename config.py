# Copy this file to config.py and fill in your own credentials.
# For cloud deployment, use environment variables instead of hardcoding here.
# Example: EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "your-email@example.com")

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "your-email@example.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-email-password")
EMAIL_RECIPIENTS = [e.strip() for e in os.getenv("EMAIL_RECIPIENTS", "recipient@example.com").split(",")]

WATCHLIST = os.getenv("WATCHLIST", "RELIANCE.NS,TCS.NS,HDFCBANK.NS,INFY.NS").split(",")

# Stock universe for dynamic screening (agent will scan these each morning and pick the best)
STOCK_UNIVERSE = [
    # Top 50 NSE liquid stocks - add or remove based on your preference
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "WIPRO.NS",
    "INFOSYS.NS", "ICICIBANK.NS", "SBIN.NS", "MARUTI.NS", "LT.NS",
    "BAJAJFINSV.NS", "HINDUNILVR.NS", "ITC.NS", "AXISBANK.NS", "SUNPHARMA.NS",
    "ASIANPAINT.NS", "KOTAKBANK.NS", "HCLTECH.NS", "TATASTEEL.NS", "COALINDIA.NS",
    "NTPC.NS", "POWERGRID.NS", "IOC.NS", "TATAMOTORS.NS", "JSWSTEEL.NS",
    "VEDL.NS", "CIPLA.NS", "BRITANNIA.NS", "NESTLEIND.NS", "EICHERMOT.NS",
    "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "BOSCHIND.NS", "DMART.NS", "ADANIPORTS.NS",
    "ADANIGREEN.NS", "ADANIENT.NS", "GAIL.NS", "BPCL.NS", "ULTRACEMCO.NS",
    "SHREECEM.NS", "SBICARD.NS", "INDIGO.NS", "SPICEJET.NS", "GODFREY.NS",
    "PAGEIND.NS", "KAJARIACER.NS", "BATAINDIA.NS", "COLPAL.NS", "GSKCONS.NS",
]

# Screener settings: how many of the best stocks to trade each day
SCREENER_MIN_STOCKS = 3  # minimum stocks to trade (if market has good setups)
SCREENER_MAX_STOCKS = 10  # maximum stocks to trade (prevents over-allocation)

MAX_RISK_PERCENT = float(os.getenv("MAX_RISK_PERCENT", 0.5))
MIN_RSI = int(os.getenv("MIN_RSI", 35))
MAX_RSI = int(os.getenv("MAX_RSI", 75))
ATR_MULTIPLIER = float(os.getenv("ATR_MULTIPLIER", 1.2))
TARGET_MULTIPLIER = float(os.getenv("TARGET_MULTIPLIER", 1.8))
LIVE_TRADING = os.getenv("LIVE_TRADING", "False").lower() == "true"
START_HOUR = int(os.getenv("START_HOUR", 9))
END_HOUR = int(os.getenv("END_HOUR", 15))
DATA_INTERVAL = os.getenv("DATA_INTERVAL", "5m")
DATA_PERIOD = os.getenv("DATA_PERIOD", "2d")
DEFAULT_CAPITAL = float(os.getenv("DEFAULT_CAPITAL", 100000.0))
SIMULATED_BALANCE = float(os.getenv("SIMULATED_BALANCE", 100000.0))
MAX_DAILY_ALLOCATION = float(os.getenv("MAX_DAILY_ALLOCATION", 0.25))
ASK_DAILY_TRADE_AMOUNT = os.getenv("ASK_DAILY_TRADE_AMOUNT", "True").lower() == "true"
DAILY_TRADE_AMOUNT = None
TRADE_LOG_FILE = "trade_log.csv"

BROKER = {
    "provider": os.getenv("BROKER_PROVIDER", "none"),
    "api_key": os.getenv("BROKER_API_KEY", ""),
    "api_secret": os.getenv("BROKER_API_SECRET", ""),
    "access_token": os.getenv("BROKER_ACCESS_TOKEN", ""),
    "access_token_secret": os.getenv("BROKER_ACCESS_TOKEN_SECRET", ""),
    "user_id": os.getenv("BROKER_USER_ID", ""),
}

