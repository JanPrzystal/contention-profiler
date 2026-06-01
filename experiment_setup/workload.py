from abc import ABC, abstractmethod
from typing import List
import subprocess
import config
from experiment_setup.core_manager import background_core_dispenser
import os
import signal

from experiment_setup.log import DEBUG, ERROR, log

class Process:
    def __init__(self, proc: subprocess.Popen, core: str):
        self.proc = proc
        self.core = core

    def stop(self) -> None:
        os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
        background_core_dispenser.release(self.core)

class Workload(ABC):

    def __init__(self, name: str):
        self.name = name
        pass

    @abstractmethod
    def get_command(self, background: bool = False) -> List[str]:
        pass

    @abstractmethod
    def profile(self) -> float:
        pass

    @abstractmethod
    def run_in_background(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


def run_background_workload(workload: Workload) -> Process:
    core = background_core_dispenser.acquire()
    log(f"Running {workload.name} in background on core {core}")

    cmd = workload.get_command(True)

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

    
def stop_process(proc: Process):
    if proc is None:
        log("Trying to stop a non-existing process!", ERROR)
        return
    
    log(f"Stopping background process with PID {proc.proc.pid}")
    proc.stop()
