"""
Trading Strategy Module
Implements the hybrid regime-switching trading strategy.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from enum import Enum


class Position(Enum):
    """Position types."""
    LONG = 1
    CASH = 0


class TradingStrategy:
    """
    Hybrid Regime-Switching Trading Strategy.
    
    Normal Regime:
    - Trend-following using RSI and MA crossover
    
    Crash Regime:
    - 100% liquidation to cash
    
    Recovery:
    - Wait for volatility mean reversion before re-entry
    
    Risk Management:
    - Stop-loss protection
    - Volatility-based position sizing
    """
    
    def __init__(
        self,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        stop_loss_pct: float = 0.05,
        max_position_size: float = 1.0,
        volatility_target: float = 0.02
    ):
        """
        Args:
            rsi_oversold: RSI level for buy signal
            rsi_overbought: RSI level for sell signal
            stop_loss_pct: Stop-loss percentage
            max_position_size: Maximum position size (0-1)
            volatility_target: Target volatility for position sizing
        """
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.stop_loss_pct = stop_loss_pct
        self.max_position_size = max_position_size
        self.volatility_target = volatility_target
    
    def calculate_position_size(
        self, 
        volatility: float
    ) -> float:
        """
        Calculate position size based on volatility.
        
        Higher volatility = smaller position.
        
        Args:
            volatility: Current realized volatility
            
        Returns:
            Position size (0 to max_position_size)
        """
        if pd.isna(volatility) or volatility <= 0:
            return self.max_position_size
        
        # Inverse volatility scaling
        size = self.volatility_target / volatility
        return min(size, self.max_position_size)
    
    def check_stop_loss(
        self,
        entry_price: float,
        current_price: float
    ) -> bool:
        """
        Check if stop-loss has been triggered.
        
        Args:
            entry_price: Position entry price
            current_price: Current market price
            
        Returns:
            True if stop-loss triggered
        """
        if entry_price <= 0:
            return False
        
        loss_pct = (entry_price - current_price) / entry_price
        return loss_pct >= self.stop_loss_pct
    
    def generate_normal_signal(
        self,
        features: pd.Series
    ) -> Position:
        """
        Generate trading signal in normal regime.
        
        Uses RSI and MA crossover.
        
        Args:
            features: Current feature values
            
        Returns:
            Position signal
        """
        rsi = features.get("rsi", 50)
        ma_crossover = features.get("ma_crossover", 0)
        
        # Buy conditions: RSI oversold OR bullish MA crossover
        if rsi < self.rsi_oversold or ma_crossover == 1:
            return Position.LONG
        
        # Sell conditions: RSI overbought
        if rsi > self.rsi_overbought:
            return Position.CASH
        
        # No clear signal - maintain current position
        return None
    
    def generate_signal(
        self,
        features: pd.Series,
        regime: str,
        current_position: Position,
        entry_price: float
    ) -> Tuple[Position, float]:
        """
        Generate trading signal based on regime and features.
        
        Args:
            features: Current feature values
            regime: Current market regime
            current_position: Current position
            entry_price: Entry price of current position
            
        Returns:
            Tuple of (new_position, position_size)
        """
        current_price = features.get("price", 0)
        volatility = features.get("volatility_10d", 0.02)
        
        # Crash or Recovery regime: 100% to cash
        if regime in ["crash", "recovery"]:
            return Position.CASH, 0.0
        
        # Check stop-loss
        if current_position == Position.LONG:
            if self.check_stop_loss(entry_price, current_price):
                return Position.CASH, 0.0
        
        # Normal regime: follow trend signals
        signal = self.generate_normal_signal(features)
        
        if signal is None:
            # No signal change
            if current_position == Position.LONG:
                position_size = self.calculate_position_size(volatility)
                return Position.LONG, position_size
            return Position.CASH, 0.0
        
        if signal == Position.LONG:
            position_size = self.calculate_position_size(volatility)
            return Position.LONG, position_size
        
        return Position.CASH, 0.0
    
    def run_strategy(
        self,
        features: pd.DataFrame,
        regimes: pd.Series
    ) -> pd.DataFrame:
        """
        Run strategy on historical data.
        
        Args:
            features: DataFrame with features
            regimes: Series of regime labels
            
        Returns:
            DataFrame with signals, positions, and sizes
        """
        signals = []
        positions = []
        position_sizes = []
        entry_prices = []
        
        current_position = Position.CASH
        current_entry_price = 0.0
        
        for idx in features.index:
            row = features.loc[idx]
            regime = regimes.loc[idx]
            
            # Generate signal
            new_position, size = self.generate_signal(
                row, 
                regime, 
                current_position,
                current_entry_price
            )
            
            # Track entry price
            if new_position == Position.LONG and current_position == Position.CASH:
                current_entry_price = row["price"]
            elif new_position == Position.CASH:
                current_entry_price = 0.0
            
            signals.append(new_position.value)
            positions.append(new_position.name)
            position_sizes.append(size)
            entry_prices.append(current_entry_price)
            
            current_position = new_position
        
        results = pd.DataFrame({
            "signal": signals,
            "position": positions,
            "position_size": position_sizes,
            "entry_price": entry_prices
        }, index=features.index)
        
        return results


if __name__ == "__main__":
    # Test strategy
    from data_handler import DataHandler, create_sample_data
    from features import FeatureEngineer
    from regime_detector import RegimeDetector
    
    # Create and load data
    create_sample_data()
    handler = DataHandler()
    crypto_df, nasdaq_df = handler.load_and_prepare(
        "crypto_btc.csv", 
        "nasdaq_index.csv"
    )
    
    # Generate features and regimes
    fe = FeatureEngineer(window=20)
    features = fe.generate_all_features(crypto_df, nasdaq_df)
    
    detector = RegimeDetector()
    regimes = detector.detect_regimes(features)
    
    # Run strategy
    strategy = TradingStrategy()
    results = strategy.run_strategy(features, regimes)
    
    print("Strategy results:")
    print(results["position"].value_counts())
    print(f"\nTotal trades: {(results['signal'].diff() != 0).sum()}")
