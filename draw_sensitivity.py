import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import pathlib

import constants

xpad = 8

def main():
    labels, dfs = get_data()
    xlim = max(labels) + xpad

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
        ax.plot(df["footprint_mb"], df["perf"], marker="o", markersize=4)
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
    image_output_path = pathlib.Path(constants.RESULTS_DIR) / "sensitivity.png"
    plt.savefig(image_output_path, dpi=300)
    plt.close()


def get_data() -> tuple[list[str], list[pd.DataFrame]]:
    parent_dir = pathlib.Path(constants.RESULTS_DIR) / "sensitivity"
    csv_paths = [parent_dir / f for f in os.listdir(parent_dir) if f.endswith(".csv")]
    labels = [p.parts[3].split('_')[1] for p in csv_paths]
    dfs = [pd.read_csv(p, delimiter=" ") for p in csv_paths]
    return labels, dfs


if __name__ == "__main__":
    main()
