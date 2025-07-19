"""
Core backtesting engine (internal use)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Callable, Any, Optional
from collections import deque
from tqdm import tqdm

from .events import MarketEvent, OrderEvent, FillEvent
from .portfolio import Portfolio
from .execution import ExecutionHandler


class BacktestEngine:
    """Main backtesting engine"""
    
    def __init__(
        self,
        data: Dict[str, Dict],
        initial_capital: float,
        commission: float = 0.001,
        slippage_model: str = 'linear',
        slippage_bps: float = 10,
        position_limits: Optional[Dict] = None,
        risk_limits: Optional[Dict] = None,
        verbose: bool = True
    ):
        self.data = data
        self.initial_capital = initial_capital
        self.commission = commission
        self.position_limits = position_limits or {}
        self.risk_limits = risk_limits or {}
        self.verbose = verbose
        
        # Initialize components
        self.portfolio = Portfolio(initial_capital)
        self.execution = ExecutionHandler(commission, slippage_model, slippage_bps)
        
        # Get all timestamps
        self.timestamps = self._get_all_timestamps()
        self.current_idx = 0
        
        # Event queue
        self.events = deque()
        
        # Results storage
        self.equity_curve = []
        self.positions_history = []
    
    def _get_all_timestamps(self) -> List[pd.Timestamp]:
        """Get unified timestamp index from all data"""
        all_timestamps = set()
        
        for symbol, data_dict in self.data.items():
            if 'ohlcv' in data_dict and not data_dict['ohlcv'].empty:
                all_timestamps.update(data_dict['ohlcv'].index)
        
        return sorted(list(all_timestamps))
    
    def run(self, strategy: Callable, params: Dict[str, Any] = None) -> Dict:
        """Run backtest with given strategy"""
        params = params or {}
        
        # Progress bar
        pbar = tqdm(total=len(self.timestamps), desc="Backtesting", disable=not self.verbose)
        
        for self.current_idx, timestamp in enumerate(self.timestamps):
            # Generate market events
            self._update_market_data(timestamp)
            
            # Get current data snapshot
            current_data = self._get_current_data(timestamp)
            
            # Get current positions
            positions = self.portfolio.get_position_dict()
            
            # Call strategy
            try:
                orders = strategy(current_data, positions, timestamp, **params)
            except Exception as e:
                if self.verbose:
                    print(f"Strategy error at {timestamp}: {e}")
                orders = []
            
            # Process orders
            self._process_orders(orders, timestamp, current_data)
            
            # Update portfolio value
            self._update_portfolio_value(timestamp, current_data)
            
            pbar.update(1)
    
    def run(self, strategy: Callable, params: Dict[str, Any] = None) -> Dict:
        """Run backtest with given strategy"""
        params = params or {}
        
        # Progress bar
        pbar = tqdm(total=len(self.timestamps), desc="Backtesting", disable=not self.verbose)
        
        for self.current_idx, timestamp in enumerate(self.timestamps):
            # Generate market events
            self._update_market_data(timestamp)
            
            # Get current data snapshot
            current_data = self._get_current_data(timestamp)
            
            # Get current positions
            positions = self.portfolio.get_position_dict()
            
            # Call strategy
            try:
                orders = strategy(current_data, positions, timestamp, **params)
            except Exception as e:
                if self.verbose:
                    print(f"Strategy error at {timestamp}: {e}")
                orders = []
            
            # Process orders
            self._process_orders(orders, timestamp, current_data)
            
            # Update portfolio value
            self._update_portfolio_value(timestamp, current_data)
            
            pbar.update(1)
        
        pbar.close()
        
        return self._compile_results()
    
    def _update_market_data(self, timestamp: pd.Timestamp):
        """Update market data for current timestamp"""
        for symbol, data_dict in self.data.items():
            if 'ohlcv' in data_dict and timestamp in data_dict['ohlcv'].index:
                event = MarketEvent(
                    timestamp=timestamp,
                    symbol=symbol,
                    data={'ohlcv': data_dict['ohlcv'].loc[timestamp]}
                )
                self.events.append(event)
    
    def _get_current_data(self, timestamp: pd.Timestamp) -> Dict:
        """Get data snapshot up to current timestamp"""
        result = {}
        
        for symbol, data_dict in self.data.items():
            result[symbol] = {}
            
            # OHLCV data
            if 'ohlcv' in data_dict:
                df = data_dict['ohlcv']
                result[symbol]['ohlcv'] = df[df.index <= timestamp]
            
            # Orderbook data (if available)
            if 'orderbook' in data_dict and not data_dict['orderbook'].empty:
                result[symbol]['orderbook'] = data_dict['orderbook'].loc[timestamp] if timestamp in data_dict['orderbook'].index else {}
            
            # Trade data (if available)
            if 'trades' in data_dict and not data_dict['trades'].empty:
                trades = data_dict['trades']
                result[symbol]['trades'] = trades[trades.index <= timestamp]
        
        return result
    
    def _process_orders(self, orders: Any, timestamp: pd.Timestamp, current_data: Dict):
        """Process orders from strategy"""
        if orders == 'close_all':
            # Close all positions
            for symbol, position in list(self.portfolio.positions.items()):
                order = OrderEvent(
                    timestamp=timestamp,
                    symbol=symbol,
                    order_type='market',
                    side='sell' if position.size > 0 else 'buy',
                    size=abs(position.size)
                )
                self._execute_order(order, current_data)
        
        elif isinstance(orders, list):
            for order_dict in orders:
                if self._validate_order(order_dict):
                    order = OrderEvent(
                        timestamp=timestamp,
                        symbol=order_dict['symbol'],
                        order_type=order_dict.get('type', 'market'),
                        side=order_dict['side'],
                        size=order_dict['size'],
                        price=order_dict.get('price')
                    )
                    self._execute_order(order, current_data)
    
    def _validate_order(self, order_dict: Dict) -> bool:
        """Validate order parameters"""
        required = ['symbol', 'side', 'size']
        return all(key in order_dict for key in required)
    
    def _execute_order(self, order: OrderEvent, current_data: Dict):
        """Execute order with slippage and commission"""
        if order.symbol not in current_data:
            return
        
        # Get current price
        if 'ohlcv' in current_data[order.symbol]:
            ohlcv = current_data[order.symbol]['ohlcv']
            if not ohlcv.empty:
                current_price = ohlcv.iloc[-1]['close']
            else:
                return
        else:
            return
        
        # Get orderbook if available
        orderbook = current_data[order.symbol].get('orderbook', {})
        
        # Execute with slippage
        fill = self.execution.execute_order(order, current_price, orderbook)
        
        # Update portfolio
        size = fill.size if fill.side == 'buy' else -fill.size
        self.portfolio.update_position(fill.symbol, size, fill.price, fill.timestamp)
        
        # Update cash
        if fill.side == 'buy':
            self.portfolio.cash -= fill.size * fill.price + fill.commission
        else:
            self.portfolio.cash += abs(fill.size) * fill.price - fill.commission
        
        # Record trade
        self.portfolio.record_trade(
            fill.symbol, fill.side, abs(fill.size), 
            fill.price, fill.commission, fill.timestamp
        )
    
    def _update_portfolio_value(self, timestamp: pd.Timestamp, current_data: Dict):
        """Update portfolio equity value"""
        prices = {}
        # Get current prices for all symbols in the data (not just positions)
        for symbol, data_dict in current_data.items():
            if 'ohlcv' in data_dict and not data_dict['ohlcv'].empty:
                prices[symbol] = data_dict['ohlcv'].iloc[-1]['close']
        
        equity = self.portfolio.calculate_equity(prices)
        self.portfolio.equity_curve.append(equity)
        self.portfolio.timestamps.append(timestamp)

    def _compile_results(self) -> Dict:
        """Compile backtest results"""
        return {
            'equity_curve': pd.Series(
                data=self.portfolio.equity_curve,
                index=self.portfolio.timestamps
            ),
            'trades': pd.DataFrame(self.portfolio.trades),
            'final_portfolio': self.portfolio.get_position_dict(),
            'initial_capital': self.initial_capital,
            'final_capital': self.portfolio.cash,
            'final_equity': self.portfolio.equity_curve[-1] if self.portfolio.equity_curve else self.initial_capital
        }
