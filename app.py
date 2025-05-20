from flask import Flask, jsonify, request
from loaders.data_loader import load_cross_listed
from features.feature_engineering import add_spread_features
from models.backtest import backtest_spread

app = Flask(__name__)

@app.route('/scan')
def scan():
    """
    Returns the latest cross-listed arbitrage metrics for given tickers.
    Query params:
      - us: U.S. ADR ticker (default: 'HSBC')
      - uk: U.K. ordinary ticker (default: 'HSBA.L')
      - period: data lookback (default: '6mo')
      - interval: bar frequency (default: '1d')
      - window: rolling window for z-score (default: 20)
      - z_thresh: z-score threshold (default: 2.0)
    """
    # Parse query parameters
    ticker_us = request.args.get('us', 'HSBC')
    ticker_uk = request.args.get('uk', 'HSBA.L')
    period    = request.args.get('period', '6mo')
    interval  = request.args.get('interval', '1d')
    window    = int(request.args.get('window', 20))
    z_thresh  = float(request.args.get('z_thresh', 2.0))

    # Load and prepare data
    raw_df = load_cross_listed(
        ticker_us, ticker_uk, fx_ticker='GBPUSD=X',
        period=period, interval=interval
    )
    df = add_spread_features(raw_df, window=window, z_thresh=z_thresh)

    # Extract latest row
    last = df.iloc[-1]
    result = {
        'date':           last.name.strftime('%Y-%m-%d'),
        'Close_US':       last['Close_US'],
        'Close_UK_USD':   last['Close_UK_USD'],
        'spread':         last['spread'],
        'z_score':        last['z_score'],
        'arb_signal':     int(last['arb_signal'])
    }
    return jsonify(result)

@app.route('/backtest')
def backtest_endpoint():
    """
    Runs a backtest on historical data and returns performance metrics.
    Same query params as /scan.
    """
    # Parse query parameters
    ticker_us = request.args.get('us', 'HSBC')
    ticker_uk = request.args.get('uk', 'HSBA.L')
    period    = request.args.get('period', '6mo')
    interval  = request.args.get('interval', '1d')
    window    = int(request.args.get('window', 20))
    z_thresh  = float(request.args.get('z_thresh', 2.0))

    # Load, prepare, and signal
    raw_df = load_cross_listed(
        ticker_us, ticker_uk, fx_ticker='GBPUSD=X',
        period=period, interval=interval
    )
    df = add_spread_features(raw_df, window=window, z_thresh=z_thresh)

    # Run backtest
    bt = backtest_spread(df)
    total_return = bt['equity'].iloc[-1]
    win_rate     = float((bt['pnl'] > 0).mean())
    sharpe_ratio = None
    if bt['pnl'].std() != 0:
        sharpe_ratio = (bt['pnl'].mean() / bt['pnl'].std()) * (252 ** 0.5)

    metrics = {
        'total_return':    total_return,
        'win_rate':        win_rate,
        'sharpe_ratio':    sharpe_ratio
    }
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(debug=True)
