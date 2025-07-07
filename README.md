
## SignalPeak

> **Forecast how many steps remain until the _first_ peak of a noisy 1-D signal, in real time.**  
> Fitted for Financial Market data

----------

### Table of contents

1.  [Why SignalPeak?](#why-signalpeak)
    
2.  [Features](#features)
    
3.  [Quick start](#quick-start)
    
4.  [CLI reference](#cli-reference)
    
5.  [Project layout](#project-layout)
    
6.  [Indicators](#indicators)
    
7.  [How it works](#how-it-works)
    
8.  [Contributing](#contributing)
    
9.  [License](#license)
    

----------

### Why SignalPeak?

Detecting the _upcoming_ maximum of a noisy curve is common in finance, chemistry, sensor telemetry, etc.  
SignalPeak answers _“how many samples are left until the very first major peak?”_ while data arrives one point at a time.  
The code is framework-agnostic, lightweight, and easy to extend—perfect for research, back-testing, or embedding in bigger apps.

----------

### Features

|  |  Description|
|--|--|
|Live streaming  | Feed values one-by-one; the predictor updates its forecast every tick. |
|Robust aggregation|Combines indicator outputs via median to damp outliers.|
|Batch back-tests|--|

----------

### Quick start

```bash 
# clone & install
git clone https://github.com/yourname/signalpeak.git
cd signalpeak
poetry install   # or: pip install -e .

# run on one .mat file
peak-forecast ./data/sample.mat --plots

# run on a folder, custom window, only gaussian+poly indicators
peak-forecast ./data --window 60 --indicators gauss poly --plots

```
Output shows a running log such as:

```bash 
[INFO] Loaded 'curve42' (180 samples)
  t=25: predicted first peak at t≈31.4 (steps left 6.4)
  t=26: predicted first peak at t≈30.7 (steps left 4.7)
  ...
[SUMMARY] First prediction was at t=25 -> peak≈31.4 (lead 6.4)
[INFO] Plot saved → results/plots/curve42.png

```

### CLI reference

| Flag | Default | Meaning |
|--|--|--|
| source |  | `.mat` file **or** directory of `.mat` files. |
| `-k`, `--key` | `y` | Variable name inside each `.mat` that holds the 1-D signal. |
| --scale |  | Multiply signal by this factor (e.g. `1e6` to scale micro-volts → volts). |
| --window | 50 | How many most-recent samples each indicator sees. |
| --indicators | gauss poly deriv | One or more of `gauss` (Gaussian fit), `poly` (quadratic), `deriv` (derivative). |
| --plots | off | Save annotated PNGs under `results/plots`. |


### Project layout

```ini
signalpeak/
├─ peak_forecasting/
│  ├─ domain/              # core logic, no I/O
│  │   ├─ signal.py
│  │   ├─ predictor.py
│  │   └─ indicators/
│  ├─ infrastructure/      # file loading, plotting
│  └─ cli/                 # user interface layer
└─ pyproject.toml

```

### Indicators
| Name (`--indicators`) | Technique | Best when… |
|--|--|--|
| `gauss` | Non-linear least-squares fit of a Gaussian bell; predicts peak center μ. | Peak is bell-shaped and partially visible. |
| `poly` | Quadratic (degree 2) least-squares fit; vertex gives peak. | You are _near_ the top and curvature is clear. |
| deriv | Savitzky–Golay smoothed first/second derivatives; extrapolates slope→0. | General-purpose; works even with non-Gaussian shapes, if noise is moderate. |

Add your own by subclassing `Indicator` and dropping the file into `domain/indicators`.

----------

### How it works

1.  **Stream** – `PeakPredictor.update(value, t)` draws a sliding window of the last _n_ points.
    
2.  **Query** – Each active indicator returns _steps left_ (float) or `None`.
    
3.  **Aggregate** – Median of non-None estimates → absolute peak index.
    
4.  **Log** – Every prediction tuple `(t, peak_idx)` is stored for analysis & plotting.
    
5.  **Plot** – `SignalPlotter` marks:
    
    -   Black dots = all peaks (`scipy.signal.find_peaks`)
        
    -   Red star = first peak (ground truth)
        
    -   Green diamonds = predicted peak positions  
        Arrows show when the prediction was issued.
        

----------

### Contributing

Issues and PRs are welcome — especially:

-   New classical indicators (e.g., Lorentzian fit, change-point detection)
    
-   Performance improvements for large data streams
    
-   Unit tests & CI pipelines
    

Run linters/tests locally:

```bash
poetry run flake8
poetry run pytest

```

### License

MIT © 2025 Yasin Mohammadi  

