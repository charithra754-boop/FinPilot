"""
Visualization Module for FinPilot
Creates equity curves, regime heatmaps, and performance dashboards.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Tuple


class StrategyVisualizer:
    """
    Generates visualizations for trading strategy analysis.
    
    Features:
    - Equity curve with drawdown overlay
    - Regime heatmap (NORMAL/CRASH/RECOVERY)
    - Performance dashboard with trade markers
    - Strategy vs Buy-and-Hold comparison
    """
    
    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """
        Args:
            style: Matplotlib style to use
        """
        try:
            plt.style.use(style)
        except OSError:
            plt.style.use("seaborn-v0_8")
        
        # Color palette
        self.colors = {
            "strategy": "#2E86AB",      # Blue for strategy
            "benchmark": "#A23B72",     # Pink for benchmark
            "drawdown": "#F18F01",      # Orange for drawdown
            "normal": "#2ECC71",        # Green for normal regime
            "crash": "#E74C3C",         # Red for crash regime
            "recovery": "#F39C12",      # Yellow for recovery
            "grid": "#E0E0E0"
        }
        
        # Key market events to annotate
        self.key_events = {
            "2020-03-12": "COVID Crash",
            "2022-05-09": "LUNA Collapse",
            "2022-11-08": "FTX Collapse",
        }
    
    def plot_equity_curve(
        self,
        equity: pd.Series,
        benchmark: Optional[pd.Series] = None,
        metrics: Optional[Dict] = None,
        figsize: Tuple[int, int] = (14, 8)
    ) -> plt.Figure:
        """
        Plot equity curve with optional benchmark and drawdown overlay.
        
        Args:
            equity: Strategy portfolio value series
            benchmark: Optional buy-and-hold benchmark
            metrics: Optional dictionary of metrics to display
            figsize: Figure size
            
        Returns:
            Matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[3, 1], sharex=True)
        
        # Main equity curve
        ax1.plot(equity.index, equity.values, 
                 color=self.colors["strategy"], linewidth=1.5, label="FinPilot Strategy")
        
        if benchmark is not None:
            ax1.plot(benchmark.index, benchmark.values,
                     color=self.colors["benchmark"], linewidth=1.2, 
                     linestyle="--", label="Buy & Hold", alpha=0.8)
        
        ax1.set_yscale("log")
        ax1.set_ylabel("Portfolio Value ($)", fontsize=12)
        ax1.set_title("FinPilot Strategy Performance", fontsize=14, fontweight="bold")
        ax1.legend(loc="upper left", fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Add metrics annotation box
        if metrics:
            textstr = "\n".join([
                f"Total Return: {metrics.get('total_return', 0):,.0f}%",
                f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}",
                f"Max Drawdown: {metrics.get('max_drawdown', 0)*100:.1f}%"
            ])
            props = dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9)
            ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
                     verticalalignment="top", bbox=props, family="monospace")
        
        # Drawdown chart
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100
        
        ax2.fill_between(drawdown.index, drawdown.values, 0,
                         color=self.colors["drawdown"], alpha=0.6)
        ax2.set_ylabel("Drawdown (%)", fontsize=12)
        ax2.set_xlabel("Date", fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(bottom=min(drawdown.min() * 1.1, -5))
        
        # Format x-axis dates
        ax2.xaxis.set_major_locator(mdates.YearLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        
        plt.tight_layout()
        return fig
    
    def plot_regime_heatmap(
        self,
        regimes: pd.Series,
        prices: pd.Series,
        figsize: Tuple[int, int] = (14, 6)
    ) -> plt.Figure:
        """
        Plot regime timeline as colored heatmap with price overlay.
        
        Args:
            regimes: Series of regime labels ('normal', 'crash', 'recovery')
            prices: Series of asset prices
            figsize: Figure size
            
        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create regime colors array
        regime_colors = {
            "normal": 0,
            "crash": 1,
            "recovery": 2
        }
        regime_values = regimes.map(regime_colors).fillna(0).values
        
        # Plot price line
        ax.plot(prices.index, prices.values, color="black", linewidth=1, label="BTC Price")
        ax.set_yscale("log")
        
        # Add regime background shading
        cmap = plt.cm.colors.ListedColormap([
            self.colors["normal"],
            self.colors["crash"],
            self.colors["recovery"]
        ])
        
        # Create spans for each regime period
        current_regime = None
        start_idx = None
        
        for i, (idx, regime) in enumerate(regimes.items()):
            if regime != current_regime:
                if current_regime is not None and start_idx is not None:
                    color = self.colors.get(current_regime, self.colors["normal"])
                    ax.axvspan(start_idx, idx, alpha=0.3, color=color, linewidth=0)
                current_regime = regime
                start_idx = idx
        
        # Add final span
        if current_regime is not None and start_idx is not None:
            color = self.colors.get(current_regime, self.colors["normal"])
            ax.axvspan(start_idx, regimes.index[-1], alpha=0.3, color=color, linewidth=0)
        
        # Add event annotations
        for date_str, label in self.key_events.items():
            try:
                event_date = pd.Timestamp(date_str)
                if event_date in prices.index or (prices.index[0] <= event_date <= prices.index[-1]):
                    # Find nearest date in index
                    nearest_idx = prices.index.get_indexer([event_date], method="nearest")[0]
                    nearest_date = prices.index[nearest_idx]
                    price_at_event = prices.iloc[nearest_idx]
                    
                    ax.annotate(label, xy=(nearest_date, price_at_event),
                                xytext=(0, 30), textcoords="offset points",
                                fontsize=9, ha="center",
                                arrowprops=dict(arrowstyle="->", color="black", alpha=0.7),
                                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
            except Exception:
                pass
        
        # Legend
        patches = [
            mpatches.Patch(color=self.colors["normal"], alpha=0.3, label="Normal"),
            mpatches.Patch(color=self.colors["crash"], alpha=0.3, label="Crash"),
            mpatches.Patch(color=self.colors["recovery"], alpha=0.3, label="Recovery"),
        ]
        ax.legend(handles=patches, loc="upper left", fontsize=10)
        
        ax.set_ylabel("BTC Price ($)", fontsize=12)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_title("Market Regime Detection", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)
        
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        
        plt.tight_layout()
        return fig
    
    def plot_performance_dashboard(
        self,
        equity: pd.Series,
        benchmark: pd.Series,
        regimes: pd.Series,
        prices: pd.Series,
        metrics: Dict,
        figsize: Tuple[int, int] = (16, 12)
    ) -> plt.Figure:
        """
        Create a comprehensive performance dashboard.
        
        Args:
            equity: Strategy portfolio value series
            benchmark: Buy-and-hold benchmark
            regimes: Series of regime labels
            prices: Series of asset prices
            metrics: Dictionary of all metrics
            figsize: Figure size
            
        Returns:
            Matplotlib Figure object
        """
        fig = plt.figure(figsize=figsize)
        
        # Create grid layout
        gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1.5], hspace=0.3, wspace=0.25)
        
        # 1. Equity curve (top, spans both columns)
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(equity.index, equity.values, color=self.colors["strategy"], 
                 linewidth=1.5, label="FinPilot Strategy")
        ax1.plot(benchmark.index, benchmark.values, color=self.colors["benchmark"],
                 linewidth=1.2, linestyle="--", label="Buy & Hold", alpha=0.8)
        ax1.set_yscale("log")
        ax1.set_ylabel("Portfolio Value ($)", fontsize=11)
        ax1.set_title("FinPilot Performance Dashboard", fontsize=16, fontweight="bold")
        ax1.legend(loc="upper left")
        ax1.grid(True, alpha=0.3)
        
        # 2. Drawdown chart (middle left)
        ax2 = fig.add_subplot(gs[1, 0])
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100
        ax2.fill_between(drawdown.index, drawdown.values, 0,
                         color=self.colors["drawdown"], alpha=0.6)
        ax2.set_ylabel("Drawdown (%)", fontsize=10)
        ax2.set_title("Drawdown Over Time", fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 3. Monthly returns heatmap (middle right)
        ax3 = fig.add_subplot(gs[1, 1])
        returns = equity.pct_change().dropna()
        monthly_returns = returns.resample("ME").apply(lambda x: (1 + x).prod() - 1) * 100
        
        # Create pivot table for heatmap
        monthly_df = pd.DataFrame({
            "Year": monthly_returns.index.year,
            "Month": monthly_returns.index.month,
            "Return": monthly_returns.values
        })
        
        if len(monthly_df) > 0:
            pivot = monthly_df.pivot_table(index="Year", columns="Month", values="Return", aggfunc="first")
            pivot.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][:len(pivot.columns)]
            
            sns.heatmap(pivot, cmap="RdYlGn", center=0, annot=False, 
                        ax=ax3, cbar_kws={"label": "Return %"}, linewidths=0.5)
            ax3.set_title("Monthly Returns", fontsize=12)
        
        # 4. Regime distribution (bottom left)
        ax4 = fig.add_subplot(gs[2, 0])
        regime_counts = regimes.value_counts()
        colors_pie = [self.colors.get(r, "gray") for r in regime_counts.index]
        ax4.pie(regime_counts.values, labels=regime_counts.index.str.title(), 
                autopct="%1.1f%%", colors=colors_pie, startangle=90)
        ax4.set_title("Regime Distribution", fontsize=12)
        
        # 5. Metrics summary (bottom right)
        ax5 = fig.add_subplot(gs[2, 1])
        ax5.axis("off")
        
        metrics_text = [
            ["Metric", "Strategy", "Benchmark"],
            ["─" * 12, "─" * 12, "─" * 12],
            ["Total Return", f"{metrics.get('total_return', 0):,.0f}%", 
             f"{metrics.get('benchmark_return', 0):,.0f}%"],
            ["Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}", 
             f"{metrics.get('benchmark_sharpe', 0):.2f}"],
            ["Max Drawdown", f"{metrics.get('max_drawdown', 0)*100:.1f}%",
             f"{metrics.get('benchmark_drawdown', 0)*100:.1f}%"],
            ["CAGR", f"{metrics.get('cagr', 0):.1f}%", "N/A"],
            ["Total Trades", f"{metrics.get('total_trades', 0)}", "1"],
        ]
        
        table = ax5.table(
            cellText=metrics_text,
            cellLoc="center",
            loc="center",
            colWidths=[0.35, 0.3, 0.3]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.8)
        
        # Style header row
        for i in range(3):
            table[(0, i)].set_text_props(fontweight="bold")
            table[(0, i)].set_facecolor("#E8E8E8")
        
        ax5.set_title("Performance Metrics", fontsize=12, pad=20)
        
        return fig
    
    def plot_stress_performance(
        self,
        normal_equity: pd.Series,
        stress_equity: pd.Series,
        stress_scenario_name: str,
        stress_start: pd.Timestamp,
        stress_end: pd.Timestamp,
        figsize: Tuple[int, int] = (14, 8)
    ) -> plt.Figure:
        """
        Plot strategy behavior during stress scenarios.
        
        Shows normal vs stress equity curves and highlights stress period.
        
        Args:
            normal_equity: Equity curve under normal conditions
            stress_equity: Equity curve under stress scenario
            stress_scenario_name: Name of the stress scenario
            stress_start: Start of stress period
            stress_end: End of stress period
            figsize: Figure size
            
        Returns:
            Matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[2, 1])
        
        # Equity comparison
        ax1.plot(normal_equity.index, normal_equity.values,
                 color=self.colors["strategy"], linewidth=1.5, label="Normal Conditions")
        ax1.plot(stress_equity.index, stress_equity.values,
                 color=self.colors["crash"], linewidth=1.5, alpha=0.8, 
                 label=f"Stress: {stress_scenario_name}")
        
        # Highlight stress period
        ax1.axvspan(stress_start, stress_end, alpha=0.2, color=self.colors["crash"],
                    label="Stress Period")
        
        ax1.set_yscale("log")
        ax1.set_ylabel("Portfolio Value ($)", fontsize=12)
        ax1.set_title(f"Strategy Robustness: {stress_scenario_name}", fontsize=14, fontweight="bold")
        ax1.legend(loc="upper left")
        ax1.grid(True, alpha=0.3)
        
        # Relative performance (stress / normal)
        aligned_idx = normal_equity.index.intersection(stress_equity.index)
        relative = (stress_equity.loc[aligned_idx] / normal_equity.loc[aligned_idx] - 1) * 100
        
        ax2.fill_between(relative.index, relative.values, 0,
                         where=(relative >= 0), color=self.colors["normal"], alpha=0.6, label="Outperform")
        ax2.fill_between(relative.index, relative.values, 0,
                         where=(relative < 0), color=self.colors["crash"], alpha=0.6, label="Underperform")
        ax2.axhline(y=0, color="black", linestyle="--", linewidth=0.8)
        ax2.set_ylabel("Relative Performance (%)", fontsize=12)
        ax2.set_xlabel("Date", fontsize=12)
        ax2.legend(loc="upper right")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_var_distribution(
        self,
        returns: pd.Series,
        var_95: float,
        var_99: float,
        cvar_95: float,
        figsize: Tuple[int, int] = (12, 6)
    ) -> plt.Figure:
        """
        Plot return distribution with VaR and CVaR markers.
        
        Args:
            returns: Series of daily returns
            var_95: Value at Risk at 95% confidence
            var_99: Value at Risk at 99% confidence
            cvar_95: Conditional VaR at 95% confidence
            figsize: Figure size
            
        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Histogram of returns
        returns_pct = returns * 100
        n, bins, patches = ax.hist(returns_pct, bins=50, density=True, 
                                    alpha=0.7, color=self.colors["strategy"],
                                    edgecolor="white", linewidth=0.5)
        
        # Color the tail returns red
        for i, patch in enumerate(patches):
            if bins[i] < -var_95 * 100:
                patch.set_facecolor(self.colors["crash"])
        
        # VaR lines
        ax.axvline(x=-var_95 * 100, color=self.colors["recovery"], linestyle="--", 
                   linewidth=2, label=f"VaR 95%: {var_95*100:.2f}%")
        ax.axvline(x=-var_99 * 100, color=self.colors["crash"], linestyle="--", 
                   linewidth=2, label=f"VaR 99%: {var_99*100:.2f}%")
        ax.axvline(x=-cvar_95 * 100, color=self.colors["crash"], linestyle=":", 
                   linewidth=2, label=f"CVaR 95%: {cvar_95*100:.2f}%")
        
        ax.set_xlabel("Daily Return (%)", fontsize=12)
        ax.set_ylabel("Density", fontsize=12)
        ax.set_title("Return Distribution with Risk Metrics", fontsize=14, fontweight="bold")
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)
        
        # Add annotation box
        textstr = f"VaR: Max expected daily loss\nCVaR: Expected loss beyond VaR"
        props = dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
                verticalalignment="top", bbox=props)
        
        plt.tight_layout()
        return fig
    
    def plot_drawdown_recovery(
        self,
        equity_curve: pd.Series,
        figsize: Tuple[int, int] = (14, 8)
    ) -> plt.Figure:
        """
        Plot drawdown events and recovery timeline.
        
        Highlights major drawdown events and shows time to recovery.
        
        Args:
            equity_curve: Series of portfolio values
            figsize: Figure size
            
        Returns:
            Matplotlib Figure object
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize, 
                                             height_ratios=[2, 1, 1], sharex=True)
        
        # 1. Equity curve
        ax1.plot(equity_curve.index, equity_curve.values,
                 color=self.colors["strategy"], linewidth=1.5)
        ax1.set_yscale("log")
        ax1.set_ylabel("Portfolio Value ($)", fontsize=11)
        ax1.set_title("Drawdown Recovery Analysis", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3)
        
        # 2. Drawdown
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max * 100
        
        ax2.fill_between(drawdown.index, drawdown.values, 0,
                         color=self.colors["drawdown"], alpha=0.6)
        ax2.set_ylabel("Drawdown (%)", fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        # Mark significant drawdowns (> 10%)
        significant_dd = drawdown[drawdown < -10]
        if not significant_dd.empty:
            for idx in significant_dd.index[::20]:  # Sample to avoid overcrowding
                ax2.annotate("", xy=(idx, drawdown.loc[idx]),
                            xytext=(idx, 0), fontsize=8,
                            arrowprops=dict(arrowstyle="->", color="red", alpha=0.5))
        
        # 3. Recovery indicator (1 = at peak, 0 = in drawdown)
        at_peak = (drawdown >= 0).astype(int)
        ax3.fill_between(at_peak.index, at_peak.values, 0,
                         color=self.colors["normal"], alpha=0.6, label="At Peak")
        ax3.fill_between(at_peak.index, at_peak.values, 1,
                         color=self.colors["crash"], alpha=0.4, label="In Drawdown")
        ax3.set_ylabel("Recovery Status", fontsize=11)
        ax3.set_xlabel("Date", fontsize=11)
        ax3.set_yticks([0, 1])
        ax3.set_yticklabels(["In DD", "Recovered"])
        ax3.legend(loc="upper right")
        
        plt.tight_layout()
        return fig
    
    def plot_volatility_regime_performance(
        self,
        equity: pd.Series,
        volatility: pd.Series,
        vol_threshold: float = 0.03,
        figsize: Tuple[int, int] = (14, 8)
    ) -> plt.Figure:
        """
        Compare strategy performance during high vs low volatility periods.
        
        Args:
            equity: Portfolio value series
            volatility: Rolling volatility series
            vol_threshold: Threshold to define high volatility
            figsize: Figure size
            
        Returns:
            Matplotlib Figure object
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize, 
                                             height_ratios=[2, 1, 1], sharex=True)
        
        # Align series
        common_idx = equity.index.intersection(volatility.index)
        equity = equity.loc[common_idx]
        volatility = volatility.loc[common_idx]
        
        # 1. Equity with volatility regime overlay
        ax1.plot(equity.index, equity.values, color=self.colors["strategy"], linewidth=1.5)
        
        # Shade high volatility periods
        high_vol = volatility > vol_threshold
        vol_changes = high_vol.diff().fillna(False)
        
        in_high_vol = False
        start = None
        for idx, changed in vol_changes.items():
            if changed:
                if high_vol.loc[idx]:
                    in_high_vol = True
                    start = idx
                else:
                    if in_high_vol and start is not None:
                        ax1.axvspan(start, idx, alpha=0.2, color=self.colors["crash"])
                    in_high_vol = False
        
        ax1.set_yscale("log")
        ax1.set_ylabel("Portfolio Value ($)", fontsize=11)
        ax1.set_title("Performance Across Volatility Regimes", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3)
        
        # 2. Volatility with threshold
        ax2.plot(volatility.index, volatility.values * 100, 
                 color=self.colors["benchmark"], linewidth=1)
        ax2.axhline(y=vol_threshold * 100, color=self.colors["crash"], 
                    linestyle="--", linewidth=1.5, label=f"Threshold: {vol_threshold*100:.1f}%")
        ax2.set_ylabel("Volatility (%)", fontsize=11)
        ax2.legend(loc="upper right")
        ax2.grid(True, alpha=0.3)
        
        # 3. Returns by regime
        returns = equity.pct_change() * 100
        high_vol_returns = returns[high_vol].dropna()
        low_vol_returns = returns[~high_vol].dropna()
        
        regime_stats = pd.DataFrame({
            "Regime": ["Low Vol", "High Vol"],
            "Mean Return": [low_vol_returns.mean(), high_vol_returns.mean()],
            "Volatility": [low_vol_returns.std(), high_vol_returns.std()],
            "Days": [len(low_vol_returns), len(high_vol_returns)]
        })
        
        ax3.axis("off")
        table = ax3.table(
            cellText=[[f"{row['Regime']}", f"{row['Mean Return']:.3f}%", 
                       f"{row['Volatility']:.2f}%", f"{row['Days']}"] 
                      for _, row in regime_stats.iterrows()],
            colLabels=["Regime", "Mean Daily Return", "Daily Vol", "Days"],
            cellLoc="center",
            loc="center",
            colWidths=[0.2, 0.25, 0.25, 0.15]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        for i in range(4):
            table[(0, i)].set_text_props(fontweight="bold")
            table[(0, i)].set_facecolor("#E8E8E8")
        
        plt.tight_layout()
        return fig
    
    def plot_crash_intensity_heatmap(
        self,
        prices: pd.Series,
        crash_intensity: pd.Series,
        position_size: pd.Series,
        figsize: Tuple[int, int] = (14, 10)
    ) -> plt.Figure:
        """
        Plot Crash Intensity Score heatmap with price and position overlay.
        
        Shows the novel CIS metric visualization for competition.
        
        Args:
            prices: Price series
            crash_intensity: CIS series (0-100)
            position_size: Position size series (0-1)
            figsize: Figure size
            
        Returns:
            Matplotlib Figure object
        """
        fig, axes = plt.subplots(4, 1, figsize=figsize, 
                                  height_ratios=[2, 1, 1, 0.5], sharex=True)
        
        # 1. Price with intensity background shading
        ax1 = axes[0]
        ax1.plot(prices.index, prices.values, color=self.colors["strategy"], 
                 linewidth=1.5, zorder=2)
        
        # Create intensity color gradient in background
        for i in range(len(crash_intensity) - 1):
            intensity = crash_intensity.iloc[i]
            # Color from green (low) to red (high intensity)
            if intensity < 30:
                color = self.colors["normal"]
            elif intensity < 60:
                color = self.colors["recovery"]
            else:
                color = self.colors["crash"]
            ax1.axvspan(crash_intensity.index[i], crash_intensity.index[i+1],
                       alpha=0.3, color=color, zorder=1)
        
        ax1.set_yscale("log")
        ax1.set_ylabel("Price ($)", fontsize=11)
        ax1.set_title("Crash Intensity Score (CIS) - Novel Risk Metric", 
                     fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3, zorder=0)
        
        # Legend for intensity zones
        patches = [
            mpatches.Patch(color=self.colors["normal"], alpha=0.5, label="Low Risk (CIS < 30)"),
            mpatches.Patch(color=self.colors["recovery"], alpha=0.5, label="Medium Risk (30-60)"),
            mpatches.Patch(color=self.colors["crash"], alpha=0.5, label="High Risk (CIS > 60)")
        ]
        ax1.legend(handles=patches, loc="upper left")
        
        # 2. Crash Intensity Score line
        ax2 = axes[1]
        ax2.fill_between(crash_intensity.index, crash_intensity.values, 0,
                        alpha=0.7, color="orange")
        ax2.axhline(y=30, color="green", linestyle="--", linewidth=1, label="Low threshold")
        ax2.axhline(y=60, color="red", linestyle="--", linewidth=1, label="High threshold")
        ax2.set_ylabel("CIS (0-100)", fontsize=11)
        ax2.set_ylim(0, 100)
        ax2.legend(loc="upper right")
        ax2.grid(True, alpha=0.3)
        
        # 3. Proportional Position Size
        ax3 = axes[2]
        ax3.fill_between(position_size.index, position_size.values * 100, 0,
                        alpha=0.7, color=self.colors["strategy"])
        ax3.set_ylabel("Position (%)", fontsize=11)
        ax3.set_ylim(0, 100)
        ax3.grid(True, alpha=0.3)
        
        # 4. Position changes (entry/exit markers)
        ax4 = axes[3]
        position_changes = position_size.diff().fillna(0)
        entries = position_changes > 0.1
        exits = position_changes < -0.1
        
        ax4.scatter(position_size.index[entries], [1] * entries.sum(), 
                   marker="^", color="green", s=50, label="Scale In")
        ax4.scatter(position_size.index[exits], [0] * exits.sum(), 
                   marker="v", color="red", s=50, label="Scale Out")
        ax4.set_yticks([0, 1])
        ax4.set_yticklabels(["Exit", "Entry"])
        ax4.set_xlabel("Date", fontsize=11)
        ax4.legend(loc="center right")
        ax4.set_ylim(-0.5, 1.5)
        
        plt.tight_layout()
        return fig
    
    def plot_cis_components(
        self,
        features: pd.DataFrame,
        crash_intensity: pd.Series,
        figsize: Tuple[int, int] = (14, 10)
    ) -> plt.Figure:
        """
        Plot individual components of the Crash Intensity Score.
        
        Shows breakdown of what's driving the CIS value.
        
        Args:
            features: DataFrame with feature values
            crash_intensity: CIS series
            figsize: Figure size
            
        Returns:
            Matplotlib Figure object
        """
        fig, axes = plt.subplots(5, 1, figsize=figsize, sharex=True)
        
        # 1. DUVOL component
        if "duvol" in features.columns:
            axes[0].plot(features.index, features["duvol"], color="red", linewidth=1)
            axes[0].axhline(y=0.5, color="black", linestyle="--", linewidth=0.8)
            axes[0].set_ylabel("DUVOL", fontsize=10)
            axes[0].set_title("CIS Component Breakdown", fontsize=14, fontweight="bold")
            axes[0].grid(True, alpha=0.3)
        
        # 2. Volatility spike
        if "volatility_10d" in features.columns and "volatility_30d" in features.columns:
            vol_ratio = features["volatility_10d"] / features["volatility_30d"]
            axes[1].plot(features.index, vol_ratio, color="orange", linewidth=1)
            axes[1].axhline(y=1.0, color="black", linestyle="--", linewidth=0.8)
            axes[1].set_ylabel("Vol Ratio", fontsize=10)
            axes[1].grid(True, alpha=0.3)
        
        # 3. NASDAQ Canary
        if "nasdaq_returns" in features.columns:
            axes[2].bar(features.index, features["nasdaq_returns"] * 100, 
                       color="blue", alpha=0.7, width=1)
            axes[2].axhline(y=-3, color="red", linestyle="--", linewidth=0.8)
            axes[2].set_ylabel("NASDAQ %", fontsize=10)
            axes[2].grid(True, alpha=0.3)
        
        # 4. Momentum
        if "returns" in features.columns:
            rolling_return = features["returns"].rolling(5).sum() * 100
            axes[3].plot(features.index, rolling_return, color="purple", linewidth=1)
            axes[3].axhline(y=0, color="black", linestyle="-", linewidth=0.5)
            axes[3].set_ylabel("5D Ret %", fontsize=10)
            axes[3].grid(True, alpha=0.3)
        
        # 5. Combined CIS
        axes[4].fill_between(crash_intensity.index, crash_intensity.values, 0,
                            alpha=0.7, color="orange")
        axes[4].set_ylabel("CIS", fontsize=10)
        axes[4].set_xlabel("Date", fontsize=11)
        axes[4].set_ylim(0, 100)
        axes[4].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def save_figure(
        self,
        fig: plt.Figure,
        filename: str,
        output_dir: str = "reports/figures",
        dpi: int = 150
    ) -> Path:
        """
        Save figure to file.
        
        Args:
            fig: Matplotlib figure
            filename: Output filename (without extension)
            output_dir: Directory to save to
            dpi: Resolution
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filepath = output_path / f"{filename}.png"
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        
        return filepath


if __name__ == "__main__":
    # Demo with sample data
    import numpy as np
    
    np.random.seed(42)
    dates = pd.date_range("2018-01-01", "2024-01-01", freq="D")
    
    # Simulated equity curve
    returns = np.random.normal(0.001, 0.02, len(dates))
    equity = pd.Series(100000 * np.exp(np.cumsum(returns)), index=dates)
    benchmark = pd.Series(100000 * np.exp(np.cumsum(returns * 0.8)), index=dates)
    
    # Simulated regimes
    regimes = pd.Series(
        np.random.choice(["normal", "crash", "recovery"], len(dates), p=[0.7, 0.15, 0.15]),
        index=dates
    )
    
    # Simulated prices
    prices = pd.Series(10000 * np.exp(np.cumsum(returns * 0.5)), index=dates)
    
    # Metrics
    metrics = {
        "total_return": 67633.77,
        "sharpe_ratio": 1.56,
        "max_drawdown": 0.4474,
        "cagr": 85.5,
        "total_trades": 265,
        "benchmark_return": 1200,
        "benchmark_sharpe": 0.9,
        "benchmark_drawdown": 0.82
    }
    
    # Generate visualizations
    viz = StrategyVisualizer()
    
    fig1 = viz.plot_equity_curve(equity, benchmark, metrics)
    viz.save_figure(fig1, "equity_curve")
    
    fig2 = viz.plot_regime_heatmap(regimes, prices)
    viz.save_figure(fig2, "regime_heatmap")
    
    fig3 = viz.plot_performance_dashboard(equity, benchmark, regimes, prices, metrics)
    viz.save_figure(fig3, "performance_dashboard")
    
    print("✅ Demo visualizations saved to reports/figures/")
