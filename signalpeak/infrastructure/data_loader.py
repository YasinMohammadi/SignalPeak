from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
from scipy.io import loadmat

from signalpeak.domain.signal import Signal


class MatlabSignalRepository:
    """Infrastructure service that converts MATLAB .mat files into `Signal`s."""

    DEFAULT_KEY = "y"

    def __init__(self, signal_key: str | None = None, scale_factor: float | None = None):
        self.signal_key = signal_key or self.DEFAULT_KEY
        self.scale_factor = scale_factor

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load(self, source: Path) -> Dict[str, Signal]:
        if not source.exists():
            raise FileNotFoundError(f"Source path '{source}' not found")
        """Load a single .mat file or every .mat file in a directory."""
        if source.is_dir():
            return self._load_directory(source)
        if source.suffix != ".mat":
            raise ValueError(f"Expected .mat file, got {source}")
        return {source.stem: self._load_file(source)}

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _load_directory(self, folder: Path) -> Dict[str, Signal]:
        signals: Dict[str, Signal] = {}
        for p in sorted(folder.glob("*.mat")):
            signals[p.stem] = self._load_file(p)
        if not signals:
            raise FileNotFoundError(f"No .mat files found in {folder}")
        return signals

    def _load_file(self, path: Path) -> Signal:
        mat = loadmat(path, squeeze_me=True, struct_as_record=False)
        key = self._resolve_key(mat)
        arr = mat[key]
        if not isinstance(arr, np.ndarray):
            raise TypeError(f"{path}: variable '{key}' is not an ndarray")
        if arr.ndim != 1:
            raise ValueError(f"{path}: variable '{key}' must be 1-D, got shape={arr.shape}")
        if self.scale_factor:
            arr = arr * self.scale_factor
        return Signal(path.stem, arr)

    def _resolve_key(self, mat: dict) -> str:
        if self.signal_key in mat and not self.signal_key.startswith("__"):
            return self.signal_key
        # fallback: first non-meta key
        cand = [k for k in mat.keys() if not k.startswith("__")]
        if len(cand) == 1:
            return cand[0]
        raise KeyError(
            f"Could not find signal key '{self.signal_key}'. Available keys: {cand}")