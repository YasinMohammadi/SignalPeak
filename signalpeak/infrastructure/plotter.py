from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from signalpeak.domain.signal import Signal


class SignalPlotter:
    """Save plots with peaks plus predictor annotations."""

    def __init__(self, output_dir: Path | str = Path("results") / "plots", peak_prom_frac: float = 0.2):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.peak_prom_frac = peak_prom_frac

    # ------------------------------------------------------------------
    def save_plot(
        self,
        signal: Signal,
        prediction_history: Optional[List[Tuple[int, float]]] = None,
    ) -> Path:
        s = signal.to_series()
        peaks, _ = self._detect_peaks(s)

        fig, ax = plt.subplots(ncols=2, nrows=1,figsize=(10, 4))
        ax0 = ax[0]
        ax1 = ax[1]
        ax0.plot(s.index, s.values, label="signal")

        # All detected peaks
        ax0.scatter(peaks, s.iloc[peaks], color="k", s=25, label="peaks")
        if peaks.size:
            first_peak = peaks.min()
            ax0.scatter(first_peak, s.iloc[first_peak], color="red", s=100, marker="*", label="first peak")

        ax1.set_ylabel("steps left")
        if prediction_history:
            t_idxs = [t for t, _ in prediction_history]
            steps_left = [abs_peak - t for t, abs_peak in prediction_history]
            ax1.plot(t_idxs, steps_left, color="orange", linestyle="--", label="steps left")
            ax1.legend(loc="upper right")
            ax1.set_ylim(-10, 75)

        # Prediction timeline
        # if prediction_history:
        #     for t_idx, abs_peak_idx in prediction_history:
        #         if abs_peak_idx < len(s):
        #             ax0.scatter(abs_peak_idx, s.iloc[int(abs_peak_idx)], color="green", marker="D", s=50)
        #             ax0.annotate(
        #                 f"pred→{abs_peak_idx:.1f}",
        #                 (t_idx, s.iloc[int(t_idx)]),
        #                 textcoords="offset points",
        #                 xytext=(0, 10),
        #                 ha="center",
        #                 fontsize=7,
        #                 arrowprops=dict(arrowstyle="->", lw=0.5, color="green"),
        #             )

        ax0.set_xlabel("sample index")
        ax0.set_ylabel("value")
        ax0.legend(loc="upper left")
        fig.tight_layout()
        out_path = self.output_dir / f"{signal.name}.png"
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
        return out_path

    # ------------------------------------------------------------------
    def _detect_peaks(self, s: pd.Series):
        prom = (s.max() - s.min()) * self.peak_prom_frac
        return find_peaks(s.values, prominence=prom)