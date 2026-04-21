import kubernetes as kube
import pathlib
import yaml
from abc import ABC, abstractmethod
from typing import Optional, List
from copy import deepcopy
import logging


class Resource(ABC):
    def __init__(self, doc: dict):
        self.doc = doc
        self.name = doc["metadata"]["name"]

    def create(self):
        try:
            self._create()
            logging.debug(f"Resource {self.name} created")
        except kube.client.ApiException as e:
            if e.status != 409:
                raise e
            else:
                logging.debug(
                    f"Resource {self.name} already exists, replacing resource..."
                )
                self.delete()
                self._create()
                logging.debug(f"Resource {self.name} replaced")

    def delete(self):
        try:
            self._delete()
            f"Resource {self.name} deleted"
        except kube.client.ApiException as e:
            if e.status != 404:
                raise e
            else:
                logging.debug(f"Tried to delete non-existent resource {self.name}")

    @abstractmethod
    def _create(self):
        pass

    @abstractmethod
    def _delete(self):
        pass


class StatefulSet(Resource):
    def __init__(
        self, client: kube.client.ApiClient, doc: dict, node_name: Optional[str] = None
    ):
        self.apps = kube.client.AppsV1Api(client)
        self.node_name = node_name
        super().__init__(doc)

    def _create(self):
        doc = deepcopy(self.doc)
        if self.node_name:
            StatefulSet._inject_node_selector(doc, self.node_name)

        self.apps.create_namespaced_stateful_set("default", body=doc)

    @staticmethod
    def _inject_node_selector(doc: dict, node_name: str):
        if "spec" not in doc or not isinstance(doc["spec"], dict):
            doc["spec"] = {}
        template = doc["spec"].get("template")
        if template is None or not isinstance(template, dict):
            template = {}
            doc["spec"]["template"] = template
        pod_spec = template.get("spec")
        if pod_spec is None or not isinstance(pod_spec, dict):
            pod_spec = {}
            template["spec"] = pod_spec

        pod_spec["nodeSelector"] = {"kubernetes.io/hostname": node_name}

    def _delete(self):
        self.apps.delete_namespaced_stateful_set(self.name, "default")


class Service(Resource):
    def __init__(self, client: kube.client.ApiClient, doc: dict):
        self.core = kube.client.CoreV1Api(client)
        super().__init__(doc)

    def _create(self):
        self.core.create_namespaced_service("default", body=self.doc)

    def _delete(self):
        self.core.delete_namespaced_service(self.name, "default")


class ServiceMonitor(Resource):

    GROUP = "monitoring.coreos.com"
    VERSION = "v1"
    PLURAL = "servicemonitors"

    def __init__(self, client: kube.client.ApiClient, doc: dict):
        self.custom_objects = kube.client.CustomObjectsApi(client)
        super().__init__(doc)

    def _create(self):
        self.custom_objects.create_namespaced_custom_object(
            ServiceMonitor.GROUP,
            ServiceMonitor.VERSION,
            "default",
            ServiceMonitor.PLURAL,
            body=self.doc,
        )

    def _delete(self):
        self.custom_objects.delete_namespaced_custom_object(
            ServiceMonitor.GROUP,
            ServiceMonitor.VERSION,
            "default",
            ServiceMonitor.PLURAL,
            self.name,
        )


class KubeController:
    def __init__(self):
        kube.config.load_kube_config()
        self.client = kube.client.ApiClient()
        self.applications: dict[str, List[Resource]] = {}
        self.application_nodes: dict[str, str] = {}

    def deploy_application(self, name: str, yaml_path: pathlib.Path, node_name: str):
        if name in self.applications:
            raise ValueError(f"Application with name {name} already exists")
        logging.debug(f"Deploying application {name} on node {node_name}")
        with open(yaml_path) as f:
            docs = list(yaml.safe_load_all(f))
            self.applications[name] = [
                self._create_resouce(doc, node_name) for doc in docs
            ]
            for resource in self.applications[name]:
                resource.create()
        logging.debug("Deployment complete.")

    def remove_application(self, name: str):
        if name not in self.applications:
            logging.warning(f"Application {name} not registered with KubeController")
        logging.debug(f"Removing application {name}...")
        for resource in self.applications[name]:
            resource.delete()
        del self.applications[name]
        logging.debug("Removal complete.")

    def _create_resouce(self, doc: dict, node_name: Optional[str]) -> Resource:
        match (doc["kind"]):
            case "StatefulSet":
                return StatefulSet(self.client, doc, node_name)
            case "Service":
                return Service(self.client, doc)
            case "ServiceMonitor":
                return ServiceMonitor(self.client, doc)
            case _:
                raise Exception(f"Resource kind unsupported: {doc['kind']}")
