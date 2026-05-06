import json
import os
import csv
import random
import time
from tracemalloc import start
from typing import Union, List
from collections import namedtuple
import config
from experiment_setup.workload import Workload
from prediction.prediction import Prediction
import logging
from experiment_setup.spec import run_background_benchmark, stop_benchmark
from prediction.prediction import get_sensitivity

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

    logging.info(f"Starting profiling for ({primary.name} with {', '.join(c.name for c in competitors)})")
    
    isolated_perf = get_sensitivity(primary.name)(0) 
        # primary.profile(config.WORKLOAD_UNDER_PROFILING_CORES)

    # Get cores for background workloads
    start, end = map(int, config.WORKLOAD_IN_BACKGROUND_CORES.split("-"))
    ncores = end - start + 1
    cores = iter(range(start, end + 1))

    # Check if there are enough cores for all competitors
    if len(competitors) > ncores:
        raise ValueError("Not enough cores for all competitors")

    # Start competitors in the background
    background_processes = []
    for competitor, core in zip(competitors, cores):
        background_processes.append(run_background_benchmark(competitor.name, str(core), competitor.size))
        # competitor.run_in_background(str(core))

    time.sleep(config.WORKLOAD_WARMUP_TIME)
    try:
        perf = primary.profile(config.WORKLOAD_UNDER_PROFILING_CORES)
        return ValidatedPrediction(actual_perf=(isolated_perf / perf), *prediction)
    finally:
        for process in background_processes:
            stop_benchmark(process)
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

def validate_pair_predictions(applications: List[Workload], competitors: List[Workload]):
    snapshot = read_snapshot()
    predictions = read_predictions()

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
            logging.info(str(row))
            writerow_and_sync(f, writer, row)

def choose_predictions(predictions: List[Prediction]) -> List[Prediction]:
    sample_size = min(config.VALIDATIONS, len(predictions))
    return random.sample(predictions, sample_size)

def validate_predictions(predictions: List[Prediction], competitors: List[Workload]) -> List[ValidatedPrediction]:
    validated_predictions = []

    sampled_predictions = choose_predictions(predictions)

    for pred in sampled_predictions:
        validated_predictions.append(validate_prediction(pred, competitors))

    return validated_predictions

def save_validated_predictions(validated_predictions: List[ValidatedPrediction]) -> None:
    with open(f"{config.RESULTS_DIR}/validated.csv", "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(ValidatedPrediction._fields)
        for pred in validated_predictions:
            row = [str(c) for c in list(pred._asdict().values())]
            writer.writerow(row)
