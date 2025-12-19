import pytest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from visualizations import StrategyVisualizer


class TestStrategyVisualizer:
    """Tests for the StrategyVisualizer class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        dates = pd.date_range("2020-01-01", "2023-01-01", freq="D")
        n = len(dates)
        
        # Simulated equity curve with growth
        returns = np.random.normal(0.001, 0.02, n)
        equity = pd.Series(100000 * np.exp(np.cumsum(returns)), index=dates)
        benchmark = pd.Series(100000 * np.exp(np.cumsum(returns * 0.7)), index=dates)
        
        # Simulated regimes
        regimes = pd.Series(
            np.random.choice(["normal", "crash", "recovery"], n, p=[0.7, 0.15, 0.15]),
            index=dates
        )
        
        # Simulated prices
        prices = pd.Series(30000 * np.exp(np.cumsum(returns * 0.5)), index=dates)
        
        # Metrics
        metrics = {
            "total_return": 500.0,
            "sharpe_ratio": 1.5,
            "max_drawdown": 0.25,
            "cagr": 50.0,
            "total_trades": 100,
            "benchmark_return": 200.0,
            "benchmark_sharpe": 0.8,
            "benchmark_drawdown": 0.40
        }
        
        return {
            "equity": equity,
            "benchmark": benchmark,
            "regimes": regimes,
            "prices": prices,
            "metrics": metrics
        }
    
    @pytest.fixture
    def visualizer(self):
        """Create a StrategyVisualizer instance."""
        return StrategyVisualizer()
    
    def test_init(self, visualizer):
        """Test visualizer initialization."""
        assert visualizer.colors is not None
        assert "strategy" in visualizer.colors
        assert "crash" in visualizer.colors
        assert visualizer.key_events is not None
    
    def test_plot_equity_curve(self, visualizer, sample_data):
        """Test equity curve plotting."""
        fig = visualizer.plot_equity_curve(
            sample_data["equity"],
            sample_data["benchmark"],
            sample_data["metrics"]
        )
        
        assert fig is not None
        # Check that figure has 2 axes (equity + drawdown)
        assert len(fig.axes) == 2
        
        # Clean up
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_plot_equity_curve_no_benchmark(self, visualizer, sample_data):
        """Test equity curve without benchmark."""
        fig = visualizer.plot_equity_curve(
            sample_data["equity"],
            benchmark=None,
            metrics=None
        )
        
        assert fig is not None
        
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_plot_regime_heatmap(self, visualizer, sample_data):
        """Test regime heatmap plotting."""
        fig = visualizer.plot_regime_heatmap(
            sample_data["regimes"],
            sample_data["prices"]
        )
        
        assert fig is not None
        
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_plot_regime_heatmap_all_regime_types(self, visualizer, sample_data):
        """Test that heatmap handles all regime types."""
        regimes = sample_data["regimes"]
        
        # Verify all regime types are present
        unique_regimes = regimes.unique()
        assert "normal" in unique_regimes
        assert "crash" in unique_regimes
        assert "recovery" in unique_regimes
        
        fig = visualizer.plot_regime_heatmap(regimes, sample_data["prices"])
        assert fig is not None
        
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_plot_performance_dashboard(self, visualizer, sample_data):
        """Test performance dashboard generation."""
        fig = visualizer.plot_performance_dashboard(
            sample_data["equity"],
            sample_data["benchmark"],
            sample_data["regimes"],
            sample_data["prices"],
            sample_data["metrics"]
        )
        
        assert fig is not None
        # Dashboard should have multiple subplots
        assert len(fig.axes) >= 4
        
        import matplotlib.pyplot as plt
        plt.close(fig)
    
    def test_save_figure(self, visualizer, sample_data):
        """Test figure saving functionality."""
        fig = visualizer.plot_equity_curve(
            sample_data["equity"],
            sample_data["benchmark"],
            sample_data["metrics"]
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = visualizer.save_figure(fig, "test_equity", output_dir=tmpdir)
            
            assert filepath.exists()
            assert filepath.suffix == ".png"
            assert filepath.stat().st_size > 0
    
    def test_save_figure_creates_directory(self, visualizer, sample_data):
        """Test that save_figure creates output directory if needed."""
        fig = visualizer.plot_equity_curve(sample_data["equity"])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = os.path.join(tmpdir, "nested", "path")
            filepath = visualizer.save_figure(fig, "test", output_dir=nested_dir)
            
            assert filepath.exists()
            assert filepath.parent.exists()
    
    def test_empty_data_handling(self, visualizer):
        """Test handling of edge cases with minimal data."""
        dates = pd.date_range("2020-01-01", periods=10, freq="D")
        equity = pd.Series([100000] * 10, index=dates)
        regimes = pd.Series(["normal"] * 10, index=dates)
        prices = pd.Series([30000] * 10, index=dates)
        
        # Should not raise errors
        fig1 = visualizer.plot_equity_curve(equity)
        fig2 = visualizer.plot_regime_heatmap(regimes, prices)
        
        assert fig1 is not None
        assert fig2 is not None
        
        import matplotlib.pyplot as plt
        plt.close("all")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
