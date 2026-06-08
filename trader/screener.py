import logging
from typing import Dict, List, Optional

from trader.data_provider import fetch_intraday_data
from trader.indicators import atr, ema, macd, rsi

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class StockScreener:
    """Scans a universe of stocks and identifies the best trading opportunities."""

    def __init__(self, config):
        self.config = config
        self.stock_universe = getattr(config, "STOCK_UNIVERSE", [
            # Top 50 NSE liquid stocks (large-cap + mid-cap)
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
        ])
        self.min_rank_stocks = getattr(config, "SCREENER_MIN_STOCKS", 3)
        self.max_rank_stocks = getattr(config, "SCREENER_MAX_STOCKS", 10)

    def get_price_strength(self, ticker: str) -> Optional[Dict]:
        """
        Analyze price momentum and trend strength for a single stock.
        Returns a dict with momentum score and trend info if setup is valid.
        """
        try:
            df = fetch_intraday_data(ticker, interval=self.config.DATA_INTERVAL, period=self.config.DATA_PERIOD)
            if df.shape[0] < 30:
                return None

            df["ema9"] = ema(df["Close"], 9)
            df["ema20"] = ema(df["Close"], 20)
            df["rsi"] = rsi(df["Close"], window=14)
            df["atr"] = atr(df, window=14)
            df["macd"], df["macd_signal"], df["macd_hist"] = macd(df)

            latest = df.iloc[-1]
            previous = df.iloc[-2]

            # Check for bullish setup
            strong_uptrend = float(latest["ema9"]) > float(latest["ema20"])
            momentum = float(latest["macd"]) > float(latest["macd_signal"]) and float(previous["macd"]) <= float(
                previous["macd_signal"]
            )
            rsi_safe = self.config.MIN_RSI < float(latest["rsi"]) < self.config.MAX_RSI
            close_above_emas = float(latest["Close"]) > float(latest["ema9"]) > float(latest["ema20"])

            if strong_uptrend and momentum and rsi_safe and close_above_emas:
                # Calculate momentum score (higher = stronger setup)
                momentum_score = (
                    float(latest["macd_hist"]) / float(latest["atr"])
                    + (float(latest["rsi"]) - 50) / 20  # RSI distance from midpoint
                    + (float(latest["Close"]) - float(latest["ema20"])) / float(latest["atr"])  # price relative to EMA
                )

                return {
                    "ticker": ticker,
                    "momentum_score": momentum_score,
                    "rsi": float(latest["rsi"]),
                    "atr": float(latest["atr"]),
                    "ema9": float(latest["ema9"]),
                    "ema20": float(latest["ema20"]),
                    "close": float(latest["Close"]),
                    "macd_hist": float(latest["macd_hist"]),
                }

            return None

        except Exception as exc:
            logging.warning(f"Error screening {ticker}: {exc}")
            return None

    def scan(self) -> List[Dict]:
        """
        Scan the stock universe and return the top N stocks with the strongest setups.
        """
        logging.info(f"Screening {len(self.stock_universe)} stocks for today's best opportunities...")
        candidates = []

        for ticker in self.stock_universe:
            signal = self.get_price_strength(ticker)
            if signal:
                candidates.append(signal)
                logging.info(f"✓ {ticker}: momentum_score={signal['momentum_score']:.3f}, RSI={signal['rsi']:.1f}")

        # Sort by momentum score (highest = best)
        candidates.sort(key=lambda x: x["momentum_score"], reverse=True)

        # Return top N stocks (between min and max configured)
        top_count = max(self.min_rank_stocks, min(self.max_rank_stocks, len(candidates)))
        top_stocks = candidates[:top_count]

        if top_stocks:
            logging.info(f"Found {len(top_stocks)} stocks to trade today:")
            for i, stock in enumerate(top_stocks, 1):
                logging.info(f"  {i}. {stock['ticker']} (score: {stock['momentum_score']:.3f})")
        else:
            logging.warning("No stocks passed screening today.")

        return top_stocks
