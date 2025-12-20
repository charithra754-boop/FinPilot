#!/usr/bin/env python3
"""
Add Crash Intensity Scoring section to competition notebook.
"""

import json

# Read notebook
with open('notebooks/competition_demo.ipynb', 'r') as f:
    notebook = json.load(f)

# New CIS cells
cis_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "# 7. Novel Feature: Crash Intensity Scoring (CIS)\n",
            "\n",
            "## Our Innovation\n",
            "\n",
            "**Problem with existing approaches**: Binary crash detection (crash/no crash) leads to:\n",
            "- Whipsaw trades from false signals\n",
            "- Over-reaction to minor corrections\n",
            "- Delayed response to genuine crashes\n",
            "\n",
            "**Our solution**: Continuous **Crash Intensity Score (CIS)** with **proportional response**.\n",
            "\n",
            "## CIS Formula\n",
            "\n",
            "$$CIS = w_1 \\cdot DUVOL_{norm} + w_2 \\cdot NCSKEW_{norm} + w_3 \\cdot Vol_{spike} + w_4 \\cdot Canary + w_5 \\cdot Momentum$$\n",
            "\n",
            "Each component normalized to 0-100, with learned weights.\n",
            "\n",
            "## Proportional Response\n",
            "\n",
            "| CIS Range | Position Size | Action |\n",
            "|-----------|---------------|--------|\n",
            "| 0-20 | 100% | Full exposure |\n",
            "| 20-50 | 50-100% | Gradual reduction |\n",
            "| 50-70 | 20-50% | Defensive |\n",
            "| 70-100 | 0-20% | Exit to cash |\n",
            "\n",
            "## Adaptive Recovery Engine\n",
            "\n",
            "Instead of arbitrary thresholds, we use:\n",
            "- Price momentum (above MA)\n",
            "- Volatility normalization\n",
            "- CIS declining trend\n",
            "- Gradual scaling back in (4 steps)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Import our novel Crash Intensity module\n",
            "from crash_intensity import CrashIntensityScorer, IntensityAwareStrategy\n",
            "\n",
            "# Initialize scorer\n",
            "scorer = CrashIntensityScorer()\n",
            "intensity_strategy = IntensityAwareStrategy()\n",
            "\n",
            "print('✅ Crash Intensity Scoring module loaded')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Calculate Crash Intensity Score for entire dataset\n",
            "crash_intensity = scorer.calculate_intensity_series(features)\n",
            "\n",
            "print('='*60)\n",
            "print('CRASH INTENSITY SCORE STATISTICS')\n",
            "print('='*60)\n",
            "print(f'\\n  Average CIS:     {crash_intensity.mean():.1f}')\n",
            "print(f'  Max CIS:         {crash_intensity.max():.1f}')\n",
            "print(f'  Min CIS:         {crash_intensity.min():.1f}')\n",
            "print(f'  Days CIS > 70:   {(crash_intensity > 70).sum()} ({(crash_intensity > 70).mean()*100:.1f}%)')\n",
            "print(f'  Days CIS < 20:   {(crash_intensity < 20).sum()} ({(crash_intensity < 20).mean()*100:.1f}%)')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Run intensity-aware strategy\n",
            "intensity_results = intensity_strategy.run_intensity_strategy(features)\n",
            "\n",
            "print('='*60)\n",
            "print('INTENSITY-AWARE STRATEGY RESULTS')\n",
            "print('='*60)\n",
            "print(f'\\n  Average Position: {intensity_results[\"position_size\"].mean()*100:.1f}%')\n",
            "print(f'  Days at 100%:     {(intensity_results[\"position_size\"] >= 0.99).sum()}')\n",
            "print(f'  Days at 0%:       {(intensity_results[\"position_size\"] <= 0.01).sum()}')\n",
            "print(f'  Recovery Events:  {intensity_results[\"in_recovery\"].sum()}')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Visualize CIS heatmap\n",
            "from visualizations import StrategyVisualizer\n",
            "viz = StrategyVisualizer()\n",
            "\n",
            "prices_aligned = features['price'].loc[intensity_results.index]\n",
            "\n",
            "fig = viz.plot_crash_intensity_heatmap(\n",
            "    prices_aligned,\n",
            "    intensity_results['crash_intensity'],\n",
            "    intensity_results['position_size']\n",
            ")\n",
            "plt.savefig('../reports/figures/crash_intensity_heatmap.png', dpi=150, bbox_inches='tight')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Why CIS is Superior\n",
            "\n",
            "| Approach | Pros | Cons |\n",
            "|----------|------|------|\n",
            "| **Binary Detection** | Simple | Whipsaws, delayed response |\n",
            "| **Rule-based Thresholds** | Interpretable | Fixed, not adaptive |\n",
            "| **CIS (Ours)** | Graduated, adaptive, proportional | More complex |\n",
            "\n",
            "**Key insight**: Crashes aren't binary - they have varying intensity. Our response should match."
        ]
    }
]

# Find where to insert (before stress testing section or before section 8)
cells = notebook['cells']
insert_idx = None

for i, cell in enumerate(cells):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if '# 8. Stress Testing' in source:
            insert_idx = i
            break

if insert_idx is not None:
    # Insert CIS cells before stress testing
    for j, new_cell in enumerate(cis_cells):
        cells.insert(insert_idx + j, new_cell)
    print(f"✅ Inserted {len(cis_cells)} CIS cells at position {insert_idx}")
else:
    # Try to find section 7 (results)
    for i, cell in enumerate(cells):
        if cell['cell_type'] == 'markdown':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if '# 7. Results' in source or '# 7.' in source:
                insert_idx = i
                break
    
    if insert_idx:
        for j, new_cell in enumerate(cis_cells):
            cells.insert(insert_idx + j, new_cell)
        print(f"✅ Inserted {len(cis_cells)} CIS cells at position {insert_idx}")
    else:
        print("❌ Could not find insertion point")

# Save notebook
with open('notebooks/competition_demo.ipynb', 'w') as f:
    json.dump(notebook, f, indent=4)

print("✅ Notebook updated with Crash Intensity Scoring section!")
