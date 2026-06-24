import os
import time
import signal

from experiment_setup.log import log, DEBUG
from experiment_setup.contention_synthesis import Bubble
import config
from experiment_setup.workload import Workload
import profiling.contentiousness as cnt


def profile_reporter_sensitivity(reporter: Workload, size_mb: int, nsoi: int = config.NSOI) -> float:
    if size_mb == 0:
        log("Profiling in isolation")
        return reporter.profile()


    bubble = Bubble(size_mb, nsoi)
    bubble.run_in_background()
    time.sleep(config.WORKLOAD_WARMUP_TIME)
    try:
        return reporter.profile()
    finally:
        bubble.stop()


def _profile_reporter(reporter: Workload) -> None:
    with open(f"{config.RESULTS_DIR}/reporter_sensitivity.csv", "w+") as f:
        f.write(f"footprint_mb,perf\n")
        
        for size_mb in range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB):
            perf = profile_reporter_sensitivity(reporter, size_mb, config.NSOI)
            f.write(f"{size_mb},{perf}\n")
            

def _profile_reporter_progressive(reporter: Workload) -> None:
    with open(f"{config.RESULTS_DIR}/reporter_sensitivity.csv", "w+") as f:
        f.write(f"footprint_mb,perf\n")

        max_soi = config.NSOI
        interval = config.DIAL_RANGE_MB // max_soi

        nsoi = 0

        for size_mb in range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB):
            if size_mb > 0:
                nsoi = max(size_mb // interval, 1)

            log(f"Profiling with SoI size {size_mb}MB and {nsoi} SoI ({size_mb}/{config.DIAL_RANGE_MB // config.NSOI})", DEBUG)

            perf = profile_reporter_sensitivity(reporter, size_mb, nsoi)
            f.write(f"{size_mb},{perf}\n")

def profile_reporter(reporter: Workload) -> None:
    if config.PROGRESSIVE_PROFILING:
        _profile_reporter_progressive(reporter)
    else:
        _profile_reporter(reporter)


def profile_reporter_contentiousness(reporter: Workload) -> float:
    result = 0.0

    with open(f"{config.RESULTS_DIR}/reporter_contentiousness.csv", "a+") as f:
        f.write(f"footprint_mb,contentiousness\n")

        reporter.run_in_background()
        
        time.sleep(config.WORKLOAD_WARMUP_TIME)

        score = reporter.profile()

        log(f"Reporter score: {score}")
        
        contentiousness = cnt.contentiousness_lookup(score)

        reporter.stop()

        f.write(f"{0},{contentiousness}\n")

        result = contentiousness

    return result

if __name__ == "__main__":
    profile_reporter()
