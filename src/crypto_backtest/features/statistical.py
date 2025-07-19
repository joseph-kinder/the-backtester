"""
Statistical features for strategy development
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Optional


def zscore(series: pd.Series, period: int) -> pd.Series:
    """Rolling Z-score"""
    mean = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    return (series - mean) / std


def rolling_corr(series1: pd.Series, series2: pd.Series, period: int) -> pd.Series:
    """Rolling correlation"""
    return series1.rolling(window=period).corr(series2)


def rolling_beta(series1: pd.Series, series2: pd.Series, period: int) -> pd.Series:
    """Rolling beta (series1 relative to series2)"""
    cov = series1.rolling(window=period).cov(series2)
    var = series2.rolling(window=period).var()
    return cov / var


def cointegration_test(series1: pd.Series, series2: pd.Series, method: str = 'engle-granger') -> float:
    """Test for cointegration between two series"""
    if method == 'engle-granger':
        # Simple Engle-Granger test
        from statsmodels.tsa.stattools import coint
        _, p_value, _ = coint(series1.dropna(), series2.dropna())
        return p_value
    else:
        # Placeholder for other methods
        return 1.0


def half_life(spread: pd.Series) -> float:
    """Calculate half-life of mean reversion"""
    spread_lag = spread.shift(1)
    spread_diff = spread - spread_lag
    spread_lag = spread_lag[1:]
    spread_diff = spread_diff[1:]
    
    # OLS regression
    model = np.polyfit(spread_lag, spread_diff, 1)
    half_life = -np.log(2) / model[0]
    return half_life


def hurst_exponent(series: pd.Series, max_lag: int = 20) -> float:
    """Calculate Hurst exponent"""
    lags = range(2, max_lag)
    tau = [np.sqrt(np.std(np.subtract(series[lag:], series[:-lag]))) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    return poly[0] * 2.0


def pca_factors(returns_matrix: pd.DataFrame, n_components: int = 3) -> pd.DataFrame:
    """Extract PCA factors from returns matrix"""
    from sklearn.decomposition import PCA
    
    # Standardize returns
    returns_std = (returns_matrix - returns_matrix.mean()) / returns_matrix.std()
    
    # Fit PCA
    pca = PCA(n_components=n_components)
    factors = pca.fit_transform(returns_std.fillna(0))
    
    # Return as DataFrame
    factor_df = pd.DataFrame(
        factors,
        index=returns_matrix.index,
        columns=[f'PC{i+1}' for i in range(n_components)]
    )
    
    return factor_df
