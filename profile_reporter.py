import time
import logging

import reporter as rp

logger = logging.getLogger(__name__)
from contention_synthesis import Bubble
import config

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


if __name__ == "__main__":
    profile_reporter()
