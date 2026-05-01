from abc import ABC, abstractmethod

class Workload(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def profile(self, cores: str) -> float:
        pass

    @abstractmethod
    def run_in_background(self, cores: str) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
