# Contributing to FinPilot

Thank you for your interest in contributing to FinPilot!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/charithra754-boop/FinPilot.git
cd FinPilot

# Install dependencies
pip install -r requirements.txt

# Run tests to verify setup
python -m pytest tests/ -v
```

## Code Standards

### Style
- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write docstrings for all public functions

### Testing
- All new features must include unit tests
- Run `pytest tests/ -v` before submitting changes
- Maintain 100% test coverage for core modules

### Commits
- Use clear, descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused and atomic

## Module Structure

| Module | Responsibility |
|--------|----------------|
| `data_handler.py` | Data loading and preprocessing |
| `features.py` | Feature engineering |
| `regime_detector.py` | Market regime detection |
| `strategy.py` | Trading logic |
| `backtester.py` | Simulation engine |
| `metrics.py` | Performance metrics |
| `visualizations.py` | Charts and dashboards |

## Adding New Features

1. Create a feature branch
2. Implement with tests
3. Update documentation
4. Submit pull request

## Questions?

Open an issue for questions or suggestions.
