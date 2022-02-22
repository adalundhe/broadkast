import os
import asyncio
from typing import Any, List, Union
from kubernetes import (
    client, 
    config as kube_config
)
from zebra_automate_logging import Logger
from .queries import Query
from .instance_ports_collection import InstancePortsCollection
from .instance import Instance
        

class InstanceIndex:

    def __init__(self, config: dict=None) -> None:

        logger = Logger()
        logger.setup('info')

        self.session_logger = logger.generate_logger()
        
        self.config_filepath = None
        self.config_context = None
        self.namespace = None
        self.v1Core = None
        self.instances = {}

        if config:
            self.config_filepath = config.get(
                'kube_config_filepath',
                os.getenv('KUBE_CONFIG_FILEPATH')
            )
            self.config_context = config.get(
                'kube_config_context',
                os.getenv('KUBE_CONFIG_CONTEXT')
            )
            
            kube_config.load_kube_config(
                config_file=self.config_filepath, 
                context=self.config_context
            )
            

            self.namespace = config.get('namespace', 'default')
            self.v1Core = client.CoreV1Api()

        try:
            self.loop = asyncio.get_event_loop()
        
        except Exception:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def __getitem__(self, key) -> Union[InstancePortsCollection, None]:
        return self.instances.get(key)

    async def update_kube_settings(self, config: dict) -> None:

        self.config_filepath = config.get('kube_config_filepath')
        self.config_context = config.get('kube_config_context')

        kube_config.load_kube_config(
            config_file=self.config_filepath, 
            context=self.config_context
        )

        self.namespace = config.get('namespace')
        if self.namespace is None:
            self.namespace = 'default'

        self.v1Core = client.CoreV1Api()

    async def get_instances_by_pod(self, key: str, query: Query=None) -> None:

        if query is None:
            query = Query()

        await query.to_selectors()

        discovered = await self._get_instance_ips_by_pod(query)
        await self._assemble_instances(key, discovered.get('ips'), discovered.get('ports'))

    async def get_instances_by_endpoint(self, key: str, query: Query=None) -> None:

        if query is None:
            query = Query()

        await query.to_selectors()

        discovered = await self._get_instance_ips_by_endpoint(query)
        await self._assemble_instances(key, discovered.get('ips'), discovered.get('ports'))

    async def _assemble_instances(self, key: str, service_ips: List[str], service_ports: List[int]):

        instance_ports = self.instances.get(key, InstancePortsCollection(key))
        
        for service_ip in service_ips:
            for service_port in service_ports:
                await instance_ports.append_instance(
                    str(service_port),
                    Instance(key, service_ip, service_port)
                )

        self.instances[key] = instance_ports

    async def _get_instance_ips_by_pod(self, query: Query) -> List[str]:

        pods = await self.loop.run_in_executor(
            None,
            self._list_namespaced_pods,
            query
        )
        
        instance_ips = [item.status.pod_ip for item in pods.items] 
        instance_ports = set()
        for item in pods.items:
            for container in item.spec.containers:
                for port in container.ports:
                    instance_ports.add(port.container_port)
                
        return {
            'ips': instance_ips,
            'ports': list(instance_ports)
        }

    async def _get_instance_ips_by_endpoint(self, query: Query) -> List[str]:

        endpoints = await self.loop.run_in_executor(
            None,
            self._list_namespaced_endpoints,
            query
        )

        instance_ips = []
        instance_ports = set()
        for item in endpoints.items:
            subsets = item.subsets or []
            for subset in subsets:
                addresses = subset.addresses or []
                ports = subset.ports or []

                for address in addresses:
                    instance_ips.append(address.ip)

                for port in ports:
                    instance_ports.add(port.port)

        return {
            'ips': instance_ips,
            'ports': instance_ports
        }

    def _list_namespaced_pods(self, query: Query) -> List[Any]:
        return self.v1Core.list_namespaced_pod(
            self.namespace,
            label_selector=query.label_selectors,
            field_selector=query.field_selectors
        )

    def _list_namespaced_endpoints(self, query: Query) -> List[Any]:
        return self.v1Core.list_namespaced_endpoints(
            self.namespace,
            label_selector=query.label_selectors,
            field_selector=query.field_selectors
        )