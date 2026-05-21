import subprocess
import os

import config
from experiment_setup.workload import Workload, Process

from experiment_setup.log import log
from experiment_setup.core_manager import background_core_dispenser


BUILD_DIR = "build"

class Sledge():    
    ELEM_SIZE = 8

    def __init__(self, size_mb: int):
        self.size = size_mb * 1_000_000 // Sledge.ELEM_SIZE
        os.makedirs(BUILD_DIR, exist_ok=True)
        subprocess.run(
            [
                "gcc",
                "-O2",
                "-fopenmp",
                f"-DLBM_SIZE={self.size}",
                "sledge.c",
                "-o",
                f"{BUILD_DIR}/sledge.out",
            ],
            stdin=subprocess.DEVNULL,
        )
        self.proc = None

    def run(self, cores: str) -> None:
        log(f"Running sledge with footprint size {self.size}")

        cmd = [
            "taskset",
            "-c",
            f"{cores}",
            f"./{BUILD_DIR}/sledge.out",
        ]
        
        if config.USE_ROOT_PRIORITY:
            cmd = config.ROOT_TASK_CMD + cmd

        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
        )
    
    def stop(self) -> None:
        if not self.proc:
            log("An attempt to stop sledge was made but no process was found", WARNING)
            return
        os.kill(self.proc.pid, 9)

class Bubble(Workload):
    ELEM_SIZE = 8 # The size of the elements used in the SoI application in bytes (int64 = 8)

    def __init__(self, size_mb: int, n_proc = 1):
        self.n_proc = n_proc
        self.size = size_mb * 1_000_000 
        end_size = round(self.size / n_proc / Bubble.ELEM_SIZE)
        log(f"Building bubble with total footprint size {self.size} and per-process size {end_size} ({self.ELEM_SIZE} bytes)")

        os.makedirs(BUILD_DIR, exist_ok=True)
        subprocess.run(
            [
                "gcc",
                "-O2",
                "-fopenmp",
                "-march=native",
                f"-DFOOTPRINT_SIZE={end_size}",
                "-DBUBBLE_TYPE=0",
                "-DNUM_THREADS=1",
                f"{config.SOI_DIR}/bubble.c",
                "-o",
                f"{BUILD_DIR}/bubble_stream.out",
            ],
            stdin=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                "gcc",
                "-O2",
                "-fopenmp",
                "-march=native",
                f"-DFOOTPRINT_SIZE={end_size}",
                "-DBUBBLE_TYPE=1",
                "-DNUM_THREADS=1",
                f"{config.SOI_DIR}/bubble.c",
                "-o",
                f"{BUILD_DIR}/bubble_rand.out",
            ],
            stdin=subprocess.DEVNULL,
        )
        self.procs = []

    def profile(self) -> float:
        raise NotImplementedError("\"profile\" not implemented for Bubble")

    def run_in_background(self) -> None:
        for i in range(self.n_proc):
            if config.BUBBLE_TYPE == "stream":
                bubble_type = "bubble_stream.out"
            elif config.BUBBLE_TYPE == "rand":
                bubble_type = "bubble_rand.out"
            else:
                bubble_type = "bubble_stream.out" if i % 2 == 0 else "bubble_rand.out"
            log(f"Running {bubble_type}")

            core = ""
            try:
                core = background_core_dispenser.acquire()
            except Exception as e:
                log(f"Failed to acquire background core for bubble process {i+1}: {e}")
                raise Exception("Failed to acquire background core for bubble process")
        
            cmd = ["taskset", "-c", f"{core}", f"./{BUILD_DIR}/{bubble_type}"]
    

            if config.USE_ROOT_PRIORITY:
                cmd = config.ROOT_TASK_CMD + cmd

            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                preexec_fn=os.setpgrp
            )
            self.procs.append(Process(proc, core))
    

    
    def stop(self) -> None:
        for proc in self.procs:
            proc.stop()
        self.procs.clear()
