# Data Directory 📊

This directory contains all raw and processed financial data.

## Structure

```
data/
├── raw/           # Original CSV files from Investing.com
└── processed/     # Cleaned, timestamp-aligned datasets
```

## Raw Data

Original CSV files with the following format:
- **Date**: `MM/DD/YYYY`
- **Price/Close**: Closing price
- **Open/High/Low**: OHLC data
- **Vol.**: Volume with K/M/B suffixes
- **Change %**: Daily percentage change

### Available Datasets

| File | Asset | Description |
|------|-------|-------------|
| `BTC_USD Bitfinex Historical Data.csv` | Bitcoin | Primary crypto asset |
| `ETH_USD Binance Historical Data.csv` | Ethereum | Secondary crypto |
| `Nasdaq 100 Historical Data.csv` | NASDAQ 100 | **Canary signal** for crashes |
| `Apple Stock Price History.csv` | AAPL | Tech stock |
| `Amazon.com Stock Price History.csv` | AMZN | Tech stock |
| `Microsoft Stock Price History.csv` | MSFT | Tech stock |
| `NVIDIA Stock Price History.csv` | NVDA | Tech stock |
| `Tesla Stock Price History.csv` | TSLA | Tech stock |
| `Meta Platforms Stock Price History.csv` | META | Tech stock |
| `Gold Futures Historical Data.csv` | Gold | Safe haven asset |
| `Silver Futures Historical Data.csv` | Silver | Precious metal |
| `Crude Oil WTI Futures Historical Data.csv` | WTI | Commodity |

## Processed Data

After running `data_handler.py`, cleaned files are saved here with:
- Standardized column names (`Close`, `Open`, `High`, `Low`, `Volume`)
- Parsed numeric values (no commas or K/M/B suffixes)
- Aligned timestamps across datasets
- Calculated returns

## Usage

```python
from src.data_handler import DataHandler

handler = DataHandler(data_dir="data/raw")
crypto_df, nasdaq_df = handler.load_and_prepare(
    "BTC_USD Bitfinex Historical Data.csv",
    "Nasdaq 100 Historical Data.csv"
)
```
