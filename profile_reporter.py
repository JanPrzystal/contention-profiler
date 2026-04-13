import os
import time
import logging
import signal

import reporter as rp

logger = logging.getLogger(__name__)
from contention_synthesis import Bubble
import config
import contentiousness as cnt

REPETITIONS = 100

def profile_sensitivity(reporter: rp.Reporter, size_mb: int) -> float:
    if size_mb == 0:
        logger.info("Profiling in isolation")
        return reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)
    bubble = Bubble(size_mb, config.N_BUBBLES)
    bubble.run()
    time.sleep(5)
    try:
        return reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)
    finally:
        bubble.stop()


def profile_reporter(reporter: rp.Reporter):
    with open(f"{config.RESULTS_DIR}/reporter_sensitivity.csv", "a+") as f:
        f.write(f"footprint_mb,perf\n")
        for size_mb in range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB):
            perf = profile_sensitivity(reporter, size_mb)
            f.write(f"{size_mb},{perf}\n")


def profile_reporter_contentiousness(reporter: rp.Reporter) -> float:
    result = 0.0

    with open(f"{config.RESULTS_DIR}/reporter_contentiousness.csv", "a+") as f:
        f.write(f"footprint_mb,contentiousness\n")
        
        # base = reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)

        bcore = config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0]
        background = reporter.run_background(bcore)
        
        time.sleep(2)

        score = reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)

        contentiousness = cnt.contentiousness_lookup(score)
        f.write(f"{0},{contentiousness}\n")

        os.killpg(os.getpgid(background.pid), signal.SIGKILL)

    return result

if __name__ == "__main__":
    profile_reporter()
