import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import pathlib
from scipy.interpolate import PchipInterpolator
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import config

xpad = 8

METRICS = ["time", "CPI", "LLC-load-misses", "LLC-store-misses", "L1-dcache-load-misses", "LLC-miss-rate"]


def plot_metrics(filename: str = "657_xz_s_data.csv"):
    csv_path = pathlib.Path(config.RESULTS_DIR) / "sensitivity" / filename
    df = pd.read_csv(csv_path, delimiter=",")
    df = df.sort_values("footprint_mb")

    x = pd.to_numeric(df["footprint_mb"], errors="coerce").to_numpy(dtype=float)
    finite_x = x[np.isfinite(x)]
    if finite_x.size == 0:
        raise ValueError("No valid footprint_mb values found in CSV")

    xlim = finite_x.max() + xpad

    fig, ax = plt.subplots(figsize=(10, 5))

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    markers = ["o", "s", "v", "^", "D"]

    for metric, marker, color in zip(METRICS, markers, colors):
        if metric not in df.columns:
            continue

        y = pd.to_numeric(df[metric], errors="coerce").to_numpy(dtype=float)
        if y.size == 0:
            continue

        valid = np.isfinite(x) & np.isfinite(y)
        if not np.any(valid):
            continue

        x_valid = x[valid]
        y_valid = y[valid]

        # Normalize each metric to its first measured value so different scales can be plotted together.
        first_value = y_valid[0]
        if first_value != 0 and np.isfinite(first_value):
            y_valid = y_valid / first_value

        if config.USE_INTERPOLATION and x_valid.size > 1:
            spline = PchipInterpolator(x_valid, y_valid)
            x_smooth = np.linspace(x_valid.min(), x_valid.max(), 400)
            y_smooth = spline(x_smooth)
            ax.plot(x_smooth, y_smooth, "-", linewidth=1.5, label=metric, color=color)
        else:
            ax.plot(x_valid, y_valid, marker=marker, markersize=4, linewidth=1.5, label=metric, color=color)

    ax.set_title("Metrics vs. footprint")
    ax.set_xlabel("MemBW footprint (MB)")
    ax.set_ylabel("Normalized value")
    ax.set_xlim([0, xlim])
    ax.set_xticks(np.arange(0, xlim + 1, 16))
    ax.grid(True)
    ax.legend()

    plt.tight_layout()
    image_output_path = pathlib.Path(config.RESULTS_DIR) / "metrics.png"
    plt.savefig(image_output_path, dpi=300)
    plt.close()


if __name__ == "__main__":
    config.USE_INTERPOLATION = False
    plot_metrics()
