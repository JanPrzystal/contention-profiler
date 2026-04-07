import logging
import matplotlib.pyplot as plt
import math
import csv

import config
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq
import numpy as np

logger = logging.getLogger(__name__)


def get_reporter_sensitivity_spline():
    x = []
    y = []
    with open(f'{config.RESULTS_DIR}/reporter_sensitivity.csv', 'r') as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)
        for row in reader:
            x.append(int(row[0]))
            y.append(float(row[1]))

    return PchipInterpolator(x, y)

def inverse_leftmost_exact(spline, y):
    for c, x0, x1 in zip(spline.c.T, spline.x[:-1], spline.x[1:]):
        coeffs = c.copy()
        coeffs[-1] -= y

        roots = np.roots(coeffs)
        roots = roots[np.isreal(roots)].real + x0
        roots = roots[(roots >= x0) & (roots <= x1)]

        if len(roots) > 0:
            return roots.min()

    return None

def contentiousness_lookup(y):
    spline = get_reporter_sensitivity_spline()

    contentiousness = inverse_leftmost_exact(spline, y)
    if contentiousness is None:
        x_min, x_max = spline.x[0], spline.x[-1]
        if y < spline(x_min):
            contentiousness = x_min
        elif y > spline(x_max):
            contentiousness = x_max
        else:
            raise ValueError("Unexpected case: y is within the range of the spline but no root was found.")

    return contentiousness


def construct_sensitivity_lookup():
    res = []
    with open(f'{config.RESULTS_DIR}/reporter_sensitivity.csv', 'r') as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)
        for row in reader:
            perf = float(row[1])
            # We perform reverse lookup, that is we find dial from performance
            dial = int(row[0])
            res.append((perf, dial))
    return res

def find_dial(sample_perf: float, lookup: list[tuple[float, int]]) -> int:
    min_diff = math.inf
    res = -1
    for perf, dial in lookup:
        diff = abs(sample_perf - perf)
        if diff < min_diff:
            res = dial
            min_diff = diff
    return res

def get_contentiousness():
    res = {}
    with open(f"{config.RESULTS_DIR}/contentiousness.csv", 'r') as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)
        for row in reader:
            res[row[0]] = float(row[1])
    return res

def save_contentiousness(scores: dict[float, int]):
    with open(f"{config.RESULTS_DIR}/contentiousness_scores.csv", "w") as f:
        for bench, score in scores.items():
            f.write(f"{bench},{score}\n")

def generate_scores():
    # lookup = construct_sensitivity_lookup()
    cont = get_contentiousness()
    data = {}
    for bench, perf in cont.items():
        # dial = find_dial(perf, lookup)
        data[bench] = perf

    logger.info(str(data))
    save_contentiousness(data)

    # Extract keys and values
    labels = list(data.keys())
    values = list(data.values())

    values, labels = zip(*sorted(zip(values, labels)))

    # Create the column chart
    plt.figure(figsize=(20, 12))
    bars = plt.bar(labels, values)

    plt.tick_params(axis='x', length=0)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2, 
            height + 0.2, 
            f'{height:.1f}', 
            ha='center', va='bottom'
        )

    # Labels and title
    plt.xlabel('SPEC CPU 2017 workload')
    plt.ylabel('Approximate MemBW benchmark footprint (MB)')

    # Display the chart
    plt.tight_layout()
    output_path = f"{config.RESULTS_DIR}/contentiousness.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_scores()
