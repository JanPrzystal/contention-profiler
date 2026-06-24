from abc import ABC, abstractmethod
import subprocess
from typing import List
import config

import experiment_setup.core_manager as cm
from experiment_setup.log import WARNING, log, DEBUG
from experiment_setup.workload import Process, Workload, stop_process

REPORTER_SCRIPT_FILES = {
    "alternating":"build/altern_reporter.out",
    "hybrid":"build/hybrid_reporter.out",
    "random":"build/rand_reporter.out",
    "streaming":"build/stream_reporter.out",
    "tinymembench": "membench/membench"
}

# class Reporter(ABC):
#     def __init__(self, script_file: str):
#         self.script_file = REPORTER_SCRIPT_FILES[script_file]
#         if self.script_file is None:
#             raise ValueError(f"Invalid script file")

#     @abstractmethod
#     def run(self, repetitions: int = 25) -> float:
#         raise NotImplementedError("Run method not implemented for this reporter")
    
#     def run_background(self):
#         raise NotImplementedError("Background profiling not implemented for this reporter")    

#     @abstractmethod
#     def process_output(self, output: dict[str, float]) -> float:
#         raise NotImplementedError
    
# class SingleValueReporter(Reporter):
#     def process_output(self, output: dict[str, float]) -> float:
#         if len(output) != 1:
#             raise ValueError("Single value reporter returned multiple values")
#         return float(next(iter(output.values()))) / 1_000_000.0

class AveragingReporter(Workload):
    def __init__(self, script_file: str):
        self.name = "AveragingReporter"

        self.script_file = REPORTER_SCRIPT_FILES[script_file]
        if self.script_file is None:
            raise ValueError(f"Invalid script file")
        
    def get_command(self, background: bool = False) -> List[str]:
        repetitions: int = config.REPORTER_REPETITIONS

        return [
            f"{self.script_file}",
            "--benchmark_min_warmup_time=1",
            f"--benchmark_repetitions={repetitions}",
            "--benchmark_enable_random_interleaving=true",
            ]

        
    def profile(self) -> float:
        log("Profiling with the reporter")
        core = config.REPORTER_CORES
    
        cmd = [
            "taskset",
            "-c",
            f"{core}"
        ] + self.get_command(False)
        
        if config.USE_ROOT_PRIORITY:
            cmd = config.ROOT_TASK_CMD + cmd

        reporter = subprocess.run(
            cmd,
            capture_output=True,
        )

        raw_output = reporter.stdout.decode("utf-8")
        output = {}
        for line in raw_output.splitlines():
            if "median" in line:
                log(line.strip())
                line = line.split()
                output[line[0]] = float(line[1])
        return self._process_output(output)
    
    
    def run_in_background(self) -> None:
        log("Running reporter in the background")
        core = cm.background_core_dispenser.acquire()

        cmd = [
            "taskset",
            "-c",
            f"{core}",
            f"{self.script_file}",
            "--benchmark_min_warmup_time=1",
            "--benchmark_repetitions=10000",
            "--benchmark_enable_random_interleaving=true",
        ]

        if config.USE_ROOT_PRIORITY:
            cmd = config.ROOT_TASK_CMD + cmd

        subprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.proc = Process(subprocess, core)

    def stop(self) -> None:
        if self.proc is not None:
            stop_process(self.proc)


    def _process_output(self, output: dict[str, float]) -> float:
        try:
            log(f"Range of reporter output: {(max(output.values()) -min(output.values())) / 1_000_000.0}", DEBUG)
            return sum(output.values()) / len(output) / 1_000_000.0
        except ZeroDivisionError:
            log(f"Division by zero: {output}", WARNING)
            return 0.0
        
class MembenchReporter(Workload):
    def __init__(self, script_file: str):
        self.name = "MembenchReporter"

        self.script_file = REPORTER_SCRIPT_FILES[script_file]
        if self.script_file is None:
            raise ValueError(f"Invalid script file")

    def get_command(self, background: bool = False) -> List[str]:
        repetitions: int = config.REPORTER_REPETITIONS if not background else 1000

        return [
            f"{self.script_file}",
            "--max-size=64M", 
            "--num-threads=1",
            f"--iterations={repetitions}",
            ]
    
    def profile(self) -> float:
        core = config.REPORTER_CORES

        cmd = self.get_command(False)
        
        cmd = ["taskset", "-c", f"{core}"] + cmd

        if config.USE_ROOT_PRIORITY:
            cmd = config.ROOT_TASK_CMD + cmd

        reporter = subprocess.run(
            cmd,
            capture_output=True,
        )

        raw_output = reporter.stdout.decode("utf-8")
        output = {}
        for line in raw_output.splitlines():
            if "MB/s" in line:
                line_split = line.split(":")
                number_text = line_split[1].split("MB/s")[0].strip()
                number = float(number_text)
                log(f"reporter raw score: {number}", DEBUG)

                # bigger number is better, but bigger score is worse, so invert the number
                score = 1/number * 100000

                output[line_split[0].strip()] = score
    
        return self._process_output(output)

    def run_in_background(self):
        core = cm.background_core_dispenser.acquire()

        cmd = self.get_command(True)
        
        if config.USE_ROOT_PRIORITY:
            cmd = config.ROOT_TASK_CMD + cmd

        reporter = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self.proc = Process(reporter, core)
    
    def stop(self) -> None:
        if self.proc is not None:
            stop_process(self.proc)
    

    def _process_output(self, output: dict[str, float]) -> float:
        try:
            return sum(output.values()) / len(output)
        except ZeroDivisionError:
            log(f"Division by zero: {output}", WARNING)
            return 0.0