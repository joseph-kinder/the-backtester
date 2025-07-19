"""
Quick test script to verify installation
"""

import sys
import os

# Add the project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test imports
    print("Testing imports...")
    from crypto_backtest import run_backtest, load_data
    from crypto_backtest.features import sma, rsi, zscore
    print("✓ Core imports successful")
    
    # Test basic functionality
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Create dummy data
    print("\nCreating test data...")
    dates = pd.date_range(end=datetime.now(), periods=100, freq='H')
    prices = 50000 + 1000 * np.sin(np.linspace(0, 4*np.pi, 100)) + np.random.normal(0, 100, 100)
    
    data = {
        'BTC/USDT': {
            'ohlcv': pd.DataFrame({
                'open': prices,
                'high': prices * 1.01,
                'low': prices * 0.99,
                'close': prices,
                'volume': np.random.uniform(100, 1000, 100)
            }, index=dates)
        }
    }
    print("✓ Test data created")
    
    # Test strategy
    def test_strategy(data, position, timestamp, **params):
        if position.get('BTC/USDT', 0) == 0:
            return [{'symbol': 'BTC/USDT', 'side': 'buy', 'size': 0.1}]
        return []
    
    # Run backtest
    print("\nRunning test backtest...")
    results = run_backtest(
        data=data,
        strategy=test_strategy,
        initial_capital=10000,
        verbose=False
    )
    
    print("✓ Backtest completed")
    print(f"Final equity: ${results.final_equity:,.2f}")
    print(f"Number of trades: {len(results.trades)}")
    
    # Test indicators
    print("\nTesting indicators...")
    ma = sma(data['BTC/USDT']['ohlcv']['close'], 20)
    rsi_val = rsi(data['BTC/USDT']['ohlcv']['close'], 14)
    z = zscore(data['BTC/USDT']['ohlcv']['close'], 20)
    print("✓ Indicators calculated successfully")
    
    print("\n✅ All tests passed! The framework is ready to use.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPlease make sure you've installed the requirements:")
    print("  pip install -r requirements-minimal.txt")
    print("  pip install -e .")
