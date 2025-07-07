from __future__ import annotations

from collections import deque
from statistics import median, mean
from typing import Deque, List, Optional, Sequence, Tuple

from .indicators.base_indicator import Indicator


class PeakPredictor:
    """Aggregates multiple indicators to forecast steps to the first peak."""

    def __init__(self, indicators: Sequence[Indicator], window_size: int = 50):
        if window_size < 5:
            raise ValueError("window_size must be >= 5")
        self.window_size = window_size
        self.buffer: Deque[float] = deque(maxlen=window_size)
        self.indicators: List[Indicator] = list(indicators)
        self.peak_reached: bool = False
        self._pred_history: List[Tuple[int, float]] = []  # (t_idx, predicted_peak_idx)

    # ------------------------------------------------------------------
    def update(self, value: float, t_idx: int) -> Optional[float]:
        """Add new value and return aggregated *absolute index* of predicted peak (optional)."""
        if self.peak_reached:
            return None
        self.buffer.append(value)
        if len(self.buffer) < 5:
            return None
        step_predictions: List[float] = []
        for ind in self.indicators:
            s = ind.predict(list(self.buffer))
            if s is not None:
                step_predictions.append(s)
        if not step_predictions:
            return None
        # Combine via median for robustness
        steps_left = mean(step_predictions)
        if steps_left is None:
            return None
        abs_peak_idx = t_idx + steps_left
        self._pred_history.append((t_idx, abs_peak_idx))
        return abs_peak_idx

    # ------------------------------------------------------------------
    @property
    def prediction_history(self) -> List[Tuple[int, float]]:
        return self._pred_history
