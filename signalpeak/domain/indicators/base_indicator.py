from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence, Optional


class Indicator(ABC):
    """Abstract base class – strategy for forecasting steps to peak."""

    @abstractmethod
    def predict(self, window: Sequence[float]) -> Optional[float]:
        """Return estimated steps to first peak (float >= 0) or None if unsure."""
        raise NotImplementedError