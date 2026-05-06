import pandas as pd
import logging
import matplotlib.pyplot as plt
import config
import os
import re
import csv

from profiling.contentiousness import inverse_leftmost_exact
from scipy.interpolate import PchipInterpolator

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_validated():
    path = f'{config.RESULTS_DIR}/validated.csv'
    # Read space-separated CSV
    df = pd.read_csv(path, sep=',')
    
    # Calculate % difference: (Prediction - Actual) / Actual * 100
    df['diff_pct'] = ((df['perf'] - df['actual_perf']) / df['actual_perf']) * 100
    
    return df

def get_contentiousness():
    path = f'{config.RESULTS_DIR}/contentiousness.csv'
    df = pd.read_csv(path, sep=',')
    df.columns = ["benchmark", "value"]
    
    return df

def get_sensitivity(benchname):
    path = f'{config.RESULTS_DIR}/sensitivity/{benchname}'
    df = pd.read_csv(path, sep=',', index_col=0)
    
    return df

def contentiousness_lookup(spline, y):
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

if __name__ == '__main__':
    validated = get_validated()
    contentiousness = get_contentiousness()

    validated = validated.set_index(["app", "competitor"])
    contentiousness = contentiousness.set_index(["benchmark"])

    with open("ideal_contentiousness.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["app", "competitor", "competitor contentiousness", "ideal contentiousness", "prediction error"])

        for filename in os.listdir(f'{config.RESULTS_DIR}/sensitivity'):
            # sensitivity = get_sensitivity(filename)
            appname = filename.replace('_data.csv', '')
            appname = re.sub(r'(^\d{3})_', r'\1.', appname)

            # Get interpolated sensitivity
            x = []
            y = []
            spline = None
            with open(f'{config.RESULTS_DIR}/sensitivity/{filename}', 'r') as f:
                reader = csv.reader(f, delimiter=",")
                next(reader)
                for row in reader:
                    x.append(int(row[0]))
                    y.append(float(row[1]))

                spline = PchipInterpolator(x, y)


            for benchmark in os.listdir(f'{config.RESULTS_DIR}/sensitivity'):
                compname = benchmark.replace('_data.csv', '')
                compname = re.sub(r'(^\d{3})_', r'\1.', compname)

                row = validated.loc[(appname, compname)]

                perf = row['actual_perf']

                cont = contentiousness.loc[compname]["value"]

                perf_normal = spline(spline.x[0])
                # log(f"looking up cont for perf {perf_normal * perf} (normal is {perf_normal})")
                needed = contentiousness_lookup(spline, perf_normal / perf)

                error = (row['perf'] - perf) / perf * 100
                writer.writerow([appname, compname, cont, needed, error])
                # log(f"For {appname}, {compname} should have contentiousness {needed}, actually has {cont}")









    