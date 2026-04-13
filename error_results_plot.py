import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import config

data = {    
    #c6
    "4MB interval (no cactu)": [18.27, 2.13, 18.27 + 15.54],
    "8MB interval (no cactu)": [23.94, 2.11, 23.94 + 13.79],
    "16MB interval": [18.46, 1.95, 18.46 + 13.47],
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