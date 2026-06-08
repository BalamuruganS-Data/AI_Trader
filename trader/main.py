import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import config
from trader.broker import BrokerInterface
from trader.indicators import atr, ema, macd, rsi
from trader.mailer import EmailClient
from trader.risk_manager import compute_size, compute_stop_loss, compute_target
from trader.screener import StockScreener
from trader.trade_logger import TradeLogger

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class IndianIntradayTrader:
    def __init__(self):
        self.screener = StockScreener(config)
        self.broker = BrokerInterface(config)
        self.trade_logger = TradeLogger(getattr(config, "TRADE_LOG_FILE", "trade_log.csv"))
        self.email_client = EmailClient(
            smtp_server=config.SMTP_SERVER,
            smtp_port=config.SMTP_PORT,
            username=config.EMAIL_USERNAME,
            password=config.EMAIL_PASSWORD,
            recipients=config.EMAIL_RECIPIENTS,
        )

    def market_open(self) -> bool:
        now = datetime.now()
        return config.START_HOUR <= now.hour < config.END_HOUR

    def get_available_balance(self) -> float:
        try:
            return self.broker.get_balance()
        except Exception as exc:
            logging.warning(f"Could not fetch live balance: {exc}")
            return getattr(config, "DEFAULT_CAPITAL", 100000.0)

    def prompt_trade_allocation(self, balance: float, requested_amount: float | None = None, interactive: bool = True) -> float:
        default_amount = getattr(config, "DAILY_TRADE_AMOUNT", None)
        max_allocation = balance * getattr(config, "MAX_DAILY_ALLOCATION", 0.25)
        if default_amount is None:
            recommended = min(max_allocation, balance)
        else:
            recommended = min(default_amount, max_allocation, balance)

        if requested_amount is not None:
            if requested_amount <= 0:
                raise ValueError("Allocation must be greater than zero.")
            if requested_amount > balance:
                raise ValueError("Allocation exceeds available balance.")
            if requested_amount > max_allocation:
                raise ValueError(f"Allocation exceeds daily allocation limit of ₹{max_allocation:.2f}.")
            return requested_amount

        if not getattr(config, "ASK_DAILY_TRADE_AMOUNT", True) or not interactive:
            return recommended

        while True:
            response = input(
                f"Available balance: ₹{balance:.2f}. "
                f"Enter amount to trade today (recommended ₹{recommended:.2f}, max ₹{max_allocation:.2f}): "
            ).strip()
            if response == "":
                return recommended
            try:
                amount = float(response.replace(",", ""))
            except ValueError:
                print("Please enter a valid number.")
                continue
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            if amount > balance:
                print("Amount exceeds available balance.")
                continue
            if amount > max_allocation:
                print(f"Amount exceeds daily allocation limit of ₹{max_allocation:.2f}.")
                continue
            return amount

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": self.broker.provider,
            "live_trading": self.broker.live,
            "mode": "dynamic stock screening",
            "stock_universe_size": len(self.screener.stock_universe),
            "daily_allocation_enabled": getattr(config, "ASK_DAILY_TRADE_AMOUNT", True),
            "max_daily_allocation_fraction": getattr(config, "MAX_DAILY_ALLOCATION", 0.25),
        }

    def analyze_symbol(self, ticker: str, capital: float) -> Optional[Dict[str, Any]]:
        """Convert a screener result into a trade setup."""
        # This is now handled by the screener; kept for backward compatibility if needed
        return None

    def place_trade(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        result = self.broker.place_order(
            ticker=trade["ticker"],
            side=trade["side"],
            quantity=trade["quantity"],
            entry_price=trade["entry_price"],
            stop_loss=trade["stop_loss"],
            target=trade["target"],
        )
        self.trade_logger.log_trade(trade, result)
        return result

    def send_trade_alert(self, trades: List[Dict[str, Any]]):
        if not trades:
            subject = "Intraday trader update: no trade taken"
            body = "No intraday setup was valid at this run. The watchlist was checked and no buy signals met the risk filters."
        else:
            subject = "Intraday trader alert: trade(s) generated"
            lines = ["Intraday trade alert summary:\n"]
            for trade in trades:
                lines.append(
                    f"{trade['ticker']} | {trade['side']} | qty={trade['quantity']} | "
                    f"entry={trade['entry_price']:.2f} | sl={trade['stop_loss']:.2f} | target={trade['target']:.2f} | "
                    f"RSI={trade['rsi']:.1f} | ATR={trade['atr']:.2f}"
                )
            body = "\n".join(lines)

        self.email_client.send(subject, body)

    def run(self, requested_amount: float | None = None, interactive: bool = True) -> List[Dict[str, Any]]:
        logging.info("Starting intraday analysis run with dynamic stock screening")
        if not self.market_open():
            logging.warning("Market hours are outside configured window. Continue when market is open.")

        balance = self.get_available_balance()
        trade_capital = self.prompt_trade_allocation(balance, requested_amount=requested_amount, interactive=interactive)
        logging.info(f"Using ₹{trade_capital:.2f} for today's intraday trading allocation")

        # Scan the market for best opportunities
        candidates = self.screener.scan()
        
        trades = []
        for candidate in candidates:
            try:
                # Calculate trade sizing based on the candidate's ATR and capital
                entry_price = candidate["close"]
                stop_loss = compute_stop_loss(entry_price, candidate["atr"], config.ATR_MULTIPLIER, config.MAX_INSTRUMENT_RISK)
                target_price = compute_target(entry_price, stop_loss, config.TARGET_MULTIPLIER)
                quantity = compute_size(trade_capital, entry_price, stop_loss, config.MAX_RISK_PERCENT / 100)

                if quantity <= 0:
                    logging.warning(f"Calculated quantity for {candidate['ticker']} is zero or negative")
                    continue

                trade = {
                    "ticker": candidate["ticker"],
                    "side": "BUY",
                    "quantity": quantity,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "target": target_price,
                    "rsi": candidate["rsi"],
                    "atr": candidate["atr"],
                    "ema9": candidate["ema9"],
                    "ema20": candidate["ema20"],
                }
                
                order = self.place_trade(trade)
                trades.append(order)
                
            except Exception as exc:
                logging.exception(f"Error processing {candidate['ticker']}: {exc}")

        try:
            self.send_trade_alert(trades)
        except Exception as exc:
            logging.error(f"Trade alert email failed: {exc}")
        logging.info("Intraday run complete")
        return trades


if __name__ == "__main__":
    trader = IndianIntradayTrader()
    trader.run()
