import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from strategy import TradingStrategy, Position

class TestTradingStrategy:
    
    def test_position_sizing(self):
        """Test position sizing based on volatility."""
        strategy = TradingStrategy(volatility_target=0.02, max_position_size=1.0)
        
        # Volatility = Target -> Size = 1.0
        assert strategy.calculate_position_size(0.02) == 1.0
        
        # Volatility = 2x Target -> Size = 0.5
        assert strategy.calculate_position_size(0.04) == 0.5
        
        # Volatility = 0.5x Target -> Size = 1.0 (capped)
        assert strategy.calculate_position_size(0.01) == 1.0
        
    def test_check_stop_loss(self):
        """Test stop loss trigger."""
        strategy = TradingStrategy(stop_loss_pct=0.05)
        
        # 4% loss -> Hold
        assert not strategy.check_stop_loss(100, 96)
        
        # 5% loss -> Sell
        assert strategy.check_stop_loss(100, 95)
        
        # 6% loss -> Sell
        assert strategy.check_stop_loss(100, 94)
    
    def test_run_strategy(self):
        """Test single-asset strategy execution."""
        dates = pd.date_range(start='2020-01-01', periods=10)
        features = pd.DataFrame({
            'price': [100] * 10,
            'rsi': [50] * 10,
            'ma_crossover': [0] * 10,
            'volatility_10d': [0.02] * 10
        }, index=dates)
        regimes = pd.Series(['normal'] * 10, index=dates)
        
        # Trigger buy signal
        features.loc[dates[1], 'rsi'] = 20 # Oversold
        
        strategy = TradingStrategy(rsi_oversold=30)
        results = strategy.run_strategy(features, regimes)
        
        assert results.loc[dates[1], 'signal'] == Position.LONG.value
        assert results.loc[dates[0], 'position'] == 'CASH'
        
    def test_run_portfolio_strategy(self):
        """Test multi-asset portfolio strategy."""
        dates = pd.date_range(start='2020-01-01', periods=5)
        
        # Asset A
        df_a = pd.DataFrame({'price': [100]*5, 'rsi': [50]*5, 'volatility_10d': [0.02]*5}, index=dates)
        
        # Asset B
        df_b = pd.DataFrame({'price': [10]*5, 'rsi': [50]*5, 'volatility_10d': [0.02]*5}, index=dates)
        
        features_dict = {'A': df_a, 'B': df_b}
        regimes = pd.Series(['normal']*5, index=dates)
        allocations = {'A': 0.6, 'B': 0.4}
        
        # Trigger buy for A
        df_a.loc[dates[1], 'rsi'] = 20
        # Trigger buy for B
        df_b.loc[dates[1], 'rsi'] = 20
        
        strategy = TradingStrategy(rsi_oversold=30, volatility_target=0.02)
        weights = strategy.run_portfolio_strategy(features_dict, regimes, allocations)
        
        # A should have weight ~0.6 (since vol match target)
        # B should have weight ~0.4
        assert weights.loc[dates[1], 'A'] == pytest.approx(0.6)
        assert weights.loc[dates[1], 'B'] == pytest.approx(0.4)
        
        # Test Global Crash -> Cash
        regimes.loc[dates[3]] = 'crash'
        weights_crash = strategy.run_portfolio_strategy(features_dict, regimes, allocations)
        
        assert weights_crash.loc[dates[3], 'A'] == 0.0
        assert weights_crash.loc[dates[3], 'B'] == 0.0
