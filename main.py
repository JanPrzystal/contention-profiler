import os
import sys
import shutil
import config
import analysis.draw_sensitivity as draw_sensitivity
import analysis.draw_validation as draw_validation
from experiment_setup.log import DEBUG, log, setup_logging

import subprocess
from py_containters.mds import MdsFactory
from py_containters.kube_workload import KubeWorkload
from typing import List
import experiment_setup.experiment as experiment
import csv
from experiment_setup.cpu_freq import CpuFreqPolicy



SPEC_COMPETITORS = [
    "628.pop2_s",
    "649.fotonik3d_s",
]

MDS_SERVICES = ["datatest", "dataforwarding", "datageneration"]




# def setup_mds():
#     log("Setting up MDS on the Kubernetes cluster")
#     mds_factory = MdsFactory()
#     etcd = mds_factory.create_workload("etcd")
#     etcd.setup()

#     applications = [mds_factory.create_workload(name) for name in MDS_SERVICES]
#     for app in applications:
#         app.setup()
#     log("MDS setup complete")
#     return applications

# def mds_experiment():
#     reporter = rp.AveragingReporter(REPORTER_SCRIPT_FILES["alternating"])
#     applications = setup_mds()
#     competitors = [SpecWorkload(name) for name in SPEC_COMPETITORS]
#     competitors.extend(applications)
#     conduct_experiment(reporter, applications, competitors)

if __name__ == "__main__":
    resume = False if len(sys.argv) < 2 else True if sys.argv[1] == "resume" else False
    
    experiments = experiment.parse_config()

    for exp in experiments:
        if not resume:
        # Clear results directory
            try:
                shutil.rmtree(config.RESULTS_DIR)
            except FileNotFoundError:
                pass
            os.makedirs(config.RESULTS_DIR, exist_ok=True)
        
        setup_logging(DEBUG)

        log(f"Starting experiment: {exp.name}")

        experiment.spec_experiment(exp)

        draw_sensitivity.draw_sensitivity()
        draw_validation.draw_validation()

        subprocess.run(["zip", "-r", f"results_{exp.name}.zip", config.RESULTS_DIR], check=True)

        log(f"Experiment {exp.name} completed\n\n")

        # if config.USE_ROOT_PRIORITY:
            # subprocess.run(["sudo", "./clean_spec.sh"], check=False)

    CpuFreqPolicy.reset_governor()
    
    log("All experiments completed.")

