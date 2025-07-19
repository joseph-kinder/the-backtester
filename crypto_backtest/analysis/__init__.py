"""
Analysis and reporting tools
"""

from .metrics import calculate_metrics
from .plots import plot_results, plot_equity

__all__ = [
    'calculate_metrics',
    'plot_results',
    'plot_equity'
]
