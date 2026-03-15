import json
import os
import csv
import time
from tracemalloc import start
from typing import Union, List
from collections import namedtuple
import config
from workload import Workload
from prediction import Prediction
import logging

ValidatedPrediction = namedtuple(
    "ValidatedPrediction", Prediction._fields + ("actual_perf",)
)

def get_key(prediction: Union[Prediction, ValidatedPrediction]) -> str:
    return f"{prediction.app} + {prediction.competitor}"


def read_predictions() -> list[Prediction]:
    with open(f"{config.RESULTS_DIR}/predictions.json", "r") as f:
        data = json.load(f)["predictions"]
        return [
            Prediction(app=p["app"], competitor=p["competitor"], perf=p["perf"])
            for p in data
        ]

def validate_prediction(prediction: Prediction, workload_map: dict[str, Workload]) -> float:
    primary = workload_map[prediction.app]

    competitors = []
    for competitor in prediction.competitor.split(" + "):
        competitors.append(workload_map[competitor])

    # competitor = workload_map[prediction.competitor]

    logging.info(f"Starting profiling for ({primary.name}, {', '.join(c.name for c in competitors)})")
    isolated_perf = primary.profile(config.WORKLOAD_UNDER_PROFILING_CORES)

    # Get cores for background workloads
    start, end = map(int, config.WORKLOAD_IN_BACKGROUND_CORES.split("-"))
    cores = iter(range(start, end + 1))

    # Check if there are enough cores for all competitors
    if len(competitors) > len(cores):
        raise ValueError("Not enough cores for all competitors")

    for competitor, core in zip(competitors, cores):
        competitor.run_in_background(str(core))

    time.sleep(5)
    try:
        perf = primary.profile(config.WORKLOAD_UNDER_PROFILING_CORES)
        return ValidatedPrediction(actual_perf=(isolated_perf / perf), *prediction)
    finally:
        for competitor in competitors:
            competitor.stop()
    

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

def validate_predictions(predictions: List[Prediction], workload_map: dict[str, Workload]):
    # snapshot = read_snapshot()
    with open(VALIDATION_FILE, "a+") as f:
        f.seek(0)

        writer = csv.writer(f, delimiter=",")
        writer.writerow(ValidatedPrediction._fields)

        # f.seek(0, os.SEEK_END)

        for p in predictions:
            key = get_key(p)
            # if key in snapshot:
            #     continue
            row = validate_prediction(p, workload_map)
            logging.info(str(row))
            writerow_and_sync(f, writer, row)

def validate_pair_predictions(applications: List[Workload], competitors: List[Workload]):
    snapshot = read_snapshot()
    predictions = read_predictions()
    workload_map = {w.name: w for w in applications + competitors}
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
            row = validate_prediction(p, workload_map)
            logging.info(str(row))
            writerow_and_sync(f, writer, row)