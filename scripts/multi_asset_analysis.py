#!/usr/bin/env python3
"""
FinPilot - Multi-Asset Analysis
Analyzes correlations between BTC and ETH during different market regimes.
"""

import sys
sys.path.insert(0, 'src')

import pandas as pd
import numpy as np
from data_handler import DataHandler
from features import FeatureEngineer
from regime_detector import RegimeDetector

print("=" * 70)
print("FINPILOT - MULTI-ASSET CORRELATION ANALYSIS")
print("=" * 70)

# 1. Load Data
print("\n[1] Loading Portfolio (BTC, ETH, NASDAQ)...")
handler = DataHandler()
crypto_files = {
    'BTC': 'BTC_USD Bitfinex Historical Data.csv',
    'ETH': 'ETH_USD Binance Historical Data.csv'
}
cryptos, nasdaq = handler.load_portfolio(crypto_files, 'Nasdaq 100 Historical Data.csv')

print(f"    Date Range: {nasdaq.index[0].strftime('%Y-%m-%d')} to {nasdaq.index[-1].strftime('%Y-%m-%d')}")
print(f"    Aligned Days: {len(nasdaq)}")

# 2. Detect Regimes (using BTC parameters)
print("\n[2] Detecting Regimes (Base: BTC)...")
# We use BTC features for regime detection as it's the market leader
fe = FeatureEngineer(window=15) # Optimized window
btc_features = fe.generate_all_features(cryptos['BTC'], nasdaq)

# Load optimized params for detection
import json
with open('models/best_params.json', 'r') as f:
    params = json.load(f)

detector = RegimeDetector(
    duvol_threshold=params['duvol_threshold'],
    nasdaq_drop_threshold=params['nasdaq_drop_threshold'],
    volatility_ratio_threshold=1.0
)
regimes = detector.detect_regimes(btc_features)

# 3. Analyze Correlations
print("\n[3] Correlation Analysis by Regime...")

# Create combined dataframe of returns
returns_df = pd.DataFrame({
    'BTC': cryptos['BTC']['returns'],
    'ETH': cryptos['ETH']['returns'],
    'NASDAQ': nasdaq['returns']
})
returns_df['Regime'] = regimes

# Calculate overall correlation
overall_corr = returns_df[['BTC', 'ETH']].corr().iloc[0,1]
print(f"    Overall BTC-ETH Correlation: {overall_corr:.4f}")

# Calculate correlation by regime
print("\n    Regime-Specific Correlations (BTC vs ETH):")
print("    " + "-" * 45)
print(f"    {'Regime':<15} {'Correlation':<15} {'Days':<10}")
print("    " + "-" * 45)

for regime in ['normal', 'crash', 'recovery']:
    subset = returns_df[returns_df['Regime'] == regime]
    if len(subset) > 10:
        corr = subset[['BTC', 'ETH']].corr().iloc[0,1]
        print(f"    {regime.upper():<15} {corr:<15.4f} {len(subset):<10}")
    else:
        print(f"    {regime.upper():<15} {'N/A':<15} {len(subset):<10}")

# 4. Analyze Downside correlations
print("\n[4] Tail Risk Analysis...")
# Correlation when BTC drops > 5%
crash_days = returns_df[returns_df['BTC'] < -0.05]
crash_corr = crash_days[['BTC', 'ETH']].corr().iloc[0,1]
print(f"    Correlation when BTC < -5%: {crash_corr:.4f} ({len(crash_days)} days)")

# 5. Conclusion
print("\n" + "=" * 70)
if overall_corr > 0.8:
    print("⚠️ HIGH CORRELATION DETECTED")
    print("   BTC and ETH are highly correlated. Diversification benefit may be")
    print("   limited during crashes, but alpha can still be generated if")
    print("   regime timing differs or volatility differs.")
else:
    print("✅ GOOD DIVERSIFICATION POTENTIAL")
print("=" * 70)
