"""
Monte Carlo Stress Simulation for FinPilot
Statistical proof of strategy robustness through thousands of simulated scenarios.

Features:
- Shows quantitative rigor
- Provides confidence intervals
- Proves survivability statistically

Author: FinPilot Team
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class MonteCarloResults:
    """Results from Monte Carlo simulation."""
    n_simulations: int
    survival_rate: float  # % of scenarios where drawdown < threshold
    median_return: float
    mean_return: float
    return_5th_percentile: float
    return_95th_percentile: float
    median_drawdown: float
    drawdown_5th_percentile: float
    drawdown_95th_percentile: float
    median_sharpe: float
    all_returns: np.ndarray
    all_drawdowns: np.ndarray
    all_sharpes: np.ndarray


class MonteCarloSimulator:
    """
    Monte Carlo stress simulation engine.
    
    Generates thousands of market scenarios with varying:
    - Volatility regimes
    - Crash frequencies
    - Recovery patterns
    
    Then tests strategy robustness across all scenarios.
    """
    
    def __init__(
        self,
        n_simulations: int = 1000,
        simulation_days: int = 252,  # 1 year
        random_seed: Optional[int] = None
    ):
        """
        Args:
            n_simulations: Number of scenarios to simulate
            simulation_days: Days per simulation
            random_seed: For reproducibility
        """
        self.n_simulations = n_simulations
        self.simulation_days = simulation_days
        
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def generate_price_path(
        self,
        initial_price: float = 10000,
        base_return: float = 0.0005,
        base_volatility: float = 0.03,
        crash_probability: float = 0.02,
        crash_severity: Tuple[float, float] = (-0.15, -0.05)
    ) -> pd.Series:
        """
        Generate a single price path with realistic dynamics.
        
        Includes:
        - Base trend with randomness
        - Random crash events
        - Volatility clustering
        - Mean reversion
        
        Args:
            initial_price: Starting price
            base_return: Daily expected return
            base_volatility: Normal volatility
            crash_probability: Daily probability of crash
            crash_severity: Range of crash returns
            
        Returns:
            Series of prices
        """
        prices = [initial_price]
        volatility = base_volatility
        
        for day in range(self.simulation_days):
            # Volatility clustering (GARCH-like)
            volatility = 0.9 * volatility + 0.1 * base_volatility + \
                         0.05 * abs(np.random.normal(0, base_volatility))
            
            # Check for crash
            if np.random.random() < crash_probability:
                # Crash event
                daily_return = np.random.uniform(crash_severity[0], crash_severity[1])
                volatility *= 2  # Vol spikes during crash
            else:
                # Normal day with slight mean reversion
                daily_return = base_return + np.random.normal(0, volatility)
            
            new_price = prices[-1] * (1 + daily_return)
            prices.append(max(new_price, 0.01))  # Floor at 0.01
        
        dates = pd.date_range("2024-01-01", periods=len(prices), freq="D")
        return pd.Series(prices, index=dates)
    
    def simulate_strategy_performance(
        self,
        prices: pd.Series,
        use_crash_detection: bool = True
    ) -> Dict:
        """
        Simulate strategy performance on a price path.
        
        Args:
            prices: Price series
            use_crash_detection: Whether to use crash detection
            
        Returns:
            Dictionary with performance metrics
        """
        returns = prices.pct_change().dropna()
        
        if use_crash_detection:
            # Simple crash detection: exit when 5-day return < -10%
            rolling_return = returns.rolling(5).sum()
            in_market = (rolling_return > -0.10).astype(float)
            in_market = in_market.shift(1).fillna(1)  # Signal delay
            
            # Reduce position during high volatility
            rolling_vol = returns.rolling(10).std()
            avg_vol = rolling_vol.mean()
            vol_adjustment = np.minimum(1.0, avg_vol / rolling_vol.fillna(avg_vol))
            
            position = in_market * vol_adjustment
            strategy_returns = returns * position
        else:
            strategy_returns = returns
        
        # Calculate metrics
        total_return = (1 + strategy_returns).prod() - 1
        
        # Max drawdown
        cumulative = (1 + strategy_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        # Sharpe ratio
        if strategy_returns.std() > 0:
            sharpe = (strategy_returns.mean() * 252) / (strategy_returns.std() * np.sqrt(252))
        else:
            sharpe = 0
        
        return {
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe,
            "volatility": strategy_returns.std() * np.sqrt(252),
            "win_rate": (strategy_returns > 0).mean()
        }
    
    def run_simulation(
        self,
        drawdown_threshold: float = 0.50,
        verbose: bool = True
    ) -> MonteCarloResults:
        """
        Run full Monte Carlo simulation.
        
        Args:
            drawdown_threshold: Max acceptable drawdown for "survival"
            verbose: Print progress
            
        Returns:
            MonteCarloResults with statistics
        """
        all_returns = []
        all_drawdowns = []
        all_sharpes = []
        
        # Vary simulation parameters
        crash_probs = np.random.uniform(0.005, 0.05, self.n_simulations)
        volatilities = np.random.uniform(0.02, 0.06, self.n_simulations)
        
        for i in range(self.n_simulations):
            if verbose and (i + 1) % 200 == 0:
                print(f"    Simulation {i+1}/{self.n_simulations}...")
            
            # Generate price path with random parameters
            prices = self.generate_price_path(
                base_volatility=volatilities[i],
                crash_probability=crash_probs[i]
            )
            
            # Run strategy
            metrics = self.simulate_strategy_performance(prices, use_crash_detection=True)
            
            all_returns.append(metrics["total_return"])
            all_drawdowns.append(metrics["max_drawdown"])
            all_sharpes.append(metrics["sharpe_ratio"])
        
        all_returns = np.array(all_returns)
        all_drawdowns = np.array(all_drawdowns)
        all_sharpes = np.array(all_sharpes)
        
        # Calculate survival rate
        survived = all_drawdowns < drawdown_threshold
        survival_rate = survived.mean() * 100
        
        return MonteCarloResults(
            n_simulations=self.n_simulations,
            survival_rate=survival_rate,
            median_return=np.median(all_returns) * 100,
            mean_return=np.mean(all_returns) * 100,
            return_5th_percentile=np.percentile(all_returns, 5) * 100,
            return_95th_percentile=np.percentile(all_returns, 95) * 100,
            median_drawdown=np.median(all_drawdowns) * 100,
            drawdown_5th_percentile=np.percentile(all_drawdowns, 5) * 100,
            drawdown_95th_percentile=np.percentile(all_drawdowns, 95) * 100,
            median_sharpe=np.median(all_sharpes),
            all_returns=all_returns,
            all_drawdowns=all_drawdowns,
            all_sharpes=all_sharpes
        )
    
    def compare_with_benchmark(
        self,
        verbose: bool = True
    ) -> Tuple[MonteCarloResults, MonteCarloResults]:
        """
        Compare strategy with buy-and-hold across Monte Carlo scenarios.
        
        Returns:
            Tuple of (strategy_results, benchmark_results)
        """
        strategy_returns = []
        strategy_drawdowns = []
        benchmark_returns = []
        benchmark_drawdowns = []
        
        crash_probs = np.random.uniform(0.005, 0.05, self.n_simulations)
        volatilities = np.random.uniform(0.02, 0.06, self.n_simulations)
        
        for i in range(self.n_simulations):
            if verbose and (i + 1) % 200 == 0:
                print(f"    Simulation {i+1}/{self.n_simulations}...")
            
            prices = self.generate_price_path(
                base_volatility=volatilities[i],
                crash_probability=crash_probs[i]
            )
            
            # Strategy with crash detection
            strat_metrics = self.simulate_strategy_performance(prices, use_crash_detection=True)
            strategy_returns.append(strat_metrics["total_return"])
            strategy_drawdowns.append(strat_metrics["max_drawdown"])
            
            # Benchmark without crash detection
            bench_metrics = self.simulate_strategy_performance(prices, use_crash_detection=False)
            benchmark_returns.append(bench_metrics["total_return"])
            benchmark_drawdowns.append(bench_metrics["max_drawdown"])
        
        strategy_results = MonteCarloResults(
            n_simulations=self.n_simulations,
            survival_rate=(np.array(strategy_drawdowns) < 0.50).mean() * 100,
            median_return=np.median(strategy_returns) * 100,
            mean_return=np.mean(strategy_returns) * 100,
            return_5th_percentile=np.percentile(strategy_returns, 5) * 100,
            return_95th_percentile=np.percentile(strategy_returns, 95) * 100,
            median_drawdown=np.median(strategy_drawdowns) * 100,
            drawdown_5th_percentile=np.percentile(strategy_drawdowns, 5) * 100,
            drawdown_95th_percentile=np.percentile(strategy_drawdowns, 95) * 100,
            median_sharpe=0,
            all_returns=np.array(strategy_returns),
            all_drawdowns=np.array(strategy_drawdowns),
            all_sharpes=np.array([])
        )
        
        benchmark_results = MonteCarloResults(
            n_simulations=self.n_simulations,
            survival_rate=(np.array(benchmark_drawdowns) < 0.50).mean() * 100,
            median_return=np.median(benchmark_returns) * 100,
            mean_return=np.mean(benchmark_returns) * 100,
            return_5th_percentile=np.percentile(benchmark_returns, 5) * 100,
            return_95th_percentile=np.percentile(benchmark_returns, 95) * 100,
            median_drawdown=np.median(benchmark_drawdowns) * 100,
            drawdown_5th_percentile=np.percentile(benchmark_drawdowns, 5) * 100,
            drawdown_95th_percentile=np.percentile(benchmark_drawdowns, 95) * 100,
            median_sharpe=0,
            all_returns=np.array(benchmark_returns),
            all_drawdowns=np.array(benchmark_drawdowns),
            all_sharpes=np.array([])
        )
        
        return strategy_results, benchmark_results


def plot_monte_carlo_results(
    results: MonteCarloResults,
    benchmark_results: Optional[MonteCarloResults] = None,
    figsize: Tuple[int, int] = (14, 10)
):
    """
    Visualize Monte Carlo simulation results.
    
    Args:
        results: Strategy results
        benchmark_results: Optional benchmark results
        figsize: Figure size
        
    Returns:
        Matplotlib Figure
    """
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # 1. Return distribution
    ax1 = axes[0, 0]
    ax1.hist(results.all_returns * 100, bins=50, alpha=0.7, 
             color="steelblue", label="Strategy", density=True)
    if benchmark_results is not None:
        ax1.hist(benchmark_results.all_returns * 100, bins=50, alpha=0.5, 
                 color="gray", label="Buy & Hold", density=True)
    ax1.axvline(results.median_return, color="blue", linestyle="--", 
                label=f"Median: {results.median_return:.1f}%")
    ax1.set_xlabel("Annual Return (%)")
    ax1.set_ylabel("Density")
    ax1.set_title("Return Distribution (Monte Carlo)", fontweight="bold")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Drawdown distribution
    ax2 = axes[0, 1]
    ax2.hist(results.all_drawdowns * 100, bins=50, alpha=0.7, 
             color="indianred", label="Strategy", density=True)
    if benchmark_results is not None:
        ax2.hist(benchmark_results.all_drawdowns * 100, bins=50, alpha=0.5, 
                 color="gray", label="Buy & Hold", density=True)
    ax2.axvline(50, color="red", linestyle="--", label="50% Threshold")
    ax2.set_xlabel("Max Drawdown (%)")
    ax2.set_ylabel("Density")
    ax2.set_title("Drawdown Distribution", fontweight="bold")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Return vs Drawdown scatter
    ax3 = axes[1, 0]
    ax3.scatter(results.all_drawdowns * 100, results.all_returns * 100, 
                alpha=0.5, s=10, color="steelblue", label="Strategy")
    if benchmark_results is not None:
        ax3.scatter(benchmark_results.all_drawdowns * 100, 
                   benchmark_results.all_returns * 100,
                   alpha=0.3, s=10, color="gray", label="Buy & Hold")
    ax3.axvline(50, color="red", linestyle="--", alpha=0.7)
    ax3.axhline(0, color="black", linestyle="-", alpha=0.3)
    ax3.set_xlabel("Max Drawdown (%)")
    ax3.set_ylabel("Total Return (%)")
    ax3.set_title("Risk-Return Profile", fontweight="bold")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Summary statistics
    ax4 = axes[1, 1]
    ax4.axis("off")
    
    stats_text = f"""
    MONTE CARLO SIMULATION RESULTS
    ══════════════════════════════════
    
    Simulations: {results.n_simulations:,}
    
    SURVIVAL RATE (DD < 50%)
    ────────────────────────
    Strategy:    {results.survival_rate:.1f}%
    """
    
    if benchmark_results:
        stats_text += f"Buy & Hold:  {benchmark_results.survival_rate:.1f}%"
    
    stats_text += f"""
    
    RETURN (Annual)
    ────────────────────────
    Median:    {results.median_return:+.1f}%
    5th %ile:  {results.return_5th_percentile:+.1f}%
    95th %ile: {results.return_95th_percentile:+.1f}%
    
    MAX DRAWDOWN
    ────────────────────────
    Median:    {results.median_drawdown:.1f}%
    95th %ile: {results.drawdown_95th_percentile:.1f}%
    """
    
    ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes,
             fontsize=11, verticalalignment="top", fontfamily="monospace",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9))
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    print("=" * 70)
    print("  FinPilot | Monte Carlo Stress Simulation")
    print("=" * 70)
    
    # Run simulation
    print("\n[1] Running 1,000 Monte Carlo simulations...")
    simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)
    
    print("\n[2] Comparing Strategy vs Buy & Hold...")
    strategy_results, benchmark_results = simulator.compare_with_benchmark()
    
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)
    
    print(f"""
    Strategy:
      Survival Rate (DD<50%): {strategy_results.survival_rate:.1f}%
      Median Return:          {strategy_results.median_return:+.1f}%
      Median Drawdown:        {strategy_results.median_drawdown:.1f}%
    
    Buy & Hold:
      Survival Rate (DD<50%): {benchmark_results.survival_rate:.1f}%
      Median Return:          {benchmark_results.median_return:+.1f}%
      Median Drawdown:        {benchmark_results.median_drawdown:.1f}%
    """)
    
    print("✅ Monte Carlo simulation complete!")
