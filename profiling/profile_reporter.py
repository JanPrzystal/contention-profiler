import os
import time
import logging
import signal

import experiment_setup.reporter as rp

logger = logging.getLogger(__name__)
from experiment_setup.contention_synthesis import Bubble
import config
import profiling.contentiousness as cnt


def profile_reporter_sensitivity(reporter: rp.Reporter, size_mb: int, nsoi: int = config.N_BUBBLES) -> float:
    if size_mb == 0:
        logger.info("Profiling in isolation")
        return reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)


    bubble = Bubble(size_mb, nsoi)
    bubble.run_in_background(config.WORKLOAD_IN_BACKGROUND_CORES)
    time.sleep(config.WORKLOAD_WARMUP_TIME)
    try:
        return reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)
    finally:
        bubble.stop()


def _profile_reporter(reporter: rp.Reporter) -> None:
    with open(f"{config.RESULTS_DIR}/reporter_sensitivity.csv", "w+") as f:
        f.write(f"footprint_mb,perf\n")
        
        for size_mb in range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB):
            perf = profile_reporter_sensitivity(reporter, size_mb)
            f.write(f"{size_mb},{perf}\n")
            

def _profile_reporter_progressive(reporter: rp.Reporter) -> None:
    with open(f"{config.RESULTS_DIR}/reporter_sensitivity.csv", "w+") as f:
        f.write(f"footprint_mb,perf\n")

        max_soi = config.N_BUBBLES
        dial_start = config.DIAL_START_MB
        interval = config.DIAL_RANGE_MB // max_soi

        nsoi = 0

        for size_mb in range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB):
            if size_mb > 0:
                nsoi = size_mb // interval + 1
            perf = profile_reporter_sensitivity(reporter, size_mb * nsoi, nsoi)
            f.write(f"{size_mb},{perf}\n")

def profile_reporter(reporter: rp.Reporter) -> None:
    if config.PROGRESSIVE_PROFILING:
        _profile_reporter_progressive(reporter)
    else:
        _profile_reporter(reporter)


def profile_reporter_contentiousness(reporter: rp.Reporter) -> float:
    result = 0.0

    with open(f"{config.RESULTS_DIR}/reporter_contentiousness.csv", "a+") as f:
        f.write(f"footprint_mb,contentiousness\n")
        
        # base = reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)

        bcore = config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0]
        background = reporter.run_background(bcore)
        
        time.sleep(config.WORKLOAD_WARMUP_TIME)

        score = reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)

        logger.info(f"Reporter score: {score}")
        
        contentiousness = cnt.contentiousness_lookup(score)

        os.kill(background.pid, signal.SIGKILL)

        f.write(f"{0},{contentiousness}\n")

        result = contentiousness

    return result

if __name__ == "__main__":
    profile_reporter()
