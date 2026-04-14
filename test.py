from time import sleep
import logging

from profile_reporter import profile_reporter_sensitivity, profile_reporter, profile_reporter_contentiousness
import profile_workload
import reporter
import spec
import atexit
import os
import signal
import sys
import prediction
import validation
import contentiousness
from contention_synthesis import Bubble, BUILD_DIR
import config
import reporter as rp
from cpu_freq import CpuFreqPolicy, Governor

logger = logging.getLogger(__name__)


if __name__ == "__main__":

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    CpuFreqPolicy.set_governor(Governor.PERFORMANCE)

    # bubble = Bubble(32, 2)
    # sleep(1)
    # bubble.run()
    # sleep(1)
    # print("Running bubble for 500 seconds")
    # sleep(500)
    # bubble.stop()


    # spec.run_background_benchmark("600.perlbench_s", "1", "train")
    # spec.run_background_benchmark("602.gcc_s", "2", "train")
    # spec.run_background_benchmark("631.deepsjeng_s", "3", "train")
    # spec.run_background_benchmark("649.fotonik3d_s", "4", "train")
    # spec.run_background_benchmark("628.pop2_s", "5", "train")
    # spec.run_background_benchmark("607.cactuBSSN_s", "6", "train")

    bench = [spec.SpecWorkload("600.perlbench_s", "train"), spec.SpecWorkload("602.gcc_s", "train"), spec.SpecWorkload("649.fotonik3d_s", "train"), spec.SpecWorkload("619.lbm_s", "train")]

    reporter = rp.AveragingReporter("build/altern_reporter.out")
    
    # profile_reporter(reporter)

    # base = profile_sensitivity(reporter, 0)

    # print(f"Reporter base performance: {base}")

    # rcnt = profile_reporter_contentiousness(reporter)

    # print(f"Reporter contentiousness: {rcnt}")

    # base = bench.profile(config.WORKLOAD_UNDER_PROFILING_CORES)

    # print(f"Workload base performance: {base}")

    # background = reporter.run_background(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0])

    # sleep(5)

    # score = bench.profile(config.WORKLOAD_UNDER_PROFILING_CORES)

    # os.kill(background.pid, signal.SIGKILL)

    # print(f"Workload performance with reporter in background: {score}")

    os.makedirs(f"{config.RESULTS_DIR}/contentiousness", exist_ok=True)

    for b in bench:
        profile_workload.profile_added_contentiousness(b, reporter)

    # # process = spec.run_background_benchmark("605.mcf_s", "1", "train")
    # for i in range(6):
    #     result = bench.profile("0")
    #     sleep(2)

    #     logger.info(f"Cactu alone: {result}")
        
        # proc = spec.run_background_benchmark("619.lbm_s", "1", "train")
        # sleep(2)
        # result = bench.profile("0")
        # spec.stop_benchmark(proc)
        # sleep(2)

        # logger.info(f"Cactu with lbm: {result}")

        # proc = spec.run_background_benchmark("631.deepsjeng_s", "2", "train")
        # sleep(2)
        # result = bench.profile("0")
        # spec.stop_benchmark(proc)
        # sleep(2)

        # logger.info(f"Cactu with deepsjeng: {result}")

        # proc = spec.run_background_benchmark("628.pop2_s", "3", "train")
        # sleep(2)
        # result = bench.profile("0")
        # spec.stop_benchmark(proc)
        # sleep(2)

        # logger.info(f"Cactu with pop2: {result}")

    CpuFreqPolicy.reset_governor()

