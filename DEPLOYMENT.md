# Cloud Deployment Guide

This app is ready to deploy to cloud platforms. Choose one below:

## Option 1: Render.com (Recommended)

**Why**: Easiest setup, free tier available, native Python support.

### Steps:
1. Sign up at [render.com](https://render.com)
2. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/ai-trader.git
   git push -u origin main
   ```
3. In Render dashboard, click **New → Web Service**
4. Connect your GitHub repo
5. Fill in:
   - **Name**: `ai-trader` (or any name)
   - **Runtime**: Python 3.10
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:app`
6. Click **Advanced** and add **Environment Variables**:
   ```
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=your-app-specific-password
   EMAIL_RECIPIENTS=recipient@gmail.com
   BROKER_PROVIDER=none
   LIVE_TRADING=False
   ```
7. Deploy and wait for it to finish (~2 minutes)
8. Visit your app at: `https://ai-trader.onrender.com`

## Option 2: Heroku

**Why**: Well-known platform, simple CLI commands.

### Steps:
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. In your project directory:
   ```bash
   heroku login
   heroku create your-app-name
   ```
3. Set environment variables:
   ```bash
   heroku config:set EMAIL_USERNAME=your-email@gmail.com
   heroku config:set EMAIL_PASSWORD=your-app-password
   heroku config:set EMAIL_RECIPIENTS=recipient@gmail.com
   heroku config:set BROKER_PROVIDER=none
   heroku config:set LIVE_TRADING=False
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```
5. Visit: `https://your-app-name.herokuapp.com`

## Option 3: PythonAnywhere

**Why**: Python-specific, simple file upload.

### Steps:
1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Go to **Files** tab and upload your project
3. Go to **Web** tab → **Add a new web app**
4. Choose **Flask** and **Python 3.x**
5. Configure the WSGI file to point to `app.py`
6. Go to **Web** tab → **Environment variables** and add:
   ```
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_RECIPIENTS=recipient@gmail.com
   ```
7. Reload the web app
8. Visit: `https://yourusername.pythonanywhere.com`

## Environment Variables for All Platforms

Set these on your cloud platform (do NOT hardcode in config.py):

| Variable | Example | Required |
|----------|---------|----------|
| EMAIL_USERNAME | your-email@gmail.com | Yes |
| EMAIL_PASSWORD | your-app-specific-password | Yes |
| EMAIL_RECIPIENTS | recipient1@gmail.com,recipient2@gmail.com | Yes |
| BROKER_PROVIDER | none, kite, or upstox | No (defaults to none) |
| BROKER_API_KEY | Your Kite/Upstox key | No |
| BROKER_API_SECRET | Your Kite/Upstox secret | No |
| BROKER_ACCESS_TOKEN | Your access token | No |
| LIVE_TRADING | False or True | No (defaults to False) |
| WATCHLIST | RELIANCE.NS,TCS.NS,HDFCBANK.NS,INFY.NS | No |

## Running Daily Tasks on Cloud

Once deployed, you may want to automatically run the end-of-day summary at market close.

### Render.com: Use Background Workers
1. Create a `worker.py` that runs `trader/end_of_day.py` on a schedule
2. Update `render.yaml` with a background worker service

### Heroku: Use Heroku Scheduler
1. Add the **Heroku Scheduler** add-on
2. Create a job: `python trader/end_of_day.py`
3. Set it to run daily at 3:30 PM IST

### PythonAnywhere: Use Always-on Tasks
1. Go to **Tasks** and add a new task
2. Command: `python trader/end_of_day.py`
3. Schedule it for daily execution

## Security Notes

- **Never commit `.env` or `config.py` to GitHub** (already in .gitignore)
- **Use Gmail app-specific passwords**, not your account password
- **Rotate broker tokens** regularly
- **Test with `LIVE_TRADING=False` first** before enabling live trading
- **Monitor trade logs** for suspicious activity

## Troubleshooting

**App won't start?**
- Check logs: `heroku logs --tail` (Heroku) or check dashboard logs (Render)
- Ensure all required env vars are set
- Run `pip install -r requirements.txt` locally to check for dependency issues

**Emails not sending?**
- Verify EMAIL_USERNAME and EMAIL_PASSWORD are correct
- For Gmail: use an app-specific password, not your account password
- Enable "Less secure app access" if using regular Gmail password

**No trades executing?**
- Check your watchlist symbols (NSE format: SYMBOL.NS)
- Verify market is open (IST 9:15 AM - 3:30 PM, Monday-Friday)
- Check the app logs for analysis output

## Next Steps

1. Deploy to Render or Heroku
2. Set up automated daily tasks (optional)
3. Monitor the app and trade logs
4. Once confident, set `LIVE_TRADING=True` and add real broker credentials
