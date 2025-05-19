import yfinance as yf
import pandas as pd

# Note to self: includes 3 lines of metadata, must account for this during data manipulation

def get_data(ticker, period="6mo", interval="1h"):
    """
    Downloads historical stock data for the given ticker and writes it to data/{ticker}.csv,
    skipping the first three metadata rows. The data/ directory must exist before saving.
    Raises ValueError if the ticker is empty.
    """
    # Download historical data
    df = yf.download(ticker, period=period, interval=interval)

    # Save to CSV
    filepath = f"data/{ticker}.csv"
    df.to_csv(filepath)

    print(f"{ticker} data saved (first 3 rows skipped).")

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOG"]
    for ticker in tickers:
        get_data(ticker)
