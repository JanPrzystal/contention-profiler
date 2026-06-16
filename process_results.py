import sys
import zipfile
import pandas as pd
from analysis.error_results_plot import draw_errors
from analysis.plot_time import draw_times

from experiment_setup.log import log, setup_logging


# zip_paths = ["results_2rand_alternating_pair.zip", "results_2rand_alternating_pair_nointerpolation.zip"]

results = []

def read_worst_errors(file, N=10):
    with zipfile.ZipFile(file) as z:
        for name in z.namelist():
            if name.endswith("validated.csv"):
                with z.open(name) as f:
                    df = pd.read_csv(f)
                    df = df[~df["app"].str.contains("607.cactuBSSN_s", na=False)]

                    df['error'] = ((df['perf'] - df['actual_perf']) / df['actual_perf']) * 100
                    df['abs_error'] = df['error'].abs()
                    df['competitors'] = df['competitor'].apply(lambda x: len(x.split(" + ")) if pd.notna(x) else 0)

                    top_n = df.sort_values(by="abs_error", ascending=False).head(N)
                    return top_n

def handle_validation_csv(file):
    df = pd.read_csv(file)
    # log(df.head())

    # remove cactu
    df = df[~df["app"].str.contains("607.cactuBSSN_s", na=False)]

    df['error'] = ((df['perf'] - df['actual_perf']) / df['actual_perf']) * 100
    df['abs_error'] = df['error'].abs()

    min_row = df.loc[df["error"].idxmin()]
    max_row = df.loc[df["error"].idxmax()]

    # df_sorted = df.sort_values(by="error")  
    median = df["error"].median()
    # df_sorted = df.sort_values(by="abs_error")  
    abs_median = df["abs_error"].median()
    abs_95 = df["abs_error"].quantile(0.95)

    return {
        "min_error": {"app": min_row["app"], "competitors": min_row["competitor"], "error": min_row["error"].item()},
        "max_error": {"app": max_row["app"], "competitors": max_row["competitor"], "error": max_row["error"].item()},
        "median": median.item(),
        "abs_median": abs_median.item(),
        "abs_95": abs_95.item()
        }


def handle_timing(file):
    timings = dict()
    for line in file:
        line = line.decode("utf-8").strip()
        name = line.split("=")[0].strip()
        score = float(line.split("=")[1].strip()[:-1])
        timings[name] = score

    return timings

def process_zip_files(zip_paths):
    global results

    for zip_path in zip_paths:
        result = {"name": zip_path.split(".zip")[0]}
        with zipfile.ZipFile(zip_path) as z:
            for name in z.namelist():
                if name.endswith("validated.csv"):
                    with z.open(name) as f:
                        validation_results = handle_validation_csv(f)
                        result['min_error'] = validation_results["min_error"]["error"]
                        result['max_error'] = validation_results["max_error"]["error"]
                        result['median_error'] = validation_results["median"]
                        result['abs_median_error'] = validation_results["abs_median"]
                        result['abs_95_error'] = validation_results["abs_95"]
                elif name.endswith("timings.txt"):
                    with z.open(name) as f:
                        result["timings"] = handle_timing(f)

        results.append(result)
        log(result)

    errors_data = {}
    time_data = {}

    for result in results:
        # Get errors data
        max_error = result['max_error']
        min_error = result['min_error']
        min_error = abs(min_error)
        errors_data[result['name']] = [
            max(min_error, max_error),
            result['abs_95_error'],
            result['abs_median_error'],
            abs(min_error) + abs(max_error)
        ]

        # Get time data
        times = result["timings"]
        time_data[result['name']] = [times['reporter'], times['contentiousness'], times['sensitivity']]

    return errors_data, time_data


if __name__ == "__main__":
    setup_logging()

    start_arg = 1
    include_baseline = False
    if sys.argv[1] == "--baseline":
        include_baseline = True
        start_arg = 2

    zip_paths = sys.argv[start_arg:] if len(sys.argv) > start_arg else ""
    errors_data, time_data = process_zip_files(zip_paths)

    draw_errors(errors_data, include_baseline)
    draw_times(time_data, include_baseline=include_baseline)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', 1000)

    for file in zip_paths:
        errors = read_worst_errors(file, 25)
        log(f"Worst errors for {file}:\n{errors}")