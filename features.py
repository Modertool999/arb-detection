import pandas as pd

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given an OHLCV DataFrame, adds columns for return, moving averages,
    volatility, and momentum, then drops NaNs.
    """
    df["return"]     = df["Close"].pct_change()
    df["ma_5"]       = df["Close"].rolling(5).mean()
    df["ma_10"]      = df["Close"].rolling(10).mean()
    df["volatility"] = df["Close"].rolling(5).std()
    df["momentum"]   = df["Close"] - df["Close"].shift(3)
    return df.dropna()
