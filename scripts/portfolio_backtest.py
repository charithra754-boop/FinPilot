#!/usr/bin/env python3
"""
FinPilot - Multi-Asset Portfolio Backtest
Runs the strategy on a BTC/ETH portfolio with regime-based allocation.
"""

import sys
sys.path.insert(0, 'src')

import json
import pandas as pd
from data_handler import DataHandler
from features import FeatureEngineer
from regime_detector import RegimeDetector
from strategy import TradingStrategy
from backtester import Backtester
from metrics import Metrics

print("=" * 70)
print("FINPILOT - MULTI-ASSET PORTFOLIO BACKTEST")
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

# 2. Features & Regimes
print("\n[2] Generating Features & Regimes...")
# Load optimized parameters
with open('models/best_params.json', 'r') as f:
    params = json.load(f)

fe = FeatureEngineer(window=params.get('feature_window', 15))

# Generate features for each asset
features_dict = {}
for asset, df in cryptos.items():
    features_dict[asset] = fe.generate_all_features(df, nasdaq)

# Detect regimes using BTC (Market Leader)
detector = RegimeDetector(
    duvol_threshold=params['duvol_threshold'],
    nasdaq_drop_threshold=params['nasdaq_drop_threshold'],
    volatility_ratio_threshold=1.0
)
regimes = detector.detect_regimes(features_dict['BTC'])
print(f"    Crash Days: {(regimes=='crash').sum()} ({((regimes=='crash').sum()/len(regimes))*100:.1f}%)")

# 3. Strategy Execution
print("\n[3] Generating Portfolio Allocations...")
strategy = TradingStrategy(
    rsi_oversold=params['rsi_oversold'],
    rsi_overbought=params['rsi_overbought'],
    stop_loss_pct=params['stop_loss_pct'],
    volatility_target=0.02 # 2% daily volatility target
)

# Portfolio Weights Config: 60% BTC, 40% ETH
# This is the "Base Allocation" in Normal Regime
allocations = {'BTC': 0.60, 'ETH': 0.40}

weights = strategy.run_portfolio_strategy(
    features_dict,
    regimes,
    allocations
)

# 4. Backtest
print("\n[4] Running Rebalancing Backtest...")
# Create a prices dataframe
prices_df = pd.DataFrame({
    'BTC': cryptos['BTC']['Close'],
    'ETH': cryptos['ETH']['Close']
})

backtester = Backtester(initial_capital=100000, slippage_pct=0.001)
results = backtester.run_portfolio_backtest(
    prices_df,
    weights,
    rebalance_threshold=0.02 # Rebalance if drift > 2%
)

# 5. Metrics
metrics_calc = Metrics(risk_free_rate=0.02)
portfolio_equity = results['portfolio_value']
metrics = metrics_calc.calculate_all_metrics(portfolio_equity)

print("\n" + "=" * 70)
print("🏆 PORTFOLIO PERFORMANCE")
print("=" * 70)

print(f"""
┌────────────────────────────────────────────────────────────────────┐
│  ALLOCATION: 60% BTC / 40% ETH (Volatility Scaled)                 │
│  REGIME:     Crash = 100% Cash                                     │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  💰 PERFORMANCE                                                    │
├────────────────────────────────────────────────────────────────────┤
│  Total Return:          {metrics['total_return']:>12,.2f}%                          │
│  Final Value:           ${portfolio_equity.iloc[-1]:>15,.2f}                   │
│  CAGR:                  {metrics['cagr']:>12.2f}%                          │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  📉 RISK METRICS                                                   │
├────────────────────────────────────────────────────────────────────┤
│  Max Drawdown:          {metrics['max_drawdown']:>12.2f}%                          │
│  Sharpe Ratio:          {metrics['sharpe_ratio']:>12.2f}                            │
│  Sortino Ratio:         {metrics['sortino_ratio']:>12.2f}                            │
│  Volatility:            {metrics['volatility']:>12.2f}%                          │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  🔄 TRADING                                                        │
├────────────────────────────────────────────────────────────────────┤
│  Total Costs:           ${results['trade_cost'].sum():>15,.2f}                   │
└────────────────────────────────────────────────────────────────────┘
""")

# Compare with BTC-only optimization result
print(f"NOTE: Compare with BTC-only Sharpe (~1.56). If > 1.6, diversification worked.")
print("=" * 70)
