from __future__ import annotations

import argparse
from pathlib import Path

from signalpeak.domain.indicators import (
    GaussianIndicator,
    PolynomialIndicator,
    DerivativeIndicator,
)
from signalpeak.domain.predictor import PeakPredictor
from signalpeak.infrastructure.data_loader import MatlabSignalRepository
from signalpeak.infrastructure.plotter import SignalPlotter


def _build_indicators(names: list[str]):
    lookup = {
        "gauss": GaussianIndicator,
        "poly": PolynomialIndicator,
        "deriv": DerivativeIndicator,
    }
    indicators = []
    for n in names:
        if n not in lookup:
            raise ValueError(f"Unknown indicator '{n}'. Choose from {list(lookup)}")
        indicators.append(lookup[n]())
    return indicators


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="peak-forecast",
        description="Stream MATLAB signals, predict time-to-first-peak, and save annotated plots.",
    )
    parser.add_argument("source", type=Path, help=".mat file or directory of .mat files")
    parser.add_argument("-k", "--key", default="y", help="Variable key inside .mat (default: 'y')")
    parser.add_argument("--scale", type=float, default=None, help="Multiply signal by this factor (optional)")
    parser.add_argument("--window", type=int, default=50, help="Look-back window size (default: 50)")
    parser.add_argument(
        "--indicators",
        nargs="*",
        default=["gauss", "poly", "deriv"],
        help="Indicators to use [gauss, poly, deriv] (default: all)",
    )
    parser.add_argument("--plots", action="store_true", help="Save annotated plots under results/plots")

    args = parser.parse_args()

    repo = MatlabSignalRepository(signal_key=args.key, scale_factor=args.scale)
    signals = repo.load(args.source)
    plotter = SignalPlotter()

    ind_objs = _build_indicators(args.indicators)

    for name, sig in signals.items():
        print(f"\n[INFO] Loaded '{name}' ({sig.length} samples)")
        predictor = PeakPredictor(indicators=ind_objs, window_size=args.window)

        for t_idx, val in enumerate(sig.stream()):
            abs_peak_idx = predictor.update(val, t_idx)
            if abs_peak_idx is not None:
                print(
                    f"  t={t_idx}: predicted first peak at t≈{abs_peak_idx:.1f} (steps left {abs_peak_idx - t_idx:.1f})"
                )
        # summary
        if predictor.prediction_history:
            first_pred = predictor.prediction_history[0]
            print(
                f"[SUMMARY] First prediction was at t={first_pred[0]} -> peak≈{first_pred[1]:.1f} (lead {first_pred[1]-first_pred[0]:.1f})"
            )
        else:
            print("[SUMMARY] No peak prediction made (insufficient data or indicators)")

        if args.plots:
            out = plotter.save_plot(sig, predictor.prediction_history)
            abs_out = out.resolve()
            try:
                display_path = abs_out.relative_to(Path.cwd())
            except ValueError:
                display_path = abs_out
            print(f"[INFO] Plot saved → {display_path}")

    print("\n[DONE]")


if __name__ == "__main__":
    main()
