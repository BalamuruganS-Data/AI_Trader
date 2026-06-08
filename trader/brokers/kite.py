import logging

try:
    from kiteconnect import KiteConnect
except ImportError:  # pragma: no cover
    KiteConnect = None


class KiteBroker:
    def __init__(self, config):
        if KiteConnect is None:
            raise ImportError("kiteconnect is required for Kite broker support. Install with `pip install kiteconnect`.")

        broker_conf = getattr(config, "BROKER", {})
        api_key = broker_conf.get("api_key")
        access_token = broker_conf.get("access_token")
        if not api_key or not access_token:
            raise ValueError("Kite broker requires api_key and access_token in BROKER config.")

        self.client = KiteConnect(api_key=api_key)
        self.client.set_access_token(access_token)
        logging.info("Initialized Zerodha Kite broker client")

    def get_balance(self) -> float:
        profile = self.client.profile()
        return float(profile.get("equity", 0.0) or 0.0)

    def place_order(self, ticker: str, side: str, quantity: int, entry_price: float, stop_loss: float, target: float) -> dict:
        symbol = ticker.replace(".NS", "")
        sl_amount = round(entry_price - stop_loss, 2)
        target_amount = round(target - entry_price, 2)
        order_payload = {
            "variety": "bo",
            "exchange": "NSE",
            "tradingsymbol": symbol,
            "transaction_type": side,
            "quantity": quantity,
            "product": "MIS",
            "order_type": "LIMIT",
            "price": round(entry_price, 2),
            "squareoff": target_amount,
            "stoploss": sl_amount,
            "validity": "DAY",
        }
        order_id = self.client.place_order(**order_payload)
        logging.info(f"Kite BO order placed: {order_id}")
        return {**order_payload, "order_id": order_id, "executed": True}
