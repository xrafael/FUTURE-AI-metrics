"""
FUTURE-AI Metrics Package

This package provides comprehensive metrics for evaluating AI tools in medical imaging,
including universality and traceability metrics.
"""

from future_ai_metrics.universality.metrics import UniversalityMetrics

try:
    from future_ai_metrics.traceability.metrics import TraceabilityMetrics
    __all__ = ['UniversalityMetrics', 'TraceabilityMetrics']
except ImportError:
    __all__ = ['UniversalityMetrics']

__version__ = '0.1.0'

