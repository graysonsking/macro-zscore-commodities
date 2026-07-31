"""Macro driven cross-sectional commodity signals.

Pipeline: fred_client -> zscore -> mapping -> signal
"""

from . import fred_client, mapping, signal, zscore

__version__ = "0.1.0"
__all__ = ["fred_client", "zscore", "mapping", "signal"]
