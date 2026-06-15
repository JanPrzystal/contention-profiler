import subprocess
import os
from typing import List

import config

from experiment_setup.workload import Workload, Process, run_background_workload
from experiment_setup.log import log, DEBUG, ERROR
from experiment_setup.core_manager import background_core_dispenser

from prediction.prediction import Prediction
from prediction.validation import ValidatedPrediction, validate_prediction
from prediction.deployment import Deployment


class SpecWorkload(Workload):
    def __init__(self, name: str, size="train"):
        super().__init__(name)
        self.size = size
        self.proc = None

    def __str__(self):
        return self.name

    def get_command(self, background: bool = False) -> List[str]:
        iterations = 10000 if background else 1
        cmd = [
            config.SPEC_PATH + "/bin/runcpu",
            f"--threads=1",
            "--config=try1",
            "--tuning=base",
            f"--iterations={iterations}",
            f"--size={self.size}",
            self.name,
        ]

        return cmd

    def profile(self) -> float:
        # return run_benchmark(self, self.name, cores, self.size)
        log(f"Running benchmark {self.name}, size = {self.size}")
        
        core = config.WORKLOAD_UNDER_PROFILING_CORES
        cmd = ["taskset", "-c", core] + self.get_command(False)
        
        if config.USE_ROOT_PRIORITY:
            cmd = config.ROOT_TASK_CMD + cmd

        log(f"Running command: {' '.join(cmd)}", DEBUG)

        self.proc = Process(subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setpgrp
        ), core)

        log("Started process")

        stdout_data, stderr_data = self.proc.proc.communicate()

        output = stdout_data.decode("utf-8")
        # log(f"Process output:\n{output}", DEBUG)

        if self.proc.proc.returncode != 0:
            # errors = self.proc.stderr.decode("utf-8")
            log(stderr_data.decode("utf-8"), ERROR)
            raise Exception("SPEC process ended with non-zero exit code")

        output_filename = _get_output_filename(output)
        if self.proc.proc.poll() is None:
            log(f"Stopping process with PID {self.proc.proc.pid}", DEBUG)
            self.proc.stop()

        return _get_benchmark_time(output_filename, self.name)


    def run_in_background(self) -> None:
        self.proc = run_background_workload(self)

    def stop(self) -> None:
        if not self.proc:
            raise Exception(f"No instance of SPEC CPU workload {self.name} found")
        
        log(f"Stopping background process with PID {self.proc.proc.pid}", DEBUG)
        self.proc.stop()


    
def _get_output_filename(runcpu_output: str) -> str:
    for line in runcpu_output.splitlines():
        line = line.strip()
        if line.startswith("format: raw ->"):
            filename = line.split(" ")[3]
            if filename.endswith(".rsf"):
                return filename
    raise Exception("Output file not found")


def _get_benchmark_time(output_file: str, benchmark_name: str) -> float:
    bench_format = benchmark_name.replace(".", "_")
    line_format = f"spec.cpu2017.results.{bench_format}.base.000.reported_time"
    with open(output_file, "r") as f:
        for line in f:
            if line.strip().startswith(line_format):
                return float(line.split(" ")[1])
        raise Exception("Benchmark reported time not found")
    

xz = SpecWorkload("657.xz_s", size=config.DATA_SIZE)
gcc = SpecWorkload("602.gcc_s", size=config.DATA_SIZE)
perlbench = SpecWorkload("600.perlbench_s", size=config.DATA_SIZE)
xalancbmk = SpecWorkload("623.xalancbmk_s", size=config.DATA_SIZE)
x264 = SpecWorkload("625.x264_s", size=config.DATA_SIZE)
imagick = SpecWorkload("638.imagick_s", size=config.DATA_SIZE)
deepsjeng = SpecWorkload("631.deepsjeng_s", size=config.DATA_SIZE)
imagick = SpecWorkload("638.imagick_s", size=config.DATA_SIZE)
leela = SpecWorkload("641.leela_s", size=config.DATA_SIZE)
exchange2 = SpecWorkload("648.exchange2_s", size=config.DATA_SIZE)
nab = SpecWorkload("644.nab_s", size=config.DATA_SIZE)
omnetpp = SpecWorkload("620.omnetpp_s", size=config.DATA_SIZE)
cactu = SpecWorkload("607.cactuBSSN_s", size=config.DATA_SIZE)
bwaves = SpecWorkload("603.bwaves_s", size=config.DATA_SIZE)
lbm = SpecWorkload("619.lbm_s", size=config.DATA_SIZE)
pop2 = SpecWorkload("628.pop2_s", size=config.DATA_SIZE)
fotonik3d = SpecWorkload("649.fotonik3d_s", size=config.DATA_SIZE)
roms = SpecWorkload("654.roms_s", size=config.DATA_SIZE)
cam4 = SpecWorkload("627.cam4_s", size=config.DATA_SIZE)
mcf = SpecWorkload("605.mcf_s", size=config.DATA_SIZE)

WORKLOADS = [
    xz, gcc, perlbench, xalancbmk, x264, imagick, 
    deepsjeng, leela, exchange2, nab, omnetpp, cactu, 
    bwaves, lbm, pop2, fotonik3d, roms, cam4, mcf
]

VALIDATION_DEPLOYMENTS = [
    # 7c, highest contentiousness, lowest performance
    Deployment(xz, [omnetpp, bwaves, cactu, lbm, pop2, fotonik3d, roms]),
    # 7c, highest contentiousness, high performance
    Deployment(imagick, [omnetpp, bwaves, lbm, cam4, pop2, fotonik3d, roms]),
    # 7c, lowest contentiousness, high performance
    Deployment(imagick, [perlbench, xalancbmk, x264, deepsjeng, leela, exchange2, nab]),
    Deployment(bwaves, [perlbench, xalancbmk, x264, deepsjeng, leela, exchange2, nab]),
    # 7c, lowest contentiousness, low performance
    Deployment(xz, [perlbench, xalancbmk, x264, deepsjeng, leela, exchange2, nab]),
    # 7c, lowest performance, high contentiousness
    Deployment(omnetpp, [bwaves, cactu, lbm, cam4, pop2, fotonik3d, roms]),
    Deployment(fotonik3d, [omnetpp, xalancbmk, bwaves, lbm, cam4, pop2, roms]),
    # 7c, low performance, medium contentiousness
    Deployment(roms, [gcc, mcf, omnetpp, xz, cactu, lbm, pop2]),
    # 7c, high performance, medium contentiousness
    Deployment(bwaves, [perlbench, x264, deepsjeng, leela, exchange2, lbm, imagick]),
    # 7c, high performance, low contentiousness
    Deployment(lbm, [gcc, x264, deepsjeng, leela, exchange2, imagick, nab]),
    # 7c, high performance, medium contentiousness
    Deployment(nab, [gcc, perlbench, xalancbmk, deepsjeng, leela, exchange2, fotonik3d]),
#---11---
    # bad results
    Deployment(deepsjeng, [omnetpp, bwaves, lbm]),
    Deployment(lbm, [mcf, deepsjeng, pop2, fotonik3d]),
    Deployment(cam4, [x264, deepsjeng, exchange2, pop2, nab, fotonik3d, roms]),
    Deployment(perlbench, [lbm]),
    Deployment(xalancbmk, [mcf, deepsjeng, leela, xz, bwaves, lbm]),

    Deployment(lbm, [mcf, omnetpp, bwaves, pop2, nab, fotonik3d, roms]),
    Deployment(roms, [x264, leela, lbm, pop2, nab, fotonik3d]),

    Deployment(deepsjeng, [lbm, fotonik3d]),
    Deployment(xz, [mcf, deepsjeng, leela, bwaves, lbm, nab]),
    Deployment(lbm, [perlbench, deepsjeng, bwaves, cactu, cam4]),
    Deployment(fotonik3d, [gcc, xalancbmk, deepsjeng, lbm, cam4 , pop2, nab]),
#---22---
    Deployment(lbm, [mcf, omnetpp, bwaves, pop2, nab, fotonik3d, roms]),

    Deployment(deepsjeng, [omnetpp, bwaves, lbm]),

    Deployment(omnetpp, [bwaves, lbm, fotonik3d]),
    Deployment(roms, [mcf, bwaves, lbm, fotonik3d]),

    Deployment(omnetpp, [leela, xz, pop2, imagick]),
    Deployment(omnetpp, [mcf, deepsjeng, bwaves, lbm, fotonik3d, roms]),

    Deployment(lbm, [mcf, omnetpp, bwaves, fotonik3d, roms]),
    Deployment(lbm, [perlbench, mcf, omnetpp, deepsjeng, bwaves, fotonik3d, roms]),
#---30---
    Deployment(omnetpp, [perlbench, gcc, deepsjeng, leela, lbm, nab]),
    Deployment(roms, [gcc, omnetpp, deepsjeng, cam4]),
    Deployment(deepsjeng, [perlbench, gcc, lbm]),

    Deployment(xz, [perlbench, mcf, omnetpp, cactu]),

    Deployment(gcc, [lbm, cactu]),

    Deployment(xz, [mcf, omnetpp, cactu, lbm, fotonik3d, roms]),
    Deployment(fotonik3d, [perlbench, mcf, omnetpp, xz, cactu, lbm, roms]),

    Deployment(bwaves, [perlbench, mcf, omnetpp, xalancbmk, lbm, fotonik3d, roms]),

    Deployment(omnetpp, [perlbench, xz, cactu, lbm, fotonik3d, roms]),
    Deployment(omnetpp, [perlbench, mcf, xz, lbm, fotonik3d, roms]),
#---40---
    Deployment(perlbench, [xalancbmk, bwaves, lbm, nab]),
    # Make every benchmark be profiled and be the competitor at least once
    # 7c to look at the case when all cores are utilized
    # 7c near worst for pearlbench
    Deployment(perlbench, [mcf, omnetpp, x264, bwaves, lbm, fotonik3d, roms]),
    # 7c bad for gcc
    Deployment(gcc, [mcf, leela, bwaves, lbm, pop2, nab, fotonik3d]),
    
    Deployment(bwaves, [omnetpp, xalancbmk, deepsjeng, exchange2, xz, lbm, fotonik3d]),

    Deployment(mcf, [gcc, omnetpp, cactu, lbm, cam4, pop2, nab]),

    Deployment(cactu, [mcf, omnetpp, xalancbmk, leela, xz, bwaves, lbm]),

    Deployment(lbm, [mcf, omnetpp, bwaves, cam4, pop2, fotonik3d, roms]),

    Deployment(omnetpp, [perlbench, mcf, deepsjeng, bwaves, lbm, pop2, fotonik3d]),

    Deployment(xalancbmk, [mcf, x264, exchange2, xz, bwaves, cam4, nab]),

    Deployment(x264, [omnetpp, deepsjeng, xz, cactu, lbm, imagick, fotonik3d]),

    Deployment(cam4, [gcc, omnetpp, x264, bwaves, lbm, imagick, fotonik3d]),

    Deployment(pop2, [mcf, omnetpp, leela, exchange2, lbm, nab, roms]),

    Deployment(deepsjeng, [omnetpp, xz, bwaves, lbm, pop2, fotonik3d, roms]),

    Deployment(imagick, [omnetpp, bwaves, lbm, cam4, pop2, fotonik3d, roms]),

    Deployment(leela, [perlbench, gcc, xalancbmk, exchange2, xz, lbm, fotonik3d]),

    Deployment(nab, [gcc, x264, exchange2, xz, cam4, pop2, roms]),

    Deployment(exchange2, [perlbench, gcc, mcf, xalancbmk, cactu, fotonik3d, roms]),

    Deployment(fotonik3d, [gcc, mcf, omnetpp, xz, lbm, pop2, roms]),

    Deployment(xz, [x264, leela, exchange2, bwaves, lbm, pop2, fotonik3d]),

    Deployment(xz, [x264, leela, exchange2, bwaves, lbm, pop2, fotonik3d])
#---59---
]
def spec_validation(predictions: List[Prediction]) -> List[ValidatedPrediction]:

    # Find the relevant predictions
    valid_keys = {
        (
            deployment.application.name,
            frozenset(comp.name for comp in deployment.competitors),
        )
        for deployment in VALIDATION_DEPLOYMENTS
    }

    filtered_predictions = [
        p
        for p in predictions
        if (
            p.app,
            frozenset(p.competitor.split(" + ")),
        ) in valid_keys
    ]

    validated_predictions = []
    for p in filtered_predictions:
        validated_predictions.append(validate_prediction(p, WORKLOADS))
    return validated_predictions

