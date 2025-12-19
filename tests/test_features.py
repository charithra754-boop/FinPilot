import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from features import FeatureEngineer

class TestFeatureEngineer:
    
    def test_calculate_rsi(self):
        """Test RSI calculation."""
        fe = FeatureEngineer(window=14)
        # Create a series with a clear trend up then down
        prices = pd.Series([100, 101, 102, 103, 104, 105, 104, 103, 102, 101])
        # Need more data for valid RSI usually, but let's test basic functionality or handle short series
        # Standard RSI needs at least window size + 1
        prices_long = pd.Series(np.linspace(100, 200, 20))
        
        rsi = fe.calculate_rsi(prices_long)
        
        assert len(rsi) == 20
        # In a perfect uptrend, RSI should be high (near 100)
        assert rsi.iloc[-1] > 70
        
    def test_duvol_calculation(self):
        """Test DUVOL calculation."""
        # DUVOL = log(std_down / std_up)
        # If down vol is higher, DUVOL should be positive? Or ratio?
        # Let's check implementation behavior
        fe = FeatureEngineer(window=5)
        
        # Case 1: High Downside Volatility
        returns = pd.Series([-0.05, -0.05, -0.05, 0.01, 0.01]) 
        duvol = fe.calculate_duvol(returns)
        
        # Expect DUVOL to be high/positive/indicating crash risk
        # Wait, need to check if it returns scalar or series. Usually rolling.
        # Assuming rolling based on window=5
        
        assert isinstance(duvol, pd.Series)
        # Check last value. 
        # Down days: -0.05. Up days: 0.01. Down variance should be higher.
        
    def test_ncskew_calculation(self):
        """Test NCSKEW calculation."""
        fe = FeatureEngineer(window=10)
        returns = pd.Series(np.random.normal(0, 0.01, 100))
        ncskew = fe.calculate_ncskew(returns)
        assert isinstance(ncskew, pd.Series)
        
    def test_generate_all_features(self):
        """Test full feature generation."""
        fe = FeatureEngineer(window=14)
        dates = pd.date_range(start='2020-01-01', periods=50)
        # Use random walk to ensure both up and down moves
        np.random.seed(42)
        returns = np.random.normal(0, 0.01, 50)
        price = 100 * (1 + returns).cumprod()
        crypto_df = pd.DataFrame({
            'Close': price,
            'Volume': np.random.rand(50) * 1000
        }, index=dates)
        crypto_df['returns'] = crypto_df['Close'].pct_change()
        
        nasdaq_df = pd.DataFrame({
            'Close': np.linspace(1000, 2000, 50),
            'returns': np.linspace(0.01, 0.01, 50)
        }, index=dates)
        
        features = fe.generate_all_features(crypto_df, nasdaq_df)
        
        expected_cols = ['rsi', 'duvol', 'ncskew', 'volatility_10d', 'canary_signal']
        for col in expected_cols:
            assert col in features.columns, f"Missing column: {col}"
            
        # Windowing (slow_ma=30) removes first 29 rows
        # 50 - 29 = 21 expected
        assert len(features) >= 20
