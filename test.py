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
from experiment_setup.log import setup_logging, log

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
    log(f"Predicted performance: {pn}")
    
    procs = []
    for i, b in enumerate(bench):
        log(f"{b.name}")
        # cores = list(range(int(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0]), int(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[1])))
        proc = spec.run_background_benchmark(b.name, str(i+1), b.size)
        procs.append(proc)

    sleep(5)

    score = reporter.run(config.REPORTER_CORES, config.REPORTER_REPETITIONS)

    for proc in procs:
        os.kill(proc.pid, signal.SIGKILL)

    cnt = contentiousness.contentiousness_lookup(score)

    log(f"Actual performance would be {sensitivity(0)/sensitivity(cnt)}")

    log(f"Workloads contentiousness: {cnt}")

    validated = validation.validate_prediction(predicion, apps) 

    validated_score = validated._asdict()["actual_perf"]

    log(f"Validated {validated_score}")

    validated_cnt = contentiousness.contentiousness_lookup(sensitivity(0) / validated_score)

    log(f"Validated contentiousness {validated_cnt}")



def test_soi_additiveness():

    reporter = rp.AveragingReporter("alternating")

    profile_reporter(reporter)

    base = 8

    log("Test with SoI")

    for i in range(1, 7):
        soi1 = Bubble(base*i, 1)
        soi2 = Bubble(base, i)

        soi1.run_in_background(config.WORKLOAD_IN_BACKGROUND_CORES)

        sleep(5)

        score = reporter.run(config.WORKLOAD_UNDER_PROFILING_CORES)

        soi1.stop()

        cnt = contentiousness.contentiousness_lookup(score)

        log(f"1x{base*i}MB: {score}, contentiousness: {cnt}")

        soi2.run_in_background(config.WORKLOAD_IN_BACKGROUND_CORES)

        sleep(5)

        score = reporter.run(config.WORKLOAD_UNDER_PROFILING_CORES)

        soi2.stop()

        cnt = contentiousness.contentiousness_lookup(score)

        log(f"{i}x{base}MB: {score}, contentiousness: {cnt}")

    log("Test with benchmarks")
    app1 = spec.SpecWorkload("657.xz_s", "train")
    app2 = spec.SpecWorkload("600.perlbench_s", "train")

    _maxc = profile_workload.profile_contentiousness([app1, app2], reporter)

    log("Profiling contentiousness of 2 apps")

    app1.run_in_background(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0])
    app2.run_in_background(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[1])

    sleep(5)

    score = reporter.run(config.WORKLOAD_UNDER_PROFILING_CORES)

    app1.stop()
    app2.stop()

    cnt = contentiousness.contentiousness_lookup(score)

    for name, cont in contentiousness.read_contentiousness().items():
        log(f"{name}: {cont}")
    log(f"Contentiousness of all apps together: {cnt}")


def test_added_contentiousness():
    log("testing added contentiousness with progressive profiling")
    config.DIAL_END_MB = 80
    config.NSOI = 5
    config.PROGRESSIVE_PROFILING = True

    reporter = rp.AveragingReporter("alternating")
    # reporter = rp.MembenchReporter("../membench/membench")

    bench = [spec.SpecWorkload("619.lbm_s", "train"), spec.SpecWorkload("600.perlbench_s", "train"), spec.SpecWorkload("649.fotonik3d_s", "train"), spec.SpecWorkload("654.roms_s", "train")]

    profile_reporter(reporter)

    for w in bench:
        profile_workload.profile_added_contentiousness(w, reporter)


if __name__ == "__main__":

    setup_logging()


    config.USE_ROOT_PRIORITY = False
    config.DATA_SIZE = "test"

    CpuFreqPolicy.set_governor(Governor.PERFORMANCE)


    config.DIAL_END_MB = 32

    # test_soi_additiveness()

    # test_combined_contentiousness()

    test_added_contentiousness()

    # stats = perf.profile("./membench/membench")

    # log (stats)


    CpuFreqPolicy.reset_governor()

