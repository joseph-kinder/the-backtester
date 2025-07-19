# Installation Guide

## Quick Installation (Recommended)

For a minimal installation with core features only:

```bash
pip install -r requirements-minimal.txt
pip install -e .
```

## Full Installation

For the complete feature set including all optional dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

## Windows Users - TA-Lib Installation

TA-Lib requires Microsoft Visual C++ Build Tools on Windows. If you need TA-Lib:

1. **Option 1: Use pre-built wheels**
   ```bash
   # Download the appropriate wheel from:
   # https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
   
   # For Python 3.12 64-bit:
   pip install TA_Lib-0.4.28-cp312-cp312-win_amd64.whl
   ```

2. **Option 2: Install build tools**
   - Download and install Microsoft C++ Build Tools from:
     https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Then: `pip install ta-lib`

3. **Option 3: Use without TA-Lib**
   - The framework includes its own implementations of common indicators
   - TA-Lib is optional and not required for most strategies

## Troubleshooting

### Import Errors
If you get import errors, make sure you're in the project directory:
```bash
cd the-backtester
pip install -e .
```

### Missing Dependencies
Install any missing dependencies individually:
```bash
pip install numpy pandas scipy statsmodels ccxt plotly
```

### Conda Environment
If using conda, create a new environment:
```bash
conda create -n crypto-backtest python=3.12
conda activate crypto-backtest
pip install -r requirements-minimal.txt
pip install -e .
```
