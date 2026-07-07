import threading

import config

class CoreManager:
    def __init__(self, cores):
        self.cores = [str(c) for c in cores]
        self.available_indices = set(range(len(self.cores)))
        self.lock = threading.Lock()

    def acquire(self) -> (int, str):
        with self.lock:
            if not self.available_indices:
                raise RuntimeError("No free cores available")

            idx = min(self.available_indices)
            self.available_indices.remove(idx)
            return idx, self.cores[idx]

    def release(self, idx: int) -> None:
        with self.lock:
            self.available_indices.add(idx)

background_cores = config.WORKLOAD_IN_BACKGROUND_CORES.split(",")
background_core_dispenser: CoreManager = CoreManager(background_cores)