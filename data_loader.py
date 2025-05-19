import pandas as pd

def load_raw_data(ticker: str) -> pd.DataFrame:
    """
    Reads data/{ticker}.csv (which has 3 metadata rows), skips them,
    parses the 4th line as headers, and returns a DataFrame indexed by Datetime.
    """
    filepath = f"data/{ticker}.csv"
    df = pd.read_csv(
        filepath,
        skiprows=3,
        header=None,
        names=["Datetime","Close","High","Low","Open","Volume"],
        parse_dates=["Datetime"],
        index_col="Datetime",
    )
    return df[["Open","High","Low","Close","Volume"]]
