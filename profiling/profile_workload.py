import os
import pandas as pd
import time
import logging
from pathlib import Path

import experiment_setup.reporter as rp
import experiment_setup.workload as workload

logger = logging.getLogger(__name__)
from experiment_setup.contention_synthesis import Bubble
import config
from experiment_setup.workload import Workload

import profiling.contentiousness as cnt

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


def _save_sensitivity_data(workload_name: str, sensitivity: dict[int, float]) -> None:
    benchmark_file = workload_name.replace(".", "_")
    path = SENSITIVITY_DIR / f"{benchmark_file}_data.csv"
    with open(path, "w+") as f:
        f.write("footprint_mb,perf\n")
        for k, v in sensitivity.items():
            f.write(f"{k},{v}\n")


def _profile_sensitivity(workload: Workload) -> None:
    sensitivity = _get_sensitivity_data(workload.name)

    sizes = range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB)
    logger.info(f"profiling sizes {sizes}")

    for size_mb in sizes:
        logger.info(f"profiling size {size_mb}MB")
        
        if size_mb in sensitivity:
            continue
        sensitivity[size_mb] = _profile_sensitivity_dial(workload, size_mb, config.N_BUBBLES)
        time.sleep(config.WORKLOAD_WIND_DOWN_TIME)

    _save_sensitivity_data(workload.name, sensitivity)

def _profile_sensitivity_dial(workload: Workload, size_mb: int, nproc: int) -> float:
    if size_mb == 0:
        logger.info("Profiling in isolation")
        return workload.profile(config.WORKLOAD_UNDER_PROFILING_CORES)
    bubble = Bubble(size_mb, nproc)
    bubble.run_in_background()

    time.sleep(config.WORKLOAD_WARMUP_TIME)
    
    try:
        return workload.profile(config.WORKLOAD_UNDER_PROFILING_CORES)
    finally:
        bubble.stop()

def _profile_contentiousness(workload: Workload, reporter: rp.Reporter) -> float:
        core = config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0]
        workload.run_in_background(core)
        try:
            time.sleep(config.WORKLOAD_WARMUP_TIME)
            score = reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)
            return cnt.contentiousness_lookup(score)
        finally:
            workload.stop()

def _save_contentiousness_data(data: dict[str,float]) -> None:
    csv_data = {"application": list(data.keys()), "contentiousness": list(data.values())}
    df = pd.DataFrame(csv_data)
    df.to_csv(f"{config.RESULTS_DIR}/contentiousness.csv", sep=",", index=False, header=True)

def profile_sensitivity(workloads: list[Workload]) -> None:
    if not os.path.isdir(SENSITIVITY_DIR):
        os.mkdir(SENSITIVITY_DIR)
    for workload in workloads:
        if config.PROGRESSIVE_PROFILING:
            _profile_sensitivity_progressive(workload)
        else:
            _profile_sensitivity(workload)
    

# Profiles the contentiousness of each workload and saves the results to a file. Returns the maximum contentiousness score across all workloads.
def profile_contentiousness(workloads: list[Workload], reporter: rp.Reporter) -> None:
    contentiousness = {}
    max_contentiousness = 0

    for workload in workloads:
        if not workload.name:
            logger.warning(f"Workload {workload} has no name, skipping contentiousness profiling")
            continue
        time.sleep(config.WORKLOAD_WIND_DOWN_TIME)

        contentiousness[workload.name] = _profile_contentiousness(workload, reporter)
        logger.info(f"{workload.name} contentiousness: {contentiousness[workload.name]}")
        # Find biggest contentiousness score
        if contentiousness[workload.name] > max_contentiousness:
            max_contentiousness = contentiousness[workload.name]
    
    _save_contentiousness_data(contentiousness)

    logger.info(f"MaxContentiousness: {max_contentiousness}")
    return max_contentiousness

def profile_added_contentiousness(workload: Workload, reporter: rp.Reporter) -> float:

    sizes = range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB)

    contentiousness = {}

    for size_mb in sizes:
        result = 0.0

        logger.info(f"Profiling {workload.name} with SoI size {size_mb}MB")

        if size_mb == 0:
            logger.info("Profiling in isolation")
            result = _profile_contentiousness(workload, reporter)
        bubble = Bubble(size_mb, config.N_BUBBLES)
        bubble.run_in_background()
        try:
            result = _profile_contentiousness(workload, reporter) - size_mb
        finally:
            bubble.stop()

        contentiousness[size_mb] = result

    logger.info(f"Saving contentiousness data for {workload.name}")
    # Save the contentiousness data 
    benchmark_file = workload.name.replace(".", "_")
    path = f"{config.RESULTS_DIR}/contentiousness/{benchmark_file}_contentiousness.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w+") as f:
        f.write("footprint_mb,contentiousness\n")
        for k, v in contentiousness.items():
            f.write(f"{k},{v}\n")

    
def _profile_sensitivity_progressive(benchmark: Workload):
    name = benchmark.name.replace(".", "_")
    path = SENSITIVITY_DIR / f"{name}_data.csv"
    with open(path, "w+") as f:
        f.write(f"footprint_mb,perf\n")

        max_soi = config.N_BUBBLES
        dial_start = config.DIAL_START_MB
        interval = config.DIAL_RANGE_MB // max_soi

        nsoi = 0
        
        for size_mb in range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB):
            if size_mb > 0:
                nsoi = size_mb // interval + 1
            perf = _profile_sensitivity_dial(benchmark, size_mb * nsoi, nsoi)
            f.write(f"{size_mb},{perf}\n")

