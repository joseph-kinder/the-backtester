"""
Arbitrage calculation features
"""

import pandas as pd
import numpy as np
from typing import Tuple


def calc_arb_spread(price1: float, price2: float, fee1: float = 0, fee2: float = 0) -> float:
    """
    Calculate arbitrage spread between two prices
    
    Args:
        price1: Price on exchange 1
        price2: Price on exchange 2
        fee1: Trading fee on exchange 1
        fee2: Trading fee on exchange 2
    
    Returns:
        Arbitrage spread (positive means profit from buying on 2 and selling on 1)
    """
    # Buy on exchange 2, sell on exchange 1
    buy_cost = price2 * (1 + fee2)
    sell_revenue = price1 * (1 - fee1)
    
    return (sell_revenue - buy_cost) / buy_cost


def triangular_arb(price_abc: float, price_bca: float, price_cab: float) -> float:
    """Calculate triangular arbitrage opportunity"""
    # Calculate if profitable to go A->B->C->A
    return price_abc * price_bca * price_cab - 1


def funding_arb(spot_price: float, perp_price: float, funding_rate: float) -> float:
    """
    Calculate funding arbitrage opportunity
    
    Args:
        spot_price: Spot market price
        perp_price: Perpetual futures price
        funding_rate: Current funding rate (8-hour)
    
    Returns:
        Expected profit from funding arbitrage
    """
    basis = (perp_price - spot_price) / spot_price
    # Annualized funding (3 payments per day * 365 days)
    annualized_funding = funding_rate * 3 * 365
    
    return annualized_funding - basis


def lead_lag_signal(series1: pd.Series, series2: pd.Series, max_lag: int = 10) -> pd.Series:
    """
    Calculate lead-lag relationship signal
    
    Returns signal indicating when series1 leads series2
    """
    correlations = []
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            corr = series1.iloc[:lag].corr(series2.iloc[-lag:])
        elif lag > 0:
            corr = series1.iloc[lag:].corr(series2.iloc[:-lag])
        else:
            corr = series1.corr(series2)
        correlations.append(corr)
    
    # Find optimal lag
    optimal_lag = np.argmax(correlations) - max_lag
    
    # Create signal based on optimal lag
    if optimal_lag > 0:
        # series1 leads series2
        signal = series1.shift(optimal_lag) - series2
    else:
        # series2 leads series1
        signal = series1 - series2.shift(-optimal_lag)
    
    return signal


def granger_causality(series1: pd.Series, series2: pd.Series, lags: int = 5) -> Tuple[float, float]:
    """
    Granger causality test
    
    Returns:
        p-value for series1 -> series2 causality
        p-value for series2 -> series1 causality
    """
    from statsmodels.tsa.stattools import grangercausalitytests
    
    # Prepare data
    data = pd.DataFrame({'x': series1, 'y': series2}).dropna()
    
    # Test both directions
    try:
        result1 = grangercausalitytests(data[['y', 'x']], lags, verbose=False)
        result2 = grangercausalitytests(data[['x', 'y']], lags, verbose=False)
        
        # Extract p-values
        p1 = min(result1[i][0]['ssr_ftest'][1] for i in range(1, lags + 1))
        p2 = min(result2[i][0]['ssr_ftest'][1] for i in range(1, lags + 1))
        
        return p1, p2
    except:
        return 1.0, 1.0
