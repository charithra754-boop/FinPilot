# Contributing to FinPilot

Thank you for your interest in contributing to FinPilot! This document outlines our development practices and standards.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/charithra754-boop/FinPilot.git
cd FinPilot

# Install dependencies
pip install -r requirements.txt

# Verify setup (48 tests should pass)
python -m pytest tests/ -v
```

## Code Standards

### Style Guidelines
- **PEP 8** compliance required
- **Type hints** for all function signatures
- **Docstrings** (Google style) for all public methods
- Maximum line length: 100 characters

### Example
```python
def calculate_crash_intensity(
    self, 
    features: pd.Series
) -> float:
    """
    Calculate the Crash Intensity Score (CIS).
    
    Args:
        features: Series containing feature values
        
    Returns:
        CIS value between 0 and 100
    """
    ...
```

### Testing Requirements
- All new features must include comprehensive unit tests
- Run full test suite before any commit: `pytest tests/ -v`
- Target >80% code coverage
- No test should take more than 1 second

### Git Workflow
- Use descriptive branch names: `feature/crash-intensity-scoring`
- Write clear commit messages: `Add CIS proportional positioning`
- Keep commits atomic and focused
- Squash before merging to main

## Module Architecture

| Layer | Modules | Responsibility |
|-------|---------|----------------|
| **Data** | `data_handler.py`, `features.py` | Ingestion, preprocessing |
| **Intelligence** | `regime_detector.py`, `crash_intensity.py` | Risk assessment |
| **Execution** | `strategy.py`, `backtester.py` | Trading simulation |
| **Analytics** | `metrics.py`, `monte_carlo.py`, `stress_testing.py` | Validation |
| **Presentation** | `visualizations.py` | Charts & reports |

## Adding New Features

1. **Design** - Document approach in an issue
2. **Branch** - Create feature branch from `main`
3. **Implement** - Write code with type hints
4. **Test** - Add comprehensive unit tests
5. **Document** - Update READMEs and docstrings
6. **Review** - Submit PR with description
7. **Merge** - Squash and merge after approval

## Quality Gates

Before any merge:
- [ ] All 48+ tests passing
- [ ] No linting errors
- [ ] Documentation updated
- [ ] No hardcoded paths
- [ ] Type hints complete

## Questions?

Open an issue for questions, suggestions, or feature requests.
