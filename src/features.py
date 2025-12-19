"""
Feature Engineering Module
Implements crash detection indicators: DUVOL, NCSKEW, and Cross-Asset Canary.
"""

import pandas as pd
import numpy as np
from typing import Tuple


class FeatureEngineer:
    """
    Calculates crash prediction features from price data.
    
    Implements three "Loophole" indicators:
    1. DUVOL: Down-to-Up Volatility ratio
    2. NCSKEW: Negative Coefficient of Skewness
    3. Cross-Asset Canary: NASDAQ leading indicator for crypto
    """
    
    def __init__(self, window: int = 20):
        """
        Args:
            window: Rolling window size for calculations
        """
        self.window = window
    
    def calculate_duvol(self, returns: pd.Series) -> pd.Series:
        """
        Calculate Down-to-Up Volatility (DUVOL).
        
        DUVOL measures the ratio of standard deviation on "down" days 
        vs "up" days. A rising DUVOL is a precursor to a crash.
        
        Formula:
            DUVOL = log(std(down_returns) / std(up_returns))
        
        Args:
            returns: Series of returns
            
        Returns:
            Series of DUVOL values
        """
        def calc_duvol(window_returns):
            up_returns = window_returns[window_returns > 0]
            down_returns = window_returns[window_returns < 0]
            
            if len(up_returns) < 2 or len(down_returns) < 2:
                return np.nan
            
            up_std = up_returns.std()
            down_std = down_returns.std()
            
            if up_std == 0:
                return np.nan
            
            return np.log(down_std / up_std)
        
        duvol = returns.rolling(window=self.window).apply(
            calc_duvol, 
            raw=False
        )
        
        return duvol
    
    def calculate_ncskew(self, returns: pd.Series) -> pd.Series:
        """
        Calculate Negative Coefficient of Skewness (NCSKEW).
        
        Measures if returns are becoming asymmetric (more heavy-tail risk).
        Higher values indicate more crash risk.
        
        Formula:
            NCSKEW = -[n(n-1)^(3/2) * sum(r^3)] / [(n-1)(n-2) * std(r)^3]
        
        Args:
            returns: Series of returns
            
        Returns:
            Series of NCSKEW values
        """
        def calc_ncskew(window_returns):
            n = len(window_returns)
            if n < 3:
                return np.nan
            
            mean_ret = window_returns.mean()
            demeaned = window_returns - mean_ret
            
            std_ret = window_returns.std()
            if std_ret == 0:
                return np.nan
            
            # Calculate third moment (skewness numerator)
            m3 = (demeaned ** 3).sum()
            
            # NCSKEW formula
            ncskew = -(n * (n - 1) ** 1.5 * m3) / ((n - 1) * (n - 2) * std_ret ** 3)
            
            return ncskew
        
        ncskew = returns.rolling(window=self.window).apply(
            calc_ncskew, 
            raw=False
        )
        
        return ncskew
    
    def calculate_canary_signal(
        self, 
        nasdaq_returns: pd.Series,
        threshold: float = -0.03,
        lookback: int = 1
    ) -> pd.Series:
        """
        Calculate Cross-Asset Canary signal.
        
        Monitors NASDAQ index - equity sell-offs lead crypto liquidations 
        by ~24 hours.
        
        Args:
            nasdaq_returns: Series of NASDAQ returns
            threshold: Threshold for detecting sell-off (default -3%)
            lookback: Days to look back for signal
            
        Returns:
            Binary series (1 = danger signal, 0 = normal)
        """
        # Check if NASDAQ had a significant drop in lookback period
        rolling_min = nasdaq_returns.rolling(window=lookback).min()
        canary_signal = (rolling_min < threshold).astype(int)
        
        return canary_signal
    
    def calculate_volatility(
        self, 
        returns: pd.Series, 
        window: int = None
    ) -> pd.Series:
        """
        Calculate rolling volatility (standard deviation of returns).
        
        Args:
            returns: Series of returns
            window: Rolling window (uses self.window if not specified)
            
        Returns:
            Series of volatility values
        """
        if window is None:
            window = self.window
        
        return returns.rolling(window=window).std()
    
    def calculate_rsi(
        self, 
        prices: pd.Series, 
        window: int = 14
    ) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: Series of prices
            window: RSI window period
            
        Returns:
            Series of RSI values (0-100)
        """
        delta = prices.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_ma_crossover(
        self, 
        prices: pd.Series,
        fast_window: int = 10,
        slow_window: int = 30
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate moving average crossover signals.
        
        Args:
            prices: Series of prices
            fast_window: Short-term MA window
            slow_window: Long-term MA window
            
        Returns:
            Tuple of (fast_ma, slow_ma)
        """
        fast_ma = prices.rolling(window=fast_window).mean()
        slow_ma = prices.rolling(window=slow_window).mean()
        
        return fast_ma, slow_ma
    
    def generate_all_features(
        self,
        crypto_df: pd.DataFrame,
        nasdaq_df: pd.DataFrame,
        price_column: str = "Close"
    ) -> pd.DataFrame:
        """
        Generate all features for the trading model.
        
        Args:
            crypto_df: Crypto price DataFrame
            nasdaq_df: NASDAQ DataFrame
            price_column: Column name for prices
            
        Returns:
            DataFrame with all features
        """
        # Ensure we have returns
        if "returns" not in crypto_df.columns:
            crypto_returns = crypto_df[price_column].pct_change()
        else:
            crypto_returns = crypto_df["returns"]
        
        if "returns" not in nasdaq_df.columns:
            nasdaq_returns = nasdaq_df[price_column].pct_change()
        else:
            nasdaq_returns = nasdaq_df["returns"]
        
        # Calculate features
        features = pd.DataFrame(index=crypto_df.index)
        
        # Price and returns
        features["price"] = crypto_df[price_column]
        features["returns"] = crypto_returns
        
        # Crash detection indicators
        features["duvol"] = self.calculate_duvol(crypto_returns)
        features["ncskew"] = self.calculate_ncskew(crypto_returns)
        features["canary_signal"] = self.calculate_canary_signal(nasdaq_returns)
        
        # Volatility measures
        features["volatility_10d"] = self.calculate_volatility(crypto_returns, 10)
        features["volatility_30d"] = self.calculate_volatility(crypto_returns, 30)
        
        # Technical indicators
        features["rsi"] = self.calculate_rsi(crypto_df[price_column])
        fast_ma, slow_ma = self.calculate_ma_crossover(crypto_df[price_column])
        features["ma_fast"] = fast_ma
        features["ma_slow"] = slow_ma
        features["ma_crossover"] = (fast_ma > slow_ma).astype(int)
        
        # NASDAQ returns for reference
        features["nasdaq_returns"] = nasdaq_returns
        
        return features.dropna()


if __name__ == "__main__":
    # Test feature engineering
    from data_handler import DataHandler, create_sample_data
    
    # Create sample data if not exists
    create_sample_data()
    
    # Load data
    handler = DataHandler()
    crypto_df, nasdaq_df = handler.load_and_prepare(
        "crypto_btc.csv", 
        "nasdaq_index.csv"
    )
    
    # Generate features
    fe = FeatureEngineer(window=20)
    features = fe.generate_all_features(crypto_df, nasdaq_df)
    
    print("Features generated:")
    print(features.columns.tolist())
    print(f"\nShape: {features.shape}")
    print(f"\nSample:\n{features.head()}")
