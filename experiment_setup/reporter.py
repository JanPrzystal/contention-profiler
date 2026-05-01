from abc import ABC, abstractmethod
import logging
import subprocess
import config


logger = logging.getLogger(__name__)

REPORTER_SCRIPT_FILES = {
    "alternating":"build/altern_reporter.out",
    "hybrid":"build/hybrid_reporter.out",
    "random":"build/rand_reporter.out",
    "streaming":"build/stream_reporter.out",
    "tinymembench": "membench/membench"
}

class Reporter(ABC):
    def __init__(self, script_file: str):
        self.script_file = REPORTER_SCRIPT_FILES[script_file]
        if self.script_file is None:
            raise ValueError(f"Invalid script file")

    @abstractmethod
    def run(self, cores: str, repetitions: int = 25) -> float:
        raise NotImplementedError("Run method not implemented for this reporter")
    
    @abstractmethod
    def run_background(self, cores: str):
        raise NotImplementedError("Background profiling not implemented for this reporter")
    
    @abstractmethod
    def process_output(self, output: dict[str, float]) -> float:
        raise NotImplementedError
    
# class SingleValueReporter(Reporter):
#     def process_output(self, output: dict[str, float]) -> float:
#         if len(output) != 1:
#             raise ValueError("Single value reporter returned multiple values")
#         return float(next(iter(output.values()))) / 1_000_000.0

class AveragingReporter(Reporter):

    def run(self, cores: str, repetitions: int = 25) -> float:
        logger.info("Profiling with the reporter")

        cmd = [
            "taskset",
            "-c",
            f"{cores}",
            f"{self.script_file}",
            "--benchmark_min_warmup_time=1",
            f"--benchmark_repetitions={repetitions}",
            "--benchmark_enable_random_interleaving=true",
        ]
        
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
                logger.info(line.strip())
                line = line.split()
                output[line[0]] = float(line[1])
        return self.process_output(output)
    
    def run_background(self, cores: str) -> subprocess.Popen:
        logger.info("Running reporter in the background")

        cmd = [
            "taskset",
            "-c",
            f"{cores}",
            f"{self.script_file}",
            "--benchmark_min_warmup_time=1",
            "--benchmark_repetitions=10000",
            "--benchmark_enable_random_interleaving=true",
        ]

        if config.USE_ROOT_PRIORITY:
            cmd = config.ROOT_TASK_CMD + cmd

        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def process_output(self, output: dict[str, float]) -> float:
        try:
            return sum(output.values()) / len(output) / 1_000_000.0
        except ZeroDivisionError:
            logger.warning(f"Division by zero: {output}")
            return 0.0
        
class MembenchReporter(Reporter):

    def run(self, cores: str, repetitions: int = 25) -> float:
        cmd = [
            f"{self.script_file}",
            "--max-size=64M", 
            "--num-threads=1",
            "--iterations=3",
        ]
        
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
                logger.debug(f"reporter raw score: {number}")

                # bigger number is better, but bigger score is worse, so invert the number
                score = 1/number * 100000

                output[line_split[0].strip()] = score
    
        return self.process_output(output)

    def run_background(self, cores: str):
        cmd = [
            f"{self.script_file}",
            "--max-size=64M", 
            "--num-threads=1",
            "--iterations=5",
        ]
        
        if config.USE_ROOT_PRIORITY:
            cmd = config.ROOT_TASK_CMD + cmd

        reporter = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return reporter
    

    def process_output(self, output: dict[str, float]) -> float:
        try:
            return sum(output.values()) / len(output)
        except ZeroDivisionError:
            logger.warning(f"Division by zero: {output}")
            return 0.0