import math
import csv

import config
from scipy.interpolate import PchipInterpolator
import numpy as np


def get_reporter_sensitivity_spline() -> PchipInterpolator:
    x = []
    y = []
    with open(f'{config.RESULTS_DIR}/reporter_sensitivity.csv', 'r') as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)
        for row in reader:
            x.append(int(row[0]))
            y.append(float(row[1]))

    return PchipInterpolator(x, y)

def inverse_leftmost_exact(spline: PchipInterpolator, y: float) -> float | None:
    for c, x0, x1 in zip(spline.c.T, spline.x[:-1], spline.x[1:]):
        coeffs = c.copy()
        coeffs[-1] -= y

        roots = np.roots(coeffs)
        roots = roots[np.isreal(roots)].real + x0
        roots = roots[(roots >= x0) & (roots <= x1)]

        if len(roots) > 0:
            return roots.min()

    return None

# Sensitivity lookup used for contentiousness calculation without interpolation
def construct_sensitivity_lookup() -> list[tuple[float, int]]:
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

# Uses lookup without interpolation to find the contentiousness
def find_dial(sample_perf: float, lookup: list[tuple[float, int]]) -> int:
    min_diff = math.inf
    res = -1
    for perf, dial in lookup:
        diff = abs(sample_perf - perf)
        if diff < min_diff:
            res = dial
            min_diff = diff
    return res


def contentiousness_lookup(y: float) -> float | None:
    if not config.USE_INTERPOLATION:
        # Use lookup table instead of interpolation
        lookup = construct_sensitivity_lookup()
        contentiousness = find_dial(y, lookup)
        return float(contentiousness)

    # Uses interpolation to find the contentiousness for a given performance value
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


contentiousness = None
# Used for simple contentiousness
def read_contentiousness(force_update=True) -> dict[str, float]:
    global contentiousness
    if not force_update and contentiousness:
        return contentiousness
    
    contentiousness = {}
    with open(f"{config.RESULTS_DIR}/contentiousness.csv", 'r') as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)
        for row in reader:
            contentiousness[row[0]] = float(row[1])
    return contentiousness

# Returns the added contentiousness data for a given application
def read_application_contentiousness(name: str) -> dict[int, float]:
    res = {}
    path = f"{config.RESULTS_DIR}/contentiousness/{name.replace('.', '_')}_contentiousness.csv"
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)
        for row in reader:
            dial = int(row[0])
            cnt = float(row[1])
            res[dial] = cnt
    return res
