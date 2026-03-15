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
        )
        experiments.append(experiment)
        print(exp)

    return experiments