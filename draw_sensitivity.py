import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import pathlib
from scipy.interpolate import PchipInterpolator, interp1d

import config

xpad = 8

def draw_sensitivity(x_max = 32):
    labels, dfs = get_data()
    # print(f"{dfs}")

    n = len(dfs)
    xlim = x_max + xpad

    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(
        nrows=rows,
        ncols=cols,
        figsize=(cols * 3, rows * 3),
        sharex=True,
        sharey=True,
    )

    if len(dfs) == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for ax, df, label in zip(axes, dfs, labels):
        # Normalize the series
        df["perf"] = df["perf"][0] / df["perf"]

        x = df["footprint_mb"].to_numpy()
        y = df["perf"].to_numpy()

        # Interpolate
        spline = PchipInterpolator(x, y)

        x_smooth = np.linspace(x.min(), x.max(), 400)
        y_smooth = spline(x_smooth)

        ax.plot(x, y, "o", markersize=4, label="measured")
        ax.plot(x_smooth, y_smooth, "-", linewidth=1.5, label="spline")
        
        ax.set_title(label)
        ax.set_xlabel("MemBW footprint (MB)")
        ax.set_ylabel("Performance (norm.)")
        xticks = np.arange(0, 128, 16)
        ax.set_xticks(xticks)
        ax.set_xlim([0, xlim])
        ax.grid(True)

    for ax in axes[n:]:
        fig.delaxes(ax)

    plt.tight_layout()
    image_output_path = pathlib.Path(config.RESULTS_DIR) / "sensitivity.png"
    plt.savefig(image_output_path, dpi=300)
    plt.close()


def get_data() -> tuple[list[str], list[pd.DataFrame]]:
    parent_dir = pathlib.Path(config.RESULTS_DIR) / "sensitivity"
    csv_paths = [parent_dir / f for f in os.listdir(parent_dir) if f.endswith(".csv")]
    labels = [p.parts[2].split('_')[1] for p in csv_paths]

    # Add reporter
    csv_paths += [pathlib.Path(config.RESULTS_DIR) / "reporter_sensitivity.csv"]
    labels += ["reporter"]

    dfs = [pd.read_csv(p, delimiter=",") for p in csv_paths]
    return labels, dfs


if __name__ == "__main__":
    draw_sensitivity(int(sys.argv[1]) if len(sys.argv) > 1 else 32)
