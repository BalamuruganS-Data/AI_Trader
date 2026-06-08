import yfinance as yf


def fetch_intraday_data(ticker: str, interval: str = "5m", period: str = "2d"):
    """Fetch recent intraday data for an NSE ticker."""
    data = yf.download(tickers=ticker, period=period, interval=interval, progress=False)
    if data.empty:
        raise ValueError(f"No data returned for {ticker}. Check ticker symbol and data source.")
    return data.dropna()
