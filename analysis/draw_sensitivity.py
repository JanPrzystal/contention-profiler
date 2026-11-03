import argparse
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

def draw_sensitivity(same_chart: bool = False, include_reporter: bool = True):
    labels, dfs = get_data(include_reporter=include_reporter)

    n = len(dfs)

    if same_chart:
        fig, ax = plt.subplots(figsize=(8, 5))
        axes = [ax]
    else:
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

    if same_chart:
        max_x = 0
        for df, label in zip(dfs, labels):
            if df.empty:
                continue

            df["perf"] = df["perf"].iloc[0] / df["perf"]
            x = df["pressure"].to_numpy()
            y = df["perf"].to_numpy()

            x_steps = np.diff(np.sort(np.unique(x)))
            tick_interval = x_steps[x_steps > 0].min()
            x = (x - x.min()) / tick_interval
            max_x = max(max_x, x.max())

            measured, = ax.plot(x, y, "o", markersize=4, label=label)
            if config.USE_INTERPOLATION:
                spline = PchipInterpolator(x, y)
                x_smooth = np.linspace(x.min(), x.max(), 400)
                y_smooth = spline(x_smooth)
                ax.plot(
                    x_smooth,
                    y_smooth,
                    "-",
                    linewidth=1.5,
                    color=measured.get_color(),
                )

        ax.set_xlabel("Number of Competitors")
        ax.set_ylabel("Performance (norm.)")
        ax.set_xticks(np.arange(0, max_x + xpad))
        ax.set_xlim([0, max_x + xpad])
        ax.grid(True)
        ax.legend()
    else:
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


def get_data(include_reporter: bool = True) -> tuple[list[str], list[pd.DataFrame]]:
    parent_dir = pathlib.Path(config.RESULTS_DIR) / "sensitivity"
    csv_paths = []
    labels = []
    
    if parent_dir.is_dir():
        csv_paths = [parent_dir / f for f in os.listdir(parent_dir) if f.endswith(".csv")]
        labels = [p.parts[2].split('_')[1] for p in csv_paths]

    # Add reporter
    if include_reporter:
        reporter_path = pathlib.Path(config.RESULTS_DIR) / "reporter_sensitivity.csv"
        if reporter_path.exists():
            csv_paths += [reporter_path]
            labels += ["reporter"]

    dfs = [pd.read_csv(p, delimiter=",") for p in csv_paths]
    return labels, dfs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--same-chart",
        action="store_true",
        help="Plot all sensitivity series on one chart.",
    )
    parser.add_argument(
        "--no-reporter",
        action="store_true",
        help="Exclude reporter sensitivity data from the plot.",
    )
    args = parser.parse_args()
    draw_sensitivity(
        same_chart=args.same_chart,
        include_reporter=not args.no_reporter,
    )
