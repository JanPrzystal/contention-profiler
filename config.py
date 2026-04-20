from typing import Final

RESULTS_DIR: Final[str] = "experiment_results"
SOI_DIR: Final[str] = "./soi"
SPEC_PATH: Final[str] = "../cpu2017"

WORKLOAD_UNDER_PROFILING_CORES: Final[str] = "0"
WORKLOAD_IN_BACKGROUND_CORES: Final[str] = "1-7"

# Reporter and SoI dial constants
REPORTER_CORES: str = "0"
DIAL_START_MB: int = 0
DIAL_STEP_MB: int = 16
DIAL_END_MB: int = 64
DIAL_RANGE_MB: int = DIAL_END_MB

# MDS constants
MDS_PROFILING_TIME_S: Final[int] = 120
MDS_STARTUP_WAIT_TIME_S: Final[int] = 30

# Kubernetes workload node names
PROFILING_NODE_NAME: Final[str] = "mc-c6"
REMOTE_NODE_NAME: Final[str] = "mc-b8"

ROOT_TASK_CMD = ["sudo", "nice", "-n", "-20"]

N_BUBBLES: int = 4
BUBBLE_TYPE = "rand"

REPORTER_REPETITIONS: int = 40

DATA_SIZE = "train"

USE_ROOT_PRIORITY = False

VALIDATIONS = 8

PROFILING_REPETITIONS = 1

USE_INTERPOLATION = True