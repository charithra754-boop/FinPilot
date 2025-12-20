"""
Stress Testing Tests for FinPilot
Tests stress scenario generation and strategy robustness.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from stress_testing import StressTestScenarios, StressScenario


class TestStressTestScenarios:
    """Test stress scenario generation."""
    
    @pytest.fixture
    def sample_prices(self):
        """Generate sample price series for testing."""
        np.random.seed(42)
        dates = pd.date_range("2020-01-01", "2022-01-01", freq="D")
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = pd.Series(10000 * np.exp(np.cumsum(returns)), index=dates)
        return prices
    
    @pytest.fixture
    def stress_tester(self):
        """Create stress tester instance."""
        return StressTestScenarios(random_seed=42)
    
    def test_flash_crash_generation(self, stress_tester, sample_prices):
        """Test flash crash scenario produces expected price drop."""
        drop_pct = 0.20  # 20% drop
        scenario = stress_tester.generate_flash_crash(
            sample_prices, 
            drop_pct=drop_pct,
            duration_days=3
        )
        
        assert isinstance(scenario, StressScenario)
        assert scenario.name == "Flash Crash (20%)"
        assert len(scenario.prices) == len(sample_prices)
        
        # Find the minimum point during stress
        stress_mask = (scenario.prices.index >= scenario.stress_start) & \
                      (scenario.prices.index <= scenario.stress_end)
        stress_prices = scenario.prices[stress_mask]
        
        # Price should drop by approximately drop_pct
        pre_crash_price = sample_prices.loc[scenario.stress_start]
        min_price = stress_prices.min()
        actual_drop = (pre_crash_price - min_price) / pre_crash_price
        
        assert actual_drop >= drop_pct * 0.9  # Allow 10% tolerance
    
    def test_volatility_spike_generation(self, stress_tester, sample_prices):
        """Test volatility spike scenario produces increased volatility."""
        vol_multiplier = 4.0
        scenario = stress_tester.generate_volatility_spike(
            sample_prices,
            volatility_multiplier=vol_multiplier,
            duration_days=20
        )
        
        assert isinstance(scenario, StressScenario)
        assert scenario.name == f"Volatility Spike ({vol_multiplier}x)"
        
        # Calculate volatility during stress period
        stress_returns = scenario.prices.pct_change().loc[
            scenario.stress_start:scenario.stress_end
        ].dropna()
        
        normal_returns = sample_prices.pct_change().loc[
            scenario.stress_start:scenario.stress_end
        ].dropna()
        
        # Stress volatility should be higher than normal
        stress_vol = stress_returns.std()
        normal_vol = normal_returns.std()
        
        # Volatility should increase (not exact multiplier due to how it's applied)
        assert stress_vol > normal_vol
    
    def test_whipsaw_generation(self, stress_tester, sample_prices):
        """Test whipsaw scenario produces price reversals."""
        scenario = stress_tester.generate_whipsaw(
            sample_prices,
            swing_pct=0.10,
            num_swings=6
        )
        
        assert isinstance(scenario, StressScenario)
        assert "Whipsaw" in scenario.name
        
        # Count direction changes during stress period
        stress_prices = scenario.prices.loc[
            scenario.stress_start:scenario.stress_end
        ]
        returns = stress_prices.pct_change().dropna()
        direction_changes = ((returns > 0) != (returns.shift(1) > 0)).sum()
        
        # Should have multiple direction changes
        assert direction_changes > 3
    
    def test_stress_scenario_dates(self, stress_tester, sample_prices):
        """Test that stress periods are within price series bounds."""
        scenario = stress_tester.generate_flash_crash(sample_prices)
        
        assert scenario.stress_start >= sample_prices.index[0]
        assert scenario.stress_end <= sample_prices.index[-1]
        assert scenario.stress_start < scenario.stress_end
    
    def test_calculate_stress_metrics(self, stress_tester, sample_prices):
        """Test stress metrics comparison."""
        # Create simple stress and normal results
        normal_results = pd.DataFrame({
            "portfolio_value": sample_prices.values * 10  # Scale up
        }, index=sample_prices.index)
        
        stress_scenario = stress_tester.generate_flash_crash(sample_prices)
        stress_results = pd.DataFrame({
            "portfolio_value": stress_scenario.prices.values * 10
        }, index=stress_scenario.prices.index)
        
        metrics = stress_tester.calculate_stress_metrics(normal_results, stress_results)
        
        assert "normal" in metrics
        assert "stress" in metrics
        assert "return_impact" in metrics
        assert "drawdown_increase" in metrics
        
        # Stress should have worse or equal drawdown
        assert metrics["stress"]["max_drawdown"] >= metrics["normal"]["max_drawdown"] - 0.1


class TestFlashCrashDetection:
    """Test that strategy correctly detects simulated flash crashes."""
    
    @pytest.fixture
    def sample_prices(self):
        np.random.seed(42)
        dates = pd.date_range("2020-01-01", "2021-01-01", freq="D")
        returns = np.random.normal(0.001, 0.02, len(dates))
        return pd.Series(10000 * np.exp(np.cumsum(returns)), index=dates)
    
    def test_flash_crash_creates_valid_scenario(self, sample_prices):
        """Flash crash should create a valid scenario object."""
        tester = StressTestScenarios()
        scenario = tester.generate_flash_crash(
            sample_prices,
            drop_pct=0.15,
            duration_days=2
        )
        
        # Verify scenario structure
        assert hasattr(scenario, 'prices')
        assert hasattr(scenario, 'stress_start')
        assert hasattr(scenario, 'stress_end')
        assert len(scenario.prices) == len(sample_prices)
