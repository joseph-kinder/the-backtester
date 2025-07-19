# Crypto Backtest Framework

A comprehensive Python toolkit for backtesting cryptocurrency trading strategies in Jupyter notebooks.

## Features

- **Notebook-first design**: All strategy logic lives in notebooks
- **Simple functional API**: Import tools, write strategy, run backtest
- **Rich feature library**: Technical indicators, statistical analysis, microstructure metrics
- **Multi-exchange support**: Via CCXT integration
- **ML model support**: ONNX runtime integration
- **Hyperparameter optimization**: Built-in Optuna support
- **Interactive visualizations**: Plotly-based charts

## Installation

### Quick Start (Recommended for Python 3.12)

```bash
# Install minimal requirements
pip install -r requirements-minimal.txt

# Install the package in development mode
pip install -e .

# Test the installation
python test_installation.py
```

### Full Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions including:
- Windows-specific TA-Lib installation
- Conda environment setup
- Troubleshooting guide

## Quick Start

```python
from crypto_backtest import run_backtest, load_data
from crypto_backtest.features import sma, rsi

# Load data
data = load_data(['BTC/USDT'], 'binance', '1h', '2024-01-01', '2024-12-31')

# Define strategy
def my_strategy(data, position, timestamp, **params):
    price = data['BTC/USDT']['ohlcv']['close']
    ma = sma(price, params['ma_period'])
    
    if price.iloc[-1] > ma.iloc[-1] and position.get('BTC/USDT', 0) == 0:
        return [{'symbol': 'BTC/USDT', 'side': 'buy', 'size': 0.1}]
    elif price.iloc[-1] < ma.iloc[-1] and position.get('BTC/USDT', 0) > 0:
        return [{'symbol': 'BTC/USDT', 'side': 'sell', 'size': 0.1}]
    
    return []

# Run backtest
results = run_backtest(
    data=data,
    strategy=my_strategy,
    initial_capital=10000,
    params={'ma_period': 20}
)

# View results
print(results.summary())
results.plot()
```

## Documentation

See the `notebooks/examples/` directory for comprehensive examples.
