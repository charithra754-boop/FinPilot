import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from metrics import Metrics

class TestMetrics:
    
    def test_sharpe_ratio(self):
        """Test Sharpe Ratio calculation."""
        metrics = Metrics(risk_free_rate=0.0)
        # Constant positive return -> High Sharpe
        returns = pd.Series([0.01] * 100)
        sharpe = metrics.calculate_sharpe_ratio(returns)
        assert sharpe > 10 # Should be very high (std=0 technically inf, but implementation might handle)
        
        # Zero returns -> Zero Sharpe
        returns = pd.Series([0.0] * 100)
        sharpe = metrics.calculate_sharpe_ratio(returns)
        assert sharpe == 0.0
        
    def test_max_drawdown(self):
        """Test Max Drawdown calculation."""
        metrics = Metrics()
        # Peak 100 -> Drop to 50 -> Recover to 100
        equity = pd.Series([100, 90, 80, 50, 60, 80, 100])
        dd = metrics.calculate_max_drawdown(equity)
        
        # Drop 100 -> 50 = 50%
        assert dd == 0.5
        
    def test_calculate_all_metrics(self):
        """Test full metrics dictionary."""
        metrics_calc = Metrics(risk_free_rate=0.0)
        equity = pd.Series([100, 110, 121]) # 10% returns
        
        metrics = metrics_calc.calculate_all_metrics(equity)
        
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown' in metrics
        assert 'cagr' in metrics # Critical check for Phase 3 fix
        
        assert metrics['total_return'] == pytest.approx(21.0)
        assert metrics['max_drawdown'] == 0.0
