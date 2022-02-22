import os
from typing import Any, List
import uuid
from zebra_automate_logging import Logger
from zebra_kube_app_discovery import InstanceIndex, Query
from zebra_broadkast.registry import DiscoveredRegistry
from .client import BroadkastClient
from google.protobuf.json_format import MessageToDict
from .proto import (
    KubeConfigUpdate,
    KubeConfigUpdateResponse,
    ServiceDiscoveryRequest,
    ServiceDiscoveryResponse,
    BroadkastServerServicer,
    DiscoveredService
)


class BroadkastServicer(BroadkastServerServicer):

    def __init__(self, config) -> None:
        logger = Logger()
        self.service_id = str(uuid.uuid4())
        self.config = config
        self.session_logger = logger.generate_logger()
        self.index = InstanceIndex(config)
        
        self.clients: List[BroadkastClient] = []
        self.replicas: List[str] = []
        self.registry = DiscoveredRegistry()

        self.broadkast_server_port = config.get(
            'broadkast_server_port', 
            os.getenv(
                'BROADKAST_SERVER_PORT',
                4677
            )
        )

    async def discover_replicas(self) -> None:
        self.replicas = await self.index.discover_service(
            'broadkast_server',
            query=Query(
                labels=[
                    {
                        'name': 'app',
                        'value': 'broadkast'
                    },
                    {
                        'name': 'role',
                        'value': 'server'
                    }
                ],
                service_port=self.broadkast_server_port
            )
        )

        for instance in self.replicas:
            if instance.instance_id != self.service_id:
                client= BroadkastClient(config={
                    'broadkast_server_address': instance.instance_address,
                    'kube_config_filepath': self.config.get(
                        'kube_config_filepath',
                        os.getenv(
                            'KUBE_CONFIG_FILEPATH'
                        )
                    ),
                    'kube_config_context': self.config.get(
                        'kube_config_context',
                        os.getenv(
                            'KUBE_CONFIG_CONTEXT'
                        )
                    )
                })

                self.clients.append(client)
        

    async def UpdateClusterConfig(self, request: KubeConfigUpdate, context: Any) -> KubeConfigUpdateResponse:
        await self.index.update_kube_settings({
            'kube_config_filepath': request.config_filepath,
            'kube_config_context': request.config_context,
            'namespace': request.namespace
        })

        return KubeConfigUpdateResponse(
            config_filepath=self.index.config_filepath,
            config_context=self.index.config_context,
            namespace=self.index.namespace,
            status='OK'
        )

    async def DiscoverService(self, request: ServiceDiscoveryRequest, context) -> ServiceDiscoveryResponse:
        
        field_selectors = None
        label_selectors = None

        self.index.namespace = request.namespace

        if request.field_selectors:
            field_selectors = [
                MessageToDict(field_selector) for field_selector in request.field_selectors
            ]

        if request.label_selectors:
            label_selectors = [
                MessageToDict(label_selector) for label_selector in request.label_selectors
            ]

        query = Query(
            fields=field_selectors,
            labels=label_selectors
        )

        print(request.service_name , self.index.instances)

        if request.service_name not in self.index.instances:

            if request.method == '' or request.method == "pod":
                await self.index.get_instances_by_pod(
                    request.service_name,
                    query=query
                )

            else:
                await self.index.get_instances_by_endpoint(
                    request.service_name,
                    query=query
                )
            
        if request.service_port:
            discovered = await self.index[request.service_name].addresses(
                request.service_port
            )
        else:
            discovered = await self.index[request.service_name].all()
            

        for instance in discovered:
            await self.registry.register_instance(
                request.service_name,
                instance
            )

        if request.is_new_service:
            for client in self.clients:

                await client.update_cluster_config(
                    self.index.config_filepath,
                    self.index.config_context,
                    namespace='dev'
                )

                await client.discover_service(
                    request.service_name,
                    query=Query(
                        labels=label_selectors,
                        fields=field_selectors
                    ),
                    service_port=request.service_port,
                    method=request.method,
                    is_new_service=False
                )

        response = ServiceDiscoveryResponse(
            service_name=request.service_name
        )

        response.instances.extend([
            DiscoveredService(
                service_name=request.service_name,
                instance_address=instance.instance_address,
                instance_id=str(instance.instance_id)
            ) for instance in self.registry[request.service_name]
        ])

        return response