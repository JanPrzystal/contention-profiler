import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import config

data = {
    "1MB interval": [6.94, 1.90, 6.94 + 6.63],
    "4MB interval": [6.96, 2.0, 6.96 + 4.85],
    "20 R. repetitions": [16.41, 1.98, 16.41 + 8.77],
    "100 R. repetitions": [11.30, 1.44, 7.66 + 6.53],
    "50 rr 2MB": [7.66, 1.40, 7.66 + 6.99],
    # "1rand": [4.62, 0.94, 13.18 + 12.27],
    # "2rand": [29.49, 5.80, 29.49 + 14.23],
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