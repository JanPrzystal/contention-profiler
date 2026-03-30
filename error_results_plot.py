import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import config

data = {    
    #c6
    "baseline": [48.71, 13.04, 48.71 + 7.49],
    "1 rand": [51.53, 1.4, 51.53 + 10.83],
    "1 rand (no cactu)": [23.50, 1.4, 23.50 + 4.54],
    "2 mixed": [50.60, 1.60, 50.60 + 33.79],
    "2 mixed (no cactu)": [21.95, 1.60, 21.95 + 13.00],
}

legend_labels = ["Max Absolute Error", "Absolute Mean Error", "Range [pp]"]

if __name__ == "__main__":
    labels = list(data.keys())
    values = np.array(list(data.values()))  # shape (n_groups, 3)

    x = np.arange(len(labels))
    width = 0.25

    plt.figure(figsize=(10, 6))

    for i in range(values.shape[1]):
        plt.bar(x + i * width, values[:, i], width, label=legend_labels[i])

    plt.axhline(0, color='black', linewidth=1)
    plt.xticks(x + width, labels)
    plt.ylabel("Error (%)")
    plt.legend()
    plt.tight_layout()
    # plt.show()

    image_output_path = f"{config.RESULTS_DIR}/errors.png"
    plt.savefig(image_output_path, dpi=300)