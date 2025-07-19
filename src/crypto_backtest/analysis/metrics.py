"""
Performance metrics calculation
"""

import pandas as pd
import numpy as np
from typing import Dict


def calculate_metrics(equity_curve: pd.Series, trades: pd.DataFrame, 
                     initial_capital: float) -> Dict[str, float]:
    """Calculate performance metrics"""
    metrics = {}
    
    # Returns
    returns = equity_curve.pct_change().dropna()
    metrics['total_return'] = (equity_curve.iloc[-1] - initial_capital) / initial_capital
    
    # Sharpe ratio (annualized)
    if len(returns) > 0:
        metrics['sharpe_ratio'] = sharpe_ratio(returns)
    else:
        metrics['sharpe_ratio'] = 0
    
    # Max drawdown
    metrics['max_drawdown'] = max_drawdown(equity_curve)
    
    # Trade statistics
    if len(trades) > 0:
        metrics['win_rate'] = win_rate(trades)
        metrics['profit_factor'] = profit_factor(trades)
        metrics['avg_trade_return'] = avg_trade_return(trades)
        metrics['avg_trade_duration'] = avg_trade_duration(trades)
    else:
        metrics['win_rate'] = 0
        metrics['profit_factor'] = 0
        metrics['avg_trade_return'] = 0
        metrics['avg_trade_duration'] = pd.Timedelta(0)
    
    return metrics


def sharpe_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Calculate annualized Sharpe ratio"""
    if len(returns) < 2:
        return 0
    
    mean_return = returns.mean()
    std_return = returns.std()
    
    if std_return == 0:
        return 0
    
    # Annualize
    sharpe = mean_return / std_return * np.sqrt(periods_per_year)
    return sharpe


def max_drawdown(equity_curve: pd.Series) -> float:
    """Calculate maximum drawdown"""
    cumulative = (1 + equity_curve.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def win_rate(trades: pd.DataFrame) -> float:
    """Calculate win rate"""
    if len(trades) == 0:
        return 0
    
    # Group by symbol to match buy/sell pairs
    wins = 0
    total = 0
    
    # Simple approach - calculate P&L for each trade
    for i, trade in trades.iterrows():
        if i > 0:  # Skip first trade
            if trade['side'] != trades.iloc[i-1]['side']:  # Opposite side
                # Calculate P&L
                if trade['side'] == 'sell':
                    pnl = trade['price'] - trades.iloc[i-1]['price']
                else:
                    pnl = trades.iloc[i-1]['price'] - trade['price']
                
                if pnl > 0:
                    wins += 1
                total += 1
    
    return wins / total if total > 0 else 0


def profit_factor(trades: pd.DataFrame) -> float:
    """Calculate profit factor"""
    if len(trades) < 2:
        return 0
    
    gross_profit = 0
    gross_loss = 0
    
    # Calculate P&L for each trade pair
    for i in range(1, len(trades)):
        if trades.iloc[i]['side'] != trades.iloc[i-1]['side']:
            if trades.iloc[i]['side'] == 'sell':
                pnl = (trades.iloc[i]['price'] - trades.iloc[i-1]['price']) * trades.iloc[i]['size']
            else:
                pnl = (trades.iloc[i-1]['price'] - trades.iloc[i]['price']) * trades.iloc[i]['size']
            
            if pnl > 0:
                gross_profit += pnl
            else:
                gross_loss += abs(pnl)
    
    return gross_profit / gross_loss if gross_loss > 0 else float('inf')


def avg_trade_return(trades: pd.DataFrame) -> float:
    """Calculate average trade return"""
    if len(trades) < 2:
        return 0
    
    returns = []
    for i in range(1, len(trades)):
        if trades.iloc[i]['side'] != trades.iloc[i-1]['side']:
            if trades.iloc[i]['side'] == 'sell':
                ret = (trades.iloc[i]['price'] - trades.iloc[i-1]['price']) / trades.iloc[i-1]['price']
            else:
                ret = (trades.iloc[i-1]['price'] - trades.iloc[i]['price']) / trades.iloc[i]['price']
            returns.append(ret)
    
    return np.mean(returns) if returns else 0


def avg_trade_duration(trades: pd.DataFrame) -> pd.Timedelta:
    """Calculate average trade duration"""
    if len(trades) < 2:
        return pd.Timedelta(0)
    
    durations = []
    for i in range(1, len(trades)):
        if trades.iloc[i]['side'] != trades.iloc[i-1]['side']:
            duration = trades.iloc[i]['timestamp'] - trades.iloc[i-1]['timestamp']
            durations.append(duration)
    
    return pd.Timedelta(np.mean(durations)) if durations else pd.Timedelta(0)
