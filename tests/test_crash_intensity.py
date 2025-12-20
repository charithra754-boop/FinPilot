"""
Tests for Crash Intensity Scoring Module
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from crash_intensity import (
    CrashIntensityScorer,
    CrashIntensityConfig,
    AdaptiveRecoveryEngine,
    IntensityAwareStrategy,
    calculate_crash_intensity_metrics
)


class TestCrashIntensityScorer:
    """Tests for CrashIntensityScorer."""
    
    @pytest.fixture
    def scorer(self):
        """Create default scorer."""
        return CrashIntensityScorer()
    
    @pytest.fixture
    def sample_features(self):
        """Create sample features for testing."""
        return pd.Series({
            "duvol": 0.7,
            "ncskew": 1.0,
            "volatility_10d": 0.04,
            "volatility_30d": 0.02,
            "nasdaq_returns": -0.02,
            "returns": -0.03,
            "rsi": 25,
            "price": 50000,
            "ma_fast": 49000,
            "ma_slow": 48000
        })
    
    def test_normalize_to_100(self, scorer):
        """Test normalization function."""
        assert scorer._normalize_to_100(0.5, 0, 1) == 50
        assert scorer._normalize_to_100(0, 0, 1) == 0
        assert scorer._normalize_to_100(1, 0, 1) == 100
        assert scorer._normalize_to_100(2, 0, 1) == 100  # Capped
        assert scorer._normalize_to_100(-1, 0, 1) == 0   # Floored
    
    def test_duvol_intensity(self, scorer):
        """Test DUVOL intensity calculation."""
        # DUVOL 0 should give low intensity
        assert scorer.calculate_duvol_intensity(0) == 0
        
        # DUVOL 1.0 (threshold) should give 100
        assert scorer.calculate_duvol_intensity(1.0) == 100
        
        # DUVOL 0.5 should give 50
        assert scorer.calculate_duvol_intensity(0.5) == 50
    
    def test_volatility_intensity(self, scorer):
        """Test volatility spike intensity."""
        # Equal volatility = no spike
        assert scorer.calculate_volatility_intensity(0.02, 0.02) == 0
        
        # 3x volatility = max intensity
        assert scorer.calculate_volatility_intensity(0.06, 0.02) == 100
        
        # 2x volatility = mid intensity
        assert scorer.calculate_volatility_intensity(0.04, 0.02) == 50
    
    def test_canary_intensity(self, scorer):
        """Test NASDAQ canary intensity."""
        # Positive NASDAQ = no danger
        assert scorer.calculate_canary_intensity(0.01) == 0
        
        # -5% NASDAQ = max danger
        assert scorer.calculate_canary_intensity(-0.05) == 100
        
        # -2.5% NASDAQ = mid danger
        assert scorer.calculate_canary_intensity(-0.025) == 50
    
    def test_crash_intensity_score(self, scorer, sample_features):
        """Test composite CIS calculation."""
        cis = scorer.calculate_crash_intensity(sample_features)
        
        # CIS should be between 0-100
        assert 0 <= cis <= 100
        
        # Given the sample features with elevated danger signals
        # CIS should be elevated
        assert cis > 30  # Should detect some danger
    
    def test_crash_intensity_zero_features(self, scorer):
        """Test CIS with all-zero features."""
        zero_features = pd.Series({
            "duvol": 0,
            "ncskew": 0,
            "volatility_10d": 0.02,
            "volatility_30d": 0.02,
            "nasdaq_returns": 0,
            "returns": 0,
            "rsi": 50
        })
        cis = scorer.calculate_crash_intensity(zero_features)
        
        # Should be very low intensity
        assert cis < 20
    
    def test_proportional_position(self, scorer):
        """Test proportional position sizing."""
        # Low intensity = full position
        assert scorer.calculate_proportional_position(10) == 1.0
        
        # High intensity = no position
        assert scorer.calculate_proportional_position(85) == 0.0
        
        # Mid intensity = reduced position
        pos = scorer.calculate_proportional_position(50)
        assert 0 < pos < 1
    
    def test_intensity_series(self, scorer):
        """Test calculating CIS for entire DataFrame."""
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        features = pd.DataFrame({
            "duvol": np.random.normal(0.3, 0.2, 100),
            "ncskew": np.random.normal(0.5, 0.3, 100),
            "volatility_10d": np.abs(np.random.normal(0.02, 0.01, 100)),
            "volatility_30d": np.abs(np.random.normal(0.02, 0.005, 100)),
            "nasdaq_returns": np.random.normal(0, 0.01, 100),
            "returns": np.random.normal(0, 0.02, 100),
            "rsi": np.random.uniform(30, 70, 100)
        }, index=dates)
        
        intensities = scorer.calculate_intensity_series(features)
        
        assert len(intensities) == 100
        assert intensities.min() >= 0
        assert intensities.max() <= 100


class TestAdaptiveRecoveryEngine:
    """Tests for AdaptiveRecoveryEngine."""
    
    @pytest.fixture
    def engine(self):
        return AdaptiveRecoveryEngine()
    
    @pytest.fixture
    def sample_features(self):
        return pd.Series({
            "price": 50000,
            "volatility_10d": 0.02,
            "volatility_30d": 0.03,
            "rsi": 45
        })
    
    def test_recovery_score(self, engine, sample_features):
        """Test recovery score calculation."""
        score = engine.calculate_recovery_score(
            sample_features,
            price_ma_10=49000,
            crash_intensity=30
        )
        
        assert 0 <= score <= 1
    
    def test_should_start_recovery_too_early(self, engine):
        """Test that recovery doesn't start too early."""
        # Only 1 day in cash - should not recover
        assert not engine.should_start_recovery(0.7, days_in_cash=1)
    
    def test_should_start_recovery_low_score(self, engine):
        """Test that recovery needs sufficient score."""
        # Low recovery score - should not recover
        assert not engine.should_start_recovery(0.3, days_in_cash=5)
    
    def test_should_start_recovery_good_conditions(self, engine):
        """Test recovery starts under good conditions."""
        # Good score and sufficient days
        assert engine.should_start_recovery(0.7, days_in_cash=5)
    
    def test_scaling_position(self, engine):
        """Test gradual position scaling."""
        # Step 0 = no position
        assert engine.calculate_scaling_position(0) == 0.0
        
        # Step 4 (default scaling_steps) = full position
        assert engine.calculate_scaling_position(4) == 1.0
        
        # Mid step = partial position
        pos = engine.calculate_scaling_position(2)
        assert 0 < pos < 1


class TestIntensityAwareStrategy:
    """Tests for IntensityAwareStrategy."""
    
    @pytest.fixture
    def strategy(self):
        return IntensityAwareStrategy()
    
    @pytest.fixture
    def sample_features(self):
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        features = pd.DataFrame({
            "price": 50000 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 100))),
            "duvol": np.random.normal(0.3, 0.2, 100),
            "ncskew": np.random.normal(0.5, 0.3, 100),
            "volatility_10d": np.abs(np.random.normal(0.02, 0.01, 100)),
            "volatility_30d": np.abs(np.random.normal(0.02, 0.005, 100)),
            "nasdaq_returns": np.random.normal(0, 0.01, 100),
            "returns": np.random.normal(0.001, 0.02, 100),
            "rsi": np.random.uniform(30, 70, 100)
        }, index=dates)
        features["ma_fast"] = features["price"].rolling(10).mean()
        features["ma_slow"] = features["price"].rolling(30).mean()
        return features.dropna()
    
    def test_run_strategy(self, strategy, sample_features):
        """Test running the intensity-aware strategy."""
        results = strategy.run_intensity_strategy(sample_features)
        
        # Should have results for all rows
        assert len(results) == len(sample_features)
        
        # Required columns
        assert "crash_intensity" in results.columns
        assert "position_size" in results.columns
        assert "signal" in results.columns
    
    def test_position_bounds(self, strategy, sample_features):
        """Test that positions stay within bounds."""
        results = strategy.run_intensity_strategy(sample_features)
        
        assert results["position_size"].min() >= 0
        assert results["position_size"].max() <= 1


class TestCrashIntensityMetrics:
    """Tests for crash intensity metrics."""
    
    def test_calculate_metrics(self):
        """Test metrics calculation."""
        np.random.seed(42)
        n = 100
        
        intensities = pd.Series(np.random.uniform(20, 80, n))
        returns = pd.Series(np.random.normal(0, 0.02, n))
        
        metrics = calculate_crash_intensity_metrics(intensities, returns)
        
        assert "intensity_return_correlation" in metrics
        assert "avg_intensity" in metrics
        assert "max_intensity" in metrics
        assert "days_above_70" in metrics
