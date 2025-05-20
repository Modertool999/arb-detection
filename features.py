import pandas as pd

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given an OHLCV df, adds columns for return, moving averages,
    volatility, and momentum, then drops NaNs.
    """
    # first row NaN, all others = (closing(t) - closing(t-1)) / closing(t-1)
    df["return"] = df["Close"].pct_change() 

    # first 4 rows NaN, rest are a 5-period moving average of the closing price
    df["ma_5"] = df["Close"].rolling(5).mean() 

    # first 9 rows NaN, rest are a 10-period moving average of the closing price
    df["ma_10"] = df["Close"].rolling(10).mean() 

    # rolling standard deviation of the closing price over the past 5 time periods
    df["volatility"] = df["Close"].rolling(5).std() 

    # difference between today’s closing price and the closing price 3 time periods ago
    df["momentum"] = df["Close"] - df["Close"].shift(3) 

    return df.dropna()

def label_arbitrage(df: pd.DataFrame, threshold: float = 0.01) -> pd.DataFrame:
    """
    Given a OHLCV df with a 'Close' column,
    - computes the one-period-ahead return,
    - sets label = 1 if |future_return| >= threshold, else 0,
    - drops the final row (no future data),
    and returns the augmented DataFrame.
    """
    # % change from this close to the next
    df["future_return"] = df["Close"].shift(-1) / df["Close"] - 1

    # label = 1 if magnitude of that return ≥ threshold
    df["label"] = (df["future_return"].abs() >= threshold).astype(int)

    # drop rows with NaN (the last row will have NaN future_return)
    return df.dropna()

