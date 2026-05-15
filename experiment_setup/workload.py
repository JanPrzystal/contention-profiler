from abc import ABC, abstractmethod
import subprocess
from experiment_setup.core_manager import background_core_dispenser
import os
import signal

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
    def profile(self) -> float:
        pass

    @abstractmethod
    def run_in_background(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
