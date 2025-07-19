"""
Market microstructure features
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def bid_ask_spread(orderbook: Dict) -> float:
    """Calculate bid-ask spread"""
    if 'bids' in orderbook and 'asks' in orderbook:
        if len(orderbook['bids']) > 0 and len(orderbook['asks']) > 0:
            best_bid = orderbook['bids'][0][0]
            best_ask = orderbook['asks'][0][0]
            return best_ask - best_bid
    return np.nan


def effective_spread(trades: pd.DataFrame, orderbook: Dict) -> float:
    """Calculate effective spread"""
    # Placeholder implementation
    return bid_ask_spread(orderbook) * 0.8


def book_imbalance(orderbook: Dict, levels: int = 5) -> float:
    """Order book imbalance"""
    if 'bids' not in orderbook or 'asks' not in orderbook:
        return 0.0
    
    bid_volume = sum(bid[1] for bid in orderbook['bids'][:levels])
    ask_volume = sum(ask[1] for ask in orderbook['asks'][:levels])
    
    if bid_volume + ask_volume > 0:
        return (bid_volume - ask_volume) / (bid_volume + ask_volume)
    return 0.0


def book_pressure(orderbook: Dict) -> float:
    """Order book pressure indicator"""
    if 'bids' not in orderbook or 'asks' not in orderbook:
        return 0.0
    
    # Weight by distance from mid price
    mid_price = (orderbook['bids'][0][0] + orderbook['asks'][0][0]) / 2
    
    bid_pressure = sum(
        bid[1] / (1 + abs(bid[0] - mid_price) / mid_price)
        for bid in orderbook['bids'][:10]
    )
    
    ask_pressure = sum(
        ask[1] / (1 + abs(ask[0] - mid_price) / mid_price)
        for ask in orderbook['asks'][:10]
    )
    
    return bid_pressure - ask_pressure


def vpin(trades: pd.DataFrame, volume_bucket_size: float) -> pd.Series:
    """Volume-synchronized Probability of Informed Trading"""
    if trades.empty:
        return pd.Series()
    
    # Placeholder implementation
    # Real implementation would bucket trades by volume
    return pd.Series(index=trades.index, data=0.5)


def trade_flow_toxicity(trades: pd.DataFrame) -> float:
    """Measure trade flow toxicity"""
    if trades.empty:
        return 0.0
    
    # Placeholder - would analyze aggressive vs passive flow
    return 0.0


def kyle_lambda(trades: pd.DataFrame, orderbook: Dict) -> float:
    """Kyle's lambda - price impact coefficient"""
    # Placeholder implementation
    return 0.001


def aggressive_flow(trades: pd.DataFrame) -> pd.Series:
    """Aggressive order flow"""
    if trades.empty:
        return pd.Series()
    
    # Placeholder - would classify trades as aggressive/passive
    return pd.Series(index=trades.index, data=0)
