import logging

try:
    from upstox_api.api import Upstox
except ImportError:  # pragma: no cover
    Upstox = None


class UpstoxBroker:
    def __init__(self, config):
        if Upstox is None:
            raise ImportError("upstox_api is required for Upstox broker support. Install with `pip install upstox_api`.")

        broker_conf = getattr(config, "BROKER", {})
        api_key = broker_conf.get("api_key")
        api_secret = broker_conf.get("api_secret")
        access_token = broker_conf.get("access_token")
        if not api_key or not api_secret or not access_token:
            raise ValueError("Upstox broker requires api_key, api_secret, and access_token in BROKER config.")

        self.client = Upstox(api_key, api_secret)
        self.client.set_access_token(access_token)
        logging.info("Initialized Upstox broker client")

    def get_balance(self) -> float:
        profile = self.client.get_profile()
        return float(profile.get("cash_balance", 0.0) or 0.0)

    def place_order(self, ticker: str, side: str, quantity: int, entry_price: float, stop_loss: float, target: float) -> dict:
        symbol = ticker.replace(".NS", "")
        order_response = self.client.place_order(
            transaction_type=side,
            exchange=Upstox.EXCHANGE_NSE,
            symbol=symbol,
            quantity=quantity,
            order_type=Upstox.ORDER_TYPE_LIMIT,
            product=Upstox.PRODUCT_MIS,
            price=round(entry_price, 2),
            stop_loss=round(stop_loss, 2),
            trigger_price=round(stop_loss, 2),
            validity=Upstox.VALIDITY_DAY,
        )
        logging.info(f"Upstox order placed: {order_response}")
        return {**order_response, "executed": True}
