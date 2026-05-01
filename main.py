import os
import random
import shutil
import config
import analysis.draw_sensitivity as draw_sensitivity
import analysis.draw_validation as draw_validation
import logging

import subprocess
from py_containters.mds import MdsFactory
from py_containters.kube_workload import KubeWorkload
from typing import List
import experiment_setup.experiment as experiment
import csv
from experiment_setup.cpu_freq import CpuFreqPolicy



logger = logging.getLogger(__name__)

SPEC_COMPETITORS = [
    "628.pop2_s",
    "649.fotonik3d_s",
]

MDS_SERVICES = ["datatest", "dataforwarding", "datageneration"]




# def setup_mds():
#     logger.info("Setting up MDS on the Kubernetes cluster")
#     mds_factory = MdsFactory()
#     etcd = mds_factory.create_workload("etcd")
#     etcd.setup()

#     applications = [mds_factory.create_workload(name) for name in MDS_SERVICES]
#     for app in applications:
#         app.setup()
#     logger.info("MDS setup complete")
#     return applications

# def mds_experiment():
#     reporter = rp.AveragingReporter(REPORTER_SCRIPT_FILES["alternating"])
#     applications = setup_mds()
#     competitors = [SpecWorkload(name) for name in SPEC_COMPETITORS]
#     competitors.extend(applications)
#     conduct_experiment(reporter, applications, competitors)

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    experiments = experiment.parse_config()

    for exp in experiments:
        logger.info(f"Starting experiment: {exp.name}")

        # Clear results directory
        try:
            shutil.rmtree(config.RESULTS_DIR)
        except FileNotFoundError:
            pass
        os.makedirs(config.RESULTS_DIR, exist_ok=True)

        experiment.spec_experiment(exp)

        draw_sensitivity.draw_sensitivity()
        draw_validation.draw_validation()

        subprocess.run(["zip", "-r", f"results_{exp.name}.zip", config.RESULTS_DIR], check=True)

        logger.info(f"Experiment {exp.name} completed\n\n")

    CpuFreqPolicy.reset_governor()
    
    print("All experiments completed.")

