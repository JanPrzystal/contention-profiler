import time

from experiment_setup import spec
from experiment_setup.log import log, DEBUG
from experiment_setup.source_of_interference import SoI, SpecSoI
import config
from experiment_setup.workload import Workload

def profile_reporter_sensitivity(reporter: Workload, size_mb: int, nsoi: int = config.NSOI) -> float:
    if size_mb == 0:
        log("Profiling in isolation")
        return reporter.profile()


    if config.USE_SPEC_SOI:
        soi = SpecSoI(spec.lbm, nsoi)
    else:
        soi = SoI(size_mb, nsoi)
    soi.run_in_background()
    time.sleep(config.WORKLOAD_WARMUP_TIME)
    try:
        return reporter.profile()
    finally:
        soi.stop()


def _profile_reporter(reporter: Workload) -> None:
    with open(f"{config.RESULTS_DIR}/reporter_sensitivity.csv", "w+") as f:
        f.write("pressure,perf\n")
        
        for size_mb in range(config.DIAL_START_MB, config.DIAL_END_MB + config.DIAL_STEP_MB, config.DIAL_STEP_MB):
            perf = profile_reporter_sensitivity(reporter, size_mb, config.NSOI)
            f.write(f"{size_mb},{perf}\n")
            

def _profile_reporter_progressive(reporter: Workload) -> None:
    max_soi = config.NSOI
    interval = config.DIAL_RANGE_MB // max_soi
    nsoi = 0

    with open(f"{config.RESULTS_DIR}/reporter_sensitivity.csv", "w+") as f:
        f.write("pressure,perf\n")

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


if __name__ == "__main__":
    profile_reporter()
