from abc import ABC, abstractmethod
import logging
import subprocess
import config


logger = logging.getLogger(__name__)


class Reporter(ABC):
    def __init__(self, script_file: str):
        self.script_file = script_file

    def run(self, cores: str, repetitions: int = 25):
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
    
    def run_background(self, cores: str):
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
    
    @abstractmethod
    def process_output(self, output: dict[str, float]) -> float:
        raise NotImplementedError
    
class SingleValueReporter(Reporter):
    def process_output(self, output: dict[str, float]) -> float:
        if len(output) != 1:
            raise ValueError("Single value reporter returned multiple values")
        return float(next(iter(output.values()))) / 1_000_000.0

class AveragingReporter(Reporter):
    def process_output(self, output: dict[str, float]) -> float:
        try:
            return sum(output.values()) / len(output) / 1_000_000.0
        except ZeroDivisionError:
            logger.warning(f"Division by zero: {output}")
            return 0.0
