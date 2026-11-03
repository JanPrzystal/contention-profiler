import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
import config

global_data = {    
    "Pair Baseline": [4345.46, 3259.61, 33030.783, ],
}

thickness = 0.5

FONTSIZE_SMALL = 12
FONTSIZE_LARGE = 14

def draw_times(
    data,
    validation: bool = True,
    include_baseline: bool = True,
    horizontal: bool = True,
):
    if include_baseline:
        for key, values in global_data.items():
            data[key] = values

    labels = [label.replace(" ", "\n") for label in data.keys()]
    values = np.array(list(data.values()))  # shape (n_groups, 3)

    x = np.arange(len(labels))
    # width = 0.25

    figsize = (8, 2 + 1.2 * len(data)) if horizontal else (1 + 4 * len(data), 6)
    plt.figure(figsize=figsize)
    plt.title("Profiling Time")

    legend = ['Reporter', 'Contentiousness', 'Sensitivity', 'Validation']
    if validation:
        legend = ['Reporter', 'Contentiousness', 'Sensitivity']

    bottom = np.zeros(len(labels))

    for i in range(values.shape[1]):
        durations = values[:, i] / 3600.0
        if horizontal:
            plt.barh(x, durations, left=bottom, label=legend[i], height=thickness)
        else:
            plt.bar(x, durations, bottom=bottom, label=legend[i], width=thickness)
        bottom += durations

    if horizontal:
        plt.yticks(x, labels, rotation=0, fontsize=FONTSIZE_LARGE, va='center')
        plt.xlabel("Time (h)", fontsize=FONTSIZE_LARGE)
    else:
        plt.xticks(x, labels, fontsize=FONTSIZE_LARGE)
        plt.ylabel("Time (h)", fontsize=FONTSIZE_LARGE)
    plt.legend()
    plt.tight_layout()
    # plt.show()

    image_output_path = f"{config.RESULTS_DIR}/times.png"
    plt.savefig(image_output_path, dpi=300)

if __name__ == "__main__":
    draw_times(global_data)
