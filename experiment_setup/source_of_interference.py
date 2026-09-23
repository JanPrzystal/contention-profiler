import subprocess
import os

import config
from experiment_setup.spec import SpecWorkload
from experiment_setup.workload import Workload, Process, run_background_workload

from experiment_setup.log import log, WARNING, ERROR, DEBUG
import experiment_setup.core_manager as cm


def compile_soi() -> bool:
    log("Compiling soi executable...")
    try:
        os.makedirs(config.BUILD_DIR, exist_ok=True)

        _ = subprocess.run(
            [
                "gcc",
                "-O3",
                "-fno-tree-loop-distribute-patterns",
                "-march=native",
                f"{config.SOI_DIR}/memory_soi.c",
                "-o",
                f"{config.BUILD_DIR}/memory_soi",
            ],
            stdin=subprocess.DEVNULL,
            check=True,
        )
        log("Success", DEBUG)
    except subprocess.CalledProcessError as e:
        log(f"Failed with code {e.returncode}", ERROR)
        log(f"Error output: {e.stderr}", ERROR)
        return False
    except FileNotFoundError:
        log("Command not found", ERROR)
        return False

    return True

soi_exists = False
def check_soi_exists() -> bool:
    global soi_exists
    if not soi_exists:
        soi_exists = os.path.isfile(f"{config.BUILD_DIR}/memory_soi")
        if not soi_exists:
            log(f"SoI executable not found at {config.BUILD_DIR}/memory_soi", DEBUG)
            soi_exists = compile_soi()

    return soi_exists

class SoI(Workload):
    ELEM_SIZE = 8 # The size of the elements used in the SoI application in bytes (int64 = 8)

    def __init__(self, size_mb: int, n_proc = 1):
        assert check_soi_exists(), "SoI executable not found. Please ensure it is compiled and available."

        # self.name = "soi_"+config.BUBBLE_TYPE
        self.name = "soi"
        self.n_proc = n_proc
        self.size = size_mb * 1_000_000 
        self.soi_size = round(self.size / n_proc / SoI.ELEM_SIZE)
        log(f"Preparing SoIs with total footprint size {self.size / 1_000_000}MB and per-process size {self.soi_size} ({self.ELEM_SIZE} bytes per element)")
        self.procs = []

    def profile(self) -> float:
        raise NotImplementedError("\"profile\" not implemented for Bubble")
    
    def get_command(self, background: bool = False) -> list[str]:
        file = "memory_soi"
    
        # arg1 = "0" if background else "10000"
        # arg2 = config.BUBBLE_TYPE

        arg1 = self.soi_size

        return [f"./{config.BUILD_DIR}/{file}", str(arg1)]

    def run_in_background(self) -> None:
        for i in range(self.n_proc):
            if config.BUBBLE_TYPE == "stream":
                soi_type = "stream"
            elif config.BUBBLE_TYPE == "rand":
                soi_type = "rand"
            else:
                soi_type = "stream" if i % 2 == 0 else "rand"
            log(f"Running soi {soi_type}")

            core = ""
            idx = -1
            try:
                idx, core = cm.background_core_dispenser.acquire()
            except Exception as e:
                log(f"Failed to acquire background core for soi process {i+1}: {e}", ERROR)
                raise Exception("Failed to acquire background core for soi process")
        
            cmd = ["taskset", "-c", str(core), *self.get_command(background=True)]

            if config.USE_ROOT_PRIORITY:
                cmd = [*config.ROOT_TASK_CMD, *cmd]

            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                preexec_fn=os.setpgrp
            )
            self.procs.append(Process(proc, idx))
    
    def stop(self) -> None:
        for proc in self.procs:
            proc.stop()
        self.procs.clear()


class SpecSoI(Workload):
    ELEM_SIZE = 8 # The size of the elements used in the SoI application in bytes (int64 = 8)

    def __init__(self, spec: SpecWorkload, n_proc = 1):
        self.workload = spec
        self.n_proc = n_proc
        self.procs = []

    def profile(self) -> float:
        raise NotImplementedError("\"profile\" not implemented for Bubble")
    
    def get_command(self, background: bool = False) -> list[str]:
        return self.workload.get_command(background)

    def run_in_background(self) -> None:
        for _ in range(self.n_proc):   
            self.procs.append(
                run_background_workload(self.workload)
            )
    
    def stop(self) -> None:
        for proc in self.procs:
            proc.stop()
        self.procs.clear()
