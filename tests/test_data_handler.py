import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_handler import DataHandler, parse_number, parse_percentage

class TestDataHandler:
    
    def test_parse_number(self):
        """Test number parsing logic."""
        assert parse_number("1,234.56") == 1234.56
        assert parse_number("1.5M") == 1_500_000.0
        assert parse_number("2.5K") == 2500.0
        assert parse_number("1B") == 1_000_000_000.0
        assert np.isnan(parse_number("-"))
        
    def test_parse_percentage(self):
        """Test percentage parsing logic."""
        assert parse_percentage("5.5%") == 0.055
        assert parse_percentage("-3.2%") == -0.032
        assert np.isnan(parse_percentage("-"))
        
    def test_align_timestamps(self):
        """Test timestamp alignment."""
        dates1 = pd.date_range(start='2020-01-01', periods=5)
        dates2 = pd.date_range(start='2020-01-03', periods=5)
        
        df1 = pd.DataFrame({'A': range(5)}, index=dates1)
        df2 = pd.DataFrame({'B': range(5)}, index=dates2)
        
        handler = DataHandler()
        aligned = handler.align_timestamps(df1, df2, method='inner')
        
        assert len(aligned[0]) == 3
        assert len(aligned[1]) == 3
        assert aligned[0].index[0] == pd.Timestamp('2020-01-03')
        
    def test_calculate_returns(self):
        """Test return calculation."""
        df = pd.DataFrame({'Close': [100, 110, 99]})
        handler = DataHandler()
        returns = handler.calculate_returns(df)
        
        assert len(returns) == 3
        assert np.isnan(returns.iloc[0])
        assert returns.iloc[1] == pytest.approx(0.10)
        assert returns.iloc[2] == pytest.approx(-0.10)
