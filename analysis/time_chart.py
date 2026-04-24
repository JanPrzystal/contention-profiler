import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import config

data = {    
    #c6
    # "c6": [4337.627, 3165.722, 33097.876, 70637.009 - 40601.753],
    # "current (1 rand)": [668.073, 1082.009, 11470.311, 45232.757 - 13220.949],
    # "current (2 mixed)": [576.676, 1351.268, 6007.805, 39982.873 - 7936.296],
    "b8 4MB interval": [561.517, 623.728, 20292.338],
    "b8 16MB interpolation": [182.062, 635.684, 7096.834],
    "c6 4MB interval": [587.2, 730.2, 13794.9],
    "c6 16MB interpolation": [168.553, 727.699, 4868.333], #99th 16.4
}

def draw_times(data, validation: bool = True):
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
