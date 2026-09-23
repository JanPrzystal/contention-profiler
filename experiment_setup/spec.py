import subprocess
import os

import config

from experiment_setup.workload import Workload, Process, run_background_workload
from experiment_setup.log import log, DEBUG, ERROR

THREADS = 1

class SpecWorkload(Workload):
    def __init__(self, name: str, size="train"):
        super().__init__(name)
        self.size = size
        self.proc = None

    def __str__(self):
        return self.name

    def get_command(self, background: bool = False) -> list[str]:
        iterations = 10000 if background else 1
        cmd = [
            config.SPEC_PATH + "/bin/runcpu",
            f"--threads={THREADS}",
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

ALL_SPEC_WORKLOADS = [
    xz,
    gcc,
    perlbench,
    xalancbmk,
    x264,
    imagick,
    deepsjeng,
    leela,
    exchange2,
    nab,
    omnetpp,
    cactu,
    bwaves,
    lbm,
    pop2,
    fotonik3d,
    roms,
    cam4,
    mcf,
]
