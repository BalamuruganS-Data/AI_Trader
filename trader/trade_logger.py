import csv
import os
from datetime import datetime
from typing import Dict


class TradeLogger:
    HEADER = [
        "timestamp",
        "ticker",
        "side",
        "quantity",
        "entry_price",
        "stop_loss",
        "target",
        "provider",
        "executed",
        "order_id",
        "rsi",
        "atr",
    ]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            directory = os.path.dirname(self.file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(self.file_path, "w", newline="", encoding="utf-8") as output:
                writer = csv.writer(output)
                writer.writerow(self.HEADER)

    def log_trade(self, trade: Dict, order: Dict):
        row = [
            datetime.now().isoformat(),
            trade.get("ticker", ""),
            trade.get("side", ""),
            trade.get("quantity", 0),
            trade.get("entry_price", 0.0),
            trade.get("stop_loss", 0.0),
            trade.get("target", 0.0),
            order.get("provider", ""),
            order.get("executed", False),
            order.get("order_id", ""),
            trade.get("rsi", ""),
            trade.get("atr", ""),
        ]
        with open(self.file_path, "a", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(row)
