"""
Crypto Backtest - A comprehensive Python toolkit for backtesting cryptocurrency trading strategies
"""

__version__ = "0.1.0"

# Import main API functions
from .api.backtest import run_backtest
from .data.loaders import load_data, load_orderbook_snapshots, load_trades
from .optimization.optimize import optimize_strategy, walk_forward_analysis

# Import all feature functions for easy access
from .features import *

# Configuration
class Config:
    def __init__(self):
        self.cache_dir = "./data"
        self.default_exchange = "binance"
        self.default_commission = 0.001
        self.progress_bars = True
        self.log_level = "INFO"
    
    def set_cache_dir(self, path):
        self.cache_dir = path
    
    def set_default_exchange(self, exchange):
        self.default_exchange = exchange
    
    def set_default_commission(self, commission):
        self.default_commission = commission
    
    def enable_progress_bars(self, enabled):
        self.progress_bars = enabled

config = Config()

# Expose main functions at package level
__all__ = [
    'run_backtest',
    'load_data',
    'load_orderbook_snapshots',
    'load_trades',
    'optimize_strategy',
    'walk_forward_analysis',
    'config'
]
