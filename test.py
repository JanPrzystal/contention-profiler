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

    apps = [app] + bench

    reporter = rp.AveragingReporter("alternating")
        
    profile_reporter(reporter)

    base = profile_workload.profile_sensitivity([app])

    _maxc = profile_workload.profile_contentiousness(bench, reporter)

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

    validated = validation.validate_prediction(predicion, apps) 

    print(f"Validated {validated}")

    validated_cnt = contentiousness.contentiousness_lookup(sensitivity(0) * validated)

    print(f"Validated contentiousness {validated_cnt}")



def test_soi_additiveness():

    reporter = rp.AveragingReporter("alternating")

    profile_reporter(reporter)

    base = 8

    print("Test with SoI")

    for i in range(1, 7):
        soi1 = Bubble(base*i, 1)
        soi2 = Bubble(base, i)

        soi1.run_in_background(config.WORKLOAD_IN_BACKGROUND_CORES)

        sleep(5)

        score = reporter.run(config.WORKLOAD_UNDER_PROFILING_CORES)

        soi1.stop()

        cnt = contentiousness.contentiousness_lookup(score)

        print(f"1x{base*i}MB: {score}, contentiousness: {cnt}")

        soi2.run_in_background(config.WORKLOAD_IN_BACKGROUND_CORES)

        sleep(5)

        score = reporter.run(config.WORKLOAD_UNDER_PROFILING_CORES)

        soi2.stop()

        cnt = contentiousness.contentiousness_lookup(score)

        print(f"{i}x{base}MB: {score}, contentiousness: {cnt}")

    print("Test with benchmarks")
    app1 = spec.SpecWorkload("657.xz_s", "train")
    app2 = spec.SpecWorkload("600.perlbench_s", "train")

    _maxc = profile_workload.profile_contentiousness([app1, app2], reporter)

    print("Profiling contentiousness of 2 apps")

    app1.run_in_background(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0])
    app2.run_in_background(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[1])

    sleep(5)

    score = reporter.run(config.WORKLOAD_UNDER_PROFILING_CORES)

    app1.stop()
    app2.stop()

    cnt = contentiousness.contentiousness_lookup(score)

    for name, cont in contentiousness.read_contentiousness().items():
        print(f"{name}: {cont}")
    print(f"Contentiousness of all apps together: {cnt}")


def test_added_contentiousness():
    print("testing added contentiousness with progressive profiling")
    config.DIAL_END_MB = 128
    config.NSOI = 7
    config.PROGRESSIVE_PROFILING = True

    reporter = rp.AveragingReporter("alternating")
    # reporter = rp.MembenchReporter("../membench/membench")

    bench = [spec.SpecWorkload("619.lbm_s", "train"), spec.SpecWorkload("600.perlbench_s", "train"), spec.SpecWorkload("649.fotonik3d_s", "train"), spec.SpecWorkload("654.roms_s", "train")]

    profile_reporter(reporter)

    for w in bench:
        profile_workload.profile_added_contentiousness(w, reporter)


if __name__ == "__main__":

    logging.basicConfig()
    logger.setLevel(logging.INFO)

    # config.USE_ROOT_PRIORITY = False

    CpuFreqPolicy.set_governor(Governor.PERFORMANCE)


    config.DIAL_END_MB = 96

    # test_soi_additiveness()

    # test_combined_contentiousness()

    test_added_contentiousness()

    # stats = perf.profile("./membench/membench")

    # print (stats)


    CpuFreqPolicy.reset_governor()

