# collectors/yahoo.py
import yfinance as yf
import pandas as pd

def fetch_price_series(
    ticker: str,
    period: str = "3mo",
    interval: str = "1h",
) -> pd.Series:
    """
    Download auto-adjusted Close prices for `ticker` via yfinance
    Returns a pd.Series (named after the ticker) indexed by timestamp
    """
    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )
    # Grab the Close column (may be a one-col DataFrame) and squeeze to 1-D
    close = df["Close"]
    s = close.squeeze()          # turns single-column DataFrame into Series
    s.name = ticker
    s.index.name = "Datetime"
    return s
