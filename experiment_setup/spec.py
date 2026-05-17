import subprocess
import os
from typing import List

import config

from experiment_setup.workload import Workload, Process
from experiment_setup.log import log, DEBUG, ERROR
from experiment_setup.core_manager import background_core_dispenser


class SpecWorkload(Workload):
    def __init__(self, name: str, size="train"):
        super().__init__(name)
        self.size = size
        self.proc = None

    def get_command(self, iterations: int = 1) -> List[str]:
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

    def profile(self, iterations: int = 1) -> float:
        # return run_benchmark(self, self.name, cores, self.size)
        log(f"Running benchmark {self.name}, size = {self.size}")
        
        core = config.WORKLOAD_UNDER_PROFILING_CORES
        cmd = ["taskset", "-c", core] + self.get_command(iterations)
        
        if config.USE_ROOT_PRIORITY:
            cmd = config.ROOT_TASK_CMD + cmd

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
        log(f"Process output:\n{output}", DEBUG)

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
        self.proc = run_background_benchmark(self.name, self.size)

    def stop(self) -> None:
        if not self.proc:
            raise Exception(f"No instance of SPEC CPU workload {self.name} found")
        
        log(f"Stopping background process with PID {self.proc.proc.pid}", DEBUG)
        self.proc.stop()

def run_background_benchmark(name: str, size: str) -> Process:
    core = background_core_dispenser.acquire()
    log(f"Running {name} in background on core {core}, size = {size}")

    cmd = [
        config.SPEC_PATH + "/bin/runcpu",
        "--iterations=10000",
        "--config=try1",
        "--tuning=base",
        f"--size={size}",
        name,
    ]

    if core is not None:
        cmd = ["taskset", "-c", f"{core}"] + cmd

    if config.USE_ROOT_PRIORITY:
        cmd = config.ROOT_TASK_CMD + cmd

    log(f"Running command: {' '.join(cmd)}", DEBUG)
    
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        preexec_fn=os.setpgrp
    )

    return Process(proc, core)

    
def stop_benchmark(proc: Process):
    log(f"Stopping background process with PID {proc.proc.pid}")
    proc.stop()

    
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