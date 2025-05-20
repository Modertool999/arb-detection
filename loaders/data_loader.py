from collectors.yahoo import fetch_price_series
import pandas as pd

def load_cross_listed(
    ticker_us: str,
    ticker_uk: str,
    fx_ticker: str = "GBPUSD=X",
    period: str = "6mo",
    interval: str = "1d",
    resample_rule: str = None
) -> pd.DataFrame:
    # 1) fetch the three Series
    us = fetch_price_series(ticker_us, period=period, interval=interval)
    uk = fetch_price_series(ticker_uk, period=period, interval=interval)
    fx = fetch_price_series(fx_ticker, period=period, interval=interval)

    # 2) optional: resample into a clean grid
    if resample_rule:
        us = us.resample(resample_rule).last()
        uk = uk.resample(resample_rule).last()
        fx = fx.resample(resample_rule).last()

    # 3) keep only timestamps present in all three
    df = pd.concat([us, uk, fx], axis=1, join="inner").dropna()
    df.columns = ["Close_US", "Close_UK", "FX"]
    return df