import pathlib
from py_containters.kube_controller import KubeController
from py_containters.kube_workload import KubeWorkload
import config

class MdsFactory:
    METRICS = {
        "datageneration": "datageneration_datagen_req_duration_bucket",
        "dataforwarding": "dataforwarding_datafwd_req_duration_bucket",
        "datatest": "datatest_datatest_req_duration_bucket",
        # Planner is not currently used in the experiments, because it contains a timer
        # which makes it's performance unaffected by resource contention
        "planner": "planning_planner_schedule_calc_bucket"
    }

    YAML_ROOT = pathlib.Path("mds/yaml")

    def __init__(self):
        self.controller = KubeController()
    
    def create_workload(self, mds_service_name: str, is_required: bool = True) -> KubeWorkload:
        metric = MdsFactory.METRICS.get(mds_service_name, None)
        yaml_file_name = f"{mds_service_name}.yaml"
        return KubeWorkload(
            mds_service_name,
            MdsFactory.YAML_ROOT / yaml_file_name,
            self.controller,
            is_required,
            config.MDS_PROFILING_TIME_S,
            metric_name=metric
        )