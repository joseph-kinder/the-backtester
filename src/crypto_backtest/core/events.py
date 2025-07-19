"""
Event system for backtesting engine (internal use)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import pandas as pd


class EventType(Enum):
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"


@dataclass
class Event:
    """Base event class"""
    timestamp: pd.Timestamp
    type: EventType = field(init=False)


@dataclass
class MarketEvent(Event):
    """Market data update event"""
    symbol: str
    data: Dict[str, Any]
    
    def __post_init__(self):
        self.type = EventType.MARKET


@dataclass
class SignalEvent(Event):
    """Trading signal event"""
    symbol: str
    signal_type: str
    strength: float
    
    def __post_init__(self):
        self.type = EventType.SIGNAL


@dataclass
class OrderEvent(Event):
    """Order event"""
    symbol: str
    order_type: str  # 'market' or 'limit'
    side: str  # 'buy' or 'sell'
    size: float
    price: Optional[float] = None
    
    def __post_init__(self):
        self.type = EventType.ORDER


@dataclass
class FillEvent(Event):
    """Fill event when order is executed"""
    symbol: str
    side: str
    size: float
    price: float
    commission: float
    slippage: float
    
    def __post_init__(self):
        self.type = EventType.FILL
