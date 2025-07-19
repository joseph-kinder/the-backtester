"""
Main backtesting API
"""

import pandas as pd
import numpy as np
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass

from ..core.engine import BacktestEngine
from ..analysis.metrics import calculate_metrics
from ..analysis.plots import plot_results


@dataclass
class BacktestResults:
    """Container for backtest results"""
    equity_curve: pd.Series
    trades: pd.DataFrame
    positions: Dict
    metrics: Dict
    initial_capital: float
    final_capital: float
    final_equity: float
    
    def plot(self):
        """Plot interactive results"""
        return plot_results(self)
    
    def summary(self) -> str:
        """Print summary statistics"""
        summary_lines = [
            "=== Backtest Results ===",
            f"Initial Capital: ${self.initial_capital:,.2f}",
            f"Final Equity: ${self.final_equity:,.2f}",
            f"Total Return: {self.metrics['total_return']:.2%}",
            f"Sharpe Ratio: {self.metrics['sharpe_ratio']:.2f}",
            f"Max Drawdown: {self.metrics['max_drawdown']:.2%}",
            f"Win Rate: {self.metrics['win_rate']:.2%}",
            f"Number of Trades: {len(self.trades)}",
            "="*24
        ]
        return "\n".join(summary_lines)
    
    def export(self, filepath: str):
        """Export results to file"""
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)


def run_backtest(
    data: Dict[str, Dict],
    strategy: Callable,
    initial_capital: float = 10000,
    params: Optional[Dict[str, Any]] = None,
    commission: float = 0.001,
    slippage_model: str = 'linear',
    slippage_bps: float = 10,
    position_limits: Optional[Dict] = None,
    risk_limits: Optional[Dict] = None,
    verbose: bool = True
) -> BacktestResults:
    """
    Run backtest on strategy
    
    Args:
        data: Market data dictionary
        strategy: Strategy function
        initial_capital: Starting capital
        params: Strategy parameters
        commission: Trading commission (e.g., 0.001 = 0.1%)
        slippage_model: Slippage model ('zero', 'linear', 'square_root')
        slippage_bps: Slippage in basis points
        position_limits: Position size limits
        risk_limits: Risk management limits
        verbose: Show progress bar
    
    Returns:
        BacktestResults object
    """
    # Initialize engine
    engine = BacktestEngine(
        data=data,
        initial_capital=initial_capital,
        commission=commission,
        slippage_model=slippage_model,
        slippage_bps=slippage_bps,
        position_limits=position_limits,
        risk_limits=risk_limits,
        verbose=verbose
    )
    
    # Run backtest
    raw_results = engine.run(strategy, params)
    
    # Calculate metrics
    metrics = calculate_metrics(
        equity_curve=raw_results['equity_curve'],
        trades=raw_results['trades'],
        initial_capital=initial_capital
    )
    
    # Create results object
    results = BacktestResults(
        equity_curve=raw_results['equity_curve'],
        trades=raw_results['trades'],
        positions=raw_results['final_portfolio'],
        metrics=metrics,
        initial_capital=raw_results['initial_capital'],
        final_capital=raw_results['final_capital'],
        final_equity=raw_results['final_equity']
    )
    
    return results
