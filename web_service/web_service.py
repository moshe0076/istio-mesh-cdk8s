from constructs import Construct, Node
from typing import List

from imports import k8s


class WebService(Construct):
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
                                               ports=[k8s.ContainerPort(container_port=container_port)])]))))
