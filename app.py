# file: app.py
from flask import Flask, jsonify, request, send_from_directory
from loaders.data_loader import load_cross_listed
from features.feature_engineering import add_spread_features
from models.backtest import backtest_spread

app = Flask(__name__, static_folder='static')


class APIError(Exception):
    """
    Custom exception class for API errors with HTTP status codes.
    """
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify({'error': error.message})
    response.status_code = error.status_code
    return response


@app.errorhandler(Exception)
def handle_exception(error):
    # You can log the error details here for debugging
    response = jsonify({'error': 'Internal server error'})
    response.status_code = 500
    return response


def parse_params():
    """
    Parse and validate common query parameters for both endpoints.
    Raises APIError on invalid input.
    """
    try:
        ticker_us = request.args.get('us', 'HSBC')
        ticker_uk = request.args.get('uk', 'HSBA.L')
        period    = request.args.get('period', '6mo')
        interval  = request.args.get('interval', '1d')
        window    = int(request.args.get('window', 20))
        z_thresh  = float(request.args.get('z_thresh', 2.0))
    except ValueError as e:
        raise APIError(f'Invalid query parameter: {e}', 400)
    return ticker_us, ticker_uk, period, interval, window, z_thresh


@app.route('/')
def serve_index():
    """
    Serve the frontend dashboard index.html from the static folder.
    """
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/scan')
def scan():
    """
    Returns the latest cross-listed arbitrage metrics for given tickers.
    """
    # Parse and validate parameters
    ticker_us, ticker_uk, period, interval, window, z_thresh = parse_params()

    # Load raw data
    df = load_cross_listed(
        ticker_us, ticker_uk, fx_ticker='GBPUSD=X',
        period=period, interval=interval
    )
    if df.empty:
        raise APIError('No data available for given tickers or parameters', 400)

    # Compute features
    df_feat = add_spread_features(df, window=window, z_thresh=z_thresh)
    if df_feat.empty:
        raise APIError('Insufficient data to compute spread features', 400)

    # Extract latest metrics
    last = df_feat.iloc[-1]
    result = {
        'date':         last.name.strftime('%Y-%m-%d'),
        'Close_US':     last['Close_US'],
        'Close_UK_USD': last['Close_UK_USD'],
        'spread':       last['spread'],
        'z_score':      last['z_score'],
        'arb_signal':   int(last['arb_signal']),
    }
    return jsonify(result)


@app.route('/backtest')
def backtest_endpoint():
    """
    Runs a backtest on historical data and returns performance metrics.
    """
    # Parse and validate parameters
    ticker_us, ticker_uk, period, interval, window, z_thresh = parse_params()

    # Load raw data
    df = load_cross_listed(
        ticker_us, ticker_uk, fx_ticker='GBPUSD=X',
        period=period, interval=interval
    )
    if df.empty:
        raise APIError('No data available for given tickers or parameters', 400)

    # Compute features
    df_feat = add_spread_features(df, window=window, z_thresh=z_thresh)
    if df_feat.empty:
        raise APIError('Insufficient data to compute spread features', 400)

    # Run backtest
    bt = backtest_spread(df_feat)
    if bt.empty:
        raise APIError('Backtest did not generate any trades', 400)

    total_return = bt['equity'].iloc[-1]
    win_rate     = float((bt['pnl'] > 0).mean())
    sharpe_ratio = None
    if bt['pnl'].std() != 0:
        sharpe_ratio = (bt['pnl'].mean() / bt['pnl'].std()) * (252 ** 0.5)

    metrics = {
        'total_return':  total_return,
        'win_rate':      win_rate,
        'sharpe_ratio':  sharpe_ratio,
    }
    return jsonify(metrics)


if __name__ == '__main__':
    app.run(debug=True)
