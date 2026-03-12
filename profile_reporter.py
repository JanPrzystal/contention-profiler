import time
import logging

import reporter as rp

logger = logging.getLogger(__name__)
from contention_synthesis import Bubble
import constants

REPETITIONS = 100

def profile_sensitivity(reporter: rp.Reporter, size_mb: int) -> float:
    if size_mb == 0:
        logger.info("Profiling in isolation")
        return reporter.run(constants.REPORTER_CORES)
    bubble = Bubble(size_mb, constants.N_BUBBLES)
    bubble.run()
    time.sleep(5)
    try:
        return reporter.run(constants.REPORTER_CORES)
    finally:
        bubble.stop()


def profile_reporter(reporter: rp.Reporter):
    with open(f"{constants.RESULTS_DIR}/reporter_sensitivity.csv", "a+") as f:
        f.write(f"footprint_mb,perf\n")
        for size_mb in range(constants.DIAL_START_MB, constants.DIAL_END_MB + constants.DIAL_STEP_MB, constants.DIAL_STEP_MB):
            perf = profile_sensitivity(reporter, size_mb)
            f.write(f"{size_mb},{perf}\n")


if __name__ == "__main__":
    profile_reporter()
