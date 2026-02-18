import subprocess
import os
import logging

logger = logging.getLogger(__name__)

BUILD_DIR = "build"

NUM_PROC = 6

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
        logger.info(f"Running sledge with footprint size {self.size}")
        self.proc = subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                f"{cores}",
                f"./{BUILD_DIR}/sledge.out",
            ],
            stdin=subprocess.DEVNULL,
        )
    
    def stop(self) -> None:
        if not self.proc:
            logger.warning("An attempt to stop sledge was made but no process was found")
            return
        os.kill(self.proc.pid, 9)

class Bubble():
    ELEM_SIZE = 8

    def __init__(self, size_mb: int):
        self.size = size_mb * 1_000_000 
        end_size = round(self.size / NUM_PROC)
        logger.info(f"Building bubble with total footprint size {self.size} and per-process footprint size {end_size}")

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
                "bubble.c",
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
                "bubble.c",
                "-o",
                f"{BUILD_DIR}/bubble_rand.out",
            ],
            stdin=subprocess.DEVNULL,
        )
        self.procs = []

    def run(self) -> None:
        logger.info(f"Running bubble with footprint size {self.size}")
        self.procs.append(subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                "2",
                f"./{BUILD_DIR}/bubble_stream.out",
            ],
            stdin=subprocess.DEVNULL,
        ))
        self.procs.append(subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                "3",
                f"./{BUILD_DIR}/bubble_stream.out",
            ],
            stdin=subprocess.DEVNULL,
        ))
        self.procs.append(subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                "4",
                f"./{BUILD_DIR}/bubble_stream.out",
            ],
            stdin=subprocess.DEVNULL,
        ))
        
        self.procs.append(subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                "5",
                f"./{BUILD_DIR}/bubble_rand.out",
            ],
            stdin=subprocess.DEVNULL,
        ))
        self.procs.append(subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                "6",
                f"./{BUILD_DIR}/bubble_rand.out",
            ],
            stdin=subprocess.DEVNULL,
        ))
        self.procs.append(subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                "7",
                f"./{BUILD_DIR}/bubble_rand.out",
            ],
            stdin=subprocess.DEVNULL,
        ))

    
    def stop(self) -> None:
        # if not self.proc1 and not self.proc2:
        #     logger.warning("An attempt to stop bubble was made but no process was found")
        #     return
        for proc in self.procs:
            os.kill(proc.pid, 9)
        self.procs.clear()
