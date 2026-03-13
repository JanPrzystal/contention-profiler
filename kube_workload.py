from workload import Workload
from kube_controller import KubeController
from typing import Optional
from metrics import query_median_latency
import pathlib
import time
import logging
import config

logger = logging.getLogger(__name__)

class KubeWorkload(Workload):
    def __init__(
        self,
        name: str,
        yaml_path: pathlib.Path,
        controller: KubeController,
        is_required: bool,
        profiling_time_s: int,
        metric_name: Optional[str] = None,
    ):
        self.controller = controller
        self.is_required = is_required
        self.yaml_path = yaml_path
        self.profiling_time_s = profiling_time_s
        self.metric_name = metric_name
        self.deployed_on: Optional[str] = None
        super().__init__(name)

    def setup(self):
        if self.is_required and self.deployed_on is None:
            self._deploy_on_node(config.REMOTE_NODE_NAME)

    def tear_down(self):
        self.controller.remove_application(self.name)

    def _deploy_on_node(self, target_node: str) -> None:
        if self.deployed_on == target_node:
            return
        if self.deployed_on is not None:
            self.controller.remove_application(self.name)
        self.controller.deploy_application(
            self.name, self.yaml_path, target_node
        )
        self.deployed_on = target_node
        logger.info(f"Deployed workload {self.name} on {target_node}")

    def profile(self, cores: str) -> float:
        if not self.metric_name:
                raise Exception(f"Profiling of workload {self.name} is not supported")
        try:
            self._deploy_on_node(config.PROFILING_NODE_NAME)
            # Wait for the microservices to be ready
            time.sleep(config.MDS_STARTUP_WAIT_TIME_S)
            time.sleep(self.profiling_time_s)
            return query_median_latency(self.metric_name, self.profiling_time_s)
        finally:
            self.stop()

    def run_in_background(self, cores) -> None:
        self._deploy_on_node(config.PROFILING_NODE_NAME)

    def stop(self) -> None:
        if self.is_required:
            self._deploy_on_node(config.REMOTE_NODE_NAME)
        else:
            self.controller.remove_application(self.name)