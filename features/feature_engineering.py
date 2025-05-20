def add_spread_features(
    df,
    window: int = 20,
    z_thresh: float = 2.0
):
    df = df.copy()
    # convert pence to GBP, apply ADR ratio, then GBP to USD
    df["Close_UK_GBP"] = df["Close_UK"] / 100.0
    ADR_RATIO = 5
    df["Close_UK_USD"] = df["Close_UK_GBP"] * df["FX"] * ADR_RATIO

    # spread and its rolling stats
    df["spread"] = df["Close_US"] - df["Close_UK_USD"]
    df["spread_mean"] = df["spread"].rolling(window).mean()
    df["spread_std"]  = df["spread"].rolling(window).std()
    df["z_score"]     = (df["spread"] - df["spread_mean"]) / df["spread_std"]
    df["arb_signal"]  = (df["z_score"].abs() >= z_thresh).astype(int)

    return df.dropna()