import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import pathlib
from scipy.interpolate import PchipInterpolator

import config

import contentiousness
import prediction

reporter_sensitivity_spline = contentiousness.get_reporter_sensitivity_spline()

reporter_sensitivity_lookup = contentiousness.construct_sensitivity_lookup()

def get_validated_df():
    path = f'{config.RESULTS_DIR}/validated.csv'
    # Read space-separated CSV
    df = pd.read_csv(path, sep=',')
    return df

def get_contentiousness():
    path = f'{config.RESULTS_DIR}/contentiousness.csv'
    df = pd.read_csv(path, sep=',')
    df.columns = ["benchmark", "value"]
    return df

def interpolated_to_base_contentiousness(cont):
    interp_perf = reporter_sensitivity_spline(cont)
    base_cont = contentiousness.find_dial(interp_perf, reporter_sensitivity_lookup)
    return base_cont

if __name__ == '__main__':
    
    contentiousnesses = get_contentiousness()
    validated = get_validated_df()

    for benchmark, cont in contentiousnesses.itertuples(index=False):

        # Get the sensitivity of the main app
        sensitivity = prediction.get_sensitivity(benchmark)

        # print(f"For benchmark {benchmark}, reporter sensitivity lookup gives {base_cont} for contentiousness {cont}")

        # construct predictions for all competing benchmarks
        for _, row in validated.iterrows():
            if row['app'] == benchmark:
                validated_perf = row['actual_perf']

                competitor = row['competitor']
                competitor_cont = float(interpolated_to_base_contentiousness(row['contentiousness']))

                print(f"Benchmark: {benchmark}, Competitor: {competitor}, Actual Performance: {validated_perf}, InterpolatedContentiousness: {row['contentiousness']}, BaseContentiousness: {competitor_cont}")

                pred_norm = sensitivity(0) / sensitivity(competitor_cont)
                interp_pred = row['perf']
                print(f"  Validated prediction: {validated_perf}, interpolation prediction {interp_pred}, base prediction {pred_norm}")
                print(f"  Interpolation error: {abs(interp_pred - validated_perf) / validated_perf * 100:.2f}%, Base error: {abs(pred_norm - validated_perf) / validated_perf * 100:.2f}%")


    

