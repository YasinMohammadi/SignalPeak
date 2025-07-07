from __future__ import annotations

from typing import Sequence, Optional

import numpy as np
from scipy.optimize import curve_fit

from .base_indicator import Indicator


class GaussianIndicator(Indicator):
    """Fit a Gaussian to the recent window and extrapolate peak center."""

    def __init__(self):
        # sensible bounds could be added; keep simple for now
        self._last_estimate: Optional[float] = None

    # ------------------------------------------------------------------
    def predict(self, window: Sequence[float]) -> Optional[float]:
        if len(window) < 5:  # need enough points
            return None
        x = np.arange(len(window), dtype=float)
        y = np.asarray(window, dtype=float)

        # Initial guesses
        A0 = y.max() - y.min()
        mu0 = len(window) * 1.2  # a bit ahead of current index
        sigma0 = max(len(window) / 5, 1.0)
        H0 = y.min()

        def gauss(t, H, A, mu, sigma):
            return H + A * np.exp(-(t - mu) ** 2 / (2 * sigma**2))

        try:
            popt, _ = curve_fit(
                gauss,
                x,
                y,
                p0=[H0, A0, mu0, sigma0],
                bounds=([y.min() - A0, 0, -np.inf, 1e-3], [y.max() + A0, np.inf, np.inf, np.inf]),
                maxfev=2000,
            )
            H, A, mu, sigma = popt
            steps_left = mu - (len(window) - 1)
            if steps_left < 0:
                return None  # peak already passed (fit unreliable)
            self._last_estimate = float(steps_left)
            return self._last_estimate
        except Exception:
            return None