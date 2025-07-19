"""
Strategy optimization functions
"""

import optuna
import pandas as pd
import numpy as np
from typing import Dict, Callable, Any, Tuple
from ..api.backtest import run_backtest


def optimize_strategy(
    data: Dict[str, Dict],
    strategy: Callable,
    param_space: Dict[str, Tuple[float, float]],
    metric: str = 'sharpe_ratio',
    n_trials: int = 100,
    n_jobs: int = 1,
    initial_capital: float = 10000,
    commission: float = 0.001,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Optimize strategy parameters using Optuna
    
    Args:
        data: Market data
        strategy: Strategy function
        param_space: Parameter search space
        metric: Metric to optimize
        n_trials: Number of optimization trials
        n_jobs: Number of parallel jobs
        initial_capital: Starting capital
        commission: Trading commission
        verbose: Show optimization progress
    
    Returns:
        Best parameters and optimization history
    """
    
    def objective(trial):
        # Sample parameters
        params = {}
        for param_name, (low, high) in param_space.items():
            if isinstance(low, int) and isinstance(high, int):
                params[param_name] = trial.suggest_int(param_name, low, high)
            else:
                params[param_name] = trial.suggest_float(param_name, low, high)
        
        # Run backtest
        try:
            results = run_backtest(
                data=data,
                strategy=strategy,
                initial_capital=initial_capital,
                params=params,
                commission=commission,
                verbose=False
            )
            
            # Return metric to optimize
            return results.metrics.get(metric, 0)
        except Exception as e:
            if verbose:
                print(f"Trial failed: {e}")
            return -float('inf')
    
    # Create study
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=n_trials, n_jobs=n_jobs, show_progress_bar=verbose)
    
    # Get best parameters
    best_params = study.best_params
    best_value = study.best_value
    
    # Run final backtest with best params
    final_results = run_backtest(
        data=data,
        strategy=strategy,
        initial_capital=initial_capital,
        params=best_params,
        commission=commission,
        verbose=False
    )
    
    return {
        'best_params': best_params,
        'best_value': best_value,
        'study': study,
        'final_results': final_results
    }


def walk_forward_analysis(
    data: Dict[str, Dict],
    strategy: Callable,
    param_space: Dict[str, Tuple[float, float]],
    train_periods: int = 252,
    test_periods: int = 63,
    step_size: int = 21,
    metric: str = 'sharpe_ratio',
    n_trials: int = 50
) -> pd.DataFrame:
    """
    Walk-forward optimization analysis
    
    Args:
        data: Market data
        strategy: Strategy function
        param_space: Parameter search space
        train_periods: Number of periods for training
        test_periods: Number of periods for testing
        step_size: Step size for rolling window
        metric: Metric to optimize
        n_trials: Trials per optimization window
    
    Returns:
        DataFrame with walk-forward results
    """
    # Get timestamps from data
    all_timestamps = set()
    for symbol_data in data.values():
        if 'ohlcv' in symbol_data:
            all_timestamps.update(symbol_data['ohlcv'].index)
    timestamps = sorted(list(all_timestamps))
    
    results = []
    
    # Rolling window optimization
    for i in range(0, len(timestamps) - train_periods - test_periods, step_size):
        train_start = i
        train_end = i + train_periods
        test_start = train_end
        test_end = test_start + test_periods
        
        if test_end >= len(timestamps):
            break
        
        # Filter data for train period
        train_data = {}
        for symbol, symbol_data in data.items():
            train_data[symbol] = {
                'ohlcv': symbol_data['ohlcv'].iloc[train_start:train_end]
            }
        
        # Optimize on training data
        opt_results = optimize_strategy(
            train_data, strategy, param_space,
            metric=metric, n_trials=n_trials, verbose=False
        )
        
        # Test on out-of-sample data
        test_data = {}
        for symbol, symbol_data in data.items():
            test_data[symbol] = {
                'ohlcv': symbol_data['ohlcv'].iloc[test_start:test_end]
            }
        
        test_results = run_backtest(
            test_data, strategy,
            params=opt_results['best_params'],
            verbose=False
        )
        
        results.append({
            'train_start': timestamps[train_start],
            'train_end': timestamps[train_end],
            'test_start': timestamps[test_start],
            'test_end': timestamps[test_end],
            'best_params': opt_results['best_params'],
            'train_metric': opt_results['best_value'],
            'test_metric': test_results.metrics.get(metric, 0),
            'test_return': test_results.metrics['total_return']
        })
    
    return pd.DataFrame(results)
