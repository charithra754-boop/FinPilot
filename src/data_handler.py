"""
Data Handler Module
Handles loading, cleaning, and aligning financial datasets.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple


def parse_number(value: str) -> float:
    """
    Parse number strings with commas and K/M/B suffixes.
    
    Args:
        value: String like "88,007.0" or "2.92K" or "302.55M"
        
    Returns:
        Float value
    """
    if pd.isna(value) or value == '-':
        return np.nan
    
    value = str(value).strip().replace('"', '')
    
    # Remove commas
    value = value.replace(',', '')
    
    # Handle K/M/B suffixes
    multiplier = 1
    if value.endswith('K'):
        multiplier = 1000
        value = value[:-1]
    elif value.endswith('M'):
        multiplier = 1_000_000
        value = value[:-1]
    elif value.endswith('B'):
        multiplier = 1_000_000_000
        value = value[:-1]
    
    try:
        return float(value) * multiplier
    except ValueError:
        return np.nan


def parse_percentage(value: str) -> float:
    """
    Parse percentage strings like "-0.63%" to float.
    
    Args:
        value: String like "-0.63%"
        
    Returns:
        Float value (as decimal, e.g., -0.0063)
    """
    if pd.isna(value) or value == '-':
        return np.nan
    
    value = str(value).strip().replace('"', '').replace('%', '')
    
    try:
        return float(value) / 100
    except ValueError:
        return np.nan


class DataHandler:
    """
    Handles loading and preprocessing of financial time series data.
    
    Features:
    - CSV loading with automatic date parsing
    - Forward-fill for missing data
    - Timestamp alignment across multiple datasets
    """
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
    
    def load_investing_csv(
        self, 
        filename: str,
        date_column: str = "Date"
    ) -> pd.DataFrame:
        """
        Load CSV file from Investing.com format.
        
        Args:
            filename: Name of the CSV file
            date_column: Column name containing dates
            
        Returns:
            DataFrame with DateTimeIndex and cleaned numeric columns
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        # Load raw CSV
        df = pd.read_csv(filepath)
        
        # Parse date column
        df[date_column] = pd.to_datetime(df[date_column], format='%m/%d/%Y')
        df = df.set_index(date_column)
        df = df.sort_index()
        
        # Parse numeric columns
        numeric_cols = ['Price', 'Open', 'High', 'Low']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(parse_number)
        
        # Parse volume
        if 'Vol.' in df.columns:
            df['Volume'] = df['Vol.'].apply(parse_number)
            df = df.drop(columns=['Vol.'])
        
        # Parse change percentage
        if 'Change %' in df.columns:
            df['Change'] = df['Change %'].apply(parse_percentage)
            df = df.drop(columns=['Change %'])
        
        # Rename columns to standard format
        df = df.rename(columns={
            'Price': 'Close'
        })
        
        return df
    
    def forward_fill(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Forward-fill missing values in the DataFrame.
        
        Args:
            df: Input DataFrame with potential missing values
            
        Returns:
            DataFrame with forward-filled values
        """
        df_filled = df.ffill().bfill()
        return df_filled
    
    def align_timestamps(
        self, 
        *dataframes: pd.DataFrame,
        method: str = "inner"
    ) -> Tuple[pd.DataFrame, ...]:
        """
        Align multiple DataFrames to have matching timestamps.
        
        Args:
            *dataframes: Variable number of DataFrames to align
            method: Join method ('inner', 'outer')
            
        Returns:
            Tuple of aligned DataFrames
        """
        if len(dataframes) < 2:
            return dataframes
        
        # Find common index
        if method == "inner":
            common_index = dataframes[0].index
            for df in dataframes[1:]:
                common_index = common_index.intersection(df.index)
        else:  # outer
            common_index = dataframes[0].index
            for df in dataframes[1:]:
                common_index = common_index.union(df.index)
            common_index = common_index.sort_values()
        
        # Reindex all DataFrames
        aligned = []
        for df in dataframes:
            aligned_df = df.reindex(common_index)
            if method == "outer":
                aligned_df = self.forward_fill(aligned_df)
            aligned.append(aligned_df)
        
        return tuple(aligned)
    
    def calculate_returns(
        self, 
        df: pd.DataFrame, 
        price_column: str = "Close",
        method: str = "simple"
    ) -> pd.Series:
        """
        Calculate returns from price data.
        
        Args:
            df: DataFrame with price data
            price_column: Column name for prices
            method: 'simple' or 'log' returns
            
        Returns:
            Series of returns
        """
        prices = df[price_column]
        
        if method == "simple":
            returns = prices.pct_change()
        elif method == "log":
            returns = np.log(prices / prices.shift(1))
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return returns
    
    def load_and_prepare(
        self,
        crypto_file: str,
        nasdaq_file: str,
        price_column: str = "Close"
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and prepare both crypto and NASDAQ data.
        
        Args:
            crypto_file: Filename for crypto data
            nasdaq_file: Filename for NASDAQ data
            price_column: Price column name
            
        Returns:
            Tuple of (crypto_df, nasdaq_df) aligned and cleaned
        """
        # Load data
        crypto_df = self.load_investing_csv(crypto_file)
        nasdaq_df = self.load_investing_csv(nasdaq_file)
        
        # Forward fill missing values
        crypto_df = self.forward_fill(crypto_df)
        nasdaq_df = self.forward_fill(nasdaq_df)
        
        # Align timestamps
        crypto_df, nasdaq_df = self.align_timestamps(crypto_df, nasdaq_df)
        
        # Calculate returns
        crypto_df["returns"] = self.calculate_returns(crypto_df, price_column)
        nasdaq_df["returns"] = self.calculate_returns(nasdaq_df, price_column)
        
        return crypto_df, nasdaq_df



if __name__ == "__main__":
    # Test with real data
    handler = DataHandler()
    
    try:
        crypto_df, nasdaq_df = handler.load_and_prepare(
            "BTC_USD Bitfinex Historical Data.csv", 
            "Nasdaq 100 Historical Data.csv"
        )
        print(f"Crypto data: {crypto_df.shape[0]} days")
        print(f"  Date range: {crypto_df.index[0]} to {crypto_df.index[-1]}")
        print(f"  Columns: {crypto_df.columns.tolist()}")
        print(f"\nNASDAQ data: {nasdaq_df.shape[0]} days")
        print(f"  Date range: {nasdaq_df.index[0]} to {nasdaq_df.index[-1]}")
        
        print(f"\nCrypto sample:\n{crypto_df.head()}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure data files are in the current directory")

