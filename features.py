import pandas as pd

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given an OHLCV DataFrame, adds columns for return, moving averages,
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
