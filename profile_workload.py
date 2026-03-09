import os
import pandas as pd
import time
import logging
from pathlib import Path

import reporter as rp

logger = logging.getLogger(__name__)
from contention_synthesis import Bubble
import constants
from workload import Workload

SENSITIVITY_DIR = Path(constants.RESULTS_DIR) / 'sensitivity'

def _get_sensitivity_data(workload_name: str) -> dict[int, float]:
    res = {}
    workload_file = workload_name.replace(".", "_")
    path = SENSITIVITY_DIR / workload_file / "data.csv"
    if not os.path.exists(path):
        return res
    with open(path, "r+") as f:
        next(f)
        for line in f:
            dial, perf = line.split(", ")
            res[int(dial)] = float(perf)
    return res


def _save_sensitivity_data(workload_name: str, sensitivity: dict[int, float]):
    benchmark_file = workload_name.replace(".", "_")
    path = SENSITIVITY_DIR / f"{benchmark_file}_data.csv"
    with open(path, "w+") as f:
        f.write("footprint_mb, perf\n")
        for k, v in sensitivity.items():
            f.write(f"{k}, {v}\n")


def _profile_sensitivity(workload: Workload) -> str:
    sensitivity = _get_sensitivity_data(workload.name)

    sizes = range(constants.DIAL_START_MB, constants.DIAL_END_MB + constants.DIAL_STEP_MB, constants.DIAL_STEP_MB)
    logger.info(f"profiling sizes {sizes}")

    for size_mb in sizes:
        logger.info(f"profiling size {size_mb}MB")
        
        if size_mb in sensitivity:
            continue
        sensitivity[size_mb] = _profile_sensitivity_dial(workload, size_mb)
        _save_sensitivity_data(workload.name, sensitivity)

def _profile_sensitivity_dial(workload: Workload, size_mb: int) -> float:
    if size_mb == 0:
        logger.info("Profiling in isolation")
        return workload.profile(constants.WORKLOAD_UNDER_PROFILING_CORES)
    bubble = Bubble(size_mb)
    bubble.run()
    try:
        return workload.profile(constants.WORKLOAD_UNDER_PROFILING_CORES)
    finally:
        bubble.stop()

def _profile_contentiousness(workload: Workload, reporter: rp.Reporter):
        workload.run_in_background(constants.WORKLOAD_IN_BACKGROUND_CORES)
        try:
            time.sleep(20)
            return reporter.run(constants.REPORTER_CORES)
        finally:
            workload.stop()

def _save_contentiousness_data(data: dict[str, dict[str,str]]):
    df = pd.DataFrame.from_dict(data, orient="index")
    df.to_csv(f"{constants.RESULTS_DIR}/contentiousness.csv", sep=" ")

def profile_sensitivity(workloads: list[Workload]) -> None:
    
    if not os.path.isdir(SENSITIVITY_DIR):
        os.mkdir(SENSITIVITY_DIR)
    for workload in workloads:
        _profile_sensitivity(workload)
    

def profile_contentiousness(workloads: list[Workload], reporter: rp.Reporter) -> None:
    contentiousness = {}
    for workload in workloads:
        contentiousness[workload.name] = _profile_contentiousness(workload, reporter)
        _save_contentiousness_data(contentiousness)
