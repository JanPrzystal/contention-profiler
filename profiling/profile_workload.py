from typing import list
import os
import pandas as pd
import time
from pathlib import Path

from analysis.draw_contentiousness import draw_contentiousness

from experiment_setup.source_of_interference import SoI
import config
from config import SENSITIVITY_DIR
from experiment_setup.workload import Workload

import profiling.perf as perf
import profiling.contentiousness as cnt

from experiment_setup.log import DEBUG, log, WARNING


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
        f.write("pressure,perf\n")
        f.writelines(f"{k},{v}\n" for k, v in sensitivity.items())


def _profile_sensitivity(workload: Workload) -> None:
    sensitivity = _get_sensitivity_data(workload.name)

    sizes = range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB)
    log(f"profiling sizes {sizes}")

    for size_mb in sizes:
        log(f"profiling size {size_mb}MB")
        
        if size_mb in sensitivity:
            continue
        sensitivity[size_mb] = _profile_sensitivity_dial(workload, size_mb, config.NSOI)
        time.sleep(config.WORKLOAD_WIND_DOWN_TIME)

    _save_sensitivity_data(workload.name, sensitivity)

def _profile_sensitivity_dial(workload: Workload, size_mb: int, nproc: int) -> float:
    if size_mb == 0:
        log("Profiling in isolation")
        return workload.profile()
    soi = SoI(size_mb, nproc)
    soi.run_in_background()

    time.sleep(config.WORKLOAD_WARMUP_TIME)
    
    try:
        return workload.profile()
    finally:
        soi.stop()

def _profile_contentiousness(workload: Workload, reporter: Workload) -> float:
        avg = 0.0
        workload.run_in_background()
        time.sleep(config.WORKLOAD_WARMUP_TIME)

        max = 0.0
        min = 0.0
        try:
            for _ in range(config.PROFILING_REPETITIONS):
                score = cnt.contentiousness_lookup(reporter.profile())
                avg += score
                max = max(max, score)
                if score < min or min == 0.0:
                    min = score
                time.sleep(config.WORKLOAD_WIND_DOWN_TIME)

        finally:
            workload.stop()

        log(f"Range of contentiousness scores for {workload.name}: {max - min}, min: {min}, max: {max}", DEBUG)

        return avg / config.PROFILING_REPETITIONS


def _save_contentiousness_data(data: dict[str,float]) -> None:
    csv_data = {"application": list(data.keys()), "contentiousness": list(data.values())}
    df = pd.DataFrame(csv_data)
    df.to_csv(f"{config.RESULTS_DIR}/contentiousness.csv", sep=",", index=False, header=True)

def profile_sensitivity(workloads: list[Workload]) -> None:
    if not os.path.isdir(SENSITIVITY_DIR):
        os.mkdir(SENSITIVITY_DIR)
    for workload in workloads:
        if config.USE_HPC:
            profile_sensitivity_hpc(workload)
        elif config.PROGRESSIVE_PROFILING:
            _profile_sensitivity_progressive(workload)
        else:
            _profile_sensitivity(workload)
    

# Profiles the contentiousness of each workload and saves the results to a file. Returns the maximum contentiousness score across all workloads.
def _profile_contentiousness_simple(workloads: list[Workload], reporter: Workload) -> float:
    contentiousness = {}
    max_contentiousness = 0

    for workload in workloads:
        if not workload.name:
            log(f"Workload {workload} has no name, skipping contentiousness profiling", WARNING)
            continue

        score = _profile_contentiousness(workload, reporter)

        contentiousness[workload.name] = score
        log(f"{workload.name} contentiousness: {contentiousness[workload.name]}")

        # Find biggest contentiousness score
        max_contentiousness = max(max_contentiousness, contentiousness[workload.name])
    
    _save_contentiousness_data(contentiousness)

    log(f"MaxContentiousness: {max_contentiousness}")
    return max_contentiousness

def profile_contentiousness(workloads: list[Workload], reporter: Workload) -> float | None:
    if config.USE_SIMPLE_CONTENTIOUSNESS:
        return _profile_contentiousness_simple(workloads, reporter)
    else:
        for workload in workloads:
            profile_added_contentiousness(workload, reporter)
        draw_contentiousness()
        return None

def profile_added_contentiousness(workload: Workload, reporter: Workload) -> None:

    sizes = range(config.DIAL_START_MB, config.DIAL_END_MB - 1, config.DIAL_STEP_MB)

    contentiousness = {}

    for size_mb in sizes:
        result = 0.0

        if size_mb == 0:
            log(f"Profiling contentiousness of {workload.name}")
            result = _profile_contentiousness(workload, reporter)

        else:
            nsoi = config.NSOI
            if config.PROGRESSIVE_PROFILING:
                nsoi = max(size_mb // (config.DIAL_RANGE_MB // config.NSOI), 1)

            log(f"Profiling {workload.name} with {nsoi} SoI size {size_mb}MB")
            
            soi = SoI(size_mb, nsoi)
            soi.run_in_background()
            try:
                result = _profile_contentiousness(workload, reporter) - size_mb
            finally:
                soi.stop()

        contentiousness[size_mb] = result

    # Save the results to a csv file
    log(f"Saving contentiousness data for {workload.name}")
    # Save the contentiousness data 
    benchmark_file = workload.name.replace(".", "_")
    path = f"{config.RESULTS_DIR}/contentiousness/{benchmark_file}_contentiousness.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w+") as f:
        f.write("pressure,contentiousness\n")
        f.writelines(f"{k},{v}\n" for k, v in contentiousness.items())

    
def _profile_sensitivity_progressive(benchmark: Workload):
    name = benchmark.name.replace(".", "_")
    path = SENSITIVITY_DIR / f"{name}_data.csv"
    with open(path, "w+") as f:
        f.write("pressure,perf\n")

        max_soi = config.NSOI
        interval = config.DIAL_RANGE_MB // max_soi

        nsoi = 0
        
        for size_mb in range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB):
            if size_mb > 0:
                nsoi = max(size_mb // interval, 1)
            perf = _profile_sensitivity_dial(benchmark, size_mb, nsoi)
            f.write(f"{size_mb},{perf}\n")

def _write_hpc_result(file, result, label):
    file.write(
        f"{label},"
        f"{result['time_elapsed']},{result['user_time']},{result['sys_time']},"
        f"{result['LLC-loads']},{result['LLC-load-misses']},"
        f"{result['LLC-stores']},{result['LLC-store-misses']},"
        f"{result['L1-dcache-loads']},{result['L1-dcache-load-misses']},"
        f"{result['L1-icache-load-misses']},{result['L1-dcache-stores']},"
        f"{result['cache-misses']},"
        f"{result['dTLB-load-misses']},{result['dTLB-store-misses']},"
        f"{result['branch-misses']},"
        f"{result['context-switches']},"
        f"{result['llc_miss_rate']},{result['cpi']}\n"
    )

def profile_sensitivity_hpc(workload: Workload, competitor: Workload | None = None, path: Path | None = None) -> None:
    name = workload.name.replace(".", "_")
    if not path:
        path = SENSITIVITY_DIR / f"{name}_data.csv"

    with open(path, "w+") as f:
        f.write("pressure,"
        "time,time_user,time_sys,"
        "LLC-loads,LLC-load-misses,"
        "LLC-stores,LLC-store-misses,"
        "L1-dcache-loads,L1-dcache-load-misses,"
        "L1-icache-load-misses,L1-dcache-stores,"
        "cache-misses,"
        "dTLB-load-misses,dTLB-store-misses,"
        "branch-misses,"
        "context-switches,"
        "LLC-miss-rate,"
        "CPI\n")

        if competitor is None:
            max_soi = config.NSOI
            interval = config.DIAL_RANGE_MB // max_soi
            nsoi = 0
            
            for size_mb in range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB):
                soi = None
                if size_mb > 0:
                    nsoi = max(size_mb // interval, 1)
                    soi = SoI(size_mb, nsoi)
                    soi.run_in_background()
                    time.sleep(config.WORKLOAD_WARMUP_TIME)

                core = config.WORKLOAD_UNDER_PROFILING_CORES
                result = perf.profile(workload.get_command(), cores=core)

                if soi is not None:
                    soi.stop()

                _write_hpc_result(f, result, size_mb)
        else:
            core = config.WORKLOAD_UNDER_PROFILING_CORES
            result = perf.profile(workload.get_command(), cores=core)
            _write_hpc_result(f, result, 0)

            competitor.run_in_background()
            time.sleep(config.WORKLOAD_WARMUP_TIME)

            core = config.WORKLOAD_UNDER_PROFILING_CORES
            result = perf.profile(workload.get_command(), cores=core)

            competitor.stop()

            _write_hpc_result(f, result, 1)


