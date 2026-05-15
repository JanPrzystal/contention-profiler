import threading

import config

class CoreManager:
    def __init__(self, cores):
        self.available = set(str(c) for c in cores)
        self.lock = threading.Lock()

    def acquire(self) -> str:
        with self.lock:
            if not self.available:
                raise RuntimeError("No free cores available")

            core = min(self.available, key=int)
            self.available.remove(core)
            return core

    def release(self, core: str) -> None:
        with self.lock:
            self.available.add(core)

background_cores = config.WORKLOAD_IN_BACKGROUND_CORES.split("-")
background_core_dispenser = CoreManager(range(int(background_cores[0]), int(background_cores[1]) + 1))