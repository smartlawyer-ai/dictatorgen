# dictatorgenai/regimes/__init__.py

from .regime import Regime, RegimeExecutionError
from.base_regime import BaseRegime

__all__ = [
    "BaseRegime",
    "Regime",
    "RegimeExecutionError",
]
