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

            last_index = df.index[-1]
            prev_index = df.index[-2]

            # Extract scalar values explicitly from individual series
            close_val = float(df["Close"].at[last_index])
            ema9_val = float(df["ema9"].at[last_index])
            ema20_val = float(df["ema20"].at[last_index])
            rsi_val = float(df["rsi"].at[last_index])
            atr_val = float(df["atr"].at[last_index])
            macd_val = float(df["macd"].at[last_index])
            macd_signal_val = float(df["macd_signal"].at[last_index])
            macd_hist_val = float(df["macd_hist"].at[last_index])

            prev_macd_val = float(df["macd"].at[prev_index])
            prev_macd_signal_val = float(df["macd_signal"].at[prev_index])

            # Check for bullish setup
            strong_uptrend = ema9_val > ema20_val
            momentum = macd_val > macd_signal_val and prev_macd_val <= prev_macd_signal_val
            rsi_safe = self.config.MIN_RSI < rsi_val < self.config.MAX_RSI
            close_above_emas = close_val > ema9_val > ema20_val

            if strong_uptrend and momentum and rsi_safe and close_above_emas:
                # Calculate momentum score (higher = stronger setup)
                momentum_score = (
                    macd_hist_val / (atr_val + 1e-9)  # Avoid division by zero
                    + (rsi_val - 50) / 20  # RSI distance from midpoint
                    + (close_val - ema20_val) / (atr_val + 1e-9)  # price relative to EMA
                )

                return {
                    "ticker": ticker,
                    "momentum_score": momentum_score,
                    "rsi": rsi_val,
                    "atr": atr_val,
                    "ema9": ema9_val,
                    "ema20": ema20_val,
                    "close": close_val,
                    "macd_hist": macd_hist_val,
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
