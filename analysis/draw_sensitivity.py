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

xpad = 1

def draw_sensitivity():
    labels, dfs = get_data()

    n = len(dfs)

    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(
        nrows=rows,
        ncols=cols,
        figsize=((cols + 1) * 3, rows * 3),
        sharex=True,
        sharey=True,
    )

    if len(dfs) == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for ax, df, label in zip(axes, dfs, labels):
        # Normalize the series
        if df.empty:
            continue
        
        df["perf"] = df["perf"].iloc[0] / df["perf"]

        x = df["pressure"].to_numpy()
        y = df["perf"].to_numpy()

        # Pressure is in MB, convert to nr of competitors
        x_steps = np.diff(np.sort(np.unique(x)))
        tick_interval = x_steps[x_steps > 0].min()

        x = (x - x.min()) / tick_interval

        xlim = x.max() + xpad

        ax.plot(x, y, "o", markersize=4, label="measured")

        if config.USE_INTERPOLATION:
            # Interpolate
            spline = PchipInterpolator(x, y)

            x_smooth = np.linspace(x.min(), x.max(), 400)
            y_smooth = spline(x_smooth)
            ax.plot(x_smooth, y_smooth, "-", linewidth=1.5, label="spline")
        
        ax.set_title(label)
        ax.set_xlabel("Number of Competitors")
        ax.set_ylabel("Performance (norm.)")

        xticks = np.arange(0, xlim)
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
