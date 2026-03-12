from abc import ABC, abstractmethod
import logging
import subprocess
import constants


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
        
        if constants.use_root_priority:
            cmd = constants.ROOT_TASK_CMD + cmd

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
    
    @abstractmethod
    def process_output(self, output: dict[str, float]):
        raise NotImplementedError
    
class SingleValueReporter(Reporter):
    def process_output(self, output: dict[str, float]) -> float:
        if len(output) != 1:
            raise ValueError("Single value reporter returned multiple values")
        return float(next(iter(output.values()))) / 1_000_000.0

class AveragingReporter(Reporter):
    def process_output(self, output: dict[str, float]) -> float:
        return sum(output.values()) / len(output) / 1_000_000.0
