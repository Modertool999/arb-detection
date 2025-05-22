#!/usr/bin/env python3

# test for git config (changed email)
"""
cross_listed_arbitrage.py

Pulls daily close prices for a U.S. ADR and its U.K. ordinary share,
converts the U.K. price from pence → GBP → USD (applying the ADR ratio),
computes the spread and its rolling z-score, and flags arbitrage signals.
"""

import pandas as pd
from collectors.yahoo import fetch_price_series



def main():
    # 1. Fetch each series (daily bars for guaranteed alignment)
    us = fetch_price_series("HSBC",    period="6mo", interval="1d")  # ADR on NYSE
    uk = fetch_price_series("HSBA.L",  period="6mo", interval="1d")  # Ordinary share on LSE
    fx = fetch_price_series("GBPUSD=X", period="6mo", interval="1d") # GBP→USD FX rate

    # 2. Align on their common timestamps
    df = pd.concat([us, uk, fx], axis=1, join="inner").dropna()
    df.columns = ["Close_US", "Close_UK", "FX"]

    # 3. Convert U.K. price properly:
    #    - LSE quotes in pence, so divide by 100 → GBP
    #    - HSBC ADR = 5 ordinary shares
    df["Close_UK_GBP"] = df["Close_UK"] / 100.0
    ADR_RATIO = 5
    df["Close_UK_USD"] = df["Close_UK_GBP"] * df["FX"] * ADR_RATIO

    # 4. Compute the raw spread
    df["spread"] = df["Close_US"] - df["Close_UK_USD"]

    # 5. Compute rolling z-score of the spread
    window   = 20
    df["spread_mean"] = df["spread"].rolling(window).mean()
    df["spread_std"]  = df["spread"].rolling(window).std()
    df["z_score"]     = (df["spread"] - df["spread_mean"]) / df["spread_std"]

    # 6. Flag potential arbitrage signals when |z| > 2
    z_thresh = 2.0
    df["arb_signal"] = (df["z_score"].abs() > z_thresh).astype(int)

    # 7. Output the last few rows and save for later analysis
    print(df[["Close_US","Close_UK_USD","spread","z_score","arb_signal"]].tail())
    df.to_csv("data/cross_listed_signals.csv")

if __name__ == "__main__":
    main()
