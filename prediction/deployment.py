
from typing import List

from experiment_setup.workload import Workload
from dataclasses import dataclass


@dataclass
class Deployment:
    application: Workload
    competitors: List[Workload]