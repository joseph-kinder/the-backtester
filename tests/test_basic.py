"""
Basic tests for crypto backtest framework
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from crypto_backtest import run_backtest
from crypto_backtest.features import sma, rsi, zscore


def create_dummy_data(symbol='BTC/USDT', days=30):
    """Create dummy OHLCV data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=days*24, freq='H')
    
    # Generate random walk price data
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, size=len(dates))
    close = 50000 * np.exp(np.cumsum(returns))
    
    # Generate OHLCV
    high = close * (1 + np.abs(np.random.normal(0, 0.005, size=len(dates))))
    low = close * (1 - np.abs(np.random.normal(0, 0.005, size=len(dates))))
    open_ = close.shift(1).fillna(close[0])
    volume = np.random.uniform(100, 1000, size=len(dates))
    
    df = pd.DataFrame({
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    
    return {symbol: {'ohlcv': df}}


def test_simple_strategy():
    """Test a simple buy and hold strategy"""
    # Create dummy data
    data = create_dummy_data()
    
    # Simple strategy
    def buy_and_hold(data, position, timestamp, **params):
        if position.get('BTC/USDT', 0) == 0:
            return [{'symbol': 'BTC/USDT', 'side': 'buy', 'size': 0.1}]
        return []
    
    # Run backtest
    results = run_backtest(
        data=data,
        strategy=buy_and_hold,
        initial_capital=10000
    )
    
    assert results is not None
    assert results.final_equity > 0
    assert len(results.trades) > 0


def test_technical_indicators():
    """Test technical indicator calculations"""
    # Create test data
    prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
    
    # Test SMA
    ma = sma(prices, 3)
    assert len(ma) == len(prices)
    assert np.isnan(ma.iloc[0])  # First values should be NaN
    assert not np.isnan(ma.iloc[2])  # Should have value after period
    
    # Test RSI
    rsi_values = rsi(prices, 5)
    assert len(rsi_values) == len(prices)
    assert all(0 <= x <= 100 for x in rsi_values.dropna())
    
    # Test Z-score
    z = zscore(prices, 5)
    assert len(z) == len(prices)


def test_strategy_with_parameters():
    """Test strategy with parameters"""
    data = create_dummy_data()
    
    def parametric_strategy(data, position, timestamp, **params):
        close = data['BTC/USDT']['ohlcv']['close']
        ma = sma(close, params['ma_period'])
        
        if len(close) < params['ma_period']:
            return []
        
        if close.iloc[-1] > ma.iloc[-1] and position.get('BTC/USDT', 0) == 0:
            return [{'symbol': 'BTC/USDT', 'side': 'buy', 'size': params['size']}]
        elif close.iloc[-1] < ma.iloc[-1] and position.get('BTC/USDT', 0) > 0:
            return 'close_all'
        
        return []
    
    results = run_backtest(
        data=data,
        strategy=parametric_strategy,
        initial_capital=10000,
        params={'ma_period': 10, 'size': 0.1}
    )
    
    assert results is not None
    assert isinstance(results.metrics, dict)
    assert 'sharpe_ratio' in results.metrics
    assert 'max_drawdown' in results.metrics


if __name__ == '__main__':
    test_simple_strategy()
    test_technical_indicators()
    test_strategy_with_parameters()
    print("All tests passed!")
