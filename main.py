#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart
from web_service import web_service
from envoy_proxy import envoy_proxy
from imports import k8s


class WebServicesChart(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        k8s.KubeNamespace(
            self,
            "web_services_namespace",
            metadata=k8s.ObjectMeta(
                name="webservices",
                labels={
                    "name": "webservices"
                }
            )
        )

        web_service.WebService(self,
                               'front-end-v1',
                               metadata_namespace="webservices",
                               metadata_name="front-end-v1",
                               labels={
                                   "app": "front-end-v1"
                               },
                               image='moshen/istio-mesh:latest',
                               replicas=1,
                               env_vars=[
                                   k8s.EnvVar(
                                       name="APP_NAME",
                                       value="front-end"
                                   ),
                                   k8s.EnvVar(
                                       name="APP_VERSION",
                                       value="V1"
                                   ),
                               ],
                               port=8080)
        web_service.WebService(self,
                               'front-end-v2',
                               metadata_namespace="webservices",
                               metadata_name="front-end-v2",
                               labels={
                                   "app": "front-end-v2"
                               },
                               image='moshen/istio-mesh:latest',
                               replicas=1,
                               env_vars=[
                                   k8s.EnvVar(
                                       name="APP_NAME",
                                       value="front-end"
                                   ),
                                   k8s.EnvVar(
                                       name="APP_VERSION",
                                       value="V2"
                                   ),
                               ],
                               port=8080)


class EnvoyProxyChart(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        envoy_proxy.EnvoyProxy(self,
                               'envoy-proxy',
                               metadata_namespace="webservices",
                               metadata_name="envoy-proxy",
                               labels={
                                   "app": "envoy-proxy"
                               },
                               image='envoyproxy/envoy:v1.20.0',
                               replicas=1,
                               env_vars=[],
                               port=8088,
                               container_port=8088)


app = App()
WebServicesChart(app, "web-services")
EnvoyProxyChart(app, "envoy-proxy")
app.synth()
