"""
Plotting and visualization functions
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_results(results):
    """Create interactive plot of backtest results"""
    # Create figure with secondary y-axis for the top subplot
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Equity Curve & Positions', 'Drawdown', 'Trade Distribution'),
        vertical_spacing=0.1,
        row_heights=[0.5, 0.25, 0.25],
        specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # 1. Equity curve (primary y-axis) - continuous line
    fig.add_trace(
        go.Scatter(
            x=results.equity_curve.index,
            y=results.equity_curve.values,
            name='Equity',
            line=dict(color='blue', width=2),
            mode='lines',
            showlegend=True
        ),
        row=1, col=1, secondary_y=False
    )
    
    # Calculate position over time
    position_series = _calculate_position_series(results.trades, results.equity_curve.index)
    
    # 2. Position (secondary y-axis) - dotted green line, no fill
    if not position_series.empty:
        fig.add_trace(
            go.Scatter(
                x=position_series.index,
                y=position_series.values,
                name='Position',
                line=dict(color='green', width=2, dash='dot'),
                mode='lines',
                showlegend=True
            ),
            row=1, col=1, secondary_y=True
        )
    
    # 3. Drawdown subplot
    cumulative = (1 + results.equity_curve.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    fig.add_trace(
        go.Scatter(
            x=drawdown.index,
            y=drawdown.values * 100,  # Convert to percentage
            fill='tozeroy',
            name='Drawdown',
            line=dict(color='red', width=1),
            showlegend=False
        ),
        row=2, col=1
    )
    
    # 4. Trade returns distribution
    if len(results.trades) > 1:
        trade_returns = []
        for i in range(1, len(results.trades)):
            if results.trades.iloc[i]['side'] != results.trades.iloc[i-1]['side']:
                if results.trades.iloc[i]['side'] == 'sell':
                    ret = (results.trades.iloc[i]['price'] - results.trades.iloc[i-1]['price']) / results.trades.iloc[i-1]['price']
                else:
                    ret = (results.trades.iloc[i-1]['price'] - results.trades.iloc[i]['price']) / results.trades.iloc[i]['price']
                trade_returns.append(ret * 100)  # Convert to percentage
        
        if trade_returns:
            fig.add_trace(
                go.Histogram(
                    x=trade_returns,
                    name='Trade Returns',
                    nbinsx=30,
                    showlegend=False
                ),
                row=3, col=1
            )
    
    # Update layout
    fig.update_layout(
        title='Backtest Results',
        height=900,
        showlegend=True,
        template='plotly_white',
        hovermode='x unified'
    )
    
    # Update axes labels
    fig.update_xaxes(title_text='Date', row=3, col=1)
    fig.update_yaxes(title_text='Equity ($)', row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text='Position Size', row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text='Drawdown (%)', row=2, col=1)
    fig.update_yaxes(title_text='Frequency', row=3, col=1)
    fig.update_xaxes(title_text='Trade Return (%)', row=3, col=1)
    
    return fig


def _calculate_position_series(trades, timestamps):
    """Calculate position size over time from trades"""
    if len(trades) == 0:
        return pd.Series()
    
    # Initialize position tracking
    positions = {}
    position_history = []
    
    # Create a series with all timestamps
    position_series = pd.Series(index=timestamps, data=0.0)
    
    # Track position changes from trades
    for _, trade in trades.iterrows():
        symbol = trade['symbol']
        
        if symbol not in positions:
            positions[symbol] = 0
        
        # Update position
        if trade['side'] == 'buy':
            positions[symbol] += trade['size']
        else:
            positions[symbol] -= trade['size']
        
        # Record total position at this timestamp
        total_position = sum(positions.values())
        position_series.loc[trade['timestamp']:] = total_position
    
    return position_series


def plot_equity(equity_curve: pd.Series):
    """Plot simple equity curve"""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=equity_curve.index,
            y=equity_curve.values,
            mode='lines',
            name='Equity',
            line=dict(color='blue', width=2)
        )
    )
    
    fig.update_layout(
        title='Equity Curve',
        xaxis_title='Date',
        yaxis_title='Equity ($)',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig
