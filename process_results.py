import sys
import zipfile
import pandas as pd
from analysis.error_results_plot import draw_errors
from analysis.time_chart import draw_times

from experiment_setup.log import log, setup_logging


zip_paths = ["results_2rand_alternating_pair.zip", "results_2rand_alternating_pair_nointerpolation.zip"]

results = []

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


    return {
        "min_error": {"app": min_row["app"], "competitors": min_row["competitor"], "error": min_row["error"].item()},
        "max_error": {"app": max_row["app"], "competitors": max_row["competitor"], "error": max_row["error"].item()},
        "median": median.item(),
        "abs_median": abs_median.item()
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
        errors_data[result['name']] = [max(min_error, max_error), result['abs_median_error'], abs(min_error - max_error)]

        # Get time data
        times = result["timings"]
        time_data[result['name']] = [times['reporter'], times['contentiousness'], times['sensitivity']]

    draw_errors(errors_data)

    draw_times(time_data, False)

if __name__ == "__main__":
    setup_logging()
    zip_paths = sys.argv[1:] if len(sys.argv) > 1 else zip_paths
    process_zip_files(zip_paths)