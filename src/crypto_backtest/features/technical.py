"""
Technical indicators for strategy development
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average"""
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average"""
    return series.ewm(span=period, adjust=False).mean()


def wma(series: pd.Series, period: int) -> pd.Series:
    """Weighted Moving Average"""
    weights = np.arange(1, period + 1)
    return series.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)


def vwap(price: pd.Series, volume: pd.Series, period: int) -> pd.Series:
    """Volume Weighted Average Price"""
    typical_price = price
    return (typical_price * volume).rolling(period).sum() / volume.rolling(period).sum()


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
    """Average True Range"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def bollinger_bands(series: pd.Series, period: int, num_std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands (middle, upper, lower)"""
    middle = sma(series, period)
    std = series.rolling(window=period).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    return middle, upper, lower


def realized_volatility(returns: pd.Series, period: int) -> pd.Series:
    """Realized volatility"""
    return returns.rolling(window=period).std() * np.sqrt(252)  # Annualized


def rsi(series: pd.Series, period: int) -> pd.Series:
    """Relative Strength Index"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """MACD (macd line, signal line, histogram)"""
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> Tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator (%K, %D)"""
    lowest_low = low.rolling(window=period).min()
    highest_high = high.rolling(window=period).max()
    k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    k_percent = sma(k_percent, smooth_k)
    d_percent = sma(k_percent, smooth_d)
    return k_percent, d_percent


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On Balance Volume"""
    return (np.sign(close.diff()) * volume).fillna(0).cumsum()


def volume_profile(price: pd.Series, volume: pd.Series, bins: int = 20) -> dict:
    """Volume Profile"""
    price_bins = pd.cut(price, bins=bins)
    volume_by_price = volume.groupby(price_bins).sum()
    poc = volume_by_price.idxmax()  # Point of Control
    return {'profile': volume_by_price, 'poc': poc.mid}
