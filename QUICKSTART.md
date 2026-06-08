# Quick Start: Indian Intraday AI Trader

## 1. Prepare the workspace
1. Open the folder `e:\Documents\AI Trader Agent` in VS Code.
2. Confirm these files exist:
   - `requirements.txt`
   - `config_example.py`
   - `trader/main.py`
   - `app.py`
   - `templates/index.html`

## 2. Create a Python environment
1. Open a terminal in VS Code.
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
3. Activate it:
   ```powershell
   .\.venv\Scripts\Activate
   ```

## 3. Install dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Create your config file
1. Copy the example config:
   ```powershell
   copy config_example.py config.py
   ```
2. Open `config.py` and set:
   - `EMAIL_USERNAME` to your email address
   - `EMAIL_PASSWORD` to your email password or app-specific password
   - `EMAIL_RECIPIENTS` to the list of recipient emails
   - `BROKER["provider"]` to `none`, `kite`, or `upstox`
   - `BROKER["api_key"]`, `BROKER["api_secret"]`, and `BROKER["access_token"]` as needed
   - Keep `LIVE_TRADING = False` until you finish dry testing

## 5. Run the app for an interactive experience

The app uses **dynamic stock screening**: each morning it scans 50+ NSE stocks, finds the ones with the strongest technical setups, and automatically trades them. You don't need to manually select which stocks to trade—the agent does it for you!

1. Run the web dashboard app:
   ```powershell
   python app.py
   ```
2. Open your browser to:
   - `http://localhost:5000`
3. The dashboard provides an end-to-end app experience where you can:
   - view broker status and available balance
   - **click "Run screener & trade"** to scan the market and execute trades on the best stocks found
   - enter or override the daily allocation amount
   - review which stocks passed the screener and were traded
   - send an end-of-day summary email with results

## How the screener works

Each time you click **"Run screener & trade"**:
1. The agent scans 50+ NSE stocks from its universe
2. For each stock, it analyzes:
   - **EMA crossover** (9-period above 20-period = uptrend)
   - **MACD momentum** (bullish crossover = acceleration)
   - **RSI** (safe entry zone, 35-75)
   - **ATR volatility** (measures risk for stop loss sizing)
3. Selects the **top 3-10 stocks** with the strongest technical setups
4. Trades them with your allocated capital
5. Automatically sets stop loss and profit targets
6. Sends email alert with results

You can customize:
- `STOCK_UNIVERSE` in `config.py` — change which stocks to scan
- `SCREENER_MIN_STOCKS` / `SCREENER_MAX_STOCKS` — control how many to trade
- `MIN_RSI` / `MAX_RSI` — tune entry filters
- `TARGET_MULTIPLIER` — control profit target size

## 7. End-of-day summary
1. After market close, the system can automatically send an email with:
   - List of all trades executed
   - Entry, exit, profit/loss for each trade
   - Total P/L for the day
   
2. Either:
   - Click **"Send summary email"** in the web dashboard, or
   - Run from CLI:
   ```powershell
   python trader/end_of_day.py
   ```

## 8. Deploy to the cloud (public web app)

To access the app from anywhere without running it locally, deploy to a cloud platform:

### Option A: Deploy to Render.com (recommended, easiest)
1. Sign up at [render.com](https://render.com)
2. Push your project to GitHub
3. Click **New → Web Service** and connect your GitHub repo
4. Set runtime to **Python 3.10+**
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app`
7. Add environment variables under **Environment** (see step 9 below)
8. Deploy and get your public URL (e.g., `https://my-trader.onrender.com`)

### Option B: Deploy to Heroku
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. In your project directory:
   ```powershell
   heroku login
   heroku create my-trader-app
   ```
3. Set environment variables:
   ```powershell
   heroku config:set EMAIL_USERNAME=your-email@gmail.com
   heroku config:set EMAIL_PASSWORD=your-app-password
   ```
4. Deploy:
   ```powershell
   git push heroku main
   ```
5. Access at `https://my-trader-app.herokuapp.com`

### Option C: Deploy to PythonAnywhere
1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your project files via **Files**
3. Create a new **Web app** → Python **Flask**
4. Point to `app.py` and configure WSGI
5. Set environment variables in the **Web** tab
6. Access at `https://yourusername.pythonanywhere.com`

## 9. Configure environment variables for cloud deployment

Whether local or cloud, set these variables using your cloud platform's environment settings:

```
EMAIL_USERNAME = your-email@gmail.com
EMAIL_PASSWORD = your-app-specific-password (not your Gmail password)
EMAIL_RECIPIENTS = recipient@gmail.com,other@gmail.com
BROKER_PROVIDER = none (or kite, upstox)
BROKER_API_KEY = (if using Kite or Upstox)
BROKER_API_SECRET = (if using Kite or Upstox)
LIVE_TRADING = False (until tested)
```

For local testing before cloud deployment, create a `.env` file in your project folder with these values, then the app will load them automatically.

## 10. Moving to live trading

1. When you are ready and tested the system:
   - set `LIVE_TRADING = True` in `config.py` or environment variable
2. Verify your broker credentials and access token.
3. Run again during market hours.
4. Always test carefully and use paper mode first.

## 11. Common settings
- `WATCHLIST`: symbols to scan
- `MAX_RISK_PERCENT`: percent of allocation risk per trade
- `MAX_DAILY_ALLOCATION`: fraction of balance to use per day
- `ASK_DAILY_TRADE_AMOUNT`: whether to prompt for allocation
- `DAILY_TRADE_AMOUNT`: fixed daily allocation if you want no interactive prompt

## 12. Notes
- This project is a prototype, not a full production trading system.
- A real Zerodha or Upstox token flow is required before live trading.
- Always verify emails, logs, and broker connectivity before risking money.
- Use `EMAIL_PASSWORD` as your Gmail app-specific password, not your account password.
- Cloud deployments are read-only by default; for persistent trade logs, consider adding cloud storage (AWS S3, Firebase, etc.).
