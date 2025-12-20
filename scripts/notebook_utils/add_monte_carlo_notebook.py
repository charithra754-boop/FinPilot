#!/usr/bin/env python3
"""Add Monte Carlo section to competition notebook."""

import json

with open('notebooks/competition_demo.ipynb', 'r') as f:
    notebook = json.load(f)

monte_carlo_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 8.5 Monte Carlo Stress Simulation\n",
            "\n",
            "Statistical proof of robustness through 1,000 simulated market scenarios.\n",
            "\n",
            "**Why Monte Carlo?**\n",
            "- Tests strategy across thousands of possible futures\n",
            "- Provides statistical confidence intervals\n",
            "- Shows survivability probability, not just single backtest"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Run Monte Carlo simulation\n",
            "from monte_carlo import MonteCarloSimulator, plot_monte_carlo_results\n",
            "\n",
            "print('Running 1,000 Monte Carlo simulations...')\n",
            "simulator = MonteCarloSimulator(n_simulations=1000, random_seed=42)\n",
            "mc_strategy, mc_benchmark = simulator.compare_with_benchmark(verbose=False)\n",
            "\n",
            "print('\\n' + '='*60)\n",
            "print('MONTE CARLO RESULTS')\n",
            "print('='*60)\n",
            "print(f'''\n",
            "  Strategy:\n",
            "    Survival Rate (DD<50%): {mc_strategy.survival_rate:.1f}%\n",
            "    Median Return:          {mc_strategy.median_return:+.1f}%\n",
            "    Median Drawdown:        {mc_strategy.median_drawdown:.1f}%\n",
            "  \n",
            "  Buy & Hold:\n",
            "    Survival Rate (DD<50%): {mc_benchmark.survival_rate:.1f}%\n",
            "    Median Return:          {mc_benchmark.median_return:+.1f}%\n",
            "    Median Drawdown:        {mc_benchmark.median_drawdown:.1f}%\n",
            "  \n",
            "  → Strategy survives {mc_strategy.survival_rate/mc_benchmark.survival_rate:.1f}x more scenarios!\n",
            "''')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Visualize Monte Carlo results\n",
            "fig = plot_monte_carlo_results(mc_strategy, mc_benchmark)\n",
            "plt.savefig('../reports/figures/monte_carlo_notebook.png', dpi=150, bbox_inches='tight')\n",
            "plt.show()"
        ]
    }
]

# Find stress testing section and add Monte Carlo after it
cells = notebook['cells']
insert_idx = None

for i, cell in enumerate(cells):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if '8.4 Stress Test Summary' in source or 'Stress Test Summary' in source:
            insert_idx = i + 1
            break

if insert_idx:
    for j, new_cell in enumerate(monte_carlo_cells):
        cells.insert(insert_idx + j, new_cell)
    print(f"✅ Inserted Monte Carlo cells at position {insert_idx}")
else:
    # Append before conclusion
    for i, cell in enumerate(cells):
        if cell['cell_type'] == 'markdown':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if '# 9. Conclusion' in source:
                insert_idx = i
                break
    
    if insert_idx:
        for j, new_cell in enumerate(monte_carlo_cells):
            cells.insert(insert_idx + j, new_cell)
        print(f"✅ Inserted Monte Carlo cells at position {insert_idx}")

with open('notebooks/competition_demo.ipynb', 'w') as f:
    json.dump(notebook, f, indent=4)

print("✅ Notebook updated with Monte Carlo section!")
