from __future__ import annotations

from typing import Iterator, Sequence, List

import pandas as pd


class Signal:
    """Domain entity representing a 1-D discrete signal (framework-agnostic)."""

    def __init__(self, name: str, values: Sequence[float], sampling_interval: float = 1.0):
        self._name: str = name
        self._values: List[float] = list(values)
        self._sampling_interval: float = float(sampling_interval)

    # ---------------------------------------------------------------------
    # Basic properties
    # ---------------------------------------------------------------------
    @property
    def name(self) -> str:
        return self._name

    @property
    def values(self) -> List[float]:
        return self._values

    @property
    def sampling_interval(self) -> float:
        return self._sampling_interval

    @property
    def length(self) -> int:
        return len(self._values)

    # ---------------------------------------------------------------------
    # Iteration helpers
    # ---------------------------------------------------------------------
    def __iter__(self) -> Iterator[float]:
        """Simple iterator over raw values (no side effects)."""
        return iter(self._values)

    def stream(self) -> Iterator[float]:
        """Simulate real-time streaming (yield one sample per call)."""
        for v in self._values:
            yield v

    # ---------------------------------------------------------------------
    # Convenience
    # ---------------------------------------------------------------------
    def to_series(self) -> pd.Series:
        """Return a pandas Series (useful for analysis / plotting)."""
        return pd.Series(self._values, name=self._name, dtype=float)