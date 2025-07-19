"""
Portfolio tracking and management (internal use)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Position:
    """Single position in a symbol"""
    symbol: str
    size: float
    avg_price: float
    timestamp: pd.Timestamp
    
    @property
    def market_value(self):
        return self.size * self.avg_price
    
    @property
    def is_long(self):
        return self.size > 0
    
    @property
    def is_short(self):
        return self.size < 0


@dataclass
class Portfolio:
    """Portfolio state tracker"""
    initial_capital: float
    cash: float = field(init=False)
    positions: Dict[str, Position] = field(default_factory=dict)
    equity_curve: List[float] = field(default_factory=list)
    timestamps: List[pd.Timestamp] = field(default_factory=list)
    trades: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        self.cash = self.initial_capital
    
    def update_position(self, symbol: str, size: float, price: float, timestamp: pd.Timestamp):
        """Update or create position"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            new_size = pos.size + size
            
            if abs(new_size) < 1e-8:  # Position closed
                del self.positions[symbol]
            else:
                # Update average price
                if pos.size * size > 0:  # Adding to position
                    pos.avg_price = (pos.avg_price * abs(pos.size) + price * abs(size)) / abs(new_size)
                pos.size = new_size
        else:
            if abs(size) > 1e-8:
                self.positions[symbol] = Position(symbol, size, price, timestamp)
    
    def get_position_dict(self) -> Dict[str, float]:
        """Get position sizes as dict for strategy function"""
        result = {symbol: pos.size for symbol, pos in self.positions.items()}
        result['cash'] = self.cash
        return result
    
    def calculate_equity(self, prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        equity = self.cash
        for symbol, pos in self.positions.items():
            if symbol in prices:
                equity += pos.size * prices[symbol]
        return equity
    
    def record_trade(self, symbol: str, side: str, size: float, price: float, 
                    commission: float, timestamp: pd.Timestamp):
        """Record executed trade"""
        self.trades.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'side': side,
            'size': size,
            'price': price,
            'commission': commission,
            'value': size * price
        })
