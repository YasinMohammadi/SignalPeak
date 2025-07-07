from __future__ import annotations

from typing import Sequence, Optional

import numpy as np
from scipy.signal import savgol_filter

from .base_indicator import Indicator


class DerivativeIndicator(Indicator):
    """Use smoothed first & second derivatives to project slope zero-crossing."""

    def __init__(self, window_length: int = 11, polyorder: int = 3):
        if window_length % 2 == 0:
            window_length += 1  # must be odd
        self.window_length = window_length
        self.polyorder = polyorder
        self._last_estimate: Optional[float] = None

    # ------------------------------------------------------------------
    def predict(self, window: Sequence[float]) -> Optional[float]:
        if len(window) < self.window_length:
            return None
        y = np.asarray(window, dtype=float)
        try:
            dy = savgol_filter(y, self.window_length, self.polyorder, deriv=1)
            ddy = savgol_filter(y, self.window_length, self.polyorder, deriv=2)
            f1 = dy[-1]
            f2 = ddy[-1]
            if f2 >= 0 or f1 <= 0:  # not concave down or not rising
                return None
            steps_left = -f1 / f2
            if steps_left < 0:
                return None
            self._last_estimate = float(steps_left)
            return self._last_estimate
        except Exception:
            return None