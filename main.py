import os
import logging
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

def conduct_experiment(reporter: rp.Reporter, applications: List[Workload], competitors: List[Workload]):
    profile_reporter.profile_reporter(reporter)
    max_contentiousness = profile_workload.profile_contentiousness(competitors, reporter)

    config.DIAL_END_MB = int(max_contentiousness + 1.0)

    profile_workload.profile_sensitivity(applications)
    contentiousness.generate_scores()
    prediction.predict_performance(applications, competitors)
    validation.validate_predictions(applications, competitors)

def spec_experiment(experiment: experiment.Experiment):
    reporter = rp.AveragingReporter(REPORTER_SCRIPT_FILES[experiment.reporter])
    applications = [SpecWorkload(name) for name in experiment.benchmarks]

    config.DIAL_STEP_MB = experiment.mem_interval
    config.DIAL_END_MB = experiment.max_mem_footprint

    config.N_BUBBLES = experiment.soi.number
    config.BUBBLE_TYPE = experiment.soi.type

    config.REPORTER_REPETITIONS = experiment.reporter_repetitions

    # We use the same workloads for applications and competitors
    conduct_experiment(reporter, applications, applications)

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
        try:
            shutil.rmtree(config.RESULTS_DIR)
        except FileNotFoundError:
            pass
        os.makedirs(config.RESULTS_DIR, exist_ok=True)

        CpuFreqPolicy.set_governor(GOVERNOR)

        spec_experiment(exp)

        CpuFreqPolicy.reset_governor()

        draw_sensitivity.draw_sensitivity()
        draw_validation.draw_validation()

        subprocess.run(["zip", "-r", f"results_{exp.name}.zip", config.RESULTS_DIR], check=True)

        logger.info(f"Experiment {exp.name} completed\n\n")
    
    print("All experiments completed.")

