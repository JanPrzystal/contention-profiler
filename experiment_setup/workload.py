from abc import ABC, abstractmethod
import subprocess
import config
import experiment_setup.core_manager as cm
import os
import signal

from experiment_setup.log import DEBUG, ERROR, log

class Process:
    def __init__(self, proc: subprocess.Popen, core_idx: int):
        self.proc = proc
        self.core_idx = core_idx

    def stop(self, timeout: float = 5.0) -> None:
        pgid = self.proc.pid  # session leader => pgid == pid
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            pass  # group already gone
        try:
            self.proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(pgid, signal.SIGKILL)  # sweep up anything left in the group
        except ProcessLookupError:
            pass
        self.proc.wait()
        
        cm.background_core_dispenser.release(self.core_idx)

class Workload(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_command(self, background: bool = False) -> list[str]:
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
    idx, core = cm.background_core_dispenser.acquire()
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
        start_new_session=True,
    )

    return Process(proc, idx)

    
def stop_process(proc: Process):
    if proc is None:
        log("Trying to stop a non-existing process!", ERROR)
        return
    
    log(f"Stopping background process with PID {proc.proc.pid}")
    proc.stop()
