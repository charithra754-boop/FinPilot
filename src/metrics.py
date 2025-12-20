"""
Evaluation Metrics Module
Calculates competition metrics: CSI, Sharpe Ratio, Max Drawdown.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class Metrics:
    """
    Calculates evaluation metrics for trading strategies.
    
    Key Metrics:
    - CSI (Crash Survivability Index)
    - Sharpe Ratio
    - Max Drawdown
    - Sortino Ratio
    - Calmar Ratio
    """
    
    def __init__(
        self,
        risk_free_rate: float = 0.02,
        trading_days: int = 252
    ):
        """
        Args:
            risk_free_rate: Annual risk-free rate
            trading_days: Trading days per year for annualization
        """
        self.risk_free_rate = risk_free_rate
        self.trading_days = trading_days
        self.daily_rf = (1 + risk_free_rate) ** (1 / trading_days) - 1
    
    def calculate_sharpe_ratio(
        self, 
        returns: pd.Series
    ) -> float:
        """
        Calculate Sharpe Ratio.
        
        Formula:
            Sharpe = (μ - r_f) / σ
        
        Args:
            returns: Series of returns
            
        Returns:
            Annualized Sharpe ratio
        """
        if returns.empty or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - self.daily_rf
        sharpe = excess_returns.mean() / returns.std()
        
        # Annualize
        return sharpe * np.sqrt(self.trading_days)
    
    def calculate_max_drawdown(
        self, 
        equity_curve: pd.Series
    ) -> float:
        """
        Calculate Maximum Drawdown.
        
        Args:
            equity_curve: Series of portfolio values
            
        Returns:
            Maximum drawdown as positive percentage
        """
        rolling_max = equity_curve.expanding().max()
        drawdown = (equity_curve - rolling_max) / rolling_max
        return abs(drawdown.min())
    
    def calculate_csi(
        self,
        strategy_return: float,
        max_drawdown: float,
        risk_free_rate: float = None
    ) -> float:
        """
        Calculate Crash Survivability Index (CSI).
        
        Formula:
            CSI = (R_strategy - R_f) / max(Drawdown)
        
        Args:
            strategy_return: Total strategy return (as decimal)
            max_drawdown: Maximum drawdown (as positive decimal)
            risk_free_rate: Risk-free rate (uses default if None)
            
        Returns:
            CSI value
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        if max_drawdown == 0:
            return float("inf") if strategy_return > 0 else 0.0
        
        return (strategy_return - risk_free_rate) / max_drawdown
    
    def calculate_sortino_ratio(
        self, 
        returns: pd.Series
    ) -> float:
        """
        Calculate Sortino Ratio (downside risk adjusted).
        
        Args:
            returns: Series of returns
            
        Returns:
            Annualized Sortino ratio
        """
        if returns.empty:
            return 0.0
        
        excess_returns = returns - self.daily_rf
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return float("inf") if excess_returns.mean() > 0 else 0.0
        
        sortino = excess_returns.mean() / downside_returns.std()
        return sortino * np.sqrt(self.trading_days)
    
    def calculate_calmar_ratio(
        self,
        annual_return: float,
        max_drawdown: float
    ) -> float:
        """
        Calculate Calmar Ratio.
        
        Args:
            annual_return: Annualized return
            max_drawdown: Maximum drawdown
            
        Returns:
            Calmar ratio
        """
        if max_drawdown == 0:
            return float("inf") if annual_return > 0 else 0.0
        
        return annual_return / max_drawdown
    
    def calculate_win_rate(
        self, 
        trades: pd.DataFrame
    ) -> float:
        """
        Calculate win rate from trades.
        
        Args:
            trades: DataFrame with trade P&L
            
        Returns:
            Win rate as percentage
        """
        if trades.empty:
            return 0.0
        
        profitable = (trades["pnl"] > 0).sum()
        return profitable / len(trades) * 100
    
    def calculate_volatility(
        self, 
        returns: pd.Series,
        annualize: bool = True
    ) -> float:
        """
        Calculate volatility.
        
        Args:
            returns: Series of returns
            annualize: Whether to annualize
            
        Returns:
            Volatility
        """
        vol = returns.std()
        if annualize:
            vol *= np.sqrt(self.trading_days)
        return vol
    
    def calculate_var(
        self,
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Value at Risk (VaR) using historical method.
        
        VaR represents the maximum expected loss at a given confidence level.
        
        Args:
            returns: Series of returns
            confidence_level: Confidence level (0.95 = 95%)
            
        Returns:
            VaR as positive percentage (e.g., 0.05 = 5% max loss)
        """
        if returns.empty:
            return 0.0
        
        # Historical VaR: percentile of losses
        var = returns.quantile(1 - confidence_level)
        return abs(var)
    
    def calculate_cvar(
        self,
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Conditional VaR (CVaR) / Expected Shortfall.
        
        CVaR is the expected loss given that the loss exceeds VaR.
        More conservative than VaR for tail risk.
        
        Args:
            returns: Series of returns
            confidence_level: Confidence level (0.95 = 95%)
            
        Returns:
            CVaR as positive percentage
        """
        if returns.empty:
            return 0.0
        
        var = returns.quantile(1 - confidence_level)
        # Average of returns worse than VaR
        tail_returns = returns[returns <= var]
        
        if tail_returns.empty:
            return abs(var)
        
        return abs(tail_returns.mean())
    
    def calculate_recovery_time(
        self,
        equity_curve: pd.Series
    ) -> Dict:
        """
        Calculate time to recover from maximum drawdown.
        
        Args:
            equity_curve: Series of portfolio values
            
        Returns:
            Dictionary with recovery metrics
        """
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        
        # Find max drawdown point
        max_dd_idx = drawdown.idxmin()
        max_dd_value = drawdown.min()
        
        # Find when we recovered (drawdown returns to 0)
        recovery_mask = (equity_curve.index > max_dd_idx) & (drawdown >= 0)
        
        if recovery_mask.any():
            recovery_idx = equity_curve.index[recovery_mask][0]
            try:
                recovery_days = (recovery_idx - max_dd_idx).days
            except AttributeError:
                # Handle integer index
                recovery_days = int(recovery_idx - max_dd_idx)
            recovered = True
        else:
            try:
                recovery_days = (equity_curve.index[-1] - max_dd_idx).days
            except AttributeError:
                recovery_days = int(len(equity_curve) - equity_curve.index.get_loc(max_dd_idx)) - 1
            recovered = False
        
        return {
            "max_drawdown_date": max_dd_idx,
            "max_drawdown_pct": abs(max_dd_value) * 100,
            "recovery_days": recovery_days,
            "recovered": recovered
        }
    
    def calculate_all_metrics(
        self,
        equity_curve: pd.Series,
        returns: pd.Series = None,
        crash_window: tuple = None
    ) -> Dict:
        """
        Calculate all evaluation metrics.
        
        Args:
            equity_curve: Series of portfolio values
            returns: Optional pre-calculated returns
            crash_window: Optional (start, end) for crash period analysis
            
        Returns:
            Dictionary of all metrics
        """
        if returns is None:
            returns = equity_curve.pct_change().dropna()
        
        # Calculate total return
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        
        # Max drawdown
        max_dd = self.calculate_max_drawdown(equity_curve)
        
        # Annualized return (assuming daily data)
        n_days = len(equity_curve)
        annual_return = (1 + total_return) ** (self.trading_days / n_days) - 1
        
        metrics = {
            "total_return": total_return * 100,
            "annual_return": annual_return * 100,
            "cagr": annual_return * 100,
            "max_drawdown": max_dd * 100,
            "sharpe_ratio": self.calculate_sharpe_ratio(returns),
            "sortino_ratio": self.calculate_sortino_ratio(returns),
            "calmar_ratio": self.calculate_calmar_ratio(annual_return, max_dd),
            "csi": self.calculate_csi(total_return, max_dd),
            "volatility": self.calculate_volatility(returns) * 100,
            "var_95": self.calculate_var(returns, 0.95) * 100,
            "var_99": self.calculate_var(returns, 0.99) * 100,
            "cvar_95": self.calculate_cvar(returns, 0.95) * 100,
            "cvar_99": self.calculate_cvar(returns, 0.99) * 100,
        }
        
        # Add recovery time metrics
        recovery_info = self.calculate_recovery_time(equity_curve)
        metrics["recovery_days"] = recovery_info["recovery_days"]
        metrics["recovered"] = recovery_info["recovered"]
        
        # Crash period analysis if provided
        if crash_window is not None:
            start, end = crash_window
            crash_equity = equity_curve.loc[start:end]
            if len(crash_equity) > 1:
                crash_return = (crash_equity.iloc[-1] / crash_equity.iloc[0]) - 1
                crash_dd = self.calculate_max_drawdown(crash_equity)
                metrics["crash_return"] = crash_return * 100
                metrics["crash_max_drawdown"] = crash_dd * 100
                metrics["crash_csi"] = self.calculate_csi(crash_return, crash_dd)
        
        return metrics
    
    def format_latex(self, metrics: Dict) -> str:
        """
        Format metrics as LaTeX for notebook display.
        
        Args:
            metrics: Dictionary of metrics
            
        Returns:
            LaTeX formatted string
        """
        latex = r"""
\begin{align}
CSI &= \frac{R_{strategy} - R_f}{\max(Drawdown)} = """ + f"{metrics.get('csi', 0):.2f}" + r""" \\
Sharpe &= \frac{\mu - r_f}{\sigma} = """ + f"{metrics.get('sharpe_ratio', 0):.2f}" + r""" \\
MaxDD &= """ + f"{metrics.get('max_drawdown', 0):.2f}" + r"""\%
\end{align}
"""
        return latex


if __name__ == "__main__":
    # Test metrics
    from data_handler import DataHandler, create_sample_data
    from features import FeatureEngineer
    from regime_detector import RegimeDetector
    from strategy import TradingStrategy
    from backtester import Backtester
    
    # Full pipeline
    create_sample_data()
    handler = DataHandler()
    crypto_df, nasdaq_df = handler.load_and_prepare(
        "crypto_btc.csv", 
        "nasdaq_index.csv"
    )
    
    fe = FeatureEngineer(window=20)
    features = fe.generate_all_features(crypto_df, nasdaq_df)
    
    detector = RegimeDetector()
    regimes = detector.detect_regimes(features)
    
    strategy = TradingStrategy()
    signals = strategy.run_strategy(features, regimes)
    
    backtester = Backtester()
    results = backtester.run_backtest(features, signals)
    
    # Calculate metrics
    metrics_calc = Metrics()
    equity = results["portfolio_value"]
    metrics = metrics_calc.calculate_all_metrics(equity)
    
    print("Evaluation Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")
    
    print("\nLaTeX Output:")
    print(metrics_calc.format_latex(metrics))
