from typing import Final

RESULTS_DIR: Final[str] = "experiment_results"
WORKLOAD_UNDER_PROFILING_CORES: Final[str] = "0"
WORKLOAD_IN_BACKGROUND_CORES: Final[str] = "3"

# Reporter and SoI dial constants
REPORTER_CORES: Final[str] = "0"
DIAL_START_MB: Final[int] = 0
DIAL_STEP_MB: Final[int] = 4
DIAL_END_MB: Final[int] = 32

# MDS constants
MDS_PROFILING_TIME_S: Final[int] = 120
MDS_STARTUP_WAIT_TIME_S: Final[int] = 30

# Kubernetes workload node names
PROFILING_NODE_NAME: Final[str] = "mc-c6"
REMOTE_NODE_NAME: Final[str] = "mc-b8"

SPEC_PATH: Final[str] = "../cpu2017"

ROOT_TASK_CMD = ["sudo", "nice", "-n", "-20"]

N_BUBBLES = 2

use_root_priority = False