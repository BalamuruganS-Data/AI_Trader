import argparse
import csv
from datetime import datetime, timedelta
from typing import Any, Dict, List

import config
from trader.data_provider import fetch_intraday_data
from trader.mailer import EmailClient


class EndOfDayReport:
    def __init__(self, log_file: str, report_date: datetime):
        self.log_file = log_file
        self.report_date = report_date
        self.trades = self._read_trades()

    def _read_trades(self) -> List[Dict[str, Any]]:
        trades = []
        try:
            with open(self.log_file, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    timestamp = datetime.fromisoformat(row["timestamp"])
                    if timestamp.date() == self.report_date.date():
                        trades.append({
                            "timestamp": timestamp,
                            "ticker": row["ticker"],
                            "side": row["side"],
                            "quantity": int(row["quantity"]),
                            "entry_price": float(row["entry_price"]),
                            "stop_loss": float(row["stop_loss"]),
                            "target": float(row["target"]),
                            "provider": row["provider"],
                            "executed": row["executed"].lower() == "true",
                            "order_id": row.get("order_id", ""),
                            "rsi": row.get("rsi", ""),
                            "atr": row.get("atr", ""),
                        })
        except FileNotFoundError:
            return []
        return trades

    def _estimate_close_price(self, ticker: str) -> float:
        data = fetch_intraday_data(ticker, interval=config.DATA_INTERVAL, period="1d")
        return float(data["Close"].iloc[-1])

    def _build_report(self) -> str:
        if not self.trades:
            return f"No trades recorded for {self.report_date.date()} in {self.log_file}."

        lines = [f"Intraday trading summary for {self.report_date.date()}:\n"]
        total_pnl = 0.0
        for trade in self.trades:
            if not trade["executed"]:
                lines.append(f"{trade['ticker']} - not executed")
                continue
            close_price = self._estimate_close_price(trade["ticker"])
            pnl = (close_price - trade["entry_price"]) * trade["quantity"]
            if trade["side"].upper() == "SELL":
                pnl = -pnl
            total_pnl += pnl
            lines.append(
                f"{trade['ticker']} | qty={trade['quantity']} | entry={trade['entry_price']:.2f} | "
                f"close={close_price:.2f} | pnl={'+' if pnl >= 0 else ''}{pnl:.2f} | "
                f"SL={trade['stop_loss']:.2f} | target={trade['target']:.2f}"
            )

        lines.append(f"\nEstimated total P/L: {'+' if total_pnl >= 0 else ''}{total_pnl:.2f}")
        return "\n".join(lines)

    def send_summary(self):
        body = self._build_report()
        subject = f"Intraday EOD summary {self.report_date.date()}"
        email_client = EmailClient(
            smtp_server=config.SMTP_SERVER,
            smtp_port=config.SMTP_PORT,
            username=config.EMAIL_USERNAME,
            password=config.EMAIL_PASSWORD,
            recipients=config.EMAIL_RECIPIENTS,
        )
        email_client.send(subject, body)
        return body


def parse_args():
    parser = argparse.ArgumentParser(description="Send an end-of-day intraday trading summary email.")
    parser.add_argument(
        "--date",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
        default=datetime.now(),
        help="Date to summarize in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=getattr(config, "TRADE_LOG_FILE", "trade_log.csv"),
        help="Path to the trade log file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    report = EndOfDayReport(log_file=args.log_file, report_date=args.date)
    summary = report.send_summary()
    print(summary)
