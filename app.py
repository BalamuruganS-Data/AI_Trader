from datetime import datetime

from flask import Flask, render_template, request

import config
from trader.end_of_day import EndOfDayReport
from trader.main import IndianIntradayTrader

app = Flask(__name__)


def get_trader():
    return IndianIntradayTrader()


@app.route("/", methods=["GET"])
def index():
    trader = get_trader()
    status = trader.get_status()
    try:
        balance = trader.get_available_balance()
    except Exception as exc:
        balance = None
        status["balance_error"] = str(exc)

    return render_template(
        "index.html",
        status=status,
        balance=balance,
        today=datetime.now().date().isoformat(),
        run_result=None,
        trades=None,
        summary_message=None,
        summary_text=None,
    )


@app.route("/run", methods=["POST"])
def run_trading():
    trader = get_trader()
    allocation = request.form.get("allocation")
    requested_amount = None
    if allocation:
        try:
            requested_amount = float(allocation.replace(",", ""))
        except ValueError:
            requested_amount = None

    try:
        trades = trader.run(requested_amount=requested_amount, interactive=False, send_email_async=True)
        result_message = f"Executed {len(trades)} trade(s). Email alert sent in background."
    except Exception as exc:
        trades = []
        result_message = f"Error: {exc}"

    balance = trader.get_available_balance()
    return render_template(
        "index.html",
        status=trader.get_status(),
        balance=balance,
        today=datetime.now().date().isoformat(),
        run_result=result_message,
        trades=trades,
        summary_message=None,
        summary_text=None,
    )


@app.route("/summary", methods=["POST"])
def send_summary():
    date_str = request.form.get("summary_date")
    if date_str:
        report_date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        report_date = datetime.now()

    report = EndOfDayReport(log_file=getattr(config, "TRADE_LOG_FILE", "trade_log.csv"), report_date=report_date)
    try:
        summary_text = report.send_summary()
        summary_message = "Summary email sent successfully."
    except Exception as exc:
        summary_text = str(exc)
        summary_message = f"Error sending summary: {exc}"

    trader = get_trader()
    balance = trader.get_available_balance()
    return render_template(
        "index.html",
        status=trader.get_status(),
        balance=balance,
        today=datetime.now().date().isoformat(),
        run_result=None,
        trades=None,
        summary_message=summary_message,
        summary_text=summary_text,
    )


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(debug=debug, host="0.0.0.0", port=port)
