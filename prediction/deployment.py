
from typing import List

from experiment_setup.workload import Workload
from dataclasses import dataclass
import random

@dataclass
class Deployment:
    application: Workload
    competitors: List[Workload]

    def __str__(self):
        competitors_str = ", ".join([str(c) for c in self.competitors])
        return f"Application: {self.application}, Competitors: [{competitors_str}]"
    

def create_random_deployment(ncompetitors: int, all_workloads: List[Workload]) -> Deployment:
    app = random.choice(all_workloads)
    competitors = random.sample([b for b in all_workloads if b != app], ncompetitors)
    return Deployment(application=app, competitors=competitors)