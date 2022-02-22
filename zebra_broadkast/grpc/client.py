import grpc
import os
import uvloop
uvloop.install()
from typing import Optional
from zebra_kube_app_discovery import Query
from zebra_automate_logging import Logger
from .proto import (
    KubeConfigUpdate,
    KubeConfigUpdateResponse,
    ServiceDiscoveryRequest,
    ServiceDiscoveryResponse,
    SelectorQuery,
    BroadkastServerStub
)



class BroadkastClient:

    def __init__(self, config: dict={}) -> None:
        logger = Logger()
        self.session_logger = logger.generate_logger()

        self.broadkast_server_ip = config.get(
            'broadkast_server_ip',
            os.getenv(
                'BROADKAST_SERVER_IP',
                'localhost'
            )
        )

        self.broadkast_server_port = config.get(
            'broadkast_server_port',
            os.getenv(
                'BROADKAST_SERVER_PORT',
                4677
            )
        )

        self.broadkast_server_address = config.get(
            'broadkast_server_address',
            os.getenv(
                'BROADKAST_SERVER_ADDRESS'
            )
        )

        if self.broadkast_server_address is None:
            self.broadkast_server_address = f'{self.broadkast_server_ip}:{self.broadkast_server_port}'
            
        self.config_filepath = config.get(
            'kube_config_filepath',
            os.getenv(
                'KUBE_CONFIG_FILEPATH'
            )
        )

        self.config_context = config.get(
            'kube_config_context',
            os.getenv(
                'KUBE_CONFIG_CONTEXT'
            )
        )

        self.namespace = config.get(
            'namespace',
            os.getenv(
                'namespace',
                'default'
            )
        )

        self.channel = grpc.aio.insecure_channel(self.broadkast_server_address)
        self.service = BroadkastServerStub(self.channel)
        

    async def update_cluster_config(self, config_filepath: str, config_context: str, namespace: str=None) -> KubeConfigUpdateResponse:

        self.config_filepath = config_filepath
        self.config_context = config_context

        if namespace:
            self.namespace = namespace
        
        update_request = KubeConfigUpdate(
            config_filepath=config_filepath,
            config_context=config_context,
            namespace=namespace
        )

        update_response: KubeConfigUpdateResponse = await self.service.UpdateClusterConfig(update_request)

        return update_response

    async def discover_service(self, service_name: str, query: Optional[Query]=None, method: Optional[str]=None, service_port: Optional[str]=None, is_new_service=True) -> ServiceDiscoveryResponse:
        discovery_request = ServiceDiscoveryRequest(
            method=method,
            service_name=service_name,
            namespace=self.namespace,
            service_port=service_port,
            is_new_service=is_new_service
        )

        if query:
            if query.fields:
                discovery_request.field_selectors.extend([
                    SelectorQuery(
                        **field.to_dict()
                    ) for field in query.fields
                ])

            if query.labels:
                discovery_request.label_selectors.extend([
                    SelectorQuery(
                        **label.to_dict()
                    ) for label in query.labels
                ])

        discovery_response: ServiceDiscoveryResponse = await self.service.DiscoverService(discovery_request)

        return discovery_response
