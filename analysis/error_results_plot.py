import matplotlib.pyplot as plt
import numpy as np

import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import config

data = {    
    #c6
    # "4MB interval (no cactu)": [18.27, 2.13, 18.27 + 15.54],
    # "8MB interval (no cactu)": [23.94, 2.11, 23.94 + 13.79],
    # "16MB interval": [18.46, 1.95, 18.46 + 13.47],
    "b8 4MB interval": [16.4, 1.5, 16.4 + 15.8],
    "b8 16MB interpolation": [23.0, 3.1, 23.0 + 21.4],
    "c6 4MB interval": [23.9, 2.0, 23.9 + 13.4],
    "c6 16MB interpolation": [21.8, 2.3, 21.8 + 12.2], #99th 16.4
}

legend_labels = [
    # "Interpolation better", 
    # "No interpolation better", 
    # "Equal"
    "Max Absolute Error", 
    # "Absolute Mean Error", 
    "Mean Absolute Error", 
    "Range [pp]"
    ]

def draw_errors(data):
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

if __name__ == "__main__":
    draw_errors(data)