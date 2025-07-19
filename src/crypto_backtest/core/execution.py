"""
Order execution and slippage modeling (internal use)
"""

import numpy as np
from typing import Dict, Optional
from .events import FillEvent


class ExecutionHandler:
    """Handles order execution with slippage and commission"""
    
    def __init__(self, commission: float = 0.001, slippage_model: str = 'linear', 
                 slippage_bps: float = 10):
        self.commission = commission
        self.slippage_model = slippage_model
        self.slippage_bps = slippage_bps
    
    def execute_order(self, order, current_price: float, orderbook: Optional[Dict] = None) -> FillEvent:
        """Execute order and return fill event"""
        # Calculate slippage
        slippage = self._calculate_slippage(order.size, current_price, order.side, orderbook)
        
        # Adjust price for slippage
        if order.side == 'buy':
            fill_price = current_price + slippage
        else:
            fill_price = current_price - slippage
        
        # Calculate commission
        commission_amount = abs(order.size) * fill_price * self.commission
        
        return FillEvent(
            timestamp=order.timestamp,
            symbol=order.symbol,
            side=order.side,
            size=order.size,
            price=fill_price,
            commission=commission_amount,
            slippage=slippage
        )
    
    def _calculate_slippage(self, size: float, price: float, side: str, 
                           orderbook: Optional[Dict] = None) -> float:
        """Calculate slippage based on model"""
        if self.slippage_model == 'zero':
            return 0.0
        
        elif self.slippage_model == 'linear':
            # Simple linear slippage based on size
            base_slippage = price * self.slippage_bps / 10000
            size_factor = min(abs(size), 10) / 10  # Cap at 10x base size
            return base_slippage * size_factor
        
        elif self.slippage_model == 'square_root':
            # Square root market impact model
            base_slippage = price * self.slippage_bps / 10000
            size_factor = np.sqrt(abs(size))
            return base_slippage * size_factor
        
        else:
            return 0.0
