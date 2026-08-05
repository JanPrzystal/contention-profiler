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

def draw_sensitivity():
    labels, dfs = get_data()

    n = len(dfs)

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

        xlim = x.max() + xpad

        ax.plot(x, y, "o", markersize=4, label="measured")

        if config.USE_INTERPOLATION:
            # Interpolate
            spline = PchipInterpolator(x, y)

            x_smooth = np.linspace(x.min(), x.max(), 400)
            y_smooth = spline(x_smooth)
            ax.plot(x_smooth, y_smooth, "-", linewidth=1.5, label="spline")
        
        ax.set_title(label)
        ax.set_xlabel("MemBW footprint (MB)")
        ax.set_ylabel("Performance (norm.)")
        xticks = np.arange(0, xlim, 16)
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
    csv_paths = []
    labels = []
    
    if parent_dir.is_dir():
        csv_paths = [parent_dir / f for f in os.listdir(parent_dir) if f.endswith(".csv")]
        labels = [p.parts[2].split('_')[1] for p in csv_paths]

    # Add reporter
    reporter_path = pathlib.Path(config.RESULTS_DIR) / "reporter_sensitivity.csv"
    if reporter_path.exists():
        csv_paths += [reporter_path]
        labels += ["reporter"]

    dfs = [pd.read_csv(p, delimiter=",") for p in csv_paths]
    return labels, dfs


if __name__ == "__main__":
    draw_sensitivity()
