"""Package that groups all peak-forecasting indicators."""
from .gaussian import GaussianIndicator  # noqa: F401
from .polynomial import PolynomialIndicator  # noqa: F401
from .derivative import DerivativeIndicator  # noqa: F401

__all__ = [
    "GaussianIndicator",
    "PolynomialIndicator",
    "DerivativeIndicator",
]