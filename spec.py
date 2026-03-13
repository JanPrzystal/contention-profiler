import signal
import subprocess
import os
import logging

import config

from workload import Workload

logger = logging.getLogger(__name__)

class SpecWorkload(Workload):
    def __init__(self, name, size="train"):
        self.size = size
        self.proc = None
        super().__init__(name)

    def profile(self, cores: str) -> float:
        # return run_benchmark(self, self.name, cores, self.size)
        logger.info(f"Running benchmark {self.name}, size = {self.size}")
        threads = 1
        
        cmd = [
            "taskset",
            "-c",
            f"{cores}",
            config.SPEC_PATH + "/bin/runcpu",
            f"--threads={threads}",
            "--config=try1",
            "--tuning=base",
            f"--size={self.size}",
            self.name,
        ]
        
        if config.use_root_priority:
            cmd = config.ROOT_TASK_CMD + cmd

        self.proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
        )
        logger.info("Started process")
        try:
            output = self.proc.stdout.decode("utf-8")
            logger.debug(f"Process output:\n{output}")
            self.proc.check_returncode()
            output_filename = _get_output_filename(output)
            return _get_benchmark_time(output_filename, self.name)

        except subprocess.CalledProcessError:
            errors = self.proc.stderr.decode("utf-8")
            logger.error(errors)
            raise Exception("SPEC process ended with non-zero exit code")

    def run_in_background(self, cores: str) -> None:
        self.proc = run_background_benchmark(self.name, cores, self.size)

    def stop(self) -> None:
        if not self.proc:
            raise Exception(f"No instance of SPEC CPU workload {self.name} found")
        os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
        

def run_background_benchmark(name: str, cores: str, size: str) -> subprocess.Popen:
    logger.info(f"Running {name} in background, size = {size}")

    cmd = [
        config.SPEC_PATH + "/bin/runcpu",
        "--iterations=10000",
        "--config=try1",
        "--tuning=base",
        f"--size={size}",
        name,
    ]

    if cores is not None:
        cmd = ["taskset", "-c", f"{cores}"] + cmd

    if config.use_root_priority:
        cmd = config.ROOT_TASK_CMD + cmd

    return subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL
    )

    
# def stop_benchmark(proc: subprocess.Popen):
    # os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    
def _get_output_filename(runcpu_output: str) -> str:
    for line in runcpu_output.splitlines():
        line = line.strip()
        if line.startswith("format: raw ->"):
            filename = line.split(" ")[3]
            if filename.endswith(".rsf"):
                return filename
    raise Exception("Output file not found")


def _get_benchmark_time(output_file: str, benchmark_name: str):
    bench_format = benchmark_name.replace(".", "_")
    line_format = f"spec.cpu2017.results.{bench_format}.base.000.reported_time"
    with open(output_file, "r") as f:
        for line in f:
            if line.strip().startswith(line_format):
                return float(line.split(" ")[1])
        raise Exception("Benchmark reported time not found")