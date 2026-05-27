import subprocess
import os
from typing import List
import sys
import re
import config

from experiment_setup.log import log, setup_logging, DEBUG

HPC_METRICS = [
    "cycles",
    "instructions",
    "L1-dcache-loads",
    "L1-dcache-load-misses",
    "L1-icache-load-misses",
    "LLC-loads",
    "LLC-load-misses",
    "LLC-store-misses",
    "LLC-stores",
    # "uncore_imc/data_reads/",
    # "uncore_imc/data_writes/",
    # "branches",
    # "branch-misses",
    # "stalled-cycles-frontend",
    # "stalled-cycles-backend",
    "dTLB-load-misses",
    "dTLB-loads",
    "dTLB-store-misses",
    "dTLB-stores",
    "cache-misses",
]

def parse_perf_output(output: str) -> dict:
    results = {}

    # Parse metrics
    for metric in HPC_METRICS:
        pattern = rf"([\d,]+|<not supported>)\s+{re.escape(metric)}"
        match = re.search(pattern, output)

        if match:
            value = match.group(1)

            if value == "<not supported>":
                results[metric] = None
            else:
                results[metric] = int(value.replace(",", ""))
        else:
            results[metric] = None

    # Parse timing info
    time_patterns = {
        "time_elapsed": r"([\d.]+)\s+seconds time elapsed",
        "user_time": r"([\d.]+)\s+seconds user",
        "sys_time": r"([\d.]+)\s+seconds sys",
    }

    for key, pattern in time_patterns.items():
        match = re.search(pattern, output)

        if match:
            results[key] = float(match.group(1))
        else:
            results[key] = None

    # Calculate derived metrics
    results["cpi"] = results["cycles"] / results["instructions"] if results["cycles"] is not None and results["instructions"] is not None else None
    results["l1_miss_rate"] = results["L1-dcache-load-misses"] / results["L1-dcache-loads"] if results["L1-dcache-load-misses"] is not None and results["L1-dcache-loads"] is not None else None
    results["llc_miss_rate"] = results["LLC-load-misses"] / results["LLC-loads"] if results["LLC-load-misses"] is not None and results["LLC-loads"] is not None else None

    return results

def profile(workload: List[str], cores: str = None) -> dict:

    cmd = [
        "perf",
        "stat",
        # "-a",
        "-e " + ",".join(HPC_METRICS),
    ] + workload

    # todo taskset
    if cores is not None:
        cmd = ["taskset", "-c", f"{cores}"] + cmd

    if config.USE_ROOT_PRIORITY:
        cmd = config.ROOT_TASK_CMD + cmd

    log(f"Running command: {' '.join(cmd)}", DEBUG)

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setpgrp
        )


    stdout_data, stderr_data = proc.communicate()

    metric_output = stderr_data.decode("utf-8")

    results = parse_perf_output(metric_output)

    log(stdout_data.decode("utf-8") + "\n\n" + metric_output, DEBUG)

    return results

    # return stdout_data.decode("utf-8") + "\n\n" + metric_output


if __name__ == "__main__":
    setup_logging()
    workload = sys.argv[1:]
    log(f"Profiling workload: {' '.join(workload)}")
    log(profile(workload, "1"))