import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pathlib
from scipy.interpolate import PchipInterpolator
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import config

xpad = 8

METRICS = [
    "time",
    "LLC-loads",
    "LLC-load-misses",
    # "LLC-store-misses",
    "L1-dcache-loads",
    "L1-dcache-load-misses",
    # "LLC-miss-rate",
    # "L1-icache-load-misses",
    # "cache-misses",
    # "dTLB-load-misses",
    "CPI",
]

NORMALIZE = True
# NORMALIZE = False

def plot_metrics(filename: str, bar_chart: bool = False):
    csv_path = pathlib.Path(config.RESULTS_DIR) / "sensitivity" / filename
    df = pd.read_csv(csv_path, delimiter=",")
    df = df.sort_values("footprint_mb")

    x = pd.to_numeric(df["footprint_mb"], errors="coerce").to_numpy(dtype=float)
    finite_x = x[np.isfinite(x)]
    if finite_x.size == 0:
        raise ValueError("No valid footprint_mb values found in CSV")

    xlim = finite_x.max() + (xpad / (xpad - finite_x.max()))

    fig, ax = plt.subplots(figsize=(10, 5))

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    markers = ["o", "s", "v", "^", "D", "X", "P", "*"]

    available_metrics = [metric for metric in METRICS if metric in df.columns]
    for metric_index, metric in enumerate(available_metrics):
        marker = markers[metric_index % len(markers)]
        color = colors[metric_index % len(colors)]

        y = pd.to_numeric(df[metric], errors="coerce").to_numpy(dtype=float)
        if y.size == 0:
            continue

        valid = np.isfinite(x) & np.isfinite(y)
        if not np.any(valid):
            continue

        x_valid = x[valid]
        y_valid = y[valid]

        # Normalize each metric to its first measured value so different scales can be plotted together.
        if NORMALIZE:
            first_value = y_valid[0]
            if first_value != 0 and np.isfinite(first_value):
                y_valid = y_valid / first_value

        if bar_chart:
            if x_valid.size > 1:
                x_spacing = np.median(np.diff(np.unique(x_valid)))
            else:
                x_spacing = 1.0
            bar_width = 0.6 * max(1.0, x_spacing) / max(1, len(available_metrics))
            offset = (metric_index - (len(available_metrics) - 1) / 2) * bar_width
            ax.bar(
                x_valid + offset,
                y_valid,
                width=bar_width,
                label=metric,
                color=color,
                alpha=0.8,
            )
            
        elif config.USE_INTERPOLATION and x_valid.size > 1:
            spline = PchipInterpolator(x_valid, y_valid)
            x_smooth = np.linspace(x_valid.min(), x_valid.max(), 400)
            y_smooth = spline(x_smooth)
            ax.plot(x_smooth, y_smooth, "-", linewidth=1.5, label=metric, color=color)
        else:
            ax.plot(x_valid, y_valid, marker=marker, markersize=4, linewidth=1.5, label=metric, color=color)

    ax.set_title("Metrics vs. footprint")
    ax.set_xlabel("MemBW footprint (MB)")
    if NORMALIZE:
        ax.set_ylabel("Normalized value")
    else:
        ax.set_ylabel("Numeric Value")

    if bar_chart:
        bar_positions = []
        for metric_index, metric in enumerate(available_metrics):
            y = pd.to_numeric(df[metric], errors="coerce").to_numpy(dtype=float)
            valid = np.isfinite(x) & np.isfinite(y)
            if not np.any(valid):
                continue
            x_valid = x[valid]
            if x_valid.size > 1:
                x_spacing = np.median(np.diff(np.unique(x_valid)))
            else:
                x_spacing = 1.0
            bar_width = 0.5 * max(1.0, x_spacing) / max(1, len(available_metrics))
            offset = (metric_index - (len(available_metrics) - 1) / 2) * bar_width
            bar_positions.extend(x_valid + offset)
        if bar_positions:
            xlim_min = -1.5 * bar_width * (len(METRICS) / 2)
            xlim_max = max(xlim, max(bar_positions) + bar_width + 1.0)
            ax.set_xlim([xlim_min, xlim_max])
            ax.set_xticks(np.arange(0, xlim_max + 1, finite_x.max()))
        else:
            ax.set_xlim([0, xlim])
            ax.set_xticks(np.arange(0, xlim + 1, finite_x.max()))
    else:
        ax.set_xlim([0, xlim])
        ax.set_xticks(np.arange(0, xlim + 1, finite_x.max()))
    ax.grid(True)
    ax.legend()

    plt.tight_layout()
    image_output_path = pathlib.Path(config.RESULTS_DIR) / "metrics.png"
    plt.savefig(image_output_path, dpi=300)
    plt.close()


if __name__ == "__main__":
    config.USE_INTERPOLATION = True

    if len(sys.argv) < 2:
        print("Provide a path!")
        exit()

    path = ""
    bar = False
    if sys.argv[1] == "--bar":
        bar = True
        if sys.argv[2] == "--raw":
            NORMALIZE = False
            path = sys.argv[3]
        else:
            path = sys.argv[2]
    else:
        path = sys.argv[1]

    plot_metrics(path, bar)
