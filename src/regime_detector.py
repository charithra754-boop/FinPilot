"""
Regime Detector Module
Implements market regime detection for regime-switching trading strategy.
"""

import pandas as pd
import numpy as np
from enum import Enum
from typing import Optional


class MarketRegime(Enum):
    """Market regime states."""
    NORMAL = "normal"
    CRASH = "crash"
    RECOVERY = "recovery"


class RegimeDetector:
    """
    Detects market regimes using multiple indicators.
    
    Regimes:
    - NORMAL: Default state, trend-following signals apply
    - CRASH: Danger detected, liquidate to cash
    - RECOVERY: Waiting for volatility mean reversion before re-entry
    """
    
    def __init__(
        self,
        duvol_threshold: float = 0.5,
        nasdaq_drop_threshold: float = -0.03,
        volatility_ratio_threshold: float = 1.0
    ):
        """
        Args:
            duvol_threshold: DUVOL level that triggers crash regime
            nasdaq_drop_threshold: NASDAQ return threshold for crash (-3%)
            volatility_ratio_threshold: Vol_10d/Vol_30d ratio for recovery
        """
        self.duvol_threshold = duvol_threshold
        self.nasdaq_drop_threshold = nasdaq_drop_threshold
        self.volatility_ratio_threshold = volatility_ratio_threshold
    
    def detect_crash_regime(
        self,
        duvol: float,
        nasdaq_return: float,
        canary_signal: int
    ) -> bool:
        """
        Detect if market is in crash regime.
        
        Triggers:
        - DUVOL > threshold OR
        - NASDAQ Return < -3% OR
        - Canary signal is active
        
        Args:
            duvol: Current DUVOL value
            nasdaq_return: Current NASDAQ return
            canary_signal: Current canary signal (0 or 1)
            
        Returns:
            True if crash regime detected
        """
        if pd.isna(duvol):
            duvol = 0
        
        crash_conditions = [
            duvol > self.duvol_threshold,
            nasdaq_return < self.nasdaq_drop_threshold,
            canary_signal == 1
        ]
        
        return any(crash_conditions)
    
    def detect_recovery_complete(
        self,
        volatility_10d: float,
        volatility_30d: float
    ) -> bool:
        """
        Detect if recovery is complete (safe to re-enter market).
        
        Recovery is complete when 10-day volatility drops below 30-day average.
        
        Args:
            volatility_10d: 10-day rolling volatility
            volatility_30d: 30-day rolling volatility
            
        Returns:
            True if safe to re-enter
        """
        if pd.isna(volatility_10d) or pd.isna(volatility_30d) or volatility_30d == 0:
            return False
        
        vol_ratio = volatility_10d / volatility_30d
        return vol_ratio < self.volatility_ratio_threshold
    
    def get_regime(
        self,
        features: pd.Series,
        current_regime: MarketRegime
    ) -> MarketRegime:
        """
        Determine the current market regime based on features and previous state.
        
        State machine:
        - NORMAL -> CRASH: When crash conditions met
        - CRASH -> RECOVERY: Immediately after entering crash
        - RECOVERY -> NORMAL: When volatility mean reverts
        
        Args:
            features: Series containing current feature values
            current_regime: Previous regime state
            
        Returns:
            New market regime
        """
        duvol = features.get("duvol", 0)
        nasdaq_returns = features.get("nasdaq_returns", 0)
        canary_signal = features.get("canary_signal", 0)
        volatility_10d = features.get("volatility_10d", 0)
        volatility_30d = features.get("volatility_30d", 0)
        
        # Check for crash signals
        is_crash = self.detect_crash_regime(duvol, nasdaq_returns, canary_signal)
        
        # State machine logic
        if current_regime == MarketRegime.NORMAL:
            if is_crash:
                return MarketRegime.CRASH
            return MarketRegime.NORMAL
        
        elif current_regime == MarketRegime.CRASH:
            # Immediately move to recovery mode
            return MarketRegime.RECOVERY
        
        elif current_regime == MarketRegime.RECOVERY:
            if is_crash:
                # Stay in crash/recovery if still dangerous
                return MarketRegime.CRASH
            
            if self.detect_recovery_complete(volatility_10d, volatility_30d):
                return MarketRegime.NORMAL
            return MarketRegime.RECOVERY
        
        return MarketRegime.NORMAL
    
    def detect_regimes(self, features: pd.DataFrame) -> pd.Series:
        """
        Detect regimes for entire feature DataFrame.
        
        Args:
            features: DataFrame with all features
            
        Returns:
            Series of regime labels
        """
        regimes = []
        current_regime = MarketRegime.NORMAL
        
        for idx in features.index:
            row = features.loc[idx]
            current_regime = self.get_regime(row, current_regime)
            regimes.append(current_regime.value)
        
        return pd.Series(regimes, index=features.index, name="regime")


if __name__ == "__main__":
    # Test regime detection
    from data_handler import DataHandler, create_sample_data
    from features import FeatureEngineer
    
    # Create sample data
    create_sample_data()
    
    # Load and prepare data
    handler = DataHandler()
    crypto_df, nasdaq_df = handler.load_and_prepare(
        "crypto_btc.csv", 
        "nasdaq_index.csv"
    )
    
    # Generate features
    fe = FeatureEngineer(window=20)
    features = fe.generate_all_features(crypto_df, nasdaq_df)
    
    # Detect regimes
    detector = RegimeDetector()
    regimes = detector.detect_regimes(features)
    
    print("Regime distribution:")
    print(regimes.value_counts())
    print(f"\nCrash periods: {(regimes == 'crash').sum()}")
    print(f"Recovery periods: {(regimes == 'recovery').sum()}")
