from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crypto-backtest",
    version="0.1.0",
    author="Joseph",
    description="A comprehensive Python toolkit for backtesting cryptocurrency trading strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/the-backtester",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "numba>=0.54.0",
        "statsmodels>=0.13.0",
        "ccxt>=4.0.0",
        "plotly>=5.0.0",
        "matplotlib>=3.4.0",
        "onnxruntime>=1.12.0",
        "scikit-learn>=1.0.0",
        "optuna>=3.0.0",
        "pyarrow>=9.0.0",
        "h5py>=3.0.0",
        "tqdm>=4.62.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "talib": [
            "ta-lib>=0.4.25",  # Optional, requires C++ build tools
        ]
    },
)
