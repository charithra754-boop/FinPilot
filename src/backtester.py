"""
Backtesting Engine Module
Simulates trading with historical data including transaction costs.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple


class Backtester:
    """
    Backtesting engine for strategy evaluation.
    
    Features:
    - Trade simulation with position sizing
    - Transaction costs (slippage)
    - Equity curve generation
    - Drawdown tracking
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        slippage_pct: float = 0.001,  # 0.1% per trade
        commission_pct: float = 0.0
    ):
        """
        Args:
            initial_capital: Starting capital
            slippage_pct: Slippage as percentage of trade value
            commission_pct: Commission as percentage of trade value
        """
        self.initial_capital = initial_capital
        self.slippage_pct = slippage_pct
        self.commission_pct = commission_pct
    
    def calculate_transaction_costs(
        self, 
        trade_value: float
    ) -> float:
        """
        Calculate total transaction costs for a trade.
        
        Args:
            trade_value: Absolute value of trade
            
        Returns:
            Total costs
        """
        slippage = abs(trade_value) * self.slippage_pct
        commission = abs(trade_value) * self.commission_pct
        return slippage + commission
    
    def run_backtest(
        self,
        features: pd.DataFrame,
        signals: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Run backtest simulation.
        
        Args:
            features: DataFrame with price data
            signals: DataFrame with signals and position sizes
            
        Returns:
            DataFrame with backtest results
        """
        results = []
        
        cash = self.initial_capital
        holdings = 0.0
        position = 0  # 0 = no position, 1 = long
        
        prev_signal = 0
        
        for idx in features.index:
            price = features.loc[idx, "price"]
            signal = signals.loc[idx, "signal"]
            position_size = signals.loc[idx, "position_size"]
            
            # Detect trades
            trade_occurred = (signal != prev_signal)
            trade_type = None
            trade_cost = 0.0
            
            if trade_occurred:
                if signal == 1 and prev_signal == 0:
                    # Buy
                    trade_type = "BUY"
                    target_value = cash * position_size
                    trade_cost = self.calculate_transaction_costs(target_value)
                    holdings = (target_value - trade_cost) / price
                    cash = cash - target_value
                    
                elif signal == 0 and prev_signal == 1:
                    # Sell
                    trade_type = "SELL"
                    sell_value = holdings * price
                    trade_cost = self.calculate_transaction_costs(sell_value)
                    cash = cash + sell_value - trade_cost
                    holdings = 0.0
            
            # Calculate portfolio value
            portfolio_value = cash + holdings * price
            
            results.append({
                "date": idx,
                "price": price,
                "signal": signal,
                "position_size": position_size,
                "cash": cash,
                "holdings": holdings,
                "holdings_value": holdings * price,
                "portfolio_value": portfolio_value,
                "trade_type": trade_type,
                "trade_cost": trade_cost
            })
            
            prev_signal = signal
        
        return pd.DataFrame(results).set_index("date")
    
    def calculate_equity_curve(
        self, 
        backtest_results: pd.DataFrame
    ) -> pd.Series:
        """
        Extract equity curve from backtest results.
        
        Args:
            backtest_results: DataFrame from run_backtest
            
        Returns:
            Series of portfolio values
        """
        return backtest_results["portfolio_value"]
    
    def calculate_drawdown(
        self, 
        equity_curve: pd.Series
    ) -> Tuple[pd.Series, float]:
        """
        Calculate drawdown series and maximum drawdown.
        
        Args:
            equity_curve: Series of portfolio values
            
        Returns:
            Tuple of (drawdown_series, max_drawdown)
        """
        rolling_max = equity_curve.expanding().max()
        drawdown = (equity_curve - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        return drawdown, max_drawdown
    
    def calculate_returns(
        self, 
        equity_curve: pd.Series
    ) -> pd.Series:
        """
        Calculate returns from equity curve.
        
        Args:
            equity_curve: Series of portfolio values
            
        Returns:
            Series of returns
        """
        return equity_curve.pct_change().dropna()
    
    def run_buy_and_hold(
        self, 
        features: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Run buy-and-hold benchmark.
        
        Args:
            features: DataFrame with price data
            
        Returns:
            DataFrame with benchmark results
        """
        initial_price = features["price"].iloc[0]
        holdings = (self.initial_capital * (1 - self.slippage_pct)) / initial_price
        
        results = []
        for idx in features.index:
            price = features.loc[idx, "price"]
            portfolio_value = holdings * price
            
            results.append({
                "date": idx,
                "price": price,
                "portfolio_value": portfolio_value
            })
        
        return pd.DataFrame(results).set_index("date")
    
    def generate_summary(
        self, 
        backtest_results: pd.DataFrame,
        benchmark_results: pd.DataFrame = None
    ) -> Dict:
        """
        Generate summary statistics.
        
        Args:
            backtest_results: Strategy backtest results
            benchmark_results: Optional benchmark results
            
        Returns:
            Dictionary of summary statistics
        """
        equity = backtest_results["portfolio_value"]
        returns = self.calculate_returns(equity)
        _, max_dd = self.calculate_drawdown(equity)
        
        # Trade statistics
        trades = backtest_results[backtest_results["trade_type"].notna()]
        total_trades = len(trades)
        total_costs = trades["trade_cost"].sum()
        
        summary = {
            "initial_capital": self.initial_capital,
            "final_value": equity.iloc[-1],
            "total_return": (equity.iloc[-1] / self.initial_capital - 1) * 100,
            "max_drawdown": max_dd * 100,
            "annual_volatility": returns.std() * np.sqrt(252) * 100,
            "total_trades": total_trades,
            "total_transaction_costs": total_costs
        }
        
        if benchmark_results is not None:
            bench_equity = benchmark_results["portfolio_value"]
            bench_return = (bench_equity.iloc[-1] / self.initial_capital - 1) * 100
            summary["benchmark_return"] = bench_return
            summary["excess_return"] = summary["total_return"] - bench_return
        
        return summary


if __name__ == "__main__":
    # Test backtester
    from data_handler import DataHandler, create_sample_data
    from features import FeatureEngineer
    from regime_detector import RegimeDetector
    from strategy import TradingStrategy
    
    # Setup
    create_sample_data()
    handler = DataHandler()
    crypto_df, nasdaq_df = handler.load_and_prepare(
        "crypto_btc.csv", 
        "nasdaq_index.csv"
    )
    
    # Generate features, regimes, signals
    fe = FeatureEngineer(window=20)
    features = fe.generate_all_features(crypto_df, nasdaq_df)
    
    detector = RegimeDetector()
    regimes = detector.detect_regimes(features)
    
    strategy = TradingStrategy()
    signals = strategy.run_strategy(features, regimes)
    
    # Run backtest
    backtester = Backtester(slippage_pct=0.001)
    results = backtester.run_backtest(features, signals)
    benchmark = backtester.run_buy_and_hold(features)
    
    # Summary
    summary = backtester.generate_summary(results, benchmark)
    print("Backtest Summary:")
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")
        else:
            print(f"  {k}: {v}")
