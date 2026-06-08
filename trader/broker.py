import logging

from trader.brokers.kite import KiteBroker
from trader.brokers.upstox import UpstoxBroker


class SimulatedBroker:
    def __init__(self, config):
        self.balance = getattr(config, "SIMULATED_BALANCE", getattr(config, "DEFAULT_CAPITAL", 100000.0))

    def get_balance(self) -> float:
        return float(self.balance)

    def place_order(self, ticker: str, side: str, quantity: int, entry_price: float, stop_loss: float, target: float) -> dict:
        order = {
            "ticker": ticker,
            "side": side,
            "quantity": quantity,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": target,
            "provider": "simulated",
            "executed": False,
        }
        logging.info(f"[BROKER SIMULATION] {order}")
        return order


class BrokerInterface:
    def __init__(self, config):
        self.live = getattr(config, "LIVE_TRADING", False)
        self.provider = getattr(config, "BROKER", {}).get("provider", "none").lower()
        self.config = config
        self.delegate = self._create_delegate(config)

    def _create_delegate(self, config):
        if not self.live or self.provider == "none":
            return SimulatedBroker(config)
        if self.provider == "kite":
            return KiteBroker(config)
        if self.provider == "upstox":
            return UpstoxBroker(config)
        raise ValueError(f"Unsupported broker provider: {self.provider}")

    def get_balance(self) -> float:
        return self.delegate.get_balance()

    def place_order(self, ticker: str, side: str, quantity: int, entry_price: float, stop_loss: float, target: float):
        return self.delegate.place_order(ticker, side, quantity, entry_price, stop_loss, target)
