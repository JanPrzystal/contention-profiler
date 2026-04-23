import yaml
from dataclasses import dataclass
from typing import List

@dataclass
class SoIConfig:
    type: str
    number: int

@dataclass
class Experiment:
    name: str
    benchmarks: List[str]
    reporter: str
    soi: SoIConfig
    max_mem_footprint: int
    mem_interval: int
    reporter_repetitions: int
    deployment: str
    root: bool
    data_size: str
    profiling_repetitions: int
    use_interpolation: bool
    progressive_profiling: bool

# VALIDATIONS = 8

def parse_config():
    with open("experiments.yaml", "r") as f:
        config = yaml.safe_load(f)

    experiments = []
    for exp in config["experiments"]:
        soi = SoIConfig(**exp["soi"])
        experiment = Experiment(
            name=exp["name"],
            benchmarks=exp["benchmarks"],
            reporter=exp["reporter"],
            soi=soi,
            max_mem_footprint=exp["max_mem_footprint"],
            mem_interval=exp["mem_interval"],
            reporter_repetitions=exp["reporter_repetitions"],
            deployment=exp["deployment"],
            root=exp["root"],
            data_size=exp["data_size"],
            profiling_repetitions=exp["profiling_repetitions"],
            use_interpolation=exp["use_interpolation"],
            progressive_profiling=exp["progressive_profiling"]
        )
        experiments.append(experiment)
        print(exp)

    return experiments