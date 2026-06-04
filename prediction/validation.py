import json
import os
import csv
import random
import time
from tracemalloc import start
from typing import Union, List
from collections import namedtuple
import config
from experiment_setup.workload import Workload, run_background_workload, stop_process
from prediction.prediction import Prediction

from prediction.prediction import get_sensitivity

from experiment_setup.log import log, INFO, WARNING, DEBUG

ValidatedPrediction = namedtuple(
    "ValidatedPrediction", Prediction._fields + ("actual_perf",)
)

def get_key(prediction: Union[Prediction, ValidatedPrediction]) -> str:
    return f"{prediction.app} + {prediction.competitor}"


def read_predictions() -> list[Prediction]:
    with open(f"{config.RESULTS_DIR}/predictions.json", "r") as f:
        data = json.load(f)["predictions"]
        return [
            Prediction(app=p["app"], competitor=p["competitor"], perf=p["perf"], contentiousness=p["contentiousness"])
            for p in data
        ]

def validate_prediction(prediction: Prediction, workloads: List[Workload]) -> ValidatedPrediction:
    # Get the tested app as a Workload object
    primary = next((w for w in workloads if w.name == prediction.app), None)

    competitors = []
    for competitor in prediction.competitor.split(" + "):
        competitor_workload = next((w for w in workloads if w.name == competitor), None)
        if competitor_workload:
            competitors.append(competitor_workload)

    log(f"Starting profiling for ({primary.name} with {', '.join(c.name for c in competitors)})")
    
    isolated_perf = get_sensitivity(primary.name)(0)

    # Get cores for background workloads
    # start, end = map(int, config.WORKLOAD_IN_BACKGROUND_CORES.split("-"))
    # ncores = end - start + 1
    # cores = iter(range(start, end + 1))

    # Check if there are enough cores for all competitors
    # if len(competitors) > ncores:
    #     raise ValueError("Not enough cores for all competitors")

    # Start competitors in the background
    background_processes = []
    for competitor in competitors:
        background_processes.append(run_background_workload(competitor))

    time.sleep(config.WORKLOAD_WARMUP_TIME)
    try:
        perf = primary.profile()
        return ValidatedPrediction(actual_perf=(isolated_perf / perf), *prediction)
    finally:
        for process in background_processes:
            stop_process(process)
        time.sleep(config.WORKLOAD_WIND_DOWN_TIME)

def read_snapshot() -> dict[str, ValidatedPrediction]:
    if not os.path.exists(VALIDATION_FILE):
        return {}
    with open(VALIDATION_FILE, "r") as f:
        data = {}
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            vp = ValidatedPrediction(**row)
            data[get_key(vp)] = vp
        return data

VALIDATION_FILE = f"{config.RESULTS_DIR}/validated.csv"


def writerow_and_sync(f, writer, row):
    writer.writerow(row)
    f.flush()  # flush Python buffers to OS
    os.fsync(f.fileno())  # force OS to write to disk

def validate_pair_predictions(applications: List[Workload], competitors: List[Workload], predictions: List[Prediction]) -> List[ValidatedPrediction]:
    snapshot = read_snapshot()
    # predictions = read_predictions()

    validated = []

    for p in predictions:
        row = validate_prediction(p, applications + competitors)
        validated.append(row)

    return validated

    with open(VALIDATION_FILE, "a+") as f:
        f.seek(0)
        is_empty = f.read(1) == ""

        writer = csv.writer(f, delimiter=",")
        if is_empty:
            writer.writerow(ValidatedPrediction._fields)

        f.seek(0, os.SEEK_END)

        for p in predictions:
            key = get_key(p)
            if key in snapshot:
                continue
            row = validate_prediction(p, applications + competitors)
            log(str(row), INFO)
            writerow_and_sync(f, writer, row)

rng = random.Random(config.RANDOM_SEED)
def rng_sample(predictions: List[Prediction], n: int) -> List[Prediction]:
    return rng.sample(predictions, min(n, len(predictions)))

def choose_predictions(predictions: dict[int, List[Prediction]], max: int = config.VALIDATIONS) -> List[Prediction]:
    sample_size = max #min(max, len(predictions))

    max_competitors = config.MAX_COMPETITORS

    predictions_list = []

    subsample_size = sample_size // max_competitors

    log(f"Sampling {subsample_size} predictions for each competitor count (1 to {max_competitors})", DEBUG)

    for i in range(1, max_competitors + 1):
        if i not in predictions:
            log(f"No predictions found for {i} competitors. Available keys: {list(predictions.keys())}", WARNING)
        else:
            # Sample random predictions with i competitors
            sample = rng_sample(predictions[i], subsample_size)
            
            # Get top contentiousness predictions with i competitors
            top_cnt = []
            seen = set()
            for pred in sorted(predictions[i], key=lambda x: x.contentiousness, reverse=True):
                if pred.contentiousness in seen:
                    continue
                seen.add(pred.contentiousness)
                top_cnt.append(pred)
                if len(top_cnt) >= config.TOP_CNT_VAlIDATIONS:
                    break


            log(f"Sampled {len(sample) + len(top_cnt)} predictions with {i} competitors", INFO)
            predictions_list.extend(sample)
            predictions_list.extend(top_cnt)

    return predictions_list

def validate_predictions(predictions: dict[int, List[Prediction]], workloads: List[Workload]) -> List[ValidatedPrediction]:
    validated_predictions = []

    sampled_predictions = choose_predictions(predictions, config.VALIDATIONS)

    counter = 0
    for pred in sampled_predictions:
        counter += 1
        log(f"Validating prediction {counter}/{len(sampled_predictions)}")
        validated_predictions.append(validate_prediction(pred, workloads))

    return validated_predictions

def save_validated_predictions(validated_predictions: List[ValidatedPrediction]) -> None:
    with open(f"{config.RESULTS_DIR}/validated.csv", "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(ValidatedPrediction._fields)
        for pred in validated_predictions:
            row = [str(c) for c in list(pred._asdict().values())]
            writer.writerow(row)
