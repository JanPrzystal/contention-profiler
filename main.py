import os
import logging
import random
import shutil
import config
import draw_sensitivity
import draw_validation
import profile_workload
import profile_reporter
import contentiousness
import prediction
import validation
import subprocess
from spec import SpecWorkload
from mds import MdsFactory
from kube_workload import KubeWorkload
from typing import List
from cpu_freq import CpuFreqPolicy, Governor
import experiment
import csv
from datetime import datetime

from time import time

import reporter as rp
from workload import Workload

logger = logging.getLogger(__name__)

SPEC_COMPETITORS = [
    "628.pop2_s",
    "649.fotonik3d_s",
]

MDS_SERVICES = ["datatest", "dataforwarding", "datageneration"]

REPORTER_SCRIPT_FILES = {
    "alternating":"build/altern_reporter.out",
    "hybrid":"build/hybrid_reporter.out",
    "random":"build/rand_reporter.out",
    "streaming":"build/stream_reporter.out"
}

GOVERNOR = Governor.PERFORMANCE

def predict_performance(applications: List[Workload]) -> List[prediction.Prediction]:
    predictions = prediction.predict_performance(applications)
    prediction.save_predictions(predictions)

    return predictions

def conduct_experiment(reporter: rp.Reporter, applications: List[Workload], pairwise: bool):
    tstart = time()
    # profile_reporter.profile_reporter(reporter)
    treporter = time() - tstart

    max_contentiousness = profile_workload.profile_contentiousness(applications, reporter)
    tcontentiousness = time() - tstart - treporter

    config.DIAL_END_MB = min(int(max_contentiousness * 2.0 + 1.0), config.DIAL_END_MB)

    profile_workload.profile_sensitivity(applications)
    tsensitivity = time() - tstart - treporter - tcontentiousness

    contentiousness.save_contentiousness_chart()

    ttotal = time() - tstart

    if pairwise:
        logger.info("Starting pairwise prediction and validation")
        prediction.predict_pair_performance(applications, applications)
        validation.validate_pair_predictions(applications, applications)

    else:
        predictions = predict_performance(applications)
        validated_predictions = validation.validate_predictions(predictions, {w.name: w for w in applications})
        validation.save_validated_predictions(validated_predictions)

    texperiment = time() - tstart
    logger.info(f"Experiment timings: \nreporter={treporter:.3f}s, \ncontentiousness={tcontentiousness:.3f}s, \nsensitivity={tsensitivity:.3f}s, \nprofiling total={ttotal:.3f}s, \nexperiment total={texperiment:.3f}s")

    # Write the times to a file
    with open(f"{config.RESULTS_DIR}/timings.txt", "w") as f:
        f.write(f"reporter={treporter:.3f}s\n")
        f.write(f"contentiousness={tcontentiousness:.3f}s\n")
        f.write(f"sensitivity={tsensitivity:.3f}s\n")
        f.write(f"profiling_total={ttotal:.3f}s\n")
        f.write(f"experiment_total={texperiment:.3f}s\n")


def spec_experiment(experiment: experiment.Experiment):
    config.DIAL_STEP_MB = experiment.mem_interval
    config.DIAL_END_MB = experiment.max_mem_footprint
    config.N_BUBBLES = experiment.soi.number
    config.BUBBLE_TYPE = experiment.soi.type
    config.REPORTER_REPETITIONS = experiment.reporter_repetitions
    config.DATA_SIZE = experiment.data_size
    config.USE_ROOT_PRIORITY = experiment.root
    config.PROFILING_REPETITIONS = experiment.profiling_repetitions
    config.USE_INTERPOLATION = experiment.use_interpolation

    reporter = rp.AveragingReporter(REPORTER_SCRIPT_FILES[experiment.reporter])
    applications = [SpecWorkload(name, config.DATA_SIZE) for name in experiment.benchmarks]

    # CPU Governor set here to take into account root priviledge configuration
    CpuFreqPolicy.set_governor(GOVERNOR)

    # Create a description file 
    with open(f"{config.RESULTS_DIR}/description.txt", "w") as f:
        f.write(f"Time of experiment: {datetime.now()}\n")
        f.write(f"Experiment: {experiment.name}\n")
        f.write(f"Benchmarks: {', '.join(experiment.benchmarks)}\n")
        f.write(f"Reporter: {experiment.reporter}\n")
        f.write(f"SOI: {experiment.soi.type} ({experiment.soi.number})\n")
        f.write(f"Max Memory Footprint: {experiment.max_mem_footprint} MB\n")
        f.write(f"Memory Interval: {experiment.mem_interval} MB\n")
        f.write(f"Reporter Repetitions: {experiment.reporter_repetitions}\n")
        f.write(f"Data Size: {experiment.data_size}\n")
        f.write(f"Root Priority: {experiment.root}\n")

    conduct_experiment(reporter, applications, experiment.deployment == "pairwise")

def setup_mds():
    logger.info("Setting up MDS on the Kubernetes cluster")
    mds_factory = MdsFactory()
    etcd = mds_factory.create_workload("etcd")
    etcd.setup()

    applications = [mds_factory.create_workload(name) for name in MDS_SERVICES]
    for app in applications:
        app.setup()
    logger.info("MDS setup complete")
    return applications

def mds_experiment():
    reporter = rp.AveragingReporter(REPORTER_SCRIPT_FILES["alternating"])
    applications = setup_mds()
    competitors = [SpecWorkload(name) for name in SPEC_COMPETITORS]
    competitors.extend(applications)
    conduct_experiment(reporter, applications, competitors)

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    experiments = experiment.parse_config()

    for exp in experiments:
        logger.info(f"Starting experiment: {exp.name}")

        # Clear results directory
        # try:
        #     shutil.rmtree(config.RESULTS_DIR)
        # except FileNotFoundError:
        #     pass
        # os.makedirs(config.RESULTS_DIR, exist_ok=True)

        spec_experiment(exp)

        draw_sensitivity.draw_sensitivity()
        draw_validation.draw_validation()

        subprocess.run(["zip", "-r", f"results_{exp.name}.zip", config.RESULTS_DIR], check=True)

        logger.info(f"Experiment {exp.name} completed\n\n")

    CpuFreqPolicy.reset_governor()
    
    print("All experiments completed.")

