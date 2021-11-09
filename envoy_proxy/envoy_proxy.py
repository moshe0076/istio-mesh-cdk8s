from constructs import Construct, Node
from typing import List
from pathlib import Path

from imports import k8s
import yaml


class EnvoyProxy(Construct):
    def __init__(self, scope: Construct, id: str, *,
                 metadata_name: str,
                 metadata_namespace: str,
                 labels: dict,
                 image: str,
                 replicas: int = 1,
                 env_vars: List[k8s.EnvVar],
                 port: int,
                 container_port: int = 8080):
        super().__init__(scope, id)
        envoy_proxy_config_file_path = str(Path(__file__).parent) + '/envoy-proxy.yaml'
        with open(envoy_proxy_config_file_path) as file:
            test = file.read()

        envoy_configmap = k8s.KubeConfigMap(
            self,
            "envoy_configmap",
            metadata=k8s.ObjectMeta(
                namespace=metadata_namespace,
                name=metadata_name,
                labels=labels
            ),
            data={
                "envoy.yaml": test
            }
        )

        k8s.KubeService(self, 'service',
                        metadata=k8s.ObjectMeta(
                            namespace=metadata_namespace,
                            name=metadata_name,
                            labels=labels

                        ),
                        spec=k8s.ServiceSpec(
                          type='ClusterIP',
                          ports=[k8s.ServicePort(port=port, target_port=k8s.IntOrString.from_number(container_port))],
                          selector=labels))

        k8s.KubeDeployment(self, 'deployment',
                           metadata=k8s.ObjectMeta(
                               namespace=metadata_namespace,
                               name=metadata_name,
                               labels=labels
                           ),
                           spec=k8s.DeploymentSpec(
                               replicas=replicas,
                               selector=k8s.LabelSelector(match_labels=labels),
                               template=k8s.PodTemplateSpec(
                                   metadata=k8s.ObjectMeta(
                                       namespace=metadata_namespace,
                                       name=metadata_name,
                                       labels=labels
                                   ),
                                   spec=k8s.PodSpec(
                                       containers=[
                                           k8s.Container(
                                               name=metadata_name,
                                               image=image,
                                               env=env_vars,
                                               ports=[k8s.ContainerPort(container_port=container_port)],
                                               volume_mounts=[
                                                   k8s.VolumeMount(
                                                       name="envoy-proxy-config",
                                                       mount_path="/etc/envoy/envoy.yaml",
                                                       sub_path="envoy.yaml"
                                                   )
                                               ]
                                           )
                                       ],
                                       volumes=[
                                           k8s.Volume(
                                               name="envoy-proxy-config",
                                               config_map=k8s.ConfigMapVolumeSource(
                                                   name=envoy_configmap.name
                                               )

                                           )
                                       ]
                                   )
                               )
                           ))
