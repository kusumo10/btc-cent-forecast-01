#!/usr/bin/env python3
"""btc-cent-forecast-01 entry: 4-hour BTC price forecast from one 72h window.

Method (walk-forward OLS mean-reversion, fitted inside the case itself):
  - work in log price; the 240-minute forward return is regressed (OLS, with
    intercept) on the trailing 24h log return, over all past checkpoints in
    the case's own 72h window whose 240-minute outcome is already observed
    (s in [1440, t-240], step 5 minutes);
  - the fitted move is shrunk 0.6 toward persistence (no move) and clipped
    to +/-60bp, then applied to the checkpoint close.
  - the 24h return is strongly mean-reverting at the 4h horizon in the
    practice regime (corr -0.59 with the 240m forward return), so the model
    leans against the last day's move; shrinkage + clip bound the worst case.

Deterministic (pure float arithmetic, no randomness), stdlib only, no
network. Reads $MAKEFUN_INPUT_DIR (or /input), writes $MAKEFUN_OUTPUT_DIR
(or /output). One <id>.out per <id>.in, in name order.
"""
import json
import math
import os

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

MIN_PRICE = 0.00001
MAX_PRICE = 9999999.99999
LOOKBACK = 1440      # minutes of trailing return used as the regressor
HORIZON = 240        # minutes ahead to forecast
STEP = 5             # minutes between walk-forward training checkpoints
SHRINK = 0.6         # shrink the fitted move toward persistence (0)
CAP = 0.006          # clip the predicted log return to +/-60bp


def price5(x):
    """x kept on the grid's 5 decimals and inside (0, 10_000_000)."""
    return round(min(MAX_PRICE, max(MIN_PRICE, x)) * 1e5) / 1e5


def ols_intercept_slope(xs, ys):
    """Ordinary least squares y ~ a + b*x. Returns (a, b)."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den <= 0.0:
        return my, 0.0
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    return my - b * mx, b


def forecast(prices):
    """Forecast the price HORIZON minutes after the last close in prices."""
    n = len(prices)
    if n == 0:
        raise ValueError("market has no prices")
    last = prices[-1]
    if not (isinstance(last, (int, float)) and math.isfinite(last) and last > 0):
        raise ValueError("market's last price is not a positive finite number")
    h = min(LOOKBACK, n - HORIZON - 1)
    if h < 60 or n - HORIZON - h < 20:
        return price5(last)  # too little history: persistence
    lp = [math.log(p) for p in prices]
    xs, ys = [], []
    for s in range(h, n - HORIZON, STEP):
        xs.append(lp[s] - lp[s - h])
        ys.append(lp[s + HORIZON] - lp[s])
    if len(xs) < 20:
        return price5(last)
    a, b = ols_intercept_slope(xs, ys)
    raw = a + b * (lp[-1] - lp[-1 - h])
    pred = SHRINK * raw
    pred = max(-CAP, min(CAP, pred))
    return price5(last * math.exp(pred))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    inputs = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    for name in inputs:
        case_id = name[:-3]
        with open(os.path.join(INPUT_DIR, name), encoding="utf-8") as f:
            case = json.load(f)
        markets = case.get("markets")
        if not isinstance(markets, list) or len(markets) != 1:
            raise ValueError(f"{name} does not hold exactly one market")
        prices = markets[0].get("prices")
        if not isinstance(prices, list) or not prices:
            raise ValueError(f"{name} has no prices")
        out = {"forecasts": [{"case": case_id, "price": forecast(prices)}]}
        with open(os.path.join(OUTPUT_DIR, case_id + ".out"), "w", encoding="utf-8") as f:
            f.write(json.dumps(out) + "\n")


if __name__ == "__main__":
    main()
