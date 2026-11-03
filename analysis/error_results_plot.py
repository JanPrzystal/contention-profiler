import matplotlib.pyplot as plt
import numpy as np

import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import config

global_data = {    
    "Pair Baseline": [16.2, 7.17, 0.98, 16.2 + 10.4],
}

legend_labels = [
    "Max Absolute Error", 
    "95th Percentile Absolute Error",
    "Median Absolute Error", 
    "Range [pp]"
    ]

default_colors = ["#1a6AAA", "#ff7f0e", "#2ca02c", "#b94444f4"]

FONTSIZE_SMALL = 11
FONTSIZE_LARGE = 14

def draw_errors(
    data: dict[str, list[float]],
    include_baseline: bool = True,
    colors: list[str] = default_colors,
    horizontal: bool = False,
) -> None:
    if include_baseline:
        for key, values in global_data.items():
            data[key] = values

    labels = list(name.replace("⁄", "/") for name in data.keys())
    values = np.array(list(data.values()))  # shape (n_groups, n_metrics)
    if colors is not None and len(colors) != values.shape[1]:
        raise ValueError(f"Expected {values.shape[1]} colors, received {len(colors)}")

    positions = np.arange(len(labels))
    width = 0.2

    figsize = (8, 3 + 1.0 * len(data)) if horizontal else (4 + 2 * len(data), 5)
    plt.figure(figsize=figsize)
    plt.title("Prediction Errors")

    for i in range(values.shape[1]):
        bar_kwargs = {"color": colors[i]} if colors is not None else {}
        if horizontal:
            rects = plt.barh(
                positions + i * width,
                values[:, i],
                height=width,
                label=legend_labels[i],
                **bar_kwargs,
            )
        else:
            rects = plt.bar(
                positions + i * width,
                values[:, i],
                width,
                label=legend_labels[i],
                **bar_kwargs,
            )

        for rect in rects:
            if horizontal:
                value = rect.get_width()
                plt.annotate(
                    f"{value:.2f}%",
                    xy=(value, rect.get_y() + rect.get_height() / 2),
                    xytext=(3 if value >= 0 else -3, 0),
                    textcoords="offset points",
                    ha="left" if value >= 0 else "right",
                    va="center",
                    fontsize=FONTSIZE_SMALL,
                )
            else:
                value = rect.get_height()
                plt.annotate(
                    f"{value:.2f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, value),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=FONTSIZE_SMALL,
                )

    tick_positions = positions + width * (values.shape[1] - 1) / 2
    if horizontal:
        plt.axvline(0, color="black", linewidth=1)
        plt.yticks(tick_positions, labels, fontsize=FONTSIZE_LARGE)
        plt.xlabel("Error (%)", fontsize=FONTSIZE_LARGE)
    else:
        plt.axhline(0, color="black", linewidth=1)
        plt.xticks(tick_positions, labels, fontsize=FONTSIZE_LARGE)
        plt.ylabel("Error (%)", fontsize=FONTSIZE_LARGE)
        lower, upper = plt.ylim()
        plt.ylim(top=upper + 0.02 * (upper - lower))

    plt.tick_params(axis="y", labelsize=FONTSIZE_SMALL)
    plt.tick_params(axis="x", labelsize=FONTSIZE_LARGE)
    plt.legend(loc='upper left') #bbox_to_anchor=(1.0, 1.0)
    plt.tight_layout()

    image_output_path = f"{config.RESULTS_DIR}/errors.png"
    plt.savefig(image_output_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    draw_errors(global_data)