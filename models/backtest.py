# file: models/backtest.py
import pandas as pd

def backtest_spread(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with 'spread' and 'arb_signal' columns (indexed by date),
    simulate entering a position when arb_signal == 1 and exiting the next day.
    Returns a DataFrame with additional columns:
      - position: +1 or -1 when in a trade, else 0
      - pnl: per-trade profit and loss
      - equity: cumulative PnL over time
    """
    df = df.copy()
    # Next-day spread for exit price
    df['next_spread'] = df['spread'].shift(-1)
    df.dropna(inplace=True)

    # Determine position: if signal and spread>0, short the spread (-1); if spread<0, long (+1)
    df['position'] = 0
    df.loc[(df.spread > 0) & (df.arb_signal == 1), 'position'] = -1
    df.loc[(df.spread < 0) & (df.arb_signal == 1), 'position'] = 1

    # Calculate PnL: position * (entry_spread - exit_spread)
    df['pnl'] = df['position'] * (df['spread'] - df['next_spread'])

    # Cumulative equity curve
    df['equity'] = df['pnl'].cumsum()
    return df

if __name__ == '__main__':
    from loaders.data_loader import load_cross_listed
    from features.feature_engineering import add_spread_features

    # Load and prepare data
    raw = load_cross_listed('HSBC', 'HSBA.L', period='6mo', interval='1d')
    df = add_spread_features(raw, window=20, z_thresh=2.0)

    # Run backtest
    results = backtest_spread(df)

    # Print summary metrics
    total_return = results.equity.iloc[-1]
    win_rate = (results.pnl > 0).mean()
    sharpe = results.pnl.mean() / results.pnl.std() * (252**0.5)

    print(f"Total return (USD): {total_return:.2f}")
    print(f"Win rate: {win_rate:.2%}")
    print(f"Annualized Sharpe ratio: {sharpe:.2f}")
    print(results[['spread', 'z_score', 'arb_signal', 'position', 'pnl', 'equity']].tail())
