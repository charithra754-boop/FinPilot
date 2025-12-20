"""
Stress Testing Module for FinPilot
Simulates flash crashes, volatility spikes, and other stress conditions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class StressScenario:
    """Container for stress test scenario data."""
    name: str
    prices: pd.Series
    original_prices: pd.Series
    stress_start: pd.Timestamp
    stress_end: pd.Timestamp
    description: str


class StressTestScenarios:
    """
    Generates and runs stress test scenarios for trading strategies.
    
    Scenarios:
    - Flash Crash: Sudden 10-20% drop in 1-5 days
    - Volatility Spike: 3-5x increase in daily volatility
    - Circuit Breaker: Simulates trading halts
    """
    
    def __init__(self, random_seed: int = 42):
        """
        Args:
            random_seed: Seed for reproducible stress scenarios
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)
    
    def generate_flash_crash(
        self,
        prices: pd.Series,
        drop_pct: float = 0.15,
        duration_days: int = 3,
        recovery_days: int = 10,
        crash_date: Optional[pd.Timestamp] = None
    ) -> StressScenario:
        """
        Generate a flash crash scenario.
        
        Creates a sudden price drop followed by partial recovery.
        
        Args:
            prices: Original price series
            drop_pct: Percentage drop (0.15 = 15% drop)
            duration_days: Days for crash to complete
            recovery_days: Days for partial recovery
            crash_date: Optional specific date for crash (default: mid-series)
            
        Returns:
            StressScenario with modified prices
        """
        modified_prices = prices.copy()
        
        # Select crash date (default to middle of series)
        if crash_date is None:
            mid_idx = len(prices) // 2
            crash_date = prices.index[mid_idx]
        
        # Find crash start index
        crash_idx = prices.index.get_loc(crash_date)
        if isinstance(crash_idx, slice):
            crash_idx = crash_idx.start
        
        crash_end_idx = min(crash_idx + duration_days, len(prices) - 1)
        recovery_end_idx = min(crash_end_idx + recovery_days, len(prices) - 1)
        
        # Pre-crash price
        pre_crash_price = prices.iloc[crash_idx]
        
        # Apply crash: linear drop over duration
        for i, idx in enumerate(range(crash_idx, crash_end_idx + 1)):
            progress = (i + 1) / duration_days
            drop_factor = 1 - (drop_pct * progress)
            modified_prices.iloc[idx] = pre_crash_price * drop_factor
        
        # Bottom price
        bottom_price = pre_crash_price * (1 - drop_pct)
        
        # Apply partial recovery (50% recovery)
        recovery_target = bottom_price + (pre_crash_price - bottom_price) * 0.5
        for i, idx in enumerate(range(crash_end_idx + 1, recovery_end_idx + 1)):
            progress = (i + 1) / recovery_days
            recovery_price = bottom_price + (recovery_target - bottom_price) * progress
            modified_prices.iloc[idx] = recovery_price
        
        # Continue from recovery level
        recovery_ratio = modified_prices.iloc[recovery_end_idx] / prices.iloc[recovery_end_idx]
        for idx in range(recovery_end_idx + 1, len(prices)):
            modified_prices.iloc[idx] = prices.iloc[idx] * recovery_ratio
        
        return StressScenario(
            name=f"Flash Crash ({drop_pct*100:.0f}%)",
            prices=modified_prices,
            original_prices=prices,
            stress_start=prices.index[crash_idx],
            stress_end=prices.index[recovery_end_idx],
            description=f"{drop_pct*100:.0f}% drop over {duration_days} days"
        )
    
    def generate_volatility_spike(
        self,
        prices: pd.Series,
        volatility_multiplier: float = 4.0,
        duration_days: int = 20,
        spike_date: Optional[pd.Timestamp] = None
    ) -> StressScenario:
        """
        Generate a volatility spike scenario.
        
        Increases daily price swings without changing trend direction.
        
        Args:
            prices: Original price series
            volatility_multiplier: Factor to increase volatility (4.0 = 4x vol)
            duration_days: Duration of high volatility period
            spike_date: Optional specific date for spike start
            
        Returns:
            StressScenario with modified prices
        """
        modified_prices = prices.copy()
        returns = prices.pct_change().fillna(0)
        
        # Select spike start date
        if spike_date is None:
            mid_idx = len(prices) // 2
            spike_date = prices.index[mid_idx]
        
        spike_idx = prices.index.get_loc(spike_date)
        if isinstance(spike_idx, slice):
            spike_idx = spike_idx.start
            
        spike_end_idx = min(spike_idx + duration_days, len(prices) - 1)
        
        # Calculate mean return for the spike period
        mean_return = returns.iloc[spike_idx:spike_end_idx + 1].mean()
        
        # Amplify returns during spike period
        for idx in range(spike_idx, spike_end_idx + 1):
            original_return = returns.iloc[idx]
            excess_return = original_return - mean_return
            amplified_return = mean_return + (excess_return * volatility_multiplier)
            
            # Apply amplified return
            if idx > 0:
                modified_prices.iloc[idx] = modified_prices.iloc[idx - 1] * (1 + amplified_return)
        
        # Continue from new level
        if spike_end_idx + 1 < len(prices):
            ratio = modified_prices.iloc[spike_end_idx] / prices.iloc[spike_end_idx]
            for idx in range(spike_end_idx + 1, len(prices)):
                modified_prices.iloc[idx] = prices.iloc[idx] * ratio
        
        return StressScenario(
            name=f"Volatility Spike ({volatility_multiplier}x)",
            prices=modified_prices,
            original_prices=prices,
            stress_start=prices.index[spike_idx],
            stress_end=prices.index[spike_end_idx],
            description=f"{volatility_multiplier}x volatility for {duration_days} days"
        )
    
    def generate_whipsaw(
        self,
        prices: pd.Series,
        swing_pct: float = 0.08,
        num_swings: int = 6,
        swing_period: int = 5
    ) -> StressScenario:
        """
        Generate a whipsaw scenario with rapid price reversals.
        
        Tests strategy's ability to handle false signals.
        
        Args:
            prices: Original price series
            swing_pct: Percentage of each swing
            num_swings: Number of price reversals
            swing_period: Days per swing
            
        Returns:
            StressScenario with modified prices
        """
        modified_prices = prices.copy()
        
        # Start whipsaw in middle of series
        mid_idx = len(prices) // 2
        total_period = num_swings * swing_period
        
        base_price = prices.iloc[mid_idx]
        
        for swing in range(num_swings):
            swing_start = mid_idx + swing * swing_period
            swing_end = min(swing_start + swing_period, len(prices))
            
            # Alternate up and down
            direction = 1 if swing % 2 == 0 else -1
            
            for i, idx in enumerate(range(swing_start, swing_end)):
                progress = i / swing_period
                swing_offset = direction * swing_pct * np.sin(progress * np.pi)
                modified_prices.iloc[idx] = base_price * (1 + swing_offset)
        
        return StressScenario(
            name=f"Whipsaw ({num_swings} swings)",
            prices=modified_prices,
            original_prices=prices,
            stress_start=prices.index[mid_idx],
            stress_end=prices.index[min(mid_idx + total_period, len(prices) - 1)],
            description=f"{num_swings} reversals of {swing_pct*100:.0f}%"
        )
    
    def run_stress_backtest(
        self,
        scenario: StressScenario,
        features: pd.DataFrame,
        strategy,
        regime_detector,
        backtester
    ) -> Dict:
        """
        Run backtest on a stress scenario.
        
        Args:
            scenario: StressScenario to test
            features: Original features DataFrame
            strategy: TradingStrategy instance
            regime_detector: RegimeDetector instance
            backtester: Backtester instance
            
        Returns:
            Dictionary with stress test results
        """
        # Update features with stress prices
        stress_features = features.copy()
        stress_features["price"] = scenario.prices
        stress_features["returns"] = scenario.prices.pct_change()
        
        # Recalculate volatility with stress data
        stress_features["volatility_10d"] = stress_features["returns"].rolling(10).std()
        stress_features["volatility_30d"] = stress_features["returns"].rolling(30).std()
        
        # Detect regimes
        regimes = regime_detector.detect_regimes(stress_features)
        
        # Run strategy
        signals = strategy.run_strategy(stress_features, regimes)
        
        # Run backtest
        results = backtester.run_backtest(stress_features, signals)
        
        # Calculate stress period metrics
        stress_mask = (results.index >= scenario.stress_start) & (results.index <= scenario.stress_end)
        stress_results = results[stress_mask]
        
        stress_metrics = {
            "scenario_name": scenario.name,
            "stress_period_return": 0,
            "stress_period_max_dd": 0,
            "time_in_cash_during_stress": 0,
            "trades_during_stress": 0,
            "detected_stress": False
        }
        
        if len(stress_results) > 0:
            equity = stress_results["portfolio_value"]
            stress_metrics["stress_period_return"] = (
                equity.iloc[-1] / equity.iloc[0] - 1
            ) * 100
            
            running_max = equity.expanding().max()
            drawdown = (equity - running_max) / running_max
            stress_metrics["stress_period_max_dd"] = abs(drawdown.min()) * 100
            
            # Time in cash
            cash_periods = (stress_results["signal"] == 0).sum()
            stress_metrics["time_in_cash_during_stress"] = (
                cash_periods / len(stress_results) * 100
            )
            
            # Trades during stress
            stress_metrics["trades_during_stress"] = (
                stress_results["trade_type"].notna().sum()
            )
            
            # Check if strategy detected stress (went to cash)
            stress_metrics["detected_stress"] = cash_periods > 0
        
        return {
            "scenario": scenario,
            "results": results,
            "stress_metrics": stress_metrics,
            "regimes": regimes
        }
    
    def calculate_stress_metrics(
        self,
        normal_results: pd.DataFrame,
        stress_results: pd.DataFrame
    ) -> Dict:
        """
        Compare normal vs stress test performance.
        
        Args:
            normal_results: Backtest results on normal data
            stress_results: Backtest results on stress data
            
        Returns:
            Dictionary comparing performance
        """
        def calc_metrics(results):
            equity = results["portfolio_value"]
            returns = equity.pct_change().dropna()
            running_max = equity.expanding().max()
            drawdown = (equity - running_max) / running_max
            
            return {
                "total_return": (equity.iloc[-1] / equity.iloc[0] - 1) * 100,
                "max_drawdown": abs(drawdown.min()) * 100,
                "volatility": returns.std() * np.sqrt(252) * 100,
                "sharpe": returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            }
        
        normal_metrics = calc_metrics(normal_results)
        stress_metrics_calc = calc_metrics(stress_results)
        
        return {
            "normal": normal_metrics,
            "stress": stress_metrics_calc,
            "return_impact": stress_metrics_calc["total_return"] - normal_metrics["total_return"],
            "drawdown_increase": stress_metrics_calc["max_drawdown"] - normal_metrics["max_drawdown"],
            "sharpe_impact": stress_metrics_calc["sharpe"] - normal_metrics["sharpe"]
        }


if __name__ == "__main__":
    # Demo stress testing
    import numpy as np
    
    # Create sample price series
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", "2024-01-01", freq="D")
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = pd.Series(10000 * np.exp(np.cumsum(returns)), index=dates)
    
    # Generate scenarios
    stress_tester = StressTestScenarios()
    
    flash_crash = stress_tester.generate_flash_crash(prices, drop_pct=0.20)
    print(f"✅ {flash_crash.name}: {flash_crash.description}")
    
    vol_spike = stress_tester.generate_volatility_spike(prices, volatility_multiplier=4.0)
    print(f"✅ {vol_spike.name}: {vol_spike.description}")
    
    whipsaw = stress_tester.generate_whipsaw(prices, swing_pct=0.10)
    print(f"✅ {whipsaw.name}: {whipsaw.description}")
    
    print("\n✅ Stress testing module ready!")
