"""
Feature calculation library
"""

# Import all features for easy access
from .technical import (
    sma, ema, wma, vwap,
    atr, bollinger_bands, realized_volatility,
    rsi, macd, stochastic,
    obv, volume_profile
)

from .statistical import (
    zscore, rolling_corr, rolling_beta,
    cointegration_test, half_life, hurst_exponent,
    pca_factors
)

from .microstructure import (
    bid_ask_spread, effective_spread,
    book_imbalance, book_pressure,
    vpin, trade_flow_toxicity,
    kyle_lambda, aggressive_flow
)

from .arbitrage import (
    calc_arb_spread, triangular_arb,
    funding_arb, lead_lag_signal,
    granger_causality
)

__all__ = [
    # Technical
    'sma', 'ema', 'wma', 'vwap',
    'atr', 'bollinger_bands', 'realized_volatility',
    'rsi', 'macd', 'stochastic',
    'obv', 'volume_profile',
    
    # Statistical
    'zscore', 'rolling_corr', 'rolling_beta',
    'cointegration_test', 'half_life', 'hurst_exponent',
    'pca_factors',
    
    # Microstructure
    'bid_ask_spread', 'effective_spread',
    'book_imbalance', 'book_pressure',
    'vpin', 'trade_flow_toxicity',
    'kyle_lambda', 'aggressive_flow',
    
    # Arbitrage
    'calc_arb_spread', 'triangular_arb',
    'funding_arb', 'lead_lag_signal',
    'granger_causality'
]
