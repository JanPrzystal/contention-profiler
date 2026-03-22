import os
import pandas as pd
import time
import logging
from pathlib import Path

import reporter as rp

logger = logging.getLogger(__name__)
from contention_synthesis import Bubble
import config
from workload import Workload

import contentiousness as cnt

SENSITIVITY_DIR = Path(config.RESULTS_DIR) / 'sensitivity'

def _get_sensitivity_data(workload_name: str) -> dict[int, float]:
    res = {}
    workload_file = workload_name.replace(".", "_")
    path = SENSITIVITY_DIR / workload_file / "data.csv"
    if not os.path.exists(path):
        return res
    with open(path, "r+") as f:
        next(f)
        for line in f:
            dial, perf = line.split(",")
            res[int(dial)] = float(perf)
    return res


def _save_sensitivity_data(workload_name: str, sensitivity: dict[int, float]):
    benchmark_file = workload_name.replace(".", "_")
    path = SENSITIVITY_DIR / f"{benchmark_file}_data.csv"
    with open(path, "w+") as f:
        f.write("footprint_mb,perf\n")
        for k, v in sensitivity.items():
            f.write(f"{k},{v}\n")


def _profile_sensitivity(workload: Workload) -> str:
    sensitivity = _get_sensitivity_data(workload.name)

    sizes = range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB)
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
        return workload.profile(config.WORKLOAD_UNDER_PROFILING_CORES)
    bubble = Bubble(size_mb, config.N_BUBBLES)
    bubble.run()
    try:
        return workload.profile(config.WORKLOAD_UNDER_PROFILING_CORES)
    finally:
        bubble.stop()

def _profile_contentiousness(workload: Workload, reporter: rp.Reporter):
        core = config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0]
        workload.run_in_background(core)
        try:
            time.sleep(10)
            score = reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)
            return cnt.contentiousness_lookup(score)
        finally:
            workload.stop()

def _save_contentiousness_data(data: dict[str, dict[str,str]]):
    df = pd.DataFrame.from_dict(data, orient="index")
    df.to_csv(f"{config.RESULTS_DIR}/contentiousness.csv", sep=",")

def profile_sensitivity(workloads: list[Workload]) -> None:
    
    if not os.path.isdir(SENSITIVITY_DIR):
        os.mkdir(SENSITIVITY_DIR)
    for workload in workloads:
        _profile_sensitivity(workload)
        time.sleep(1)
    

def profile_contentiousness(workloads: list[Workload], reporter: rp.Reporter) -> None:
    contentiousness = {}
    max_contentiousness = 0
    # lookup = cnt.construct_sensitivity_lookup()

    for workload in workloads:
        if not workload.name:
            continue
        time.sleep(1)

        contentiousness[workload.name] = _profile_contentiousness(workload, reporter)
        logger.info(f"{workload.name} contentiousness: {contentiousness[workload.name]}")
        _save_contentiousness_data(contentiousness)
        if contentiousness[workload.name] > max_contentiousness:
            max_contentiousness = contentiousness[workload.name]
    
    logger.info(f"MaxContentiousness: {max_contentiousness}")
    return max_contentiousness
