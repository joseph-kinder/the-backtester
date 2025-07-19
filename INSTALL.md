# Installation Guide

## Standard Installation

For a complete installation with all features:

```bash
pip install -r requirements.txt
pip install -e .
```

## Troubleshooting

### Import Errors
If you get import errors, make sure you're in the project directory:
```bash
cd the-backtester
pip install -e .
```

### Missing Dependencies
If you encounter issues, you can try installing the core dependencies individually before running the main installation command:
```bash
pip install numpy pandas scipy statsmodels ccxt plotly
```

### Conda Environment
If using conda, create a new environment:
```bash
conda create -n crypto-backtest python=3.12
conda activate crypto-backtest
pip install -r requirements.txt
pip install -e .
```
