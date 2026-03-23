import os
import logging
import time
import constants
import profile_workload
import profile_reporter
import contentiousness
import prediction
import validation
from spec import SpecWorkload
from mds import MdsFactory
from kube_workload import KubeWorkload
from typing import List
from cpu_freq import CpuFreqPolicy, Governor

import reporter as rp
from workload import Workload

logger = logging.getLogger(__name__)

SPEC_NAMES = [
    "600.perlbench_s",
    "602.gcc_s",
    "605.mcf_s",
    "620.omnetpp_s",
    "623.xalancbmk_s",
    "625.x264_s",
    "631.deepsjeng_s",
    "641.leela_s",
    "648.exchange2_s",
    "657.xz_s",
    "603.bwaves_s",
    "607.cactuBSSN_s",
    "619.lbm_s",
    "627.cam4_s",
    "628.pop2_s",
    "638.imagick_s",
    "644.nab_s",
    "649.fotonik3d_s",
    "654.roms_s",
]

SPEC_COMPETITORS = [
    "607.cactuBSSN_s",
    "628.pop2_s",
    "603.bwaves_s",
    "654.roms_s",
    "649.fotonik3d_s",
    "619.lbm_s"
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
    tstart = time()
    profile_reporter.profile_reporter(reporter)
    treporter = time() - tstart
    profile_workload.profile_sensitivity(applications)
    tsensitivity = time() - tstart - treporter
    profile_workload.profile_contentiousness(competitors, reporter)
    tcontentiousness = time() - tstart - treporter - tsensitivity
    contentiousness.generate_scores()
    ttotal = time() - tstart
    prediction.predict_performance(applications, competitors)
    validation.validate_predictions(applications, competitors)

    texperiment = time() - tstart
    logger.info(f"Experiment timings: \nreporter={treporter:.3f}s, \ncontentiousness={tcontentiousness:.3f}s, \nsensitivity={tsensitivity:.3f}s, \nprofiling total={ttotal:.3f}s, \nexperiment total={texperiment:.3f}s")

    # Write the times to a file
    with open(f"{constants.RESULTS_DIR}/timings.txt", "w") as f:
        f.write(f"reporter={treporter:.3f}s\n")
        f.write(f"contentiousness={tcontentiousness:.3f}s\n")
        f.write(f"sensitivity={tsensitivity:.3f}s\n")
        f.write(f"profiling_total={ttotal:.3f}s\n")
        f.write(f"experiment_total={texperiment:.3f}s\n")

def spec_experiment():
    workloads = [SpecWorkload(name) for name in SPEC_NAMES]
    reporter = rp.AveragingReporter(REPORTER_SCRIPT_FILES["alternating"])

    # We use the same workloads for applications and competitors
    conduct_experiment(reporter, workloads, workloads)

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
    os.makedirs(constants.RESULTS_DIR, exist_ok=True)
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    CpuFreqPolicy.set_governor(GOVERNOR)
    spec_experiment()
    CpuFreqPolicy.reset_governor()
