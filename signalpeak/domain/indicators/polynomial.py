from __future__ import annotations

from typing import Sequence, Optional

import numpy as np

from .base_indicator import Indicator


class PolynomialIndicator(Indicator):
    """Quadratic fit (parabolic) to estimate vertex ahead."""

    def __init__(self):
        self._last_estimate: Optional[float] = None

    # ------------------------------------------------------------------
    def predict(self, window: Sequence[float]) -> Optional[float]:
        if len(window) < 5:
            return None
        x = np.arange(len(window), dtype=float)
        y = np.asarray(window, dtype=float)
        try:
            a, b, c = np.polyfit(x, y, 2)
            if a >= 0:
                return None  # parabola not concave down – cannot predict peak
            t_vertex = -b / (2 * a)
            steps_left = t_vertex - (len(window) - 1)
            if steps_left < 0:
                return None
            self._last_estimate = float(steps_left)
            return self._last_estimate
        except Exception:
            return None