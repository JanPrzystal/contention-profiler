import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import config

global_data = {    
    "Baseline c6": [4345.46, 3259.61, 33030.783, ],
}

def draw_times(data, validation: bool = True):
    for key, values in global_data.items():
        data[key] = values

    labels = list(data.keys())
    values = np.array(list(data.values()))  # shape (n_groups, 3)

    x = np.arange(len(labels))
    # width = 0.25

    plt.figure(figsize=(10, 6))

    legend = ['Reporter', 'Contentiousness', 'Sensitivity', 'Validation']
    if validation:
        legend = ['Reporter', 'Contentiousness', 'Sensitivity']

    bottom = np.zeros(len(labels))

    for i in range(values.shape[1]):
        heights = values[:, i] / 3600.0
        plt.bar(x, heights, bottom=bottom, label=legend[i], width=0.5)
        bottom += heights

    plt.xticks(x, labels)
    plt.ylabel("Time (h)")
    plt.legend()
    plt.tight_layout()
    # plt.show()

    image_output_path = f"{config.RESULTS_DIR}/times.png"
    plt.savefig(image_output_path, dpi=300)

if __name__ == "__main__":
    draw_times(data)
