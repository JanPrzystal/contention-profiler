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
import perf

logger = logging.getLogger(__name__)

def test_combined_contentiousness():
    bench = [spec.SpecWorkload("619.lbm_s", "train"), spec.SpecWorkload("600.perlbench_s", "train"), spec.SpecWorkload("649.fotonik3d_s", "train"), spec.SpecWorkload("654.roms_s", "train")]

    app = spec.SpecWorkload("657.xz_s", "train")

    reporter = rp.AveragingReporter("build/altern_reporter.out")
        
    # profile_reporter(reporter)

    # base = profile_workload.profile_sensitivity([app])

    # _maxc = profile_workload.profile_contentiousness(bench, reporter)

    sensitivity = prediction.get_sensitivity(app.name)
    predicion = prediction.predict_app_performance(app, bench, sensitivity)
    pn = predicion._asdict()["perf"]
    print(f"Predicted performance: {pn}")
    
    procs = []
    for i, b in enumerate(bench):
        print(f"{b.name}")
        # cores = list(range(int(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0]), int(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[1])))
        proc = spec.run_background_benchmark(b.name, str(i+2), b.size)
        procs.append(proc)

    sleep(5)

    score = reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)

    for proc in procs:
        os.kill(proc.pid, signal.SIGKILL)

    cnt = contentiousness.contentiousness_lookup(score)

    print(f"Actual performance would be {sensitivity(0)/sensitivity(cnt)}")

    print(f"Workloads contentiousness: {cnt}")

    validated = validation.validate_prediction(predicion, {w.name: w for w in bench}) 

    print(f"Validated {validated}")

    validated_cnt = contentiousness.contentiousness_lookup(sensitivity(0) * validated)

if __name__ == "__main__":

    logging.basicConfig()
    logger.setLevel(logging.INFO)

    CpuFreqPolicy.set_governor(Governor.PERFORMANCE)


    config.DIAL_END_MB = 128

    test_combined_contentiousness()

    # stats = perf.profile("./membench/membench")

    # print (stats)


    # spec.run_background_benchmark("600.perlbench_s", "1", "train")
    # spec.run_background_benchmark("602.gcc_s", "2", "train")
    # spec.run_background_benchmark("631.deepsjeng_s", "3", "train")
    # proc1 = spec.run_background_benchmark("649.fotonik3d_s", "4", "train")
    # proc2 = spec.run_background_benchmark("619.lbm_s", "5", "train")
    # spec.run_background_benchmark("628.pop2_s", "5", "train")
    # spec.run_background_benchmark("607.cactuBSSN_s", "6", "train")

    # stats = perf.profile("./membench/membench")

    # print (stats)

    # spec.stop_benchmark(proc1)
    # spec.stop_benchmark(proc2)
# 600.perlbench_s + 619.lbm_s + 649.fotonik3d_s + 654.roms_s
    # bench = [spec.SpecWorkload("619.lbm_s", "train"), spec.SpecWorkload("600.perlbench_s", "train"), spec.SpecWorkload("649.fotonik3d_s", "train"), spec.SpecWorkload("654.roms_s", "train")]

    # app = spec.SpecWorkload("657.xz_s", "train")

    # reporter = rp.AveragingReporter("build/altern_reporter.out")
    # reporter = rp.MembenchReporter("../membench/membench")
    
 

    CpuFreqPolicy.reset_governor()

