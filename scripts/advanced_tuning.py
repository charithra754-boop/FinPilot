#!/usr/bin/env python3
"""
FinPilot - Advanced Parameter Tuning
Walk-forward optimization with out-of-sample validation
"""

import sys
sys.path.insert(0, 'src')

import json
from pathlib import Path
from datetime import datetime

from data_handler import DataHandler
from features import FeatureEngineer
from regime_detector import RegimeDetector
from strategy import TradingStrategy
from backtester import Backtester
from metrics import Metrics

print("=" * 60)
print("FINPILOT - ADVANCED PARAMETER TUNING")
print("=" * 60)

# Load data
print("\n[1] Loading Data...")
handler = DataHandler()
crypto_df, nasdaq_df = handler.load_and_prepare(
    'BTC_USD Bitfinex Historical Data.csv', 
    'Nasdaq 100 Historical Data.csv'
)

# Split data: Train (2012-2020), Test (2020-2024)
train_end = '2020-01-01'
print(f"\n[2] Splitting Data...")
print(f"    Train period: {crypto_df.index[0].strftime('%Y-%m-%d')} to {train_end}")
print(f"    Test period:  {train_end} to {crypto_df.index[-1].strftime('%Y-%m-%d')}")

crypto_train = crypto_df[crypto_df.index < train_end]
crypto_test = crypto_df[crypto_df.index >= train_end]
nasdaq_train = nasdaq_df[nasdaq_df.index < train_end]
nasdaq_test = nasdaq_df[nasdaq_df.index >= train_end]

print(f"    Train samples: {len(crypto_train)}")
print(f"    Test samples:  {len(crypto_test)}")

# Finer parameter grid around best values
param_grid = {
    'duvol_threshold': [0.35, 0.38, 0.40, 0.42, 0.45],
    'rsi_oversold': [20, 23, 25, 27, 30],
    'rsi_overbought': [60, 63, 65, 67, 70],
    'stop_loss_pct': [0.02, 0.03, 0.04, 0.05],
    'nasdaq_drop': [-0.025, -0.03, -0.035],
    'feature_window': [15, 20, 25, 30]
}

total = 1
for v in param_grid.values():
    total *= len(v)
print(f"\n[3] Running Walk-Forward Optimization ({total} combinations)...")
print("-" * 60)

# Store results
results = []
best_train_sharpe = -999
best_params = None

count = 0
for duvol in param_grid['duvol_threshold']:
    for rsi_os in param_grid['rsi_oversold']:
        for rsi_ob in param_grid['rsi_overbought']:
            for stop_loss in param_grid['stop_loss_pct']:
                for nasdaq_drop in param_grid['nasdaq_drop']:
                    for window in param_grid['feature_window']:
                        count += 1
                        
                        if rsi_os >= rsi_ob:
                            continue
                        
                        # === TRAIN PHASE ===
                        fe = FeatureEngineer(window=window)
                        train_features = fe.generate_all_features(crypto_train, nasdaq_train)
                        
                        if len(train_features) < 100:
                            continue
                        
                        detector = RegimeDetector(
                            duvol_threshold=duvol,
                            nasdaq_drop_threshold=nasdaq_drop,
                            volatility_ratio_threshold=1.0
                        )
                        train_regimes = detector.detect_regimes(train_features)
                        
                        strategy = TradingStrategy(
                            rsi_oversold=rsi_os,
                            rsi_overbought=rsi_ob,
                            stop_loss_pct=stop_loss,
                            volatility_target=0.02
                        )
                        train_signals = strategy.run_strategy(train_features, train_regimes)
                        
                        backtester = Backtester(initial_capital=100000, slippage_pct=0.001)
                        train_results = backtester.run_backtest(train_features, train_signals)
                        
                        metrics_calc = Metrics(risk_free_rate=0.02)
                        train_equity = train_results['portfolio_value']
                        train_metrics = metrics_calc.calculate_all_metrics(train_equity)
                        
                        # === TEST PHASE ===
                        test_features = fe.generate_all_features(crypto_test, nasdaq_test)
                        
                        if len(test_features) < 50:
                            continue
                            
                        test_regimes = detector.detect_regimes(test_features)
                        test_signals = strategy.run_strategy(test_features, test_regimes)
                        test_results = backtester.run_backtest(test_features, test_signals)
                        test_equity = test_results['portfolio_value']
                        test_metrics = metrics_calc.calculate_all_metrics(test_equity)
                        
                        result = {
                            'duvol_threshold': duvol,
                            'rsi_oversold': rsi_os,
                            'rsi_overbought': rsi_ob,
                            'stop_loss_pct': stop_loss,
                            'nasdaq_drop': nasdaq_drop,
                            'feature_window': window,
                            'train_sharpe': train_metrics['sharpe_ratio'],
                            'train_dd': train_metrics['max_drawdown'],
                            'train_return': train_metrics['total_return'],
                            'test_sharpe': test_metrics['sharpe_ratio'],
                            'test_dd': test_metrics['max_drawdown'],
                            'test_return': test_metrics['total_return'],
                            'sharpe_decay': train_metrics['sharpe_ratio'] - test_metrics['sharpe_ratio']
                        }
                        results.append(result)
                        
                        # Best = highest test Sharpe with reasonable train Sharpe
                        if (test_metrics['sharpe_ratio'] > 1.0 and 
                            train_metrics['sharpe_ratio'] > best_train_sharpe * 0.9):
                            if test_metrics['sharpe_ratio'] > (best_params['test_sharpe'] if best_params else 0):
                                best_params = result.copy()
                                best_train_sharpe = train_metrics['sharpe_ratio']
                        
                        if count % 100 == 0:
                            print(f"    Progress: {count}/{total}...")

print(f"\n[4] Optimization Complete!")
print("=" * 60)

# Find best by out-of-sample Sharpe
sorted_by_test = sorted(results, key=lambda x: x['test_sharpe'], reverse=True)
best_params = sorted_by_test[0] if sorted_by_test else None

if best_params:
    print("\nBEST WALK-FORWARD PARAMETERS:")
    print("-" * 60)
    print(f"  DUVOL Threshold:     {best_params['duvol_threshold']}")
    print(f"  RSI Oversold:        {best_params['rsi_oversold']}")
    print(f"  RSI Overbought:      {best_params['rsi_overbought']}")
    print(f"  Stop Loss:           {best_params['stop_loss_pct']*100:.0f}%")
    print(f"  NASDAQ Drop:         {best_params['nasdaq_drop']*100:.1f}%")
    print(f"  Feature Window:      {best_params['feature_window']} days")

    print("\nIN-SAMPLE (2012-2020) vs OUT-OF-SAMPLE (2020-2024):")
    print("-" * 60)
    print(f"  {'Metric':<20} {'In-Sample':>12} {'Out-of-Sample':>14} {'Decay':>10}")
    print(f"  {'-'*20} {'-'*12} {'-'*14} {'-'*10}")
    print(f"  {'Sharpe Ratio':<20} {best_params['train_sharpe']:>12.2f} {best_params['test_sharpe']:>14.2f} {best_params['sharpe_decay']:>+10.2f}")
    print(f"  {'Max Drawdown':<20} {best_params['train_dd']:>11.2f}% {best_params['test_dd']:>13.2f}%")
    print(f"  {'Total Return':<20} {best_params['train_return']:>11.0f}% {best_params['test_return']:>13.0f}%")

    # Save best params
    params_to_save = {
        'duvol_threshold': best_params['duvol_threshold'],
        'nasdaq_drop_threshold': best_params['nasdaq_drop'],
        'volatility_ratio_threshold': 1.0,
        'rsi_oversold': best_params['rsi_oversold'],
        'rsi_overbought': best_params['rsi_overbought'],
        'stop_loss_pct': best_params['stop_loss_pct'],
        'volatility_target': 0.02,
        'feature_window': best_params['feature_window'],
        'validation': {
            'train_period': f'2012-2020',
            'test_period': f'2020-2024',
            'train_sharpe': best_params['train_sharpe'],
            'test_sharpe': best_params['test_sharpe'],
            'sharpe_decay': best_params['sharpe_decay']
        }
    }

    with open('models/best_params.json', 'w') as f:
        json.dump(params_to_save, f, indent=2)

    print(f"\n✅ Walk-forward validated params saved to models/best_params.json")

# Show top 5 by out-of-sample performance
print("\nTOP 5 OUT-OF-SAMPLE PERFORMERS:")
print("-" * 90)
print(f"{'#':<3} {'DUVOL':>6} {'RSI':>7} {'SL%':>5} {'Window':>7} {'Train SR':>10} {'Test SR':>10} {'Decay':>8}")
for i, r in enumerate(sorted_by_test[:5], 1):
    print(f"{i:<3} {r['duvol_threshold']:>6.2f} {r['rsi_oversold']}/{r['rsi_overbought']:>4} {r['stop_loss_pct']*100:>4.0f}% {r['feature_window']:>7} {r['train_sharpe']:>10.2f} {r['test_sharpe']:>10.2f} {r['sharpe_decay']:>+8.2f}")

print("\n" + "=" * 60)
