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

def draw_errors(data: dict[str, list[float]], include_baseline: bool = True) -> None:
    if include_baseline:
        for key, values in global_data.items():
            data[key] = values

    labels = list(data.keys())
    values = np.array(list(data.values()))  # shape (n_groups, n_metrics)

    x = np.arange(len(labels))
    width = 0.18

    plt.figure(figsize=(3 + 3*len(data), 6))
    plt.title("Prediction Errors")

    for i in range(values.shape[1]):
        rects = plt.bar(x + i * width, values[:, i], width, label=legend_labels[i])

        # Add numeric labels on top of each bar
        for rect in rects:
            height = rect.get_height()
            plt.annotate(
                f"{height:.2f}%",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.axhline(0, color='black', linewidth=1)
    plt.xticks(x + width * (values.shape[1] - 1) / 2, labels)
    plt.ylabel("Error (%)")
    plt.legend()
    plt.tight_layout()
    # plt.show()

    image_output_path = f"{config.RESULTS_DIR}/errors.png"
    plt.savefig(image_output_path, dpi=300)

if __name__ == "__main__":
    draw_errors(global_data)