# FUTURE-AI Metrics Project Structure

## Overview
This project provides comprehensive metrics for evaluating AI tools in medical imaging, organized into separate modules for universality and traceability metrics.

## Directory Structure

```
FUTURE-AI-metrics/
├── future_ai_metrics/          # Main package directory
│   ├── __init__.py            # Package initialization and exports
│   ├── universality/          # Universality metrics module
│      ├── __init__.py
│      └── metrics.py        # UniversalityMetrics class
├── config/                    # Configuration files directory
│   ├── universality_metrics_config.json
│   └── xxxx_metrics_config.json
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_universality_metrics.py
│   └── test_xxxx_metrics.py
├── requirements.txt           # Python dependencies
├── Readme.md                  # Project documentation
└── PROJECT_STRUCTURE.md       # This file
```

## Usage

### Importing Metrics Classes

```python
# Import from main package
from future_ai_metrics import UniversalityMetrics

# Or import from specific modules
from future_ai_metrics.universality.metrics import UniversalityMetrics
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_universality_metrics.py

# Run with verbose output
python -m pytest tests/ -v
```

## Configuration

Configuration files are stored in the `config/` directory, with separate files for each metric type:
- `config/universality_metrics_config.json`: Contains `real_requirements` and `compatibility_categories`

## Adding New Metrics

1. Create a new module directory under `future_ai_metrics/`
2. Add `__init__.py` and `metrics.py` files
3. Create corresponding test file in `tests/`
4. Update `future_ai_metrics/__init__.py` to export the new class
5. Create a new configuration file in `config/` directory (e.g., `config/new_metrics_config.json`)
6. Update the metric class to load from the new config file

