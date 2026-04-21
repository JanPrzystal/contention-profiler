from time import sleep
import logging

from profiling.profile_reporter import profile_reporter, profile_reporter_contentiousness
import profiling.profile_workload as profile_workload
import experiment_setup.reporter as reporter
import experiment_setup.spec as spec
import atexit
import os
import signal
import sys
import prediction.prediction as prediction
import prediction.validation as validation
import profiling.contentiousness as contentiousness
from experiment_setup.contention_synthesis import Bubble, BUILD_DIR
import config
import experiment_setup.reporter as rp
from experiment_setup.cpu_freq import CpuFreqPolicy, Governor

logger = logging.getLogger(__name__)


if __name__ == "__main__":

    logging.basicConfig()
    logger.setLevel(logging.INFO)

    # CpuFreqPolicy.set_governor(Governor.PERFORMANCE)

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

    bench = [spec.SpecWorkload("600.perlbench_s", "train"), spec.SpecWorkload("602.gcc_s", "train"), spec.SpecWorkload("631.deepsjeng_s", "train")]

    reporter = rp.AveragingReporter("build/altern_reporter.out")
    # reporter = rp.MembenchReporter("../membench/membench")
    
    # profile_reporter_progressive(reporter)
    # profile_reporter(reporter)

    # base = profile_sensitivity(reporter, 0)

    # _maxc = profile_workload.profile_contentiousness(bench, reporter)

    # print(f"Reporter base performance: {base}")

    for i in range(6):
        rcnt = profile_reporter_contentiousness(reporter)

        print(f"Reporter contentiousness: {rcnt}")

        procs = []
        for b in bench:
            cores = list(range(int(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0]), int(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[1])))
            proc = b.run_in_background(cores.pop(0))
            procs.append(proc)

        sleep(5)

        score = reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)

        cnt = contentiousness.contentiousness_lookup(score)

        print(f"Workloads contentiousness: {cnt}")


    # base = bench.profile(config.WORKLOAD_UNDER_PROFILING_CORES)

    # print(f"Workload base performance: {base}")

    # background = reporter.run_background(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0])

    # sleep(5)

    # score = bench.profile(config.WORKLOAD_UNDER_PROFILING_CORES)

    # os.kill(background.pid, signal.SIGKILL)

    # print(f"Workload performance with reporter in background: {score}")

    # os.makedirs(f"{config.RESULTS_DIR}/contentiousness", exist_ok=True)

    # for b in bench:
    #     profile_workload.profile_added_contentiousness(b, reporter)

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

    # CpuFreqPolicy.reset_governor()

