from time import sleep
import logging

import experiment_setup.core_manager as cm
from experiment_setup.experiment import sample_deployments
from profiling.profile_reporter import profile_reporter, profile_reporter_contentiousness
from profiling import profile_workload
import experiment_setup.spec as spec
import os
import signal
from prediction import prediction
import prediction.validation as validation
from profiling import contentiousness
from experiment_setup.source_of_interference import SoI, compile_soi
import config
import experiment_setup.reporter as rp
from experiment_setup.cpu_freq import CpuFreqPolicy, Governor
import profiling.perf as perf
from experiment_setup.log import INFO, setup_logging, log, DEBUG
from analysis.plot_metrics import plot_metrics
import prediction.deployment as deployment

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
    log(f"Predicted performance: {pn}", logging.INFO)
    
    procs = []
    for i, b in enumerate(bench):
        log(f"{b.name}", logging.INFO)
        # cores = list(range(int(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[0]), int(config.WORKLOAD_IN_BACKGROUND_CORES.split("-")[1])))
        proc = spec.run_background_workload(b)
        procs.append(proc)

    sleep(5)

    score = reporter.profile(config.REPORTER_CORES, config.REPORTER_REPETITIONS)

    for proc in procs:
        os.kill(proc.pid, signal.SIGKILL)

    cnt = contentiousness.contentiousness_lookup(score)

    log(f"Actual performance would be {sensitivity(0)/sensitivity(cnt)}", logging.INFO)

    log(f"Workloads contentiousness: {cnt}",logging.INFO)

    validated = validation.validate_prediction(predicion, apps) 

    validated_score = validated._asdict()["actual_perf"]

    log(f"Validated {validated_score}", logging.INFO)

    validated_cnt = contentiousness.contentiousness_lookup(sensitivity(0) / validated_score)

    log(f"Validated contentiousness {validated_cnt}", logging.INFO)



def test_soi_additiveness():

    reporter = rp.AveragingReporter("alternating")

    profile_reporter(reporter)

    base = 8

    log("Test with SoI", logging.INFO)

    for i in range(1, 7):
        soi1 = SoI(base*i, 1)
        soi2 = SoI(base, i)

        soi1.run_in_background()

        sleep(5)

        score = reporter.profile(config.WORKLOAD_UNDER_PROFILING_CORES)

        soi1.stop()

        cnt = contentiousness.contentiousness_lookup(score)

        log(f"1x{base*i}MB: {score}, contentiousness: {cnt}", logging.INFO)

        soi2.run_in_background()

        sleep(5)

        score = reporter.profile(config.WORKLOAD_UNDER_PROFILING_CORES)

        soi2.stop()

        cnt = contentiousness.contentiousness_lookup(score)

        log(f"{i}x{base}MB: {score}, contentiousness: {cnt}", logging.INFO)

    log("Test with benchmarks", logging.INFO)
    app1 = spec.SpecWorkload("657.xz_s", "train")
    app2 = spec.SpecWorkload("600.perlbench_s", "train")

    _maxc = profile_workload.profile_contentiousness([app1, app2], reporter)

    log("Profiling contentiousness of 2 apps", logging.INFO)

    app1.run_in_background()
    app2.run_in_background()

    sleep(5)

    score = reporter.profile(config.WORKLOAD_UNDER_PROFILING_CORES)

    app1.stop()
    app2.stop()

    cnt = contentiousness.contentiousness_lookup(score)

    for name, cont in contentiousness.read_contentiousness().items():
        log(f"{name}: {cont}", logging.INFO)
    log(f"Contentiousness of all apps together: {cnt}", logging.INFO)


def test_added_contentiousness():
    log("testing added contentiousness with progressive profiling", logging.INFO)
    config.PROGRESSIVE_PROFILING = True

    reporter = rp.AveragingReporter("alternating")
    # reporter = rp.MembenchReporter("tinymembench")

    bench = [spec.SpecWorkload("619.lbm_s", "train"), spec.SpecWorkload("600.perlbench_s", "train"), spec.SpecWorkload("649.fotonik3d_s", "train"), spec.SpecWorkload("654.roms_s", "train")]

    profile_reporter(reporter)

    for w in bench:
        profile_workload.profile_added_contentiousness(w, reporter)

def test_hpc_spec():
    config.USE_HPC = True

    profile_workload.profile_sensitivity(spec.WORKLOADS)

    plot_metrics("649_fotonik3d_s_data.csv")

def test_hpc_reporter():
    # reporter = rp.MembenchReporter("tinymembench")
    reporter = rp.AveragingReporter("alternating")

    config.REPORTER_REPETITIONS = 5

    log("Profiling reporter with HPC", logging.INFO)

    config.USE_HPC = True

    profile_workload.profile_sensitivity([reporter])

    # log(f"Perf results: {perf_results}", logging.INFO)

def test_hpc_soi():
    soi = SoI(16, 1)

    config.USE_HPC = True

    profile_workload.profile_sensitivity([soi])

    plot_metrics("soi_rand_data.csv")

def test_equilibrium_prediction():
    bench = [spec.deepsjeng, spec.leela, spec.bwaves, spec.cam4, spec.nab, spec.fotonik3d]
    app = spec.lbm

    config.USE_SIMPLE_CONTENTIOUSNESS = True

    pred_simple = prediction.predict_app_performance(app, bench)

    log(f"Prediction with simple contentiousness {pred_simple}")

    config.USE_SIMPLE_CONTENTIOUSNESS = False

    prediction.setup_contentiousness_data(bench)

    pred_adv = prediction.predict_app_performance(app, bench)

    log(f"Prediction with advanced contentiousness {pred_adv}")

def test_spec_repeatability():
    cactu = spec.SpecWorkload("607.cactuBSSN_s", "train")

    repetitions = 10

    for i in range(repetitions):
        time = cactu.profile()
        log(f"Cactu {i}: {time}", logging.INFO)

    xz = spec.SpecWorkload("657.xz_s", "train")

    for i in range(repetitions):
        time = xz.profile()
        log(f"XZ {i}: {time}", logging.INFO)

def test_reporter_repetitions(repetitions: int):
    reporter = rp.AveragingReporter("alternating")

    config.REPORTER_REPETITIONS = repetitions

    log(f"Testing reporter repetitions {repetitions}", logging.INFO)

    profile_reporter(reporter)

def test_same_core():
    # global background_core_dispenser

    config.DIAL_END_MB = 16
    config.DIAL_RANGE_MB = 16

    config.PROGRESSIVE_PROFILING = True
    config.NSOI = 1

    reporter = rp.AveragingReporter("alternating")

    cores = [0,1,8]
    with open(f"{config.RESULTS_DIR}/cores_test.txt", "w") as f:
        f.write(f"Using Reporter {reporter.name}\n")
        for app in spec.WORKLOADS:
            for core in cores: 
                cm.background_core_dispenser = cm.CoreManager([core])

                app.run_in_background()

                sleep(config.WORKLOAD_WARMUP_TIME)

                score = reporter.profile()

                app.stop()

                f.write(f"Reporter score with {app.name} on core {core}: {score}\n")

def profile_reporter_all_cores():
    config.DIAL_END_MB = 256
    config.DIAL_RANGE_MB = 256

    config.PROGRESSIVE_PROFILING = True
    config.NSOI = 16

    cores = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0]
    cm.background_core_dispenser = cm.CoreManager(cores)
    
    reporter = rp.AveragingReporter("alternating")

    profile_reporter(reporter)

def profile_reporter_hpc_cores():
    config.USE_HPC = True
    config.DIAL_END_MB = 16
    config.DIAL_RANGE_MB = 16

    config.PROGRESSIVE_PROFILING = True
    config.NSOI = 1

    cores = [0]
    cm.background_core_dispenser = cm.CoreManager(cores)
    
    # reporter = rp.MembenchReporter("tinymembench")
    reporter = rp.AveragingReporter("alternating")

    profile_workload.profile_sensitivity([reporter])

    app1 = spec.omnetpp
    app2 = spec.fotonik3d

    path = config.SENSITIVITY_DIR / f"{app1}_data.csv"

    profile_workload.profile_sensitivity_hpc(app1, app2)

def profile_spec_competition_hpc():
    app1 = spec.omnetpp
    app2 = spec.fotonik3d

    cores = [0,1,8]
    for core in cores: 
        cm.background_core_dispenser = cm.CoreManager([core])
        path = config.SENSITIVITY_DIR / f"{app1}_c{core}_data.csv"

        profile_workload.profile_sensitivity_hpc(app1, app2, path)


def main():
    config.USE_ROOT_PRIORITY = False
    config.DATA_SIZE = "train"

    CpuFreqPolicy.set_governor(Governor.PERFORMANCE)

    compile_soi()

    config.DIAL_END_MB = 160
    config.DIAL_RANGE_MB = 160

    config.PROGRESSIVE_PROFILING = True
    config.NSOI = 5

    # reporter = rp.AveragingReporter("streaming")
    reporter = rp.MembenchReporter("tinymembench")
    # reporter.profile()
    profile_reporter(reporter)

    CpuFreqPolicy.reset_governor()

if __name__ == "__main__":
    # main()
    setup_logging(DEBUG)

    deployments = sample_deployments(spec.ALL_SPEC_WORKLOADS, 15, 20)

    apps = set(item for x in deployments for item in x.competitors)

    for app in apps:
        print(f"{app.name}")
