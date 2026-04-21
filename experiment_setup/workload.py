class Workload():

    def __init__(self, name: str):
        self.name = name

    def profile(self, cores: str) -> float:
        pass

    def run_in_background(self, cores: str) -> None:
        pass

    def stop(self) -> None:
        pass
