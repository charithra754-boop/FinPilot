"""
Crash Intensity Scoring Module for FinPilot
Novel approach: Continuous crash scoring with proportional response and adaptive recovery.

This module implements:
1. Crash Intensity Score (CIS) - Continuous 0-100 metric
2. Proportional Position Sizing - Graduated response to crash intensity
3. Adaptive Recovery Engine - Optimal re-entry timing

Author: FinPilot Team
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CrashIntensityConfig:
    """Configuration for Crash Intensity Scoring."""
    # Component weights (must sum to 1.0)
    duvol_weight: float = 0.25
    ncskew_weight: float = 0.20
    volatility_weight: float = 0.25
    canary_weight: float = 0.15
    momentum_weight: float = 0.15
    
    # Thresholds for normalization
    duvol_high: float = 1.0        # DUVOL above this = 100 intensity
    ncskew_high: float = 2.0       # NCSKEW above this = 100 intensity
    vol_spike_multiplier: float = 3.0  # Vol 3x average = 100 intensity
    
    # Recovery parameters
    recovery_threshold: float = 0.60   # Recovery score needed to re-enter
    min_recovery_days: int = 3         # Minimum days before considering re-entry
    scaling_steps: int = 4             # Number of steps to scale back in


class CrashIntensityScorer:
    """
    Calculates Crash Intensity Score (CIS) - a novel continuous metric.
    
    Unlike binary crash detection, CIS provides a 0-100 score indicating
    crash severity, enabling proportional position sizing.
    
    Innovation:
    - Continuous scoring instead of binary threshold
    - Multi-factor weighted combination
    - Proportional response reduces whipsaws
    - Adaptive recovery timing
    """
    
    def __init__(self, config: CrashIntensityConfig = None):
        """
        Args:
            config: CrashIntensityConfig with weights and thresholds
        """
        self.config = config or CrashIntensityConfig()
        self._validate_config()
    
    def _validate_config(self):
        """Ensure weights sum to 1.0."""
        total = (
            self.config.duvol_weight +
            self.config.ncskew_weight +
            self.config.volatility_weight +
            self.config.canary_weight +
            self.config.momentum_weight
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def _normalize_to_100(
        self, 
        value: float, 
        low: float, 
        high: float
    ) -> float:
        """
        Normalize a value to 0-100 scale.
        
        Args:
            value: Raw value
            low: Value that maps to 0
            high: Value that maps to 100
            
        Returns:
            Normalized value 0-100
        """
        if high == low:
            return 50.0
        
        normalized = (value - low) / (high - low) * 100
        return min(max(normalized, 0), 100)
    
    def calculate_duvol_intensity(
        self, 
        duvol: float
    ) -> float:
        """
        Calculate DUVOL contribution to crash intensity.
        
        Higher DUVOL = higher crash intensity.
        DUVOL > 1.0 is very dangerous.
        
        Args:
            duvol: DUVOL value
            
        Returns:
            Intensity 0-100
        """
        if pd.isna(duvol):
            return 0.0
        
        # DUVOL of 0 = neutral, DUVOL of 1.0+ = dangerous
        return self._normalize_to_100(duvol, 0, self.config.duvol_high)
    
    def calculate_ncskew_intensity(
        self, 
        ncskew: float
    ) -> float:
        """
        Calculate NCSKEW contribution to crash intensity.
        
        Higher NCSKEW = more negative skew = higher crash probability.
        
        Args:
            ncskew: NCSKEW value
            
        Returns:
            Intensity 0-100
        """
        if pd.isna(ncskew):
            return 0.0
        
        return self._normalize_to_100(ncskew, 0, self.config.ncskew_high)
    
    def calculate_volatility_intensity(
        self, 
        current_vol: float,
        avg_vol: float
    ) -> float:
        """
        Calculate volatility spike contribution.
        
        Volatility 3x above average = maximum intensity.
        
        Args:
            current_vol: Current 10-day volatility
            avg_vol: Long-term average volatility
            
        Returns:
            Intensity 0-100
        """
        if pd.isna(current_vol) or pd.isna(avg_vol) or avg_vol <= 0:
            return 0.0
        
        vol_ratio = current_vol / avg_vol
        max_ratio = self.config.vol_spike_multiplier
        
        return self._normalize_to_100(vol_ratio, 1.0, max_ratio)
    
    def calculate_momentum_intensity(
        self, 
        returns_5d: float
    ) -> float:
        """
        Calculate negative momentum contribution.
        
        Sharp negative returns indicate crash in progress.
        
        Args:
            returns_5d: 5-day cumulative return
            
        Returns:
            Intensity 0-100
        """
        if pd.isna(returns_5d):
            return 0.0
        
        # Negative returns increase intensity
        # -20% return = 100 intensity
        if returns_5d >= 0:
            return 0.0
        
        return self._normalize_to_100(abs(returns_5d), 0, 0.20)
    
    def calculate_canary_intensity(
        self, 
        nasdaq_return: float
    ) -> float:
        """
        Calculate NASDAQ canary signal contribution.
        
        NASDAQ drop of -5% = maximum intensity.
        
        Args:
            nasdaq_return: NASDAQ daily return
            
        Returns:
            Intensity 0-100
        """
        if pd.isna(nasdaq_return):
            return 0.0
        
        if nasdaq_return >= 0:
            return 0.0
        
        # -5% NASDAQ drop = 100 intensity
        return self._normalize_to_100(abs(nasdaq_return), 0, 0.05)
    
    def calculate_crash_intensity(
        self, 
        features: pd.Series
    ) -> float:
        """
        Calculate the composite Crash Intensity Score (CIS).
        
        Formula:
            CIS = w1·DUVOL_norm + w2·NCSKEW_norm + w3·Vol_spike + 
                  w4·Canary + w5·Momentum
        
        Args:
            features: Series with feature values
            
        Returns:
            Crash Intensity Score 0-100
        """
        # Get feature values
        duvol = features.get("duvol", 0)
        ncskew = features.get("ncskew", 0)
        vol_10d = features.get("volatility_10d", 0)
        vol_30d = features.get("volatility_30d", vol_10d)
        nasdaq_return = features.get("nasdaq_returns", 0)
        
        # Calculate 5-day momentum
        returns = features.get("returns", 0)
        returns_5d = returns * 5 if not pd.isna(returns) else 0  # Approximate
        
        # Calculate individual intensities
        duvol_int = self.calculate_duvol_intensity(duvol)
        ncskew_int = self.calculate_ncskew_intensity(ncskew)
        vol_int = self.calculate_volatility_intensity(vol_10d, vol_30d)
        momentum_int = self.calculate_momentum_intensity(returns_5d)
        canary_int = self.calculate_canary_intensity(nasdaq_return)
        
        # Weighted combination
        cis = (
            self.config.duvol_weight * duvol_int +
            self.config.ncskew_weight * ncskew_int +
            self.config.volatility_weight * vol_int +
            self.config.momentum_weight * momentum_int +
            self.config.canary_weight * canary_int
        )
        
        return min(cis, 100)
    
    def calculate_proportional_position(
        self, 
        crash_intensity: float,
        base_position: float = 1.0
    ) -> float:
        """
        Calculate proportional position size based on crash intensity.
        
        Novel approach: Graduated response instead of binary exit.
        
        Args:
            crash_intensity: CIS value 0-100
            base_position: Maximum position size (default 100%)
            
        Returns:
            Adjusted position size 0-1
        """
        # Linear scaling: CIS 0 = 100% position, CIS 100 = 0% position
        # But we add a "safety buffer" - start reducing at CIS 20
        
        if crash_intensity < 20:
            return base_position
        elif crash_intensity > 80:
            return 0.0
        else:
            # Linear reduction from 100% at CIS=20 to 0% at CIS=80
            reduction = (crash_intensity - 20) / 60
            return base_position * (1 - reduction)
    
    def calculate_intensity_series(
        self, 
        features: pd.DataFrame
    ) -> pd.Series:
        """
        Calculate CIS for entire feature DataFrame.
        
        Args:
            features: DataFrame with all features
            
        Returns:
            Series of CIS values
        """
        intensities = []
        
        for idx in features.index:
            row = features.loc[idx]
            cis = self.calculate_crash_intensity(row)
            intensities.append(cis)
        
        return pd.Series(intensities, index=features.index, name="crash_intensity")


class AdaptiveRecoveryEngine:
    """
    Optimizes re-entry timing after crashes.
    
    Innovation: Don't wait for arbitrary thresholds.
    Use multiple signals to detect optimal recovery point.
    
    Key insight: Fast recovery is as important as crash avoidance
    for the competition metric (CSI).
    """
    
    def __init__(
        self, 
        config: CrashIntensityConfig = None
    ):
        """
        Args:
            config: Configuration with recovery parameters
        """
        self.config = config or CrashIntensityConfig()
        self.days_since_exit = 0
        self.in_recovery_mode = False
        self.scaling_position = 0.0
    
    def calculate_recovery_score(
        self, 
        features: pd.Series,
        price_ma_10: float,
        crash_intensity: float
    ) -> float:
        """
        Calculate recovery readiness score.
        
        Higher score = safer to re-enter.
        
        Components:
        - Price above short-term MA
        - Volatility declining
        - Volume normalizing
        - Crash intensity decreasing
        
        Args:
            features: Current feature values
            price_ma_10: 10-day moving average
            crash_intensity: Current CIS
            
        Returns:
            Recovery score 0-1
        """
        price = features.get("price", 0)
        vol_10d = features.get("volatility_10d", 0)
        vol_30d = features.get("volatility_30d", vol_10d)
        
        components = []
        
        # 1. Price above MA (momentum recovering)
        if price > 0 and price_ma_10 > 0:
            price_strength = min(price / price_ma_10, 1.1)
            price_score = (price_strength - 0.9) / 0.2  # 0.9-1.1 range to 0-1
            components.append(max(0, min(price_score, 1)))
        else:
            components.append(0)
        
        # 2. Volatility decreasing (calming down)
        if vol_10d > 0 and vol_30d > 0:
            vol_ratio = vol_10d / vol_30d
            # vol_ratio < 1 means short-term vol is below average = calming
            vol_score = max(0, 1 - vol_ratio)
            components.append(min(vol_score * 2, 1))  # Scale up
        else:
            components.append(0)
        
        # 3. Crash intensity low
        intensity_score = max(0, (50 - crash_intensity) / 50)
        components.append(intensity_score)
        
        # 4. RSI recovering (not oversold anymore)
        rsi = features.get("rsi", 50)
        if rsi > 30 and rsi < 70:
            rsi_score = 1.0  # In neutral zone = good
        elif rsi <= 30:
            rsi_score = rsi / 30  # Still oversold
        else:
            rsi_score = 0.8  # Overbought, be cautious
        components.append(rsi_score)
        
        # Weighted average
        weights = [0.3, 0.25, 0.25, 0.2]
        recovery_score = sum(c * w for c, w in zip(components, weights))
        
        return recovery_score
    
    def should_start_recovery(
        self, 
        recovery_score: float,
        days_in_cash: int
    ) -> bool:
        """
        Determine if conditions are right to begin re-entering.
        
        Args:
            recovery_score: Current recovery score 0-1
            days_in_cash: Days since exiting position
            
        Returns:
            True if should start scaling back in
        """
        # Minimum waiting period
        if days_in_cash < self.config.min_recovery_days:
            return False
        
        # Recovery score threshold
        return recovery_score >= self.config.recovery_threshold
    
    def calculate_scaling_position(
        self, 
        current_step: int
    ) -> float:
        """
        Calculate position size during scaling-in period.
        
        Instead of jumping back to 100%, gradually scale in.
        
        Args:
            current_step: Current step in scaling process (1 to scaling_steps)
            
        Returns:
            Position size 0-1
        """
        if current_step <= 0:
            return 0.0
        
        if current_step >= self.config.scaling_steps:
            return 1.0
        
        # Linear scaling
        return current_step / self.config.scaling_steps


class IntensityAwareStrategy:
    """
    Trading strategy using Crash Intensity Scoring.
    
    Combines:
    - CrashIntensityScorer for continuous risk assessment
    - AdaptiveRecoveryEngine for optimal re-entry
    - Proportional position sizing
    
    This is the novel component that differentiates FinPilot.
    """
    
    def __init__(
        self, 
        config: CrashIntensityConfig = None,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70
    ):
        """
        Args:
            config: CrashIntensityConfig
            rsi_oversold: RSI buy threshold
            rsi_overbought: RSI sell threshold
        """
        self.config = config or CrashIntensityConfig()
        self.scorer = CrashIntensityScorer(self.config)
        self.recovery_engine = AdaptiveRecoveryEngine(self.config)
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
    
    def run_intensity_strategy(
        self, 
        features: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Run the intensity-aware strategy.
        
        Args:
            features: DataFrame with features
            
        Returns:
            DataFrame with signals, positions, intensities
        """
        results = []
        
        position = 0.0
        days_in_cash = 0
        recovery_step = 0
        in_recovery_mode = False
        
        for idx in features.index:
            row = features.loc[idx]
            
            # Calculate crash intensity
            cis = self.scorer.calculate_crash_intensity(row)
            
            # Get proportional position based on intensity
            max_position = self.scorer.calculate_proportional_position(cis)
            
            # Check RSI for entry/exit signals
            rsi = row.get("rsi", 50)
            ma_fast = row.get("ma_fast", 0)
            ma_slow = row.get("ma_slow", 0)
            price = row.get("price", 0)
            
            # Determine target position
            if cis > 70:
                # High crash intensity - stay in cash
                target_position = 0.0
                days_in_cash += 1
                in_recovery_mode = True
                recovery_step = 0
            elif in_recovery_mode:
                # In recovery mode - check for re-entry
                recovery_score = self.recovery_engine.calculate_recovery_score(
                    row, ma_fast, cis
                )
                
                if self.recovery_engine.should_start_recovery(recovery_score, days_in_cash):
                    recovery_step += 1
                    target_position = self.recovery_engine.calculate_scaling_position(recovery_step)
                    
                    if recovery_step >= self.config.scaling_steps:
                        in_recovery_mode = False
                        recovery_step = 0
                else:
                    target_position = 0.0
                    days_in_cash += 1
            else:
                # Normal trading - use RSI + proportional sizing
                if rsi < self.rsi_oversold or (ma_fast > ma_slow and ma_slow > 0):
                    target_position = max_position
                elif rsi > self.rsi_overbought:
                    target_position = max_position * 0.5  # Reduce but don't exit
                else:
                    target_position = position  # Hold
                
                days_in_cash = 0
            
            # Apply position
            position = min(target_position, max_position)
            
            results.append({
                "date": idx,
                "crash_intensity": cis,
                "max_position": max_position,
                "position_size": position,
                "signal": 1 if position > 0 else 0,
                "in_recovery": in_recovery_mode,
                "recovery_step": recovery_step,
                "days_in_cash": days_in_cash
            })
        
        return pd.DataFrame(results).set_index("date")


def calculate_crash_intensity_metrics(
    intensity_series: pd.Series,
    returns: pd.Series
) -> Dict:
    """
    Calculate metrics for crash intensity performance.
    
    Args:
        intensity_series: Series of CIS values
        returns: Series of returns
        
    Returns:
        Dictionary of metrics
    """
    # Correlation between intensity and subsequent returns
    next_day_returns = returns.shift(-1)
    corr = intensity_series.corr(next_day_returns)
    
    # Average intensity before crashes (return < -5%)
    crash_mask = returns < -0.05
    if crash_mask.any():
        avg_intensity_before_crash = intensity_series.shift(1)[crash_mask].mean()
    else:
        avg_intensity_before_crash = 0
    
    # False alarm rate (high intensity but positive returns)
    high_intensity = intensity_series > 70
    positive_returns = returns > 0
    if high_intensity.any():
        false_alarm_rate = (high_intensity & positive_returns).sum() / high_intensity.sum()
    else:
        false_alarm_rate = 0
    
    return {
        "intensity_return_correlation": corr,
        "avg_intensity_before_crash": avg_intensity_before_crash,
        "false_alarm_rate": false_alarm_rate * 100,
        "avg_intensity": intensity_series.mean(),
        "max_intensity": intensity_series.max(),
        "days_above_70": (intensity_series > 70).sum()
    }


if __name__ == "__main__":
    # Demo the crash intensity system
    import numpy as np
    
    print("=" * 70)
    print("  FinPilot | Crash Intensity Scoring System Demo")
    print("=" * 70)
    
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", "2024-01-01", freq="D")
    n = len(dates)
    
    features = pd.DataFrame({
        "price": 10000 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, n))),
        "duvol": np.random.normal(0.3, 0.3, n),
        "ncskew": np.random.normal(0.5, 0.5, n),
        "volatility_10d": np.abs(np.random.normal(0.02, 0.01, n)),
        "volatility_30d": np.abs(np.random.normal(0.02, 0.005, n)),
        "nasdaq_returns": np.random.normal(0.001, 0.01, n),
        "returns": np.random.normal(0.001, 0.02, n),
        "rsi": np.random.uniform(30, 70, n)
    }, index=dates)
    
    features["ma_fast"] = features["price"].rolling(10).mean()
    features["ma_slow"] = features["price"].rolling(30).mean()
    features = features.dropna()
    
    # Initialize system
    scorer = CrashIntensityScorer()
    strategy = IntensityAwareStrategy()
    
    # Calculate intensities
    intensities = scorer.calculate_intensity_series(features)
    
    print(f"\n📊 Crash Intensity Statistics:")
    print(f"   Average CIS:    {intensities.mean():.1f}")
    print(f"   Max CIS:        {intensities.max():.1f}")
    print(f"   Days above 70:  {(intensities > 70).sum()}")
    print(f"   Days below 20:  {(intensities < 20).sum()}")
    
    # Run strategy
    results = strategy.run_intensity_strategy(features)
    
    print(f"\n📈 Strategy Statistics:")
    print(f"   Avg Position:   {results['position_size'].mean()*100:.1f}%")
    print(f"   Days in Cash:   {(results['signal'] == 0).sum()}")
    print(f"   Recovery Events: {results['in_recovery'].sum()}")
    
    print("\n✅ Crash Intensity Scoring System ready!")
