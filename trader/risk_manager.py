def compute_stop_loss(entry_price: float, atr_value: float, atr_multiplier: float, min_risk_pct: float) -> float:
    atr_stop = entry_price - atr_value * atr_multiplier
    percent_stop = entry_price * (1 - min_risk_pct)
    return max(atr_stop, percent_stop)


def compute_target(entry_price: float, stop_loss: float, target_multiplier: float) -> float:
    risk_amount = entry_price - stop_loss
    return entry_price + risk_amount * target_multiplier


def compute_size(capital: float, entry_price: float, stop_loss: float, risk_fraction: float) -> int:
    risk_amount = entry_price - stop_loss
    if risk_amount <= 0:
        return 0
    max_risk_value = capital * risk_fraction
    quantity = max_risk_value / risk_amount
    max_quantity_by_cash = int(capital / entry_price)
    return max(0, min(int(quantity), max_quantity_by_cash))
